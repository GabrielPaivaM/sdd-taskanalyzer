# sdd-taskanalyzer

Módulo de métricas de produtividade desenvolvido com Spec-Driven Development
(SDD) e assistentes de IA, como parte do Bootcamp III (Fase 2).

O módulo recebe uma lista de tarefas e devolve métricas agregadas: totais,
tempo médio de conclusão (geral e por prioridade) e taxa de atraso.

## Estrutura

| Caminho | Finalidade |
|---|---|
| `specs/task_analyzer_spec.md` | Contrato SDD (fonte da verdade) |
| `CONTEXT_RULES.md` | Regras de governança para agentes de IA |
| `tests/test_harness.py` | Suíte de testes automatizados (pytest) |
| `src/task_analyzer.py` | Código gerado via IA e homologado por humano |

## Como executar

Requer Python 3.11 ou superior.

```bash
python -m venv venv
# Windows:      venv\Scripts\activate
# Linux/macOS:  source venv/bin/activate
pip install -r requirements.txt
python -m pytest -v --cov=src --cov-report=term-missing
```

## Exemplo de uso

```python
from datetime import datetime, timezone

from src.task_analyzer import analyze_tasks

tarefas = [
    {
        "id_tarefa": 1,
        "titulo": "Escrever especificação",
        "prioridade": "alta",
        "status": "concluida",
        "data_criacao": datetime(2026, 1, 5, 9, 0, tzinfo=timezone.utc),
        "prazo": datetime(2026, 1, 7, 9, 0, tzinfo=timezone.utc),
        "data_conclusao": datetime(2026, 1, 6, 9, 0, tzinfo=timezone.utc),
    }
]
print(analyze_tasks(tarefas))
```

## Fluxo de trabalho

Git Flow simplificado: `main` recebe alterações apenas via Pull Request, a
partir de branches `feature/*`. Todo código gerado por IA passa por
homologação humana antes do merge.

## Status do build

Fase 2: testes executados localmente (100% aprovados).
CI/CD com GitHub Actions e Docker entram na Fase 3.
