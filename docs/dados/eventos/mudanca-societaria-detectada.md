# MudancaSocietariaDetectada

O diff mensal do dump da Receita detectou mudança no quadro de uma empresa do universo.

| Campo | Valor |
|---|---|
| Emissor | Contexto de Vínculo Societário |
| Contexto | societario |
| `type` | `br.combustiveis.societario.mudanca.societaria.detectada.v1` |
| Chave de idempotência | `(cnpj, competencia_dump)` |
| Garantia de ordem | por CNPJ |
| Consumidores v1 | Sentinela · Serviço de risco |

## Payload (`data`)

```json
{
  "cnpj": "string",
  "competencia_dump": "AAAA-MM",
  "tipo": "entrada_socio | saida_socio | baixa | reabertura_endereco | mudanca_endereco",
  "pessoa_id": "string (opcional, pseudonimizado)",
  "posto_ids_afetados": "array"
}
```

Tipos acima são descritivos; o JSON Schema formal versionado acompanha a implementação e valida no outbox.

## Semântica e garantias

- Derivado do diff entre dumps arquivados — sem arquivo do mês, não há evento (janela irrecuperável).
- `reabertura_endereco` é o gatilho do padrão sucessão de fachada.
- NUNCA carrega CPF — apenas pessoa_id, e só quando já resolvido.
