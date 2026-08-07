# Webhooks — entrega assinada de eventos

Extensibilidade da plataforma: em vez de polling, assinantes recebem eventos do subconjunto público do [catálogo](../dados/eventos/README.md).

## Eventos assináveis

| Evento (`type` no envelope) | Quem pode assinar |
|---|---|
| `br.combustiveis.entrega.snapshot.publicado.v1` | Todos os clientes autenticados |
| `br.combustiveis.normativo.ato.normativo.publicado.v1` | Todos os clientes autenticados |
| `br.combustiveis.investigacao.caso.transicoes.v1` (só `publicado`) | Órgão, com escopo |

Eventos internos (`LimiarDeRiscoCruzado`, tudo de identidade e societário) **não são assináveis** — e nenhum payload de webhook carrega dado do cofre, nem pseudonimizado.

## Registro

`POST /v1/webhooks/assinaturas` com `Idempotency-Key` ([contrato](openapi.yaml)). O segredo HMAC é exibido **uma única vez** na resposta de criação — guarde-o; rotação gera segredo novo com janela de convivência de 48h (as entregas carregam `kid` para você saber qual validar).

## Verificação da assinatura

Cabeçalhos de cada entrega:

```
X-Webhook-Signature: v1=<hex(hmac_sha256(segredo, timestamp + "." + corpo))>
X-Webhook-Timestamp: <unix epoch segundos>
X-Webhook-Id:        <uuid da entrega — estável entre retries>
X-Webhook-Kid:       <id do segredo>
```

Validação obrigatória do assinante:
1. Rejeitar se `|now − timestamp| > 300s` (anti-replay).
2. Recalcular o HMAC sobre `timestamp + "." + corpo bruto` e comparar em tempo constante.
3. Deduplicar por `X-Webhook-Id` — retries reenviam o mesmo id.

## Entrega, retry e replay

- Corpo: envelope CloudEvents 1.0 idêntico ao do catálogo.
- Sucesso = HTTP 2xx em ≤ 10s. Qualquer outra coisa → retry com backoff exponencial + jitter por até **24h**.
- Esgotadas as tentativas → **DLQ visível** (`GET /v1/webhooks/assinaturas/{id}` expõe contadores e últimas falhas) e replay sob demanda pelo painel/API.
- Ordem **não** é garantida entre entregas — consuma pela chave de idempotência do evento, não pela ordem de chegada.

## Responsabilidades do assinante

Endpoint idempotente; validação de assinatura **antes** de processar; nunca logar o corpo antes de validar (conteúdo não verificado é entrada não confiável — a mesma regra que a plataforma aplica às fontes vale para quem consome a plataforma).
