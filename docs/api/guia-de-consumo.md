# Guia de Consumo da API

Regras transversais do contrato [openapi.yaml](openapi.yaml). O contrato é a fonte; este guia explica como usá-lo sem tropeçar.

## Antes de tudo: o que está no ar

Este guia descreve o desenho ALVO — autenticação, quota, expiração de cursor e webhooks incluídos. **O que está executável hoje é o `x-estado` de cada operação no `openapi.yaml`**, e é ele que vale para quem vai integrar agora:

- `implemented` — servida pelo runtime público, **sem autenticação nenhuma**. Filtre por isto para montar sua allowlist.
- `planned` / `restricted` — declaradas no contrato, ainda **404** no runtime.

A base fica na raiz do host (`servers`); as rotas de negócio carregam `/v1` no próprio path e `/saude` responde na raiz, fora do versionamento.

## Autenticação

| Cliente | Mecanismo |
|---|---|
| Órgão, distribuidora, frota, posto | OIDC (Keycloak) — authorization code para humanos, client credentials para M2M. Access token de 15 min; refresh rotativo |
| Consumo público / datasets | `X-Api-Key` com quota |

O papel e o **escopo** (UF, órgão, rede) viajam no token e são avaliados no gateway (ABAC). Pedir fora do escopo → `403` com `codigo: escopo_negado` — não é erro do cliente re-tentável.

## Consulta temporal (`as_of`)

Todo recurso histórico aceita `?as_of=2025-03-12T00:00:00Z`:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.../v1/postos/A-1042?as_of=2025-03-12T00:00:00Z"
```

- Omitido → snapshot corrente (a resposta declara `versao_snapshot`).
- A semântica é a da dimensão de **validade**; auditoria fina de "o que sabíamos quando" usa o [modelo bitemporal](../dados/modelo-bitemporal.md) via dossiê, não a API pública.
- Todo número retornado é reproduzível: guarde `versao_snapshot` e o mesmo pedido devolve o mesmo resultado.

## Paginação

Cursor keyset opaco — **não** interprete nem construa cursores:

```
GET /v1/precos?municipio=MACAPA&limit=100
→ { "itens": [...], "proximo_cursor": "MjAyNi0w..." }
GET /v1/precos?municipio=MACAPA&limit=100&cursor=MjAyNi0w...
```

`municipio` é o **nome** como a ANP publica, não código IBGE — a PIC não tem código IBGE em nenhuma fonte. A entrada é normalizada (caixa alta, sem acento) e o valor aplicado volta em `filtros`.

Página estável sob escrita concorrente (por isso não há offset). Cursor expira em 24h; expirado → `400` com `codigo: cursor_expirado` — recomece.

> Expiração de cursor é desenho alvo: o runtime de hoje não expira cursor. O que ele já recusa com `400 cursor_invalido` é cursor ilegível ou de outra coleção — a chave de `/v1/precos` é composta (semana, posto, produto) e a de `/v1/postos` não é.

## Idempotência

Todo POST com efeito exige `Idempotency-Key` (UUID). Mesma chave + mesmo corpo → mesma resposta (replay seguro); mesma chave + corpo diferente → `409`.

## Erros

RFC 9457 (`application/problem+json`), sempre com `codigo` do catálogo de domínio:

| `codigo` | Significado | Ação do cliente |
|---|---|---|
| `escopo_negado` | Papel válido, escopo não | Não re-tentar |
| `cursor_expirado` | Cursor > 24h | Reiniciar paginação |
| `cobertura_insuficiente` | Dado existente não sustenta a resposta pedida | Tratar como "sem dado", não como zero |
| `as_of_anterior_a_base` | Data pedida antes do primeiro dado | Ajustar janela |
| `quota_excedida` | Rate limit | Respeitar `Retry-After` |

## Rate limiting

Token bucket por credencial. Cabeçalhos: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After` (no 429). Backoff exponencial com jitter é responsabilidade do cliente; o [despachante de webhooks](webhooks.md) existe exatamente para você **não** precisar de polling agressivo.

## Versionamento e depreciação

- Major na URL (`/v1/`). Mudança aditiva não avisa; remoção/renomeação só em major novo.
- Depreciação com **12 meses** de convivência, anunciada por cabeçalho `Sunset` e no changelog do contrato.
- O `openapi.yaml` deste repositório é a fonte — geradores de cliente devem apontar para ele, versionado por tag.

## O que a API não faz — por desenho

- Não retorna score/ranking sem papel de órgão ([ADR-005](../arquitetura/adr/adr-005-score-restrito-a-orgaos.md)) — não é permissão faltando, é contrato.
- Não retorna CPF nem dado do cofre, para nenhum papel — resolução de identidade é fluxo do cofre, fora da API.
- Não afirma fraude em nenhum campo de nenhuma resposta — descrições são factuais, datadas e com fonte.
