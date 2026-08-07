# SnapshotPublicado

Nova versão materializada as-of está disponível para rotas quentes.

| Campo | Valor |
|---|---|
| Emissor | Contexto de Entrega |
| Contexto | entrega |
| `type` | `br.combustiveis.entrega.snapshot.publicado.v1` |
| Chave de idempotência | `(versao_snapshot)` |
| Garantia de ordem | global |
| Consumidores v1 | Cache (invalidação por versão) · ficha pública (revalidação SSG) · API |

## Payload (`data`)

```json
{
  "versao_snapshot": "string",
  "as_of_validade": "timestamp",
  "as_of_transacao": "timestamp",
  "escopos": "array (ficha, ranking, series)"
}
```

Tipos acima são descritivos; o JSON Schema formal versionado acompanha a implementação e valida no outbox.

## Semântica e garantias

- Invalidação de cache é por troca de versão na chave — nunca delete seletivo.
- A ficha pública declara a versão que exibe; 'atual' = snapshot mais recente, não now().
