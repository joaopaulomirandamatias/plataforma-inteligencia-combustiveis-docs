# FonteColetada

Um arquivo de fonte externa foi baixado, validado e depositado na zona bruta.

| Campo | Valor |
|---|---|
| Emissor | Conectores de ingestão |
| Contexto | ingestao |
| `type` | `br.combustiveis.ingestao.fonte.coletada.v1` |
| Chave de idempotência | `(fonte, url, hash_conteudo)` |
| Garantia de ordem | por fonte |
| Consumidores v1 | Curador de dados · linhagem · gatilho de normalização |

## Payload (`data`)

```json
{
  "fonte": "F01..F10",
  "url": "string",
  "hash_conteudo": "sha256 hex",
  "bytes": "integer",
  "coletado_em": "timestamp UTC",
  "esquema_validado": "boolean",
  "quarentena": "boolean"
}
```

Tipos acima são descritivos; o JSON Schema formal versionado acompanha a implementação e valida no outbox.

## Semântica e garantias

- Emitido mesmo quando o arquivo vai para quarentena (`quarentena: true`) — a coleta aconteceu; a carga é que não.
- NÃO significa que o dado foi normalizado ou carregado.
- Hash idêntico ao da coleta anterior é reemissão da fonte: evento sai, consumidores deduplicam pela chave.
