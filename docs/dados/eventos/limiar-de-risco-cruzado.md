# LimiarDeRiscoCruzado

A avaliação de risco de um posto cruzou limiar pré-declarado — gatilho único de abertura de caso.

| Campo | Valor |
|---|---|
| Emissor | Serviço de risco |
| Contexto | risco |
| `type` | `br.combustiveis.risco.limiar.de.risco.cruzado.v1` |
| Chave de idempotência | `(posto_id, modelo, versao, janela)` |
| Garantia de ordem | por posto |
| Consumidores v1 | Investigador (via Sentinela) |

## Payload (`data`)

```json
{
  "posto_id": "string",
  "modelo": "string",
  "versao": "string",
  "janela": "string",
  "score": "decimal",
  "limiar": "decimal",
  "cobertura": "decimal",
  "razoes_topk": "array de {feature, contribuicao}"
}
```

Tipos acima são descritivos; o JSON Schema formal versionado acompanha a implementação e valida no outbox.

## Semântica e garantias

- Score abaixo de cobertura mínima NÃO emite — dado insuficiente não vira caso.
- `razoes_topk` viaja junto: o caso nasce explicável.
- Este evento é interno — jamais chega a webhook externo.
