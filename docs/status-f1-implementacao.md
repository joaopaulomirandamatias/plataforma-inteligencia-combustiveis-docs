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
| F1-08a codebook/pacote cego | 🔄 em validação | testes e implementação em `main`; aguardando CI antes de promoção |
| F1-08b amostragem | ⬜ não iniciada | depende do contrato F1-08a verde |
| F1-08c adjudicação | ⬜ não iniciada | rótulos humanos devem ser append-only |
| F1-08d relatório | ⬜ não iniciada | depende de amostra real rotulada |

## Produção

O backend e o worker Railway acompanham somente a branch `deploy`, promovida pelo GitHub Actions depois de lint, PostgreSQL 16, suíte completa e validação explícita do contrato OpenAPI. O frontend usa o mesmo padrão `main → CI → deploy → Railway`.

A API usa `/saude` como healthcheck. Na validação da F1-07b, o serviço permaneceu com 11 migrações aplicadas e healthcheck HTTP 200. O worker preserva cron `0 6 * * *`, volume `/data` e política de restart existente.

## Limites que continuam intencionais

- Não há alegação empírica de precisão ≥ 0,98 ou recall ≥ 0,95 sem amostra independente rotulada.
- Não há parâmetros `m/u` ou limiares de produção inventados.
- F05 ainda não entra no golden record enquanto não existir parser estruturado com contrato próprio.
- Geografia continua ausente do Entity Resolution até GEO-01 produzir coordenadas verificáveis.
- Nenhuma etapa da F1 move fatos existentes; identidade é versionada em camada própria.
