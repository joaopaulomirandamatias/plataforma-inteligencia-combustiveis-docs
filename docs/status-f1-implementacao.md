# Status executado — F1 Entity Resolution

Atualizado em 2026-08-08. Este arquivo separa deliberadamente três estados que não podem ser confundidos:

1. **implementado** — existe código/teste/artefato no repositório;
2. **validado tecnicamente** — passou por lint + suíte completa em PostgreSQL 16 + contrato OpenAPI no Railway CI Sandbox;
3. **promovido oficialmente** — passou pelo GitHub Actions oficial, foi promovido para `deploy` e confirmado no Railway de produção.

A validação no Railway CI Sandbox é evidência técnica suplementar. Ela **não autoriza** mover `deploy`, aplicar migrações manualmente ou declarar rollout em produção enquanto o gate oficial estiver bloqueado.

| Card | Estado | Evidência principal |
|---|---|---|
| F1-01 fila de revisão | ✅ concluída / produção | migração 010, módulo de revisão, testes e produção saudável |
| F1-02 normalização | ✅ concluída / produção | normalizadores determinísticos e testes de CNPJ/CEP/UF/texto |
| F1-03 blocking | ✅ concluída / produção | blocking cross-source mensurável, redução/cobertura, sem vínculo automático |
| F1-04 similaridade + FS | ✅ concluída / produção | vetor multi-campo + Fellegi–Sunter somente com parâmetros explícitos |
| F1-05 calibração | ✅ engenharia / ⏳ empírico | dois limiares e métricas implementados; parâmetros reais dependem de rótulos humanos |
| F1-06 clusters | ✅ concluída / produção | migração 011, snapshots imutáveis, revisão/split e consultas as-of |
| F1-07a golden record puro | ✅ concluída / produção | política versionada, proveniência, alternativas, cobertura e corte bitemporal |
| F1-07b adaptador F01 | ✅ concluída / produção | PostgreSQL → candidatos F01 → golden record; rollout protegido |
| F1-08a codebook/pacote cego v1 | ✅ concluída / produção | IDs opacos; pacote sem score/threshold/destino/chaves internas |
| F1-08a v2 blindagem de estratos | 🟢 PR #5 / sandbox verde / oficial bloqueado | estratos permanecem internos; pacote exporta somente ID opaco + evidências factuais; 269 testes + OpenAPI 8/8 |
| F1-08b amostragem | 🟢 `main` / sandbox verde / oficial bloqueado | quotas exatas, ranking SHA-256 por seed e reconciliação interna; `main`: 269 testes + OpenAPI 8/8 |
| F1-08c rótulos/adjudicação | 🟢 `main` / sandbox verde / oficial bloqueado | migração 012 append-only, dupla revisão e trigger SQL de divergência; `main`: 269 testes + OpenAPI 8/8 |
| F1-08d relatório formal | 🟢 PR #1 / sandbox verde / oficial bloqueado | holdout, Wilson 95%, estratos, blocking, Kappa, versões e JSON canônico; 283 testes + OpenAPI 8/8 |
| F1-08e operação | 🟢 PR #3 / sandbox verde / oficial bloqueado | `pic-er`: pacote cego, registro, rótulos, adjudicação e status; 275 testes + OpenAPI 8/8 |
| F1-09 pipeline de candidatos | 🟢 PR #4 / sandbox verde / oficial bloqueado | migração 013, escala explícita e pipeline F01↔F02/F03→fila; 292 testes + OpenAPI 8/8 |
| F1-10 fila → amostra cega | 🟢 PR #6 / composição sandbox verde / oficial bloqueado | validação integrada #4 + #5 + #6; bloqueio estrutural contra vazamento de estratos/referências; 299 testes + OpenAPI 8/8 |
| F1-11 manifesto reproduzível | 🟢 PR #7 / sandbox verde / oficial bloqueado | manifesto canônico auto-verificável, hash derivado e CLI; 287 testes + OpenAPI 8/8 |

## Railway CI Sandbox

Foi criado um projeto Railway isolado, `PIC CI Sandbox`, com PostgreSQL 16 dedicado e sem credenciais de produção. O runner:

- recria banco descartável por serviço;
- executa `ruff check .`;
- executa a suíte padrão `pytest -ra`;
- executa novamente o contrato OpenAPI com `--strict-markers`;
- imprime `CI_RESULT=PASS` somente após todos os gates passarem.

Resultados confirmados:

| Alvo | Resultado técnico |
|---|---|
| `main` F1-08b/c | 269 passed, 1 skipped, 2 deselected; OpenAPI 8/8; PASS |
| PR #5 F1-08a v2 | 269 passed, 1 skipped, 2 deselected; OpenAPI 8/8; PASS |
| PR #1 F1-08d | 283 passed, 1 skipped, 2 deselected; OpenAPI 8/8; PASS |
| PR #3 F1-08e | 275 passed, 1 skipped, 2 deselected; OpenAPI 8/8; PASS |
| PR #4 F1-09 | 292 passed, 1 skipped, 2 deselected; OpenAPI 8/8; PASS |
| PR #6 integrada com #4+#5 | 299 passed, 1 skipped, 2 deselected; OpenAPI 8/8; PASS |
| PR #7 F1-11 | 287 passed, 1 skipped, 2 deselected; OpenAPI 8/8; PASS |
| integration train #1+#3+#4+#5+#6+#7 | **331 passed**, 1 skipped, 2 deselected; OpenAPI 8/8; **PASS** |

O integration train usa os artefatos das PRs em uma branch temporária e cobre simultaneamente migração 013, pipeline, blindagem v2, fila→amostra, operação, manifesto e relatório formal. Ele serve para detectar incompatibilidades entre cards antes dos merges oficiais.

## Defeitos reais encontrados pelo sandbox e corrigidos

### PR #4 — ordenação de imports

O primeiro source-build válido da PR #4 foi bloqueado pelo `ruff` por `I001` em `tests/test_pipeline_entity_resolution_carga.py`. A correção foi aplicada na branch real da PR, sem relaxar lint. Após o ajuste, a suíte completa passou, inclusive:

- `tests/test_migracao_013_compatibilidade.py`;
- `tests/test_pipeline_entity_resolution.py`;
- `tests/test_pipeline_entity_resolution_carga.py`;
- `tests/test_pipeline_entity_resolution_postgres.py`;
- `tests/test_pontuacao_candidatos.py`.

### PR #7 — round-trip do manifesto

O primeiro run válido da PR #7 revelou que `dataclasses.asdict()` preservava estruturas `tuple` em memória enquanto o próprio validador aceitava apenas `list`. Assim, um artefato produzido pelo sistema podia falhar no próprio round-trip. A branch real foi corrigida para aceitar `list/tuple` na representação interna e normalizar para lista sem flexibilizar outros tipos. Depois da correção, os testes de manifesto passaram e o integration train completo permaneceu verde.

## Produção

O backend e o worker Railway acompanham somente a branch `deploy`, promovida pelo GitHub Actions oficial depois de lint, PostgreSQL 16, suíte completa e validação explícita do contrato OpenAPI.

A API usa `/saude` como healthcheck. O último SHA confirmado em produção continua sendo:

`fe222717a9beec1e2684f8b6ea56aeb2a6c4cda8`

Esse SHA corresponde à F1-08a v1. API e worker estão no mesmo commit de `deploy`. As migrações `012_rotulos_entity_resolution.sql` e `013_escala_pontuacao_candidatos.sql` **não são consideradas em produção** até ocorrer CI oficial verde + promoção automática para `deploy` + confirmação posterior no Railway.

## Bloqueio operacional atual — GitHub Actions

O GitHub Actions oficial continua encerrando o job antes de executar qualquer etapa. O check-run informou:

> The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings.

Consequências:

- job `validar` termina antes de receber runner (`runner_id = 0`, `steps = null`);
- F1-08b/c permanecem em `main`, mas não são promovidas para `deploy`;
- PRs #1, #3, #4, #5, #6 e #7 permanecem sem autorização para merge oficial;
- o Railway CI Sandbox não substitui o gate documentado;
- não é permitido contornar o gate movendo `deploy` ou aplicando 012/013 manualmente.

Ação externa necessária: regularizar **GitHub → Settings → Billing & plans**, verificando pagamento, limite de gastos do Actions e minutos/uso em repositórios privados.

## Ordem de integração após desbloqueio

A ordem deve preservar dependências e fazer o CI oficial rodar depois de cada merge:

1. reexecutar CI oficial de `main` para F1-08b/c + migração 012;
2. permitir promoção automática para `deploy` somente se verde;
3. confirmar API/worker no mesmo SHA, 12 migrações e `/saude` HTTP 200;
4. mesclar PR #5 — codebook v2 / blindagem de estratos;
5. mesclar PR #1 — relatório formal F1-08d;
6. mesclar PR #3 — operação F1-08e;
7. mesclar PR #7 — manifesto reproduzível F1-11, após #3;
8. mesclar PR #4 — pipeline F1-09 / migração 013;
9. retarget/rebase e mesclar PR #6 — fila→amostra, já sobre #4 + #5;
10. após cada merge, aguardar CI oficial verde, promoção e confirmação antes do card seguinte.

## Próxima fase empírica

Depois que a árvore acima estiver oficialmente promovida, o trabalho deixa de ser apenas engenharia de infraestrutura e passa a exigir dados humanos reais:

1. gerar população real de candidatos;
2. congelar fontes, cortes, commit, normalizador, blocking, similaridade, modelo, seed e quotas no manifesto F1-11;
3. gerar amostra estratificada determinística;
4. produzir pacotes cegos v2;
5. obter pelo menos dois revisores humanos independentes;
6. adjudicar divergências;
7. separar treino/calibração/holdout por identidade/cluster, sem vazamento;
8. auditar blocking de forma independente;
9. congelar parâmetros e limiares;
10. executar o relatório F1-08d no holdout final.

Somente essa fase pode sustentar alegações empíricas de qualidade.

## Limites que continuam intencionais

- Não há alegação empírica de precisão ≥ 0,98 ou recall ≥ 0,95 sem amostra independente rotulada.
- O holdout final mede limiares congelados; ele nunca participa da escolha desses limiares.
- `INDETERMINADO` é cobertura não resolvida e não entra como classe negativa.
- A meta de precisão/recall só é considerada sustentada quando o **limite inferior** do intervalo de Wilson 95% também atende ao requisito.
- `blocking_recall` e `reduction_ratio` são reportados separadamente para impedir que a avaliação condicional ao classificador esconda pares perdidos antes do score.
- Peso Fellegi–Sunter `log2(m/u)` não é probabilidade e não é convertido implicitamente para `[0,1]`.
- `probabilidade_01` exige artefato explícito de calibração.
- F1-09 começa apenas por pendências `cnpj_sem_posto`; `cnpj_ausente/invalido` exigem política de chave própria.
- F05 ainda não entra no golden record enquanto não existir parser estruturado com contrato próprio.
- Geografia continua ausente do Entity Resolution até GEO-01 produzir coordenadas verificáveis.
- Nenhuma etapa da F1 move fatos existentes; identidade é versionada em camada própria.
