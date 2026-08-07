# LigacaoIdentidadeRevisada

Decisão humana sobre um par candidato da fila de revisão.

| Campo | Valor |
|---|---|
| Emissor | Fila de revisão humana |
| Contexto | identidade |
| `type` | `br.combustiveis.identidade.ligacao.identidade.revisada.v1` |
| Chave de idempotência | `(par_id, decisao_id)` |
| Garantia de ordem | por par |
| Consumidores v1 | Auditoria · Serviço de identidade (active learning) |

## Payload (`data`)

```json
{
  "par_id": "string",
  "decisao_id": "string",
  "decisao": "liga | nao_liga | escala",
  "revisor_papel": "string",
  "justificativa": "string"
}
```

Tipos acima são descritivos; o JSON Schema formal versionado acompanha a implementação e valida no outbox.

## Semântica e garantias

- Toda decisão vira exemplo de treino do classificador (active learning).
- O ator humano vai na trilha de auditoria; aqui circula apenas o papel.
- `escala` = caso difícil promovido a discussão de codebook.
