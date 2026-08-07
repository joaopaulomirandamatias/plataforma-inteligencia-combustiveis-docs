# ColetaPMQCRegistrada

Uma amostra do PMQC virou fato bitemporal ligado a um posto reconciliado.

| Campo | Valor |
|---|---|
| Emissor | Contexto de Qualidade |
| Contexto | qualidade |
| `type` | `br.combustiveis.qualidade.coleta.pmqc.registrada.v1` |
| Chave de idempotência | `(posto_id, amostra_id)` |
| Garantia de ordem | por posto |
| Consumidores v1 | Sentinela · Serviço de risco |

## Payload (`data`)

```json
{
  "posto_id": "string",
  "amostra_id": "string",
  "produto": "string",
  "resultado": "conforme | nao_conforme",
  "ensaios_reprovados": "array de string",
  "coletada_em": "date (validade)",
  "localizador": "linhagem"
}
```

Tipos acima são descritivos; o JSON Schema formal versionado acompanha a implementação e valida no outbox.

## Semântica e garantias

- Só é emitido após reconciliação — amostra sem posto_id fica pendente e NÃO gera evento.
- `nao_conforme` é fato oficial da fonte, não juízo da plataforma.
- A data relevante para ML é `coletada_em` (validade), não a de emissão.
