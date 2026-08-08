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
Dockerfile.ci
        ↓
serviço ci-* no PIC CI Sandbox
        ↓
PostgreSQL 16 privado postgres-ci
        ↓
banco descartável exclusivo por validação
        ↓
ruff
pytest -ra
pytest contrato OpenAPI
```

O contrato OpenAPI é baixado do repositório público canônico de documentação.

## Isolamento

O PostgreSQL do sandbox:

- pertence a outro projeto Railway;
- não tem domínio público;
- usa somente a rede privada do sandbox;
- não contém dados de produção;
- recebe bancos descartáveis como `pic_ci_main`, `pic_ci_pr1`, `pic_ci_pr4` etc.;
- pode ser recriado sem efeito sobre a plataforma operacional.

O runner nunca recebe `DATABASE_URL` de produção.

## Resultado até 2026-08-08

### `main`

Validação técnica concluída:

- `ruff`: aprovado;
- PostgreSQL 16 real;
- 269 testes aprovados;
- 1 skip esperado;
- 2 testes de rede excluídos pelo marker padrão;
- contrato OpenAPI: 8/8 testes aprovados.

A branch usada para o runner difere de `main` somente pelos quatro artefatos de CI do sandbox. Portanto o resultado valida a implementação de `main`, incluindo F1-08b/c e a migração 012.

### PR #5 — codebook cego v2

Validação técnica concluída no sandbox. A PR continua draft porque o gate oficial do GitHub Actions permanece bloqueado.

### PR #1 — relatório formal F1-08d

Validação técnica concluída:

- 283 testes aprovados;
- 1 skip esperado;
- 2 testes de rede excluídos;
- contrato OpenAPI: 8/8 aprovado.

A PR continua draft.

## Regra de promoção

**CI Railway verde não substitui a branch `deploy` nem promove produção automaticamente.**

Enquanto o GitHub Actions oficial estiver bloqueado:

1. usar o sandbox para encontrar/corrigir problemas técnicos;
2. manter PRs draft;
3. não mover `deploy`;
4. não aplicar migrações em produção;
5. após regularizar Billing & plans, reexecutar o GitHub Actions oficial;
6. somente o SHA verde no gate oficial pode ser promovido para `deploy` e chegar ao Railway de produção.

## Artefatos do runner

As branches temporárias de validação usam:

- `Dockerfile.ci`;
- `Dockerfile.ci.dockerignore`;
- `railway.ci.json`;
- `ci/railway_ci.py`.

Esses arquivos não alteram `railway.json` nem o Dockerfile de produção.

## Limpeza

Depois que o GitHub Actions voltar e as PRs forem validadas no gate oficial, os serviços/branches `ci/*` e o projeto `PIC CI Sandbox` podem ser removidos. Até lá, eles são somente uma bancada de testes isolada.