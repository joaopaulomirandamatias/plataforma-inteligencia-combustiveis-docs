# Status executado — F1 Entity Resolution

Atualizado em 2026-08-08 após promoção oficial do F1-15.

Este documento separa quatro estados:

1. **implementado** — existe código, migração, teste ou artefato;
2. **validado tecnicamente** — passou pelos gates automatizados;
3. **integrado em `main`** — a mudança está no branch principal;
4. **promovido oficialmente** — o GitHub Actions oficial aprovou o SHA, promoveu-o para `deploy` e o Railway confirmou o rollout.

## Estado executivo atual

- `main` e `deploy` estão em `0a7616ada0e1b97e7ca040571b91dae2f2cd44f2`.
- Tree SHA do produto promovido: `e51c74d091553487710961679aa0d84e1249301d`.
- PR #16 foi validada oficialmente e mesclada.
- GitHub Actions voltou a funcionar após regularização de Billing.
- CI oficial da PR #16: **369 passed, 1 skipped, 2 deselected** + **OpenAPI 8/8** + lint verde.
- CI oficial de `main` também ficou verde e a etapa de promoção para `deploy` foi executada com sucesso.
- Railway `pic-api` e `pic-worker` executam o mesmo SHA promovido e estão `SUCCESS`.
- `/saude` respondeu **HTTP 200** após o rollout.
- Migrações 012, 013, 014, 015 e 016 foram aplicadas pelo fluxo normal de inicialização; nenhuma foi aplicada manualmente.
- Postgres, `pic-api`, `pic-web` e `pic-worker` estão em estado `SUCCESS` no ambiente de produção.
- O worker mantém o cron `0 6 * * *`.
- Issue #2 de bloqueio do GitHub Actions foi encerrada como resolvida.

## Cards F1

| Card | Estado | Evidência principal |
|---|---|---|
| F1-01 fila de revisão | ✅ produção | migração 010, revisão e testes |
| F1-02 normalização | ✅ produção | normalizadores determinísticos |
| F1-03 blocking | ✅ produção | blocking cross-source mensurável |
| F1-04 similaridade + FS | ✅ produção | vetor multi-campo e FS com parâmetros explícitos |
| F1-05 calibração | ✅ engenharia / ⏳ empírico | estrutura pronta; parâmetros reais dependem de ground truth humano |
| F1-06 clusters | ✅ produção | migração 011 e snapshots imutáveis |
| F1-07 golden record | ✅ produção | política versionada e proveniência |
| F1-08a v2 blindagem | ✅ produção | codebook `f1-08a-v2`; estratos não chegam ao revisor |
| F1-08b amostragem | ✅ produção | seed + quotas determinísticas |
| F1-08c rótulos/adjudicação | ✅ produção | migração 012, append-only e gate SQL de divergência |
| F1-08d relatório formal | ✅ produção | Wilson 95%, holdout, Kappa, blocking e métricas por estrato |
| F1-08e operação | ✅ produção | `pic-er`, importação e status |
| F1-09 pipeline candidatos | ✅ produção | migração 013 e escalas explícitas |
| F1-10 fila → amostra | ✅ produção | pacote cego com barreiras de vazamento |
| F1-11 manifesto | ✅ produção | manifesto canônico e verificável |
| F1-12 população congelada | ✅ produção | `populacao_sha256` vinculado aos snapshots/cortes |
| F1-13 revisores independentes | ✅ produção | migração 014, exatamente dois revisores antes dos rótulos |
| F1-14 pacote por revisor | ✅ produção | migração 015, pacote cego individual, SHA e mapa exato de itens |
| F1-15 split treino/calibração/teste | ✅ produção | migração 016 e grupos estruturais com barreira de leakage |

## Validação oficial

O fluxo oficial executou no GitHub Actions:

- PostgreSQL 16 em container;
- checkout do backend;
- checkout do contrato OpenAPI canônico do repositório de documentação;
- Python 3.13;
- instalação das dependências;
- `ruff check .`;
- `pytest -ra`;
- reexecução explícita de `tests/test_conformidade_contrato.py -q --strict-markers`;
- promoção do SHA exato para `deploy` apenas no `push` verde de `main`.

Resultado final da árvore promovida:

- **369 passed**;
- **1 skipped**;
- **2 deselected**;
- **OpenAPI 8/8**;
- lint verde;
- promoção para `deploy` verde.

## Railway — produção

Projeto: `Plataforma Combustível`.

Serviços confirmados:

| Serviço | Estado |
|---|---|
| Postgres | `SUCCESS` |
| pic-api | `SUCCESS` |
| pic-web | `SUCCESS` |
| pic-worker | `SUCCESS` |

SHA do backend/worker promovido:

`0a7616ada0e1b97e7ca040571b91dae2f2cd44f2`

No startup da API foram registradas como aplicadas pelo fluxo normal:

- `012_rotulos_entity_resolution.sql`;
- `013_escala_pontuacao_candidatos.sql`;
- `014_atribuicao_revisores_entity_resolution.sql`;
- `015_pacote_revisor_entity_resolution.sql`;
- `016_particionamento_entity_resolution.sql`.

Após o startup, `/saude` retornou HTTP 200.

## Railway CI Sandbox

O `PIC CI Sandbox` foi criado como ambiente isolado de validação durante o bloqueio de Billing do GitHub Actions. Ele cumpriu um papel útil: encontrou erros reais antes da promoção e permitiu validar a árvore final com PostgreSQL 16 sem tocar em produção.

Principais resultados históricos:

| Alvo | Resultado |
|---|---|
| integration train #1+#3+#4+#5+#6+#7 | **331 passed**, 1 skipped, 2 deselected; OpenAPI 8/8 |
| F1-12 | **338 passed**, 1 skipped, 2 deselected; OpenAPI 8/8 |
| F1-13 | **347 passed**, 1 skipped, 2 deselected; OpenAPI 8/8 |
| F1-14 | **359 passed**, 1 skipped, 2 deselected; OpenAPI 8/8 |
| F1-15 final | **369 passed**, 1 skipped, 2 deselected; OpenAPI 8/8 |

Deployment final do F1-15 no sandbox: `55be0aa3-11e5-44b6-919d-578a3fba8993`.

A árvore validada no sandbox foi a mesma árvore posteriormente aprovada pelo GitHub Actions oficial.

O sandbox agora é **redundante**, não autoridade de promoção. Sua remoção deve ser uma decisão explícita porque implica apagar infraestrutura Railway.

## Defeitos reais encontrados e corrigidos antes da promoção

- F1-09: `ruff I001` em teste do pipeline;
- F1-11: incompatibilidade de round-trip `tuple`/`list` no manifesto;
- F1-12: `ruff I001` ao adicionar teste de isolamento da fila;
- F1-13: necessidade de constraint trigger para impedir atribuição parcial de um único revisor;
- F1-14: `ruff I001` e loophole de hash+contagem sem mapa exato de itens;
- F1-15: `ruff B023` em closure do desempate e necessidade de barreira SQL contra o mesmo registro cru atravessar partições.

## F1-14 — proveniência do julgamento humano

F1-14 fecha a ligação entre o julgamento humano e o artefato cego associado ao revisor.

Antes do primeiro rótulo são registrados:

- `pacote_sha256`;
- manifesto e codebook;
- revisor;
- quantidade de itens;
- mapa exato de `item_id` do pacote.

Quando F1-14 está ativo, o rótulo precisa citar exatamente o SHA registrado. Rótulos históricos permanecem compatíveis com `NULL`; não existe backfill inventado.

SHA-256 prova integridade/reprodutibilidade do artefato, não autenticidade da pessoa nem correção do julgamento.

## F1-15 — separação treino/calibração/teste

F1-15 congela o split antes dos rótulos humanos.

Cada par de revisão é tratado como aresta entre registros `(fonte, chave)`. Pares conectados por qualquer registro, inclusive transitivamente, formam um grupo indivisível. Assim, o mesmo registro observado não pode aparecer em treino e teste, ou calibração e teste.

Seed e pesos das partições são entradas explícitas do protocolo; não existem proporções escondidas no código.

O PostgreSQL valida no `COMMIT`:

- cobertura de todos os itens;
- contagem dos grupos;
- existência das três partições;
- referências `candidato_ligacao:<id>` válidas;
- ausência do mesmo registro de origem em partições distintas.

Limite metodológico: um componente estrutural não é declarado como identidade física verdadeira. Dois componentes distintos ainda podem representar o mesmo posto; isso só pode ser auditado depois de ground truth humano real.

## Fronteira atual da engenharia

A engenharia pré-rótulo cobre agora:

1. snapshots/cortes de fontes congelados;
2. geração auditável da população candidata;
3. `populacao_sha256` determinístico;
4. amostragem estratificada e pacote cego;
5. registro imutável do experimento;
6. exatamente dois revisores independentes pré-atribuídos;
7. pacote cego individual por revisor com SHA e mapa de itens;
8. split treino/calibração/teste congelado por grupos estruturais antes dos rótulos;
9. rótulos append-only;
10. adjudicação por terceiro independente;
11. relatório formal de holdout com Wilson 95%, blocking e concordância.

O próximo avanço científico depende de **evidência empírica real**, não de mais resultados sintéticos.

## Próxima fase empírica — não fabricar

1. selecionar os snapshots reais que formarão o experimento;
2. gerar a população real de candidatos;
3. congelar manifesto, população e split;
4. definir formalmente seed e pesos de treino/calibração/teste;
5. registrar dois revisores humanos reais independentes;
6. produzir os pacotes cegos individuais e registrar seus SHAs;
7. coletar rótulos independentes;
8. adjudicar divergências com terceiro humano independente;
9. auditar leakage residual após ground truth; se o teste estiver contaminado, criar novo teste sem observar métricas finais;
10. usar treino para parâmetros/modelo;
11. usar calibração para limiares;
12. congelar parâmetros e thresholds;
13. auditar blocking independentemente;
14. abrir o holdout `teste` uma única vez;
15. executar F1-08d e aceitar ou rejeitar as metas conforme os dados.

Não inventar:

- rótulos de revisores;
- `m/u`;
- thresholds;
- precisão/recall;
- Kappa;
- blocking recall;
- calibração;
- evidência de identidade física.

## Limites intencionais mantidos

- falso positivo de identidade é mais custoso que vínculo perdido;
- `INDETERMINADO` não vira negativo automaticamente;
- peso Fellegi–Sunter `log2(m/u)` não é probabilidade;
- `probabilidade_01` exige calibração explícita;
- F05 permanece fora do ER/golden record até parser estruturado próprio;
- geografia permanece fora até GEO-01 produzir coordenadas verificáveis;
- fatos continuam imutáveis/bitemporais; identidade é camada separada e versionada;
- nenhuma etapa F1 autoriza alegação de fraude.
