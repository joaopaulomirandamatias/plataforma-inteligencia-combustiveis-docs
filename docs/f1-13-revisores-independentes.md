# F1-13 — atribuição auditável de revisores independentes

## Problema

F1-08c tornou rótulos e adjudicações append-only e exige dois rótulos divergentes antes da adjudicação. Porém, o contrato original aceita `revisor_id` informado pelo lote de importação sem registrar previamente **quem estava designado** para revisar cada item.

Para a validação empírica isso deixa uma lacuna de protocolo: a dupla de revisores poderia ser escolhida ou alterada depois de iniciada a rotulagem, e um terceiro identificador não designado ainda conseguiria registrar um rótulo.

## Objetivo

F1-13 adiciona uma camada opcional e auditável de atribuição:

```text
experimento + itens registrados
        ↓
congelar dois revisores distintos
        ↓
atribuição append-only por item
        ↓
revisor A ─┐
           ├─ rótulos independentes
revisor B ─┘
        ↓
concordância → rótulo final humano
        ou
     divergência
        ↓
adjudicador C, diferente de A e B
```

A atribuição não contém rótulos, scores, thresholds, estratos visíveis ao revisor ou respostas esperadas.

## Contrato de persistência

Migração `014_atribuicao_revisores_entity_resolution.sql` adiciona:

`identidade.atribuicao_revisor_er`

- chave: `(experimento_id, item_id, revisor_id)`;
- `ordem ∈ {1,2}`;
- unicidade também por `(experimento_id, item_id, ordem)`;
- FK para o item cego do experimento;
- `INSERT` + `SELECT` para papéis de escrita; sem `UPDATE`/`DELETE`.

A integridade não depende somente da camada Python. O banco possui também:

1. trigger `BEFORE INSERT` que recusa criar atribuição depois que o item já recebeu qualquer rótulo;
2. `CONSTRAINT TRIGGER DEFERRABLE INITIALLY DEFERRED` que exige **exatamente dois revisores** quando a transação é confirmada, permitindo inserir ordem 1 e 2 na mesma transação mas rejeitando atribuição parcial por SQL direto;
3. trigger em `rotulo_er` que, no modo controlado, aceita apenas revisores atribuídos;
4. trigger em `adjudicacao_er` que proíbe um dos revisores atribuídos de adjudicar o mesmo item.

## Compatibilidade

Experimentos históricos sem nenhuma atribuição continuam seguindo o contrato F1-08c. Quando um item possui atribuições F1-13, o banco muda para o modo controlado daquele item:

- rótulo de revisor não atribuído falha alto;
- os dois revisores atribuídos podem registrar no máximo um rótulo cada, regra já garantida por F1-08c;
- adjudicador igual a um revisor atribuído falha alto.

O novo protocolo empírico deve usar sempre o modo controlado.

## Congelamento antes da revisão

A operação `atribuir_dois_revisores`:

1. exige experimento com itens registrados;
2. exige dois IDs opacos, não vazios e distintos;
3. recusa ativação depois que qualquer rótulo já existe no experimento;
4. atribui os dois revisores a todos os itens numa mesma transação;
5. repetir exatamente a mesma atribuição é idempotente;
6. tentar trocar, completar ou reinterpretar uma atribuição existente falha alto.

Isso impede usar o resultado humano para decidir retrospectivamente quem “conta” como revisor.

## Independência e cegamento

F1-13 não cria uma tela de colaboração entre revisores e não exporta rótulos de um revisor para o outro. O material entregue continua sendo o pacote cego F1-08a/F1-10/F1-12.

A função de consulta por revisor devolve apenas `item_id` cegos atribuídos; não devolve rótulos alheios nem referências internas.

## Operação

A CLI adiciona:

```text
pic-er atribuir-revisores \
  --experimento <experimento_id> \
  --revisor-a <id-opaco-a> \
  --revisor-b <id-opaco-b>
```

O comando deve ser executado depois de registrar o experimento e seus itens e **antes** da primeira importação de rótulos.

## Critérios de aceite

- [x] exatamente dois revisores distintos por item no modo controlado;
- [x] atribuição cobre todos os itens do experimento;
- [x] mesma atribuição é idempotente;
- [x] troca/atribuição parcial posterior falha alto;
- [x] ativação depois do primeiro rótulo falha alto;
- [x] SQL direto de revisor não atribuído falha alto;
- [x] SQL direto com apenas um revisor é rejeitado no commit;
- [x] SQL direto não consegue ativar F1-13 depois de existir rótulo;
- [x] os dois revisores atribuídos continuam podendo rotular independentemente;
- [x] adjudicador não pode ser nenhum dos dois revisores do item;
- [x] atribuição é append-only para o papel da aplicação;
- [x] experimento legado sem atribuição continua compatível;
- [x] CLI operacional para congelar a dupla de revisores;
- [x] lint + PostgreSQL 16 + suíte completa + OpenAPI verdes no Railway CI Sandbox;
- [ ] merge e migração 014 dependem do GitHub Actions oficial.

## Evidência técnica

PR draft: `#9` — `work/f1-13-revisores-independentes`.

Branch real validada:

`59d56d581283608d4a94a7eb0a24d4da1d03cc72`

Railway CI Sandbox, deployment:

`73c04009-d941-479f-9757-aa88cdf76d3a`

Resultado:

- `ruff check .`: PASS;
- suíte completa: **347 passed, 1 skipped, 2 deselected**;
- atribuição de revisores: **6 passed**;
- CLI de atribuição: **1 passed**;
- invariantes SQL da migração 014: **2 passed**;
- contrato OpenAPI: **8/8 passed**;
- `CI_RESULT=PASS`.

Esta evidência é técnica suplementar. O GitHub Actions oficial permanece bloqueado por Billing & plans; portanto F1-13 não está promovida, a migração 014 não foi aplicada em produção e a PR permanece draft.

## Limites

F1-13 não prova qualidade dos rótulos. Ele prova apenas que a composição do painel de revisão foi congelada e aplicada de forma auditável. Concordância, Kappa, adjudicação, precisão, recall e calibração permanecem resultados/etapas posteriores e dependem de dados humanos reais.
