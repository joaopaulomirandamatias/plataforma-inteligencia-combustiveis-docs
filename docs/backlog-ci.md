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
Woodpecker compartilhado
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

O servidor e os agentes Woodpecker são compartilhados entre repositórios. Por
isso, typecheck, testes e lint aplicáveis rodam localmente antes do push; commits
são agrupados em um único push; PR só é aberta pronta para revisão. Falha de
clone/Git `128`, rede de dependências ou timeout em código não alterado é
reexecutada no mesmo pipeline, sem commit vazio.

## Backend (`plataforma-inteligencia-combustiveis`)

O pipeline Woodpecker executa:

1. PostgreSQL 16 real como service container, fixado por digest;
2. checkout do backend;
3. checkout do repositório canônico de documentação;
4. Python 3.13 + instalação das dependências de desenvolvimento;
5. `ruff check src tests`;
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
8. exige que todos os objetos públicos de `GET /saude` e `GET /v1/precos`,
   inclusive objetos aninhados, declarem `additionalProperties: false`;
9. fixa como obrigatórias somente as chaves sempre serializadas pelo runtime e
   observadas em produção, incluindo o literal `estado: pronto`.

O backend continua fixando um commit imutável deste repositório. Assim, o CI de
docs protege o contrato antes do merge, e o CI do backend protege a integração
quando o SHA fixado for atualizado.

### Proteção contra corrida

Imediatamente antes da promoção, o pipeline busca `origin/main` de novo e
compara o SHA validado com o SHA atual. No núcleo, a promoção também é
serializada com `concurrency.limit: 1`. Isso não equivale a cancelar
automaticamente todo CI obsoleto ainda na fila; quando um novo push substitui o
anterior, o pipeline antigo da mesma PR deve ser cancelado operacionalmente.

Se outro commit chegou enquanto a suíte rodava, a execução antiga termina sem
promover. Isso impede que um CI lento faça `--force-with-lease` e retroceda
produção para um SHA mais velho.

## Frontend (`plataforma-inteligencia-combustiveis-web`)

O pipeline Woodpecker executa:

1. clone explícito da documentação canônica e prova do SHA usado pelo léxico;
2. Node 22, pnpm 9.15.9 e `pnpm install --frozen-lockfile`;
3. typecheck integral com `tsc --noEmit`;
4. testes com a paridade do léxico obrigada a executar em CI;
5. auditoria de dependências de produção;
6. build Next.js;
7. verificação do payload RSC em PR e push para `main`;
8. promoção protegida `main → deploy`, em pipeline dependente, somente no push
   já validado.

O fluxo atual não depende de cache implícito: prepara pnpm 9.15.9, executa
typecheck, testes, auditoria, build e pente do payload RSC. A paridade do léxico
clona explicitamente a documentação e falha, em vez de pular, quando não pode
ser comprovada.

## Railway production

Projeto: `Plataforma Combustível`.

| Serviço | Source | Proteção | Health/readiness |
|---|---|---|---|
| `pic-api` | backend / `deploy` | CI backend | `/saude`, 60 s efetivos; painel ainda diverge em 30 s |
| `pic-worker` | backend / `deploy` | CI backend | cron `null` por pausa operacional, restart `NEVER`, volume `/data` (reconfirmado em 2026-10-20) |
| `pic-web` | frontend / `deploy` | CI frontend | `/`, 30 s |
| Postgres | serviço gerenciado | — | Railway |

A API e o worker compartilham o artefato, mas o worker preserva `PIC_MODO`,
política `NEVER` e o volume existente. O cron é estado operacional do serviço:
em operação normal era `0 4 * * *`; em 2026-10-19 foi levado a `null`, sem
redeploy, por causa da F06 em `NXDOMAIN` e das reingestões GEO anteriores ao
saneamento. API e portal seguem servindo o snapshot publicado, mas nenhuma
ingestão diária automática ocorre durante a pausa.

Atualização controlada das fontes ANP continua possível pelo one-shot
`/railway.worker-anp.json`, com SHA, Migrator e contagens verificados antes e
depois. A F06 permanece isolada em `/railway.worker-f06.json`. A volta do cron
depende de prova F06 bem-sucedida no Railway e de um ciclo completo sem erros.
O one-shot não altera o NO-GO das migrações GEO 023/024 nem substitui seu gate
de backup restaurável e saneamento.
O PR #74 do backend fechou o falso verde: `quarentena`, `sem_deposito`,
`corrompido` e status desconhecido encerram a agenda com erro; F06 em `NXDOMAIN`
usa o exit code `5`; e ausência esperada de publicação em F02/F03 continua em
`0`. Os pipelines Woodpecker #14 e #15 passaram e promoveram
`main == deploy == 51eb12dd8ba95fc3eb90832287d3f58c83928b77`. O worker teve
o caminho feliz exercitado em 2026-10-20: o deployment
`59506094-6e6e-4a4f-964f-840f6ca580c1` executou três fontes sem erro e deixou
F06 fora da allowlist. O backfill F02 `2026-05` foi isolado no deployment
`50e3219a-51bd-4139-b651-cb5f4916c3a0`, que terminou normalmente. Depois dos
jobs, o serviço voltou a `/railway.worker.json` com cron `null`. O operador
continua obrigado a conferir resumo, logs e deltas. O procedimento detalhado
está em
`docs/operacao-migracoes.md` no repositório do backend.

O CLI do Railway agora alerta que `railway.json`/`railway.toml` continuam
funcionando somente até 2026-12-01. A migração para
`.railway/railway.ts` é a próxima tarefa de infraestrutura; ela não foi misturada
ao backfill para que mudança de configuração e mudança de dados mantenham trilhas
de validação separadas.

A auditoria de 2026-10-20 encontrou drift hoje mascarado pelos manifests: o
painel descreve `RAILPACK` para os três serviços do núcleo, timeout/retry da API
em 30 s/10 e restart do migrator como `ON_FAILURE/10`, enquanto os deployments
efetivos usam Dockerfile, API em 60 s/3 e migrator `NEVER`. Esses valores devem
ser materializados antes do corte, ou a retirada do CaC pode alterar o runtime.

O projeto Railway reúne runtimes dos repositórios de núcleo, portal web e gestão
— a documentação não possui serviço — e já contém o partial
`pic-gestao-backend`. Por isso o novo módulo deve exportar o partial `pic-core`
e assumir somente `pic-api`, `pic-worker`, `pic-migrator` e o volume
`pic-worker-volume`; fontes GitHub e variáveis ficam fora da primeira fase. O
plano é bloqueado se criar/remover recursos, alterar ou redimensionar o volume,
afetar serviços web/gestão ou remover variáveis. Não usar confirmação
destrutiva. Antes de qualquer comando, vincular explicitamente o checkout
isolado ao projeto `626ec780-fc73-4b2a-a0bc-8c0acf6c08a4`, ambiente
`production`, e conferir `railway status`; um checkout temporário foi encontrado
vinculado a outro projeto e não pode ser reutilizado por suposição.

Perfis one-shot ANP, F01, F02 mensal e F06 não são quatro estados desejados do
mesmo serviço. Depois da migração, um executor operacional serializado deve
aplicar o `startCommand` temporário ao snapshot do deployment, restaurar a
configuração estável em `finally`, aguardar o job e exigir plano IaC limpo. O
`finally` sozinho não cobre morte do processo, host ou rede: antes de cada uso,
o executor deve reconciliar o estado remoto com o estável; a operação e o
snapshot anterior precisam ficar em registro durável com lease; e uma rotina de
reparo independente deve conseguir restaurar o estado sem depender do processo
original. F06 permanece isolada e nenhum perfil pode religar a agenda completa
por acidente.

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

Assim testes, README e alterações apenas no pipeline continuam sendo validados
pelo Woodpecker sem gastar rollout de produção quando o executável é idêntico.

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
