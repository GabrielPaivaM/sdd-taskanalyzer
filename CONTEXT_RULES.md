# CONTEXT_RULES — TaskAnalyzer

Regras persistentes de governança para agentes de IA. Valem para **toda**
solicitação de geração ou alteração de código neste repositório. Não são
sugestões.

## Diretrizes arquiteturais (obrigatórias)

| Nº | Diretriz |
|---|---|
| DA-01 | Utilizar Python 3.11 ou superior. |
| DA-02 | Aplicar type hints em todas as funções, métodos e atributos públicos, incluindo o tipo de retorno. |
| DA-03 | Seguir o princípio da Responsabilidade Única (SRP): cada função tem um único propósito e um único motivo para mudar. |
| DA-04 | Aderir ao PEP 8: nomes descritivos em snake_case, linhas de até 88 caracteres, imports organizados no topo do arquivo. |
| DA-05 | Documentar módulo, classes e funções com docstrings no padrão Google style, descrevendo Args, Returns e Raises. |
| DA-06 | Manter funções pequenas e coesas, preferencialmente com até 30 linhas de corpo. |
| DA-07 | Validar as entradas em função dedicada, separada da função de cálculo das métricas. |
| DA-08 | Tratar exceções de forma específica, com `TaskValidationError` e mensagens que identifiquem o dado responsável pela falha. |
| DA-09 | Emitir logs com o módulo padrão `logging`, sem `print()`. Nível INFO para o fluxo normal e ERROR para falhas. |
| DA-10 | Usar apenas a biblioteca padrão do Python no módulo de produção. Dependências de teste restritas a pytest e pytest-cov. |
| DA-11 | Manter o código legível e manutenível, com nomes de variáveis e funções descritivos. |

## Proibições explícitas

| Nº | Proibição |
|---|---|
| PR-01 | Não utilizar bibliotecas externas não autorizadas nesta especificação. |
| PR-02 | Não alterar, remover ou adaptar os cenários de teste fornecidos. |
| PR-03 | Não modificar a estrutura de pastas definida para o repositório. |
| PR-04 | Não persistir dados em arquivos, bancos de dados ou serviços externos. |
| PR-05 | Não alterar a assinatura (nome e parâmetros) das funções públicas sem autorização registrada na especificação. |
| PR-06 | Não gerar código de funcionalidade sem os testes correspondentes. |
| PR-07 | Não inserir código duplicado, morto ou sem necessidade comprovada. |
| PR-08 | Não assumir comportamentos que não estejam descritos no contrato de negócio. Diante de ambiguidade, solicitar esclarecimento em vez de inferir. |
| PR-09 | Não capturar exceções de forma ampla (`except Exception`) nem silenciar erros. |
| PR-10 | Não comentar código em excesso: comentários apenas onde a intenção não for evidente. |
| PR-11 | Não retornar estrutura diferente da definida na especificação, nem incluir chaves adicionais. |

## Regras de interação com o agente de IA

- Fornecer sempre o contexto completo (especificação e este arquivo) antes de cada solicitação de geração.
- Solicitar uma unidade de código por vez, validando cada entrega antes de avançar.
- Exigir que o agente explique as decisões técnicas adotadas.
- Revisar criticamente todo código gerado antes de qualquer commit, sem exceção.
- Rejeitar e solicitar nova geração sempre que a resposta violar qualquer proibição acima.
- Registrar no repositório as solicitações relevantes e as decisões tomadas.
