# CasoAberto / CasoRefutado / CasoPublicado

Transições do ciclo de vida do agregado Caso na corrente com veto.

| Campo | Valor |
|---|---|
| Emissor | Orquestrador de agentes |
| Contexto | investigacao |
| `type` | `br.combustiveis.investigacao.caso.transicoes.v1` |
| Chave de idempotência | `(caso_id, transicao)` |
| Garantia de ordem | por caso |
| Consumidores v1 | Portal do órgão · webhooks (só CasoPublicado) · Auditoria |

## Payload (`data`)

```json
{
  "caso_id": "string",
  "transicao": "aberto | refutado | publicado",
  "posto_id": "string",
  "gatilho": "referência ao LimiarDeRiscoCruzado",
  "dossie_uri": "string (só em publicado)",
  "motivo_refutacao": "string (só em refutado)"
}
```

Tipos acima são descritivos; o JSON Schema formal versionado acompanha a implementação e valida no outbox.

## Semântica e garantias

- `refutado` é sucesso do sistema, não falha — o Refutador derrubou antes de sair.
- `publicado` implica: passou pelo Guardião (ADR-008). Não existe publicado sem essa passagem.
- Externamente assinável apenas CasoPublicado, e apenas por órgão com escopo.
