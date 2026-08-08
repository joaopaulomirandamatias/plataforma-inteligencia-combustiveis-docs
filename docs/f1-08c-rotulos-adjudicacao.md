# F1-08c — Persistência de rótulos e adjudicação

## Objetivo

Persistir a revisão humana do experimento de Entity Resolution sem permitir que um rótulo original seja apagado, sobrescrito ou reinterpretado retroativamente.

A persistência é parte da evidência científica. O banco deve conseguir responder, para cada item:

- qual experimento e manifesto o originaram;
- qual versão do codebook estava vigente;
- quais revisores emitiram rótulos independentes;
- quando cada rótulo foi registrado;
- se houve divergência;
- qual adjudicação foi emitida depois, por quem e com qual justificativa;
- quais rótulos originais fundamentaram a adjudicação.

---

## Modelo append-only

### `identidade.experimento_er`

Cabeçalho imutável do experimento:

- `experimento_id` — identificador opaco e estável;
- `manifesto_sha256`;
- `codebook_versao`;
- `seed_amostragem`;
- `criado_em` pelo banco.

Uma mesma `experimento_id` não pode reaparecer com manifesto/codebook/seed diferente.

### `identidade.item_experimento_er`

Mapa interno entre o item cego e a referência técnica:

- `experimento_id`;
- `item_id` — o UUID opaco entregue ao revisor;
- `referencia_interna` — candidato/registro técnico que **não aparece no pacote cego**;
- `estrato_primario`;
- `estratos` estruturados;
- `criado_em`.

Unicidade por `(experimento_id, item_id)` e por `(experimento_id, referencia_interna)`.

### `identidade.rotulo_er`

Um rótulo independente por revisor/item:

- `experimento_id`;
- `item_id`;
- `revisor_id` opaco;
- `rotulo ∈ {MESMO_PONTO, PONTOS_DIFERENTES, INDETERMINADO}`;
- `justificativa` opcional apenas quando o codebook permitir; para `INDETERMINADO`, motivo estruturado é recomendado;
- `registrado_em` pelo banco.

Chave única `(experimento_id, item_id, revisor_id)`. O segundo envio do mesmo revisor não faz UPDATE: deve ser recusado. Uma correção humana futura exige um evento separado, se for metodologicamente permitida.

### `identidade.adjudicacao_er`

Evento posterior, sem apagar rótulos:

- `experimento_id`;
- `item_id`;
- `adjudicador_id`;
- `rotulo_final` nos mesmos três estados;
- `justificativa` obrigatória;
- `registrado_em`;
- referência explícita à versão do codebook/protocolo de adjudicação quando houver.

No máximo uma adjudicação vigente por item nesta fase. Se a metodologia exigir revisão da adjudicação no futuro, deve nascer uma tabela/evento versionado próprio — não um UPDATE.

---

## Invariantes de banco

O papel de escrita da aplicação recebe apenas `SELECT` e `INSERT` nessas tabelas. `UPDATE` e `DELETE` são negados pelo PostgreSQL, não por convenção de código.

Restrições obrigatórias:

- rótulo fora do conjunto fechado é rejeitado;
- item inexistente no experimento é rejeitado por FK;
- revisor/adjudicador vazio é rejeitado;
- justificativa de adjudicação vazia é rejeitada;
- segundo rótulo do mesmo revisor/item é conflito, nunca upsert destrutivo;
- adjudicação não altera `rotulo_er`;
- registrar rótulos/adjudicação não altera `posto_chave_fonte`, cluster, fatos ou fila F1-01.

---

## Blindagem

O módulo de importação recebe o **mapa interno separado** gerado pela F1-08b e respostas contendo somente `item_id + rotulo + revisor_id (+ justificativa)`. Ele não precisa receber score, limiares ou decisão automática.

A aplicação deve recusar campos de modelo em payloads de revisão se forem introduzidos em uma API futura; eles não fazem parte do contrato da revisão humana.

---

## Concordância e adjudicação

Uma função de leitura deve classificar cada item em:

- `SEM_REVISAO`;
- `UMA_REVISAO`;
- `CONCORDANTE` — dois ou mais rótulos válidos e todos iguais;
- `DIVERGENTE` — rótulos humanos distintos;
- `ADJUDICADO` — existe adjudicação append-only.

A decisão final para avaliação:

1. usa adjudicação quando existente;
2. caso contrário, usa o rótulo consensual quando houver concordância suficiente definida pelo protocolo;
3. caso contrário, permanece sem rótulo final e não é forçada para positivo/negativo.

`INDETERMINADO` continua sendo um estado real do processo, não um negativo disfarçado.

---

## Critérios de aceite executáveis

- [ ] migração aditiva/idempotente;
- [ ] experimento e itens são imutáveis;
- [ ] rótulo por revisor/item é exatamente uma vez;
- [ ] dois revisores podem rotular o mesmo item independentemente;
- [ ] divergência é detectada sem alterar rótulos;
- [ ] adjudicação é novo registro e exige justificativa;
- [ ] papel de escrita não consegue `UPDATE`/`DELETE`;
- [ ] nenhum efeito em fatos, clusters ou identidade vigente;
- [ ] suíte PostgreSQL + lint + contrato OpenAPI verdes;
- [ ] migração aplicada no Railway sem regressão de `/saude`.
