# CI alternativo isolado no Railway

## Motivo

Em 2026-08-08 o GitHub Actions deixou de iniciar jobs por bloqueio de billing/spending limit da conta. O check-run oficial registra que o runner não é iniciado enquanto o pagamento/limite não for regularizado.

Esse bloqueio **não autoriza** apontar produção para `main`, mover `deploy` manualmente ou aplicar migrações sem gate.

Para continuar encontrando regressões técnicas sem tocar na produção, foi criado um projeto Railway privado separado:

```text
PIC CI Sandbox
```

Ele não recebe URL nem credencial do PostgreSQL de produção.

## Arquitetura

```text
branch de validação GitHub
        ↓
Dockerfile.ci + railway.ci.json
        ↓
serviço ci-* no PIC CI Sandbox
        ↓
PostgreSQL 16 privado postgres-ci
        ↓
banco descartável exclusivo por validação
        ↓
ruff check .
pytest -ra
pytest tests/test_conformidade_contrato.py -q --strict-markers
        ↓
CI_RESULT=PASS
```

O contrato OpenAPI é baixado do repositório público canônico de documentação.

## Isolamento

O PostgreSQL do sandbox:

- pertence a outro projeto Railway;
- não tem domínio público;
- usa somente a rede privada do sandbox;
- não contém dados de produção;
- recebe bancos descartáveis como `pic_ci_main`, `pic_ci_pr4`, `pic_ci_pr7` e `pic_ci_integration_train`;
- pode ser recriado sem efeito sobre a plataforma operacional.

O runner nunca recebe `DATABASE_URL` de produção.

## Artefatos do runner

As branches temporárias de validação usam:

- `Dockerfile.ci`;
- `Dockerfile.ci.dockerignore`;
- `railway.ci.json`;
- `ci/railway_ci.py`.

O `Dockerfile.ci` inclui os artefatos de runtime que a suíte inspeciona (`Dockerfile`, `railway.json`, `docker-compose.yml`, `docker/`, `src/`, `db/` e `tests/`). O `.dockerignore` específico do CI não exclui `tests/`.

O runner marca exclusivamente `/app` como `safe.directory` para que testes que chamam Git funcionem dentro da imagem sem desabilitar globalmente a proteção do Git.

Esses arquivos não alteram `railway.json` nem o Dockerfile de produção.

## Procedimento correto para criar uma validação

### 1. Criar branch de validação

A branch deve partir exatamente do SHA/branch que será validado e receber somente os artefatos de CI ou a composição explícita que se deseja testar.

### 2. Verificar a branch antes de criar o serviço

Nunca criar serviço apontando para uma branch inexistente. Um serviço criado antes da referência existir pode acabar usando o snapshot/default de `main`, produzindo resultado enganoso.

### 3. Criar/configurar o serviço

O serviço precisa usar:

```text
Dockerfile: Dockerfile.ci
Railway config: railway.ci.json
Restart policy: NEVER
```

E receber somente variáveis do sandbox:

```text
PIC_CI_ADMIN_URL=postgresql://postgres@postgres-ci.railway.internal:5432/postgres
PIC_CI_DB_NAME=<banco descartável exclusivo>
PIC_CI_APP_PASSWORD=<senha efêmera de teste>
```

### 4. Forçar source-build depois da configuração

`redeploy` pode reutilizar um snapshot construído antes da configuração do CI. Por isso, depois de configurar o serviço, deve existir um novo commit na branch de validação para provocar **source-build**.

O build válido precisa conter a linha:

```text
[internal] load build definition from Dockerfile.ci
```

Se o runtime começar com:

```text
[iniciar] migrando
```

isso é o entrypoint da aplicação de produção e **não é uma execução válida do runner de CI**.

O runtime válido começa com algo equivalente a:

```text
[ci] preparando banco descartável ...
[ci] OpenAPI canônico: ...
[ci] $ ruff check .
```

### 5. Aceitar somente evidência completa

Uma validação só é considerada tecnicamente verde quando os logs mostram todos os itens:

1. `All checks passed!` para `ruff`;
2. resumo completo do `pytest -ra`;
3. `8 passed` no contrato OpenAPI explícito;
4. `CI_RESULT=PASS`.

O status Railway `SUCCESS` sozinho não é suficiente para documentar a evidência.

## Resultados confirmados em 2026-08-08

| Alvo | Suíte | Contrato | Resultado |
|---|---:|---:|---|
| `main` F1-08b/c | 269 passed, 1 skipped, 2 deselected | 8/8 | PASS |
| PR #5 F1-08a v2 | 269 passed, 1 skipped, 2 deselected | 8/8 | PASS |
| PR #1 F1-08d | 283 passed, 1 skipped, 2 deselected | 8/8 | PASS |
| PR #3 F1-08e | 275 passed, 1 skipped, 2 deselected | 8/8 | PASS |
| PR #4 F1-09 | 292 passed, 1 skipped, 2 deselected | 8/8 | PASS |
| PR #6 sobre #4+#5 | 299 passed, 1 skipped, 2 deselected | 8/8 | PASS |
| PR #7 F1-11 | 287 passed, 1 skipped, 2 deselected | 8/8 | PASS |
| integration train #1+#3+#4+#5+#6+#7 | **331 passed, 1 skipped, 2 deselected** | **8/8** | **PASS** |

O skip esperado é `tests/test_empacotamento.py` quando `uv` não está disponível dentro da imagem do sandbox. Os dois testes deselected são os testes marcados como `rede`, excluídos pela configuração padrão da suíte hermética.

## Integration train

Para detectar incompatibilidades entre cards antes dos merges oficiais, foi criada uma árvore temporária que combina:

```text
PR #5 — blindagem codebook v2
PR #1 — relatório formal
PR #3 — operação pic-er
PR #7 — manifesto reproduzível
PR #4 — pipeline + migração 013
PR #6 — fila → amostra
```

A árvore foi construída reutilizando os blobs das branches reais e as duas correções encontradas pelo próprio sandbox. O source-build final executado no Railway coletou 334 itens, selecionou 332 pela política hermética e concluiu:

```text
331 passed
1 skipped
2 deselected
OpenAPI 8/8
CI_RESULT=PASS
```

Esse resultado prova compatibilidade técnica da composição naquele snapshot. Não significa que as PRs foram oficialmente aprovadas ou promovidas.

## Defeitos detectados pelo sandbox

### PR #4 — `ruff I001`

O primeiro source-build válido encontrou import block não ordenado em `tests/test_pipeline_entity_resolution_carga.py`. O erro foi corrigido na branch real, sem relaxar lint. A reexecução passou com 292 testes e depois também passou nas composições de 299 e 331 testes.

### PR #7 — round-trip `tuple/list`

O primeiro run válido revelou que `dataclasses.asdict()` podia manter `tuple` em memória, enquanto o validador do manifesto aceitava apenas `list`. Um artefato produzido pelo próprio sistema podia falhar no round-trip.

A branch real foi corrigida para aceitar `list/tuple` na representação interna e normalizar para lista, mantendo rejeição de outros tipos. A reexecução passou com 287 testes e o integration train também ficou verde.

## Falsos negativos operacionais já observados

Alguns serviços temporários apareceram como `FAILED` antes de o runner correto ser configurado. Esses deployments:

- apontavam para `main` ou branch inexistente;
- usavam a imagem/entrypoint de produção;
- tentavam executar `[iniciar] migrando` sem a configuração normal da aplicação;
- **não representam falha da PR**.

Somente source-builds explicitamente associados à branch/commit esperados e ao `Dockerfile.ci` entram na evidência técnica.

## Regra de promoção

**CI Railway verde não substitui a branch `deploy` nem promove produção automaticamente.**

Enquanto o GitHub Actions oficial estiver bloqueado:

1. usar o sandbox para encontrar/corrigir problemas técnicos;
2. manter PRs sem merge oficial;
3. não mover `deploy`;
4. não aplicar migrações em produção;
5. após regularizar Billing & plans, reexecutar o GitHub Actions oficial;
6. somente o SHA verde no gate oficial pode ser promovido para `deploy` e chegar ao Railway de produção.

## Produção observada após as validações

A produção continuou isolada durante todo o processo. API e worker permanecem no mesmo SHA de `deploy`:

```text
fe222717a9beec1e2684f8b6ea56aeb2a6c4cda8
```

Não houve promoção manual das migrações 012 ou 013.

## Limpeza

Depois que o GitHub Actions voltar, as PRs forem validadas no gate oficial e a promoção for concluída, os serviços/branches `ci/*` e o projeto `PIC CI Sandbox` podem ser removidos. Até lá, eles funcionam somente como bancada de testes isolada e evidência suplementar.