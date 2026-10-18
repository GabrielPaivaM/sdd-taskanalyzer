"""Módulo TaskAnalyzer: métricas de produtividade a partir de tarefas.

O módulo é puramente computacional: não persiste dados, não expõe
interface e utiliza apenas a biblioteca padrão do Python.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

PRIORIDADES_VALIDAS: tuple[str, ...] = ("baixa", "media", "alta")
STATUS_VALIDOS: tuple[str, ...] = ("concluida", "pendente", "cancelada")
TITULO_MAX_CARACTERES: int = 120
SEGUNDOS_POR_HORA: float = 3600.0


class TaskValidationError(Exception):
    """Erro levantado quando os dados de entrada violam o contrato."""


@dataclass(frozen=True)
class _Tarefa:
    """Representação interna e já validada de uma tarefa."""

    id_tarefa: int
    prioridade: str
    status: str
    data_criacao: datetime
    prazo: datetime
    data_conclusao: datetime | None


def _validar_id(tarefa: dict[str, Any]) -> int:
    """Valida o campo id_tarefa.

    Args:
        tarefa: Dicionário bruto da tarefa.

    Returns:
        O identificador validado.

    Raises:
        TaskValidationError: Se o id estiver ausente, não for int ou for <= 0.
    """
    valor = tarefa.get("id_tarefa")
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise TaskValidationError(
            f"Campo 'id_tarefa' deve ser inteiro positivo; recebido: {valor!r}."
        )
    return valor


def _validar_titulo(tarefa: dict[str, Any], id_tarefa: int) -> None:
    """Valida o campo titulo.

    Args:
        tarefa: Dicionário bruto da tarefa.
        id_tarefa: Identificador da tarefa, usado na mensagem de erro.

    Raises:
        TaskValidationError: Se o título for vazio, não for str ou exceder 120.
    """
    titulo = tarefa.get("titulo")
    if not isinstance(titulo, str) or not titulo.strip():
        raise TaskValidationError(
            f"Tarefa {id_tarefa}: campo 'titulo' deve ser texto não vazio."
        )
    if len(titulo) > TITULO_MAX_CARACTERES:
        raise TaskValidationError(
            f"Tarefa {id_tarefa}: 'titulo' excede {TITULO_MAX_CARACTERES} caracteres."
        )


def _validar_texto_enum(
    tarefa: dict[str, Any],
    campo: str,
    permitidos: tuple[str, ...],
    id_tarefa: int,
    ignorar_caixa: bool,
) -> str:
    """Valida um campo textual restrito a um conjunto de valores.

    Args:
        tarefa: Dicionário bruto da tarefa.
        campo: Nome do campo a validar.
        permitidos: Valores aceitos.
        id_tarefa: Identificador da tarefa, usado na mensagem de erro.
        ignorar_caixa: Se True, compara sem distinção de maiúsculas.

    Returns:
        O valor validado (em minúsculas quando ignorar_caixa é True).

    Raises:
        TaskValidationError: Se o campo estiver ausente ou fora do domínio.
    """
    valor = tarefa.get(campo)
    if not isinstance(valor, str):
        raise TaskValidationError(
            f"Tarefa {id_tarefa}: campo '{campo}' ausente ou não é texto."
        )
    normalizado = valor.lower() if ignorar_caixa else valor
    if normalizado not in permitidos:
        raise TaskValidationError(
            f"Tarefa {id_tarefa}: '{campo}' inválido ({valor!r}); "
            f"aceitos: {', '.join(permitidos)}."
        )
    return normalizado


def _validar_data(valor: Any, campo: str, id_tarefa: int) -> datetime:
    """Valida que um valor é datetime com fuso horário definido.

    Args:
        valor: Valor a validar.
        campo: Nome do campo, usado na mensagem de erro.
        id_tarefa: Identificador da tarefa, usado na mensagem de erro.

    Returns:
        O datetime validado.

    Raises:
        TaskValidationError: Se não for datetime ou não tiver fuso horário.
    """
    if not isinstance(valor, datetime):
        raise TaskValidationError(
            f"Tarefa {id_tarefa}: campo '{campo}' deve ser datetime."
        )
    if valor.tzinfo is None or valor.utcoffset() is None:
        raise TaskValidationError(
            f"Tarefa {id_tarefa}: campo '{campo}' deve ter fuso horário (UTC)."
        )
    return valor


def _validar_conclusao(
    tarefa: dict[str, Any], status: str, criacao: datetime, id_tarefa: int
) -> datetime | None:
    """Valida data_conclusao conforme o status da tarefa.

    Args:
        tarefa: Dicionário bruto da tarefa.
        status: Status já validado.
        criacao: Data de criação já validada.
        id_tarefa: Identificador da tarefa, usado na mensagem de erro.

    Returns:
        A data de conclusão, ou None quando a tarefa não está concluída.

    Raises:
        TaskValidationError: Se a data for incoerente com o status ou anterior
            à data de criação.
    """
    valor = tarefa.get("data_conclusao")
    if status != "concluida":
        if valor is not None:
            raise TaskValidationError(
                f"Tarefa {id_tarefa}: 'data_conclusao' deve ser None "
                f"quando o status é '{status}'."
            )
        return None
    if valor is None:
        raise TaskValidationError(
            f"Tarefa {id_tarefa}: 'data_conclusao' é obrigatória para 'concluida'."
        )
    conclusao = _validar_data(valor, "data_conclusao", id_tarefa)
    if conclusao < criacao:
        raise TaskValidationError(
            f"Tarefa {id_tarefa}: 'data_conclusao' anterior a 'data_criacao'."
        )
    return conclusao


def _validar_tarefa(tarefa: Any) -> _Tarefa:
    """Valida uma tarefa completa e a converte para a forma interna.

    Args:
        tarefa: Dicionário bruto da tarefa.

    Returns:
        A tarefa validada.

    Raises:
        TaskValidationError: Se qualquer campo violar o contrato.
    """
    if not isinstance(tarefa, dict):
        raise TaskValidationError("Cada tarefa deve ser um dicionário.")
    id_tarefa = _validar_id(tarefa)
    _validar_titulo(tarefa, id_tarefa)
    prioridade = _validar_texto_enum(
        tarefa, "prioridade", PRIORIDADES_VALIDAS, id_tarefa, ignorar_caixa=True
    )
    status = _validar_texto_enum(
        tarefa, "status", STATUS_VALIDOS, id_tarefa, ignorar_caixa=False
    )
    criacao = _validar_data(tarefa.get("data_criacao"), "data_criacao", id_tarefa)
    prazo = _validar_data(tarefa.get("prazo"), "prazo", id_tarefa)
    if prazo < criacao:
        raise TaskValidationError(
            f"Tarefa {id_tarefa}: 'prazo' anterior a 'data_criacao'."
        )
    conclusao = _validar_conclusao(tarefa, status, criacao, id_tarefa)
    return _Tarefa(id_tarefa, prioridade, status, criacao, prazo, conclusao)


def _validar_tarefas(tasks: Any) -> list[_Tarefa]:
    """Valida a lista de tarefas e garante ids únicos.

    Args:
        tasks: Lista bruta de dicionários.

    Returns:
        Lista de tarefas validadas (vazia se a entrada for vazia).

    Raises:
        TaskValidationError: Se a entrada não for lista, houver ids repetidos
            ou alguma tarefa for inválida.
    """
    if not isinstance(tasks, list):
        raise TaskValidationError("A entrada deve ser uma lista de tarefas.")
    validadas = [_validar_tarefa(tarefa) for tarefa in tasks]
    ids = [tarefa.id_tarefa for tarefa in validadas]
    if len(ids) != len(set(ids)):
        raise TaskValidationError("Existem tarefas com 'id_tarefa' repetido.")
    return validadas


def _horas_de_conclusao(tarefa: _Tarefa) -> float:
    """Calcula o tempo, em horas, entre criação e conclusão.

    Args:
        tarefa: Tarefa concluída.

    Returns:
        Duração em horas.
    """
    if tarefa.data_conclusao is None:
        return 0.0
    delta = tarefa.data_conclusao - tarefa.data_criacao
    return delta.total_seconds() / SEGUNDOS_POR_HORA


def _media_horas(tarefas: list[_Tarefa]) -> float:
    """Calcula o tempo médio de conclusão, evitando divisão por zero.

    Args:
        tarefas: Tarefas concluídas.

    Returns:
        Média em horas, ou 0.0 se a lista estiver vazia.
    """
    if not tarefas:
        return 0.0
    return sum(_horas_de_conclusao(t) for t in tarefas) / len(tarefas)


def _taxa_atraso(tarefas: list[_Tarefa]) -> float:
    """Calcula o percentual de tarefas concluídas após o prazo.

    Args:
        tarefas: Tarefas concluídas.

    Returns:
        Percentual de 0.0 a 100.0, ou 0.0 se a lista estiver vazia.
    """
    if not tarefas:
        return 0.0
    atrasadas = sum(
        1
        for t in tarefas
        if t.data_conclusao is not None and t.data_conclusao > t.prazo
    )
    return atrasadas / len(tarefas) * 100


def _calcular_metricas(tarefas: list[_Tarefa]) -> dict[str, Any]:
    """Monta o dicionário de métricas a partir de tarefas já validadas.

    Args:
        tarefas: Tarefas validadas.

    Returns:
        Dicionário de métricas, com floats arredondados a duas casas.
    """
    concluidas = [t for t in tarefas if t.status == "concluida"]
    por_prioridade = {
        prioridade: round(
            _media_horas([t for t in concluidas if t.prioridade == prioridade]), 2
        )
        for prioridade in PRIORIDADES_VALIDAS
    }
    return {
        "total_tarefas": len(tarefas),
        "total_concluidas": len(concluidas),
        "total_pendentes": sum(1 for t in tarefas if t.status == "pendente"),
        "tempo_medio_conclusao_horas": round(_media_horas(concluidas), 2),
        "tempo_medio_conclusao_horas_por_prioridade": por_prioridade,
        "taxa_atraso_percentual": round(_taxa_atraso(concluidas), 2),
    }


def analyze_tasks(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Calcula métricas de produtividade a partir de uma lista de tarefas.

    Args:
        tasks: Lista de dicionários, cada um com os campos id_tarefa, titulo,
            prioridade, status, data_criacao, prazo e data_conclusao.

    Returns:
        Dicionário com total_tarefas, total_concluidas, total_pendentes,
        tempo_medio_conclusao_horas, tempo_medio_conclusao_horas_por_prioridade
        e taxa_atraso_percentual.

    Raises:
        TaskValidationError: Se a entrada violar o contrato da especificação.
    """
    logger.info("Iniciando análise de tarefas.")
    try:
        tarefas = _validar_tarefas(tasks)
    except TaskValidationError as erro:
        logger.error("Entrada inválida: %s", erro)
        raise
    metricas = _calcular_metricas(tarefas)
    logger.info("Análise concluída: %d tarefa(s).", metricas["total_tarefas"])
    return metricas
