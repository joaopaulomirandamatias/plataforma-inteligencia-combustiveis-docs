# CI/CD — estado operacional

A Frente 4 deixou de ser backlog: backend e frontend têm CI executável, o Railway está ligado aos repositórios e produção **não acompanha mais `main` diretamente**.

## Fluxo vigente

```text
developer/agent
      │
      ▼
    main
      │ push
      ▼
GitHub Actions
  │
  ├─ falha ───────────────► deploy NÃO avança
  │
  └─ sucesso
       │
       ▼
 branch deploy
       │
       ▼
 Railway production
```

`deploy` é branch máquina-a-máquina. Desenvolvimento acontece em `main`; ninguém deve fazer desenvolvimento manual em `deploy`.

## Backend (`plataforma-inteligencia-combustiveis`)

O workflow executa:

1. PostgreSQL 16 real como service container;
2. checkout do backend;
3. checkout do repositório canônico de documentação;
4. Python 3.13 + instalação das dependências de desenvolvimento;
5. `ruff check .`;
6. suíte completa `pytest -ra`;
7. execução explícita da conformidade OpenAPI com `--strict-markers`;
8. promoção do SHA para `deploy` **somente se ele ainda for o HEAD atual de `main`**.

Isso corrige duas classes de falso verde:

- testes de banco pulando por ausência de PostgreSQL;
- teste de contrato pulando porque `docs` não estava disponível no filesystem.

## Contrato canônico (`plataforma-inteligencia-combustiveis-docs`)

O próprio repositório de documentação também valida toda mudança em PR e push
para `main`. O gate usa dependências travadas no `package-lock.json` e:

1. prova que o checkout corresponde ao SHA do evento;
2. exige OpenAPI `3.1.0`;
3. recusa `$ref` remoto antes de qualquer tentativa de resolução;
4. resolve referências internas e valida a estrutura OpenAPI;
5. exige `operationId` presente e único;
6. reprova exemplos incompatíveis com seus schemas;
7. executa regressões sintéticas que precisam falhar quando esses controles são
   quebrados.

O backend continua fixando um commit imutável deste repositório. Assim, o CI de
docs protege o contrato antes do merge, e o CI do backend protege a integração
quando o SHA fixado for atualizado.

### Proteção contra corrida

O workflow usa `concurrency` com cancelamento da execução anterior. Além disso, imediatamente antes da promoção ele busca `origin/main` de novo e compara o SHA validado com o SHA atual.

Se outro commit chegou enquanto a suíte rodava, a execução antiga termina sem promover. Isso impede que um CI lento faça `--force` e retroceda produção para um SHA mais velho.

## Frontend (`plataforma-inteligencia-combustiveis-web`)

O workflow executa:

1. `pnpm/action-setup` antes do cache — ordem necessária para o runner encontrar o executável;
2. Node 22;
3. `pnpm install --frozen-lockfile`;
4. testes;
5. auditoria de dependências de produção;
6. build Next.js;
7. verificação do payload RSC em push para `main`;
8. mesma promoção protegida `main → deploy` usada no backend.

A primeira execução real encontrou a ordem incorreta `setup-node/cache` antes da instalação do pnpm; a falha foi corrigida e validada pelo próprio CI.

## Railway production

Projeto: `Plataforma Combustível`.

| Serviço | Source | Proteção | Health/readiness |
|---|---|---|---|
| `pic-api` | backend / `deploy` | CI backend | `/saude`, 30 s |
| `pic-worker` | backend / `deploy` | CI backend | cron `0 6 * * *`, volume `/data` |
| `pic-web` | frontend / `deploy` | CI frontend | `/`, 30 s |
| Postgres | serviço gerenciado | — | Railway |

A API e o worker compartilham o artefato, mas o worker preserva `PIC_MODO`, cron, política `NEVER` e o volume existente.

## Watch paths

Railway só reconstrói quando muda algo capaz de alterar o artefato/runtime.

Backend:

```text
/src/**
/db/migrations/**
/docker/**
/Dockerfile
/pyproject.toml
/railway.json
/.dockerignore
```

Frontend:

```text
/src/**
/scripts/**
/public/**
/package.json
/pnpm-lock.yaml
/next.config.mjs
/tsconfig.json
/next-env.d.ts
```

Assim testes, README e alterações apenas no workflow continuam sendo validados pelo GitHub Actions sem gastar rollout de produção quando o executável é idêntico.

## Healthchecks

- `pic-api`: `/saude` deve responder 200; o endpoint inclui a dependência de banco necessária ao runtime.
- `pic-web`: `/` deve ficar pronto antes do rollout ser considerado saudável.

“Container iniciou” não é mais suficiente para considerar API/web aptos a servir.

## Regra para mudanças futuras

1. nunca apontar produção de volta para `main`;
2. nunca remover a verificação explícita do OpenAPI do backend;
3. um teste vermelho não é contornado promovendo `deploy` manualmente;
4. falha de infraestrutura do runner deve ser distinguida de falha do código e reexecutada quando for claramente externa (ex.: timeout ao baixar `postgres:16`);
5. migração nova só chega ao Railway após CI verde; o healthcheck ainda precisa aprovar o rollout final.

## Estado

**Concluído e em uso desde 2026-08-08.** A evolução da F1 já usa este pipeline como gate de produção.
