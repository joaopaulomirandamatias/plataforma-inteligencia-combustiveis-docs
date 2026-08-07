# PrecoSemanalRegistrado

Preço de um posto numa semana ANP entrou na série.

| Campo | Valor |
|---|---|
| Emissor | Contexto de Preços |
| Contexto | precos |
| `type` | `br.combustiveis.precos.preco.semanal.registrado.v1` |
| Chave de idempotência | `(posto_id, semana, produto)` |
| Garantia de ordem | por posto |
| Consumidores v1 | Detector de anomalia de preço |

## Payload (`data`)

```json
{
  "posto_id": "string",
  "semana": "AAAA-Www",
  "produto": "string",
  "preco": "decimal",
  "localizador": "linhagem"
}
```

Tipos acima são descritivos; o JSON Schema formal versionado acompanha a implementação e valida no outbox.

## Semântica e garantias

- Ausência de evento numa semana = posto não coletado (cobertura), nunca preço zero.
- Anomalia NÃO é calculada aqui — este evento é matéria-prima, o detector consome a série.
