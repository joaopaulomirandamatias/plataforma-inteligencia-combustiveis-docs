# Model Cards — índice e template

Um card por modelo, obrigatório antes da homologação ([governança](../governanca-de-modelo.md)). O card responde o que um auditor perguntaria — antes de ele perguntar.

## Modelos

| Modelo | Card | Status |
|---|---|---|
| Risco de não conformidade | [risco-nao-conformidade.md](risco-nao-conformidade.md) | especificação inicial |
| Anomalia de preço | *a especificar na implementação* | — |
| Classificador de pares (identidade) | especificado em [entity-resolution](../../dados/entity-resolution.md) §4; card na implementação | — |

## Template

```markdown
# <nome do modelo> — vN

## Objetivo e unidade de decisão
O que prevê, para decidir o quê, sobre qual unidade (posto? bomba? par?).

## Dados
Período, fontes (F01..F10), gabarito, exclusões e por quê.

## Features
Referência ao feature store (nome + versão) — nunca lista solta.
Confirmação explícita do corte temporal (transacao, não validade).

## Métricas
As do protocolo congelado, com intervalo e baseline. Nada além delas.

## Limites conhecidos
Onde o modelo NÃO vale: cobertura mínima, regiões sub-representadas,
vieses do gabarito, condições de rejeição.

## Fairness e cobertura
Quem está sub-representado no dado e o que isso implica na saída.

## Versão, responsável, aprovações
```
