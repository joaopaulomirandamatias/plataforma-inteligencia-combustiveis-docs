# Status executado — F1 Entity Resolution

Atualizado em 2026-08-08. Este documento separa deliberadamente quatro estados que não podem ser confundidos:

1. **implementado** — existe código, migração, teste ou artefato;
2. **validado tecnicamente** — passou por lint + suíte completa em PostgreSQL 16 + contrato OpenAPI no Railway CI Sandbox;
3. **integrado em `main`** — o conteúdo chegou ao branch de desenvolvimento, ainda sem significar aprovação para produção;
4. **promovido oficialmente** — passou pelo GitHub Actions oficial, foi promovido para `deploy` e confirmado no Railway de produção.

A validação no Railway CI Sandbox é evidência técnica suplementar. Ela não autoriza mover `deploy`, aplicar migrações manualmente ou declarar rollout em produção.

## Estado executivo atual

- Produção continua em `deploy` @ `fe222717a9beec1e2684f8b6ea56aeb2a6c4cda8`.
- `main` está em `6636274321b0a73777c27005f27064f52a822df2` e recebeu por merges concorrentes a pilha F1 até uma versão intermediária do F1-15, além de arquivos temporários do Railway CI Sandbox.
- A PR #16 reconcilia `main` com a árvore limpa e final do F1-15.
- A árvore resultante da PR #16 é `e51c74d091553487710961679aa0d84e1249301d`, exatamente a árvore já validada no sandbox.
- GitHub Actions continua bloqueado por Billing & plans: novas tentativas ainda terminam antes do primeiro step.
- Não houve promoção de `deploy` nem aplicação manual das migrações 012–016 em produção.
- As antigas PRs empilhadas #1, #3, #4, #5, #6, #7, #8, #9, #10 e #15 foram encerradas como **supersedidas/absorvidas**, não mergeadas novamente.
- A PR #16 é a única PR aberta e o único caminho de reconciliação autorizado.

## Cards F1

| Card | Estado atual | Evidência principal |
|---|---|---|
| F1-01 fila de revisão | ✅ produção | migração 010, revisão e testes |
| F1-02 normalização | ✅ produção | normalizadores determinísticos |
| F1-03 blocking | ✅ produção | blocking cross-source mensurável |
| F1-04 similaridade + FS | ✅ produção | vetor multi-campo e FS com parâmetros explícitos |
| F1-05 calibração | ✅ engenharia / ⏳ empírico | thresholds e parâmetros reais dependem de rótulos humanos |
| F1-06 clusters | ✅ produção | migração 011 e snapshots imutáveis |
| F1-07 golden record | ✅ produção | política versionada e proveniência |
| F1-08a v2 blindagem | 🟢 integrado em `main` / sandbox verde / oficial bloqueado | codebook `f1-08a-v2`; estratos não chegam ao revisor |
| F1-08b amostragem | 🟢 integrado em `main` / sandbox verde / oficial bloqueado | seed + quotas determinísticas |
| F1-08c rótulos/adjudicação | 🟢 integrado em `main` / sandbox verde / oficial bloqueado | migração 012, append-only e gate SQL de divergência |
| F1-08d relatório formal | 🟢 integrado em `main` / sandbox verde / oficial bloqueado | Wilson 95%, holdout, Kappa, blocking e métricas por estrato |
| F1-08e operação | 🟢 integrado em `main` / sandbox verde / oficial bloqueado | `pic-er`, importação e status |
| F1-09 pipeline candidatos | 🟢 integrado em `main` / sandbox verde / oficial bloqueado | migração 013 e escalas explícitas |
| F1-10 fila → amostra | 🟢 integrado em `main` / sandbox verde / oficial bloqueado | pacote cego com barreiras de vazamento |
| F1-11 manifesto | 🟢 integrado em `main` / sandbox verde / oficial bloqueado | manifesto canônico e verificável |
| F1-12 população congelada | 🟢 integrado em `main` / sandbox verde / oficial bloqueado | `populacao_sha256` vinculado aos snapshots/cortes |
| F1-13 revisores independentes | 🟢 integrado em `main` / sandbox verde / oficial bloqueado | migração 014, exatamente dois revisores antes dos rótulos |
| F1-14 pacote por revisor | 🟢 integrado em `main` / sandbox verde / oficial bloqueado | migração 015, pacote cego individual, SHA e mapa exato de itens |
| F1-15 split treino/calibração/teste | 🟢 PR #16 reconcilia versão final / sandbox verde / oficial bloqueado | migração 016 e componentes conectados sem leakage direto |

## Railway CI Sandbox — evidência técnica

O projeto isolado `PIC CI Sandbox` usa PostgreSQL 16 dedicado, banco descartável por execução e nenhuma credencial de produção. O gate executa:

- `ruff check .`;
- `pytest -ra`;
- contrato OpenAPI novamente com `--strict-markers`;
- `CI_RESULT=PASS` somente após todos os gates.

Resultados principais acumulados:

| Alvo | Resultado |
|---|---|
| integration train #1+#3+#4+#5+#6+#7 | **331 passed**, 1 skipped, 2 deselected; OpenAPI 8/8 |
| F1-12 | **338 passed**, 1 skipped, 2 deselected; OpenAPI 8/8 |
| F1-13 | **347 passed**, 1 skipped, 2 deselected; OpenAPI 8/8 |
| F1-14 | **359 passed**, 1 skipped, 2 deselected; OpenAPI 8/8 |
| F1-15 final | **369 passed**, 1 skipped, 2 deselected; OpenAPI 8/8; `CI_RESULT=PASS` |

Deployment final F1-15 no sandbox: `55be0aa3-11e5-44b6-919d-578a3fba8993`.

A árvore validada é `e51c74d091553487710961679aa0d84e1249301d`, a mesma árvore produzida pela PR #16.

## Defeitos reais encontrados e corrigidos

O sandbox não foi tratado como mera formalidade. Ele encontrou e bloqueou defeitos reais, todos corrigidos na branch de produto antes da validação final:

- F1-09: `ruff I001` em teste do pipeline;
- F1-11: incompatibilidade de round-trip `tuple`/`list` no manifesto;
- F1-12: `ruff I001` ao adicionar teste de isolamento da fila;
- F1-13: necessidade de constraint trigger para impedir atribuição parcial de um único revisor;
- F1-14: `ruff I001` e, na revisão adversarial, loophole de hash+contagem sem mapa exato de itens;
- F1-15: `ruff B023` em closure do desempate e necessidade de barreira SQL contra o mesmo registro cru atravessar partições.

## F1-14 — proveniência do julgamento humano

F1-14 adiciona a migração 015 e fecha a ligação entre julgamento humano e o artefato efetivamente associado ao revisor.

O protocolo novo registra antes do primeiro rótulo:

- `pacote_sha256`;
- manifesto e codebook;
- revisor opaco;
- quantidade de itens;
- mapa exato de `item_id` do pacote.

Quando F1-14 está ativo, o rótulo precisa citar exatamente o SHA registrado. Rótulos históricos permanecem compatíveis com `NULL`; não existe backfill inventado.

SHA-256 aqui prova integridade/reprodutibilidade do artefato, não autenticidade da pessoa nem correção do julgamento.

## F1-15 — separação treino/calibração/teste

F1-15 adiciona a migração 016 e congela o split antes dos rótulos humanos.

Cada par de revisão é tratado como aresta entre registros `(fonte, chave)`. Pares conectados por qualquer registro, inclusive transitivamente, formam um grupo indivisível. Assim, o mesmo registro observado não pode aparecer em treino e teste, ou calibração e teste.

Seed e pesos das partições são entradas explícitas do protocolo; o código não esconde proporções padrão.

O PostgreSQL valida no `COMMIT`:

- cobertura de todos os itens;
- contagem de grupos;
- existência das três partições;
- referências `candidato_ligacao:<id>` válidas;
- ausência do mesmo registro de origem em partições distintas.

Limite metodológico: um componente estrutural não é declarado como identidade física verdadeira. Dois componentes distintos ainda podem representar o mesmo posto; isso só pode ser auditado após ground truth humano real.

## Reconciliação do `main`

Durante a execução, PRs temporárias #11–#14 foram mergeadas diretamente em `main`. Isso absorveu a pilha funcional F1, mas também levou arquivos do runner temporário e uma versão intermediária do F1-15.

A PR #16 resolve sem reescrever histórico:

1. remove `Dockerfile.ci`, `Dockerfile.ci.dockerignore`, `railway.ci.json`, `ci/railway_ci.py` e três markers temporários;
2. aplica a correção final B023 do F1-15;
3. adiciona a operação final de congelamento/exportação do split;
4. adiciona o teste operacional correspondente.

A árvore resultante é byte a byte igual à árvore validada no sandbox.

## Produção

A produção continua protegida pela branch `deploy`.

SHA confirmado:

`fe222717a9beec1e2684f8b6ea56aeb2a6c4cda8`

API e worker permanecem nesse estado. As migrações 012, 013, 014, 015 e 016 **não são consideradas aplicadas em produção**.

Nunca usar como atalho:

- mover `deploy` manualmente;
- apontar Railway para `main`;
- aplicar 012–016 manualmente;
- declarar rollout porque o sandbox ficou verde.

## Bloqueio operacional — GitHub Actions

Mesmo após o usuário informar que o GitHub foi ativado, novas tentativas oficiais em 2026-08-08 continuam terminando sem executar qualquer step. A anotação do check continua informando:

> The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings.

Portanto, o desbloqueio ainda não foi propagado ao executor do GitHub Actions ou permanece alguma restrição de pagamento/spending limit.

Issue #2 permanece aberta até o primeiro job oficial realmente receber runner e executar lint/testes.

## Sequência segura quando o Actions desbloquear

Não existe mais necessidade de mesclar a antiga cadeia #1/#3/#4/#5/#6/#7/#8/#9/#10/#15: elas foram encerradas como supersedidas.

A sequência agora é curta:

1. executar GitHub Actions oficial na PR #16;
2. somente se verde, mesclar #16 em `main`;
3. executar o CI oficial do novo `main`;
4. permitir que o workflow promova o **SHA exato** aprovado para `deploy`;
5. confirmar no Railway que API e worker executam o mesmo SHA;
6. confirmar `/saude` HTTP 200;
7. confirmar aplicação controlada das migrações 012–016;
8. só então iniciar o experimento empírico real.

## Fronteira atual da engenharia

A engenharia pré-rótulo agora cobre:

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

A partir daqui, a principal fronteira não é criar mais resultados sintéticos: é coletar evidência empírica real.

## Próxima fase empírica — não fabricar

Após o rollout oficial:

1. gerar a população real a partir dos snapshots escolhidos;
2. congelar manifesto, população e split;
3. produzir os pacotes cegos individuais;
4. registrar dois revisores humanos reais;
5. coletar rótulos independentes;
6. adjudicar divergências com terceiro humano independente;
7. auditar blocking por conjunto independente;
8. usar treino apenas para parâmetros/modelo;
9. usar calibração apenas para limiares;
10. congelar parâmetros/thresholds;
11. abrir o holdout `teste` uma única vez;
12. executar F1-08d e aceitar ou rejeitar as metas conforme os dados.

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
