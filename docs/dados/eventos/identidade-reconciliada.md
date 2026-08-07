# IdentidadeReconciliada

Nova versão de um cluster de identidade foi publicada.

| Campo | Valor |
|---|---|
| Emissor | Serviço de identidade |
| Contexto | identidade |
| `type` | `br.combustiveis.identidade.identidade.reconciliada.v1` |
| Chave de idempotência | `(cluster_id, versao)` |
| Garantia de ordem | global (por versão) |
| Consumidores v1 | Todos os contextos (o posto_id é o shared kernel) |

## Payload (`data`)

```json
{
  "cluster_id": "string",
  "versao": "integer",
  "posto_id": "string",
  "registros": "array de {fonte, id_na_fonte}",
  "motivo": "nova_evidencia | revisao_humana | correcao"
}
```

Tipos acima são descritivos; o JSON Schema formal versionado acompanha a implementação e valida no outbox.

## Semântica e garantias

- Versões são imutáveis — consumidores tratam a maior versão como corrente.
- Fusões/separações chegam como nova versão; consultas as-of continuam vendo o mapa antigo.
- NÃO carrega golden record completo — quem precisa consulta as-of.
