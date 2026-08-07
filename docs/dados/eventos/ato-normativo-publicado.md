# AtoNormativoPublicado

A varredura do Diário Oficial detectou ato novo ou alteração de vigência relevante.

| Campo | Valor |
|---|---|
| Emissor | Analista regulatório |
| Contexto | normativo |
| `type` | `br.combustiveis.normativo.ato.normativo.publicado.v1` |
| Chave de idempotência | `(orgao, ato_id, versao)` |
| Garantia de ordem | por órgão |
| Consumidores v1 | RAG (reindexação) · Serviço de risco (reavaliação de limites) · webhooks |

## Payload (`data`)

```json
{
  "orgao": "ANP | Inmetro | outro",
  "ato_id": "string",
  "versao": "string",
  "vigencia_inicio": "date",
  "altera": "array de ato_id",
  "resumo_impacto": "string"
}
```

Tipos acima são descritivos; o JSON Schema formal versionado acompanha a implementação e valida no outbox.

## Semântica e garantias

- Mudança de limite de especificação (ex.: E30/B15) dispara reavaliação de modelos — consumo obrigatório pelo Risco.
- `altera` mantém o encadeamento de vigências — ato alterador nunca substitui, encadeia.
