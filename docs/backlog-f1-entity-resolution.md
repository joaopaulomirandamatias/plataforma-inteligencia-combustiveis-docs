# F1 — Entity Resolution · sequência executável

Este backlog transforma a especificação de [`dados/entity-resolution.md`](dados/entity-resolution.md) em entregas pequenas, verificáveis e reversíveis. A regra de custo é assimétrica: **deixar de ligar dois registros é recuperável; ligar registros de postos diferentes propaga um histórico errado**.

## F1-01 — fila de revisão humana imutável

**Objetivo:** criar o primeiro artefato executável da F1 sem mudar nenhuma identidade vigente. Pares ambíguos podem ser registrados, revisados e usados depois como rótulo de treino, mas uma decisão desta etapa **não remapeia `posto_chave_fonte`**.

### Contrato de persistência

Duas tabelas aditivas no contexto `identidade`:

1. `candidato_ligacao`
   - par de chaves de fonte em ordem canônica (`fonte_a/chave_a < fonte_b/chave_b`);
   - `score` entre 0 e 1;
   - `metodo` e `versao_modelo` obrigatórios;
   - `evidencias` JSON objeto, nunca texto livre não estruturado;
   - `criado_em` pelo banco;
   - unicidade por par + versão do modelo.
2. `decisao_ligacao`
   - no máximo uma decisão por candidato;
   - `decisao ∈ {aceitar, rejeitar}`;
   - `revisor_id` opaco, sem e-mail/CPF/nome obrigatório;
   - `justificativa` obrigatória;
   - `decidido_em` pelo banco.

As duas tabelas são **append-only** para o papel de escrita da aplicação: `INSERT` e `SELECT`, nunca `UPDATE`/`DELETE`. Corrigir uma decisão errada será um evento próprio em card posterior; a F1-01 não permite apagar história.

### API interna de domínio

O backend deve oferecer funções para:

- canonicalizar um par independentemente da ordem recebida;
- enfileirar de forma idempotente o mesmo par/modelo;
- registrar uma decisão exatamente uma vez;
- recusar score fora de `[0,1]`, par consigo mesmo, evidência que não seja objeto, decisão desconhecida e justificativa vazia.

### Fora do escopo deste card

- cálculo de similaridade;
- blocking;
- geocodificação;
- Fellegi–Sunter / gradient boosting;
- alteração de `identidade.posto_chave_fonte`;
- clusterização ou golden record;
- qualquer endpoint público.

### Critérios de aceite

- [ ] migração aditiva e idempotente;
- [ ] par A↔B e B↔A produzem a mesma identidade de candidato;
- [ ] duplicata do mesmo par + versão retorna o candidato existente;
- [ ] decisão é única e append-only;
- [ ] decisão `aceitar` não altera `posto_chave_fonte`;
- [ ] papel de escrita não consegue `UPDATE`/`DELETE` nas tabelas novas;
- [ ] suíte padrão e lint verdes no CI;
- [ ] migração aplicada em produção sem regressão de `/saude`.

## Próximos cards

F1-02 normalização e representação de registros por fonte → F1-03 blocking mensurável → F1-04 vetor de similaridade e baseline Fellegi–Sunter → F1-05 calibração dos dois limiares → F1-06 cluster versionado + operação de separação → F1-07 golden record com proveniência campo a campo → F1-08 amostra rotulada e medição formal de precisão/recall.
