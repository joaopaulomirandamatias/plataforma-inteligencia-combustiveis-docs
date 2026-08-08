# Backlog — CI (Frente 4)

A objeção que barrava CI caiu: os três repos agora têm remoto no GitHub, então um workflow tem onde rodar (antes, `.github/workflows/` num repo sem remoto seria "portão que parece existir e nunca roda").

## Frontend (`-web`)
- Workflow: `pnpm install` → `pnpm test` → `pnpm run auditar` (barra high+ em produção).
- **Decisão de card:** `pnpm run verificar:payload` custa um `next build` — decidir se roda em TODO push ou só no merge para `main` (custo vs. cobertura).

## Backend
- Nunca teve CI. `pytest` roda **sem banco** — os testes de banco pulam sozinhos, então um workflow mínimo já pega regressão de lógica pura.
- **Conformidade de contrato** (era o item 5 da fila antiga do F0-04): a malha pula em silêncio quando o repo de docs não está ao lado. O CI deve cloná-lo ao lado (ou apontar `PIC_OPENAPI`/`PIC_BACKEND_POLITICA`) e **falhar** se o contrato não for conferido — senão a suíte fica verde com a defesa do contrato desligada.

## Auto-deploy (relacionado, mas é do usuário)
Conectar `pic-api`→repo backend e `pic-web`→repo `-web` no dashboard do Railway (Source). Minha CLI não tem escopo GitHub; é clique do usuário. Depois disso, merge na `main` = deploy automático.

Não iniciado. Registrado para não perder a razão (que já não existe) junto com o backlog.
