# Status executado — F1 Entity Resolution

Atualizado em 2026-08-08. Este arquivo registra **o que passou por código + CI +, quando aplicável, Railway**. O backlog continua descrevendo a sequência e os critérios; este status evita confundir especificação futura com implementação já validada.

| Card | Estado | Evidência principal |
|---|---|---|
| F1-01 fila de revisão | ✅ concluída | migração 010, módulo de revisão, testes, produção saudável |
| F1-02 normalização | ✅ concluída | normalizadores determinísticos e testes de CNPJ/CEP/UF/texto |
| F1-03 blocking | ✅ concluída | blocking cross-source mensurável, redução/cobertura, sem vínculo automático |
| F1-04 similaridade + FS | ✅ concluída | vetor multi-campo + Fellegi–Sunter somente com parâmetros explícitos |
| F1-05 calibração | ✅ engenharia / ⏳ empírico | dois limiares e métricas implementados; valores de produção dependem da F1-08 |
| F1-06 clusters | ✅ concluída | migração 011, snapshots imutáveis, revisão/split, as-of, Railway com 11 migrações |
| F1-07a golden record puro | ✅ concluída | política versionada, proveniência, alternativas, cobertura e corte bitemporal |
| F1-07b adaptador F01 | ✅ concluída | PostgreSQL → candidatos F01 → golden record, CI verde e rollout protegido |
| F1-08a codebook/pacote cego | ✅ concluída | labels fechados, IDs opacos, pacote sem score/threshold/destino/chaves internas; CI e promoção verdes |
| F1-08b amostragem | 🧪 implementada / CI bloqueado | quotas exatas, ranking SHA-256 por seed e mapa interno separado implementados em `main` |
| F1-08c rótulos/adjudicação | 🧪 implementada / CI bloqueado | migração 012 + persistência append-only + dupla revisão/adjudicação implementadas em `main` |
| F1-08d relatório de holdout | 🧪 branch/PR de validação | motor puro + testes na PR #1; holdout não calibra limiar, `INDETERMINADO` não vira negativo, IC de Wilson 95% |

## Produção

O backend e o worker Railway acompanham somente a branch `deploy`, promovida pelo GitHub Actions depois de lint, PostgreSQL 16, suíte completa e validação explícita do contrato OpenAPI. O frontend usa o mesmo padrão `main → CI → deploy → Railway`.

A API usa `/saude` como healthcheck. A última etapa confirmada antes do bloqueio do Actions preservava 11 migrações aplicadas; a migração `012_rotulos_entity_resolution.sql` **não deve ser considerada em produção até existir CI verde + promoção para `deploy` + confirmação no Railway**.

## Bloqueio operacional atual — GitHub Actions

O Actions não está falhando por teste, código, PostgreSQL ou indisponibilidade genérica de runner. O próprio check-run do GitHub informa:

> The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings.

Consequências:

- jobs terminam antes de receber runner (`runner_id = 0`, nenhuma etapa executada);
- F1-08b/c permanecem em `main`, mas **não** são promovidas para `deploy`;
- F1-08d permanece isolada em `work/f1-08d-relatorio` / PR #1;
- não é permitido contornar o gate movendo `deploy` manualmente;
- após regularizar **GitHub → Settings → Billing & plans / Actions spending limit**, os jobs devem ser reexecutados antes de qualquer promoção.

## Limites que continuam intencionais

- Não há alegação empírica de precisão ≥ 0,98 ou recall ≥ 0,95 sem amostra independente rotulada.
- O holdout final mede limiares congelados; ele nunca participa da escolha desses limiares.
- `INDETERMINADO` é cobertura não resolvida e não entra como classe negativa.
- Não há parâmetros `m/u` ou limiares de produção inventados.
- F05 ainda não entra no golden record enquanto não existir parser estruturado com contrato próprio.
- Geografia continua ausente do Entity Resolution até GEO-01 produzir coordenadas verificáveis.
- Nenhuma etapa da F1 move fatos existentes; identidade é versionada em camada própria.
