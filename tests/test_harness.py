"""Test Harness do TaskAnalyzer (pytest).

Traduz os cenários de aceite da especificação v1.1 em testes automatizados.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.task_analyzer import TaskValidationError, analyze_tasks  # noqa: E402

BASE = datetime(2026, 1, 5, 9, 0, tzinfo=timezone.utc)


def _tarefa(
    id_tarefa: int,
    prioridade: str,
    status: str,
    prazo_h: float = 48,
    conclusao_h: float | None = None,
) -> dict[str, Any]:
    """Cria uma tarefa válida; prazo e conclusão em horas após BASE."""
    return {
        "id_tarefa": id_tarefa,
        "titulo": f"Tarefa {id_tarefa}",
        "prioridade": prioridade,
        "status": status,
        "data_criacao": BASE,
        "prazo": BASE + timedelta(hours=prazo_h),
        "data_conclusao": (
            None if conclusao_h is None else BASE + timedelta(hours=conclusao_h)
        ),
    }


@pytest.fixture
def tarefas_validas() -> list[dict[str, Any]]:
    """Cenário 1: cinco tarefas, uma concluída fora do prazo."""
    return [
        _tarefa(1, "alta", "concluida", prazo_h=48, conclusao_h=24),
        _tarefa(2, "alta", "concluida", prazo_h=24, conclusao_h=72),
        _tarefa(3, "media", "concluida", prazo_h=10, conclusao_h=10),
        _tarefa(4, "baixa", "pendente"),
        _tarefa(5, "media", "cancelada"),
    ]


# ---------- Cenário 1: sucesso ----------
def test_metricas_com_tarefas_validas(tarefas_validas):
    resultado = analyze_tasks(tarefas_validas)
    assert resultado["total_tarefas"] == 5
    assert resultado["total_concluidas"] == 3
    assert resultado["total_pendentes"] == 1
    assert resultado["tempo_medio_conclusao_horas"] == 35.33
    assert resultado["taxa_atraso_percentual"] == 33.33


def test_tempo_medio_por_prioridade(tarefas_validas):
    por_prioridade = analyze_tasks(tarefas_validas)[
        "tempo_medio_conclusao_horas_por_prioridade"
    ]
    assert por_prioridade == {"baixa": 0.0, "media": 10.0, "alta": 48.0}


def test_estrutura_do_retorno_e_fixa(tarefas_validas):
    assert set(analyze_tasks(tarefas_validas)) == {
        "total_tarefas",
        "total_concluidas",
        "total_pendentes",
        "tempo_medio_conclusao_horas",
        "tempo_medio_conclusao_horas_por_prioridade",
        "taxa_atraso_percentual",
    }


def test_ordem_das_tarefas_nao_influencia(tarefas_validas):
    assert analyze_tasks(tarefas_validas) == analyze_tasks(tarefas_validas[::-1])


def test_prioridade_sem_distincao_de_caixa():
    tarefa = _tarefa(1, "ALTA", "concluida", conclusao_h=5)
    assert analyze_tasks([tarefa])["tempo_medio_conclusao_horas_por_prioridade"][
        "alta"
    ] == 5.0


# ---------- Casos de borda ----------
def test_conclusao_exatamente_no_prazo():
    tarefa = _tarefa(1, "alta", "concluida", prazo_h=10, conclusao_h=10)
    assert analyze_tasks([tarefa])["taxa_atraso_percentual"] == 0.0


def test_todas_concluidas_com_atraso():
    tarefa = _tarefa(1, "alta", "concluida", prazo_h=1, conclusao_h=5)
    assert analyze_tasks([tarefa])["taxa_atraso_percentual"] == 100.0


def test_lista_vazia_retorna_zeros():
    resultado = analyze_tasks([])
    assert resultado["total_tarefas"] == 0
    assert resultado["tempo_medio_conclusao_horas"] == 0.0
    assert resultado["taxa_atraso_percentual"] == 0.0


def test_apenas_pendentes_retorna_medias_zero():
    resultado = analyze_tasks([_tarefa(1, "alta", "pendente")])
    assert resultado["total_pendentes"] == 1
    assert resultado["tempo_medio_conclusao_horas"] == 0.0
    assert resultado["taxa_atraso_percentual"] == 0.0
    assert resultado["tempo_medio_conclusao_horas_por_prioridade"]["alta"] == 0.0


# ---------- Cenário 2: exceção ----------
def test_data_conclusao_anterior_a_criacao():
    tarefa = _tarefa(7, "alta", "concluida", conclusao_h=-3)
    with pytest.raises(TaskValidationError, match="anterior a 'data_criacao'"):
        analyze_tasks([tarefa])


def _sem_campo(campo: str) -> dict[str, Any]:
    tarefa = _tarefa(1, "alta", "pendente")
    del tarefa[campo]
    return tarefa


def _com(campo: str, valor: Any, **extra: Any) -> dict[str, Any]:
    tarefa = _tarefa(1, "alta", "pendente")
    tarefa[campo] = valor
    tarefa.update(extra)
    return tarefa


@pytest.mark.parametrize(
    "entrada",
    [
        _sem_campo("prioridade"),
        _com("prioridade", "urgente"),
        _com("status", "em_andamento"),
        _com("id_tarefa", 0),
        _com("id_tarefa", True),
        _com("titulo", "   "),
        _com("titulo", "x" * 121),
        _com("data_criacao", datetime(2026, 1, 5, 9, 0)),
        _com("prazo", BASE - timedelta(hours=1)),
        _com("data_conclusao", BASE + timedelta(hours=1)),
        _tarefa(1, "alta", "concluida"),
        "nao_e_dict",
    ],
    ids=[
        "prioridade_ausente",
        "prioridade_fora_do_dominio",
        "status_invalido",
        "id_zero",
        "id_booleano",
        "titulo_vazio",
        "titulo_longo",
        "data_sem_fuso",
        "prazo_antes_da_criacao",
        "pendente_com_conclusao",
        "concluida_sem_conclusao",
        "tarefa_nao_dict",
    ],
)
def test_entrada_invalida_levanta_erro(entrada):
    with pytest.raises(TaskValidationError):
        analyze_tasks([entrada])


def test_ids_duplicados():
    tarefas = [_tarefa(1, "alta", "pendente"), _tarefa(1, "baixa", "pendente")]
    with pytest.raises(TaskValidationError, match="repetido"):
        analyze_tasks(tarefas)


def test_entrada_nao_e_lista():
    with pytest.raises(TaskValidationError, match="lista"):
        analyze_tasks("texto")  # type: ignore[arg-type]
