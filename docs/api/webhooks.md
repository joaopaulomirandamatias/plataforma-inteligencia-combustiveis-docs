# Webhooks — entrega assinada de eventos

> **Estado: desenho, não implementado — nada nesta página está no ar.** As três operações de assinatura (`criarAssinatura`, `listarAssinaturas`, `removerAssinatura`) estão em `x-estado: planned` no [contrato](openapi.yaml) e devolvem **404** no runtime, que é anônimo: assinatura pressupõe cliente identificado e segredo HMAC, e os dois dependem da autenticação, que não existe. Efeito prático hoje: **não há como assinar nada, e nenhuma entrega é despachada** — a única forma de acompanhar mudança é consultar as operações `implemented` (ver o [guia de consumo](guia-de-consumo.md)). O documento segue aqui porque é o desenho contra o qual a implementação será cobrada; não há prazo declarado.

Extensibilidade pretendida: em vez de polling, assinantes receberiam eventos do subconjunto público do [catálogo](../dados/eventos/README.md).

## Eventos assináveis

> Desenho. Nenhum destes eventos é entregue hoje, e não existe cliente autenticado a quem entregar.

| Evento (`type` no envelope) | Quem pode assinar |
|---|---|
| `br.combustiveis.entrega.snapshot.publicado.v1` | Todos os clientes autenticados |
| `br.combustiveis.normativo.ato.normativo.publicado.v1` | Todos os clientes autenticados |
| `br.combustiveis.investigacao.caso.transicoes.v1` (só `publicado`) | Órgão, com escopo |

Eventos internos (`LimiarDeRiscoCruzado`, tudo de identidade e societário) **não são assináveis** — e nenhum payload de webhook carrega dado do cofre, nem pseudonimizado.

## Registro

> Desenho. `POST /v1/webhooks/assinaturas` devolve 404 — a rota não é servida.

`POST /v1/webhooks/assinaturas` com `Idempotency-Key` ([contrato](openapi.yaml)). O segredo HMAC é exibido **uma única vez** na resposta de criação — guarde-o; rotação gera segredo novo com janela de convivência de 48h (as entregas carregam `kid` para você saber qual validar).

## Verificação da assinatura

> Desenho. Nenhum segredo HMAC é emitido hoje, porque não há criação de assinatura; os cabeçalhos abaixo descrevem a entrega pretendida.

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

> Desenho. Não há despachante em execução: nada é entregue e nada vai para DLQ. Note que a leitura de DLQ citada abaixo (`GET /v1/webhooks/assinaturas/{id}`) sequer é declarada no contrato — o único método daquele caminho é `DELETE`, também `planned`. A visibilidade da DLQ é, portanto, desenho sem contrato: quando for implementada, o `openapi.yaml` precisa ganhar a operação antes.

- Corpo: envelope CloudEvents 1.0 idêntico ao do catálogo.
- Sucesso = HTTP 2xx em ≤ 10s. Qualquer outra coisa → retry com backoff exponencial + jitter por até **24h**.
- Esgotadas as tentativas → **DLQ visível** (`GET /v1/webhooks/assinaturas/{id}` expõe contadores e últimas falhas) e replay sob demanda pelo painel/API.
- Ordem **não** é garantida entre entregas — consuma pela chave de idempotência do evento, não pela ordem de chegada.

## Responsabilidades do assinante

> Desenho — o que será exigido de quem assinar, quando houver assinatura.

Endpoint idempotente; validação de assinatura **antes** de processar; nunca logar o corpo antes de validar (conteúdo não verificado é entrada não confiável — a mesma regra que a plataforma aplica às fontes vale para quem consome a plataforma).
