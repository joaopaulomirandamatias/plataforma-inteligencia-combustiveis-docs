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

## Critérios de aceite

- [ ] exatamente dois revisores distintos por item no modo controlado;
- [ ] atribuição cobre todos os itens do experimento;
- [ ] mesma atribuição é idempotente;
- [ ] troca/atribuição parcial posterior falha alto;
- [ ] ativação depois do primeiro rótulo falha alto;
- [ ] SQL direto de revisor não atribuído falha alto;
- [ ] os dois revisores atribuídos continuam podendo rotular independentemente;
- [ ] adjudicador não pode ser nenhum dos dois revisores do item;
- [ ] atribuição é append-only para o papel da aplicação;
- [ ] experimento legado sem atribuição continua compatível;
- [ ] lint + PostgreSQL 16 + suíte completa + OpenAPI verdes no Railway CI Sandbox;
- [ ] merge e migração 014 dependem do GitHub Actions oficial.

## Limites

F1-13 não prova qualidade dos rótulos. Ele prova apenas que a composição do painel de revisão foi congelada e aplicada de forma auditável. Concordância, Kappa, adjudicação, precisão, recall e calibração permanecem resultados/etapas posteriores e dependem de dados humanos reais.
