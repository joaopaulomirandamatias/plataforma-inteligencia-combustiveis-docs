# F1 — Entity Resolution · sequência executável

Este backlog transforma a especificação de [`dados/entity-resolution.md`](dados/entity-resolution.md) em entregas pequenas, verificáveis e reversíveis. A regra de custo é assimétrica: **deixar de ligar dois registros é recuperável; ligar registros de postos diferentes propaga um histórico errado**.

## F1-01 — fila de revisão humana imutável ✅

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

### Critérios de aceite

- [x] migração aditiva e idempotente;
- [x] par A↔B e B↔A produzem a mesma identidade de candidato;
- [x] duplicata do mesmo par + versão retorna o candidato existente;
- [x] decisão é única e append-only;
- [x] decisão `aceitar` não altera `posto_chave_fonte`;
- [x] papel de escrita não consegue `UPDATE`/`DELETE` nas tabelas novas;
- [x] suíte padrão e lint verdes no CI;
- [x] migração aplicada em produção sem regressão de `/saude`.

**Evidência de fechamento (2026-08-08):** migração `010_fila_revisao_identidade.sql`; módulo `pic.resolucao_identidade`; suíte `test_fila_revisao_identidade.py`; GitHub Actions backend verde com PostgreSQL 16 e contrato OpenAPI; Railway com 10 migrações aplicadas e healthcheck `/saude` retornando 200.

## F1-02 — representação normalizada por fonte ✅

**Objetivo:** produzir campos comparáveis para blocking/similaridade sem substituir nem corrigir o dado de origem. O original continua na zona bruta/fato; a normalização é uma projeção versionada e reproduzível.

### Entrega

- normalizadores puros para CNPJ, CEP, UF, texto empresarial e endereço;
- representação de identidade com `fonte`, `chave_fonte`, versão do normalizador e campos normalizados;
- nenhuma inferência de que dois registros são o mesmo posto;
- saída determinística: mesma entrada + mesma versão = mesmos campos;
- teste explícito para acentos, pontuação, sufixos societários e valores ausentes;
- CNPJ só atravessa como identificador quando os dígitos verificadores são válidos;
- sem geocodificação: coordenada entra quando GEO-01 existir.

### Critérios de aceite

- [x] regras de normalização documentadas e versionadas;
- [x] funções puras e determinísticas;
- [x] original nunca é sobrescrito;
- [x] CNPJ inválido não é transformado em identificador confiável;
- [x] testes de casos difíceis verdes no CI;
- [x] nenhum efeito sobre API pública ou identidade vigente.

**Evidência de fechamento (2026-08-08):** módulo `pic.normalizacao_identidade`, versão `f1-02-v1`, e suíte `test_normalizacao_identidade.py`; CI completo verde.

## F1-03 — blocking mensurável

**Objetivo:** reduzir o universo de comparações antes de qualquer score, registrando por que cada par foi candidato e quanto trabalho foi eliminado. **Compartilhar bloco significa somente “vale comparar”, nunca “é o mesmo posto”.**

### Blocos disponíveis sem geocodificação

1. **CNPJ raiz** — oito primeiros dígitos de um CNPJ validado. É bloco, não evidência de ponto físico: matriz e filiais podem compartilhar raiz.
2. **CEP + tipo de logradouro** — só quando CEP válido e o tipo do primeiro token do endereço está reconhecido.
3. **Nome normalizado por tokens** — bloco textual conservador para recuperar casos sem identificador forte; não será chamado de “fonético” até existir algoritmo/validação próprios.

O bloco geográfico da especificação (`geohash + vizinhas`) fica **indisponível e reportado como tal** até GEO-01 produzir coordenadas. A ausência não pode ser mascarada por um substituto inventado.

### Saída e métricas obrigatórias

- pares canônicos identificados por `(fonte, chave_fonte)`;
- conjunto de motivos/blocos compartilhados por par;
- total de registros;
- total teórico de comparações entre fontes;
- pares produzidos pelo blocking;
- taxa de redução de comparações;
- número de registros sem qualquer chave de bloco;
- contagem de pares por família de bloco;
- execução determinística e independente da ordem da entrada.

### Critérios de aceite

- [ ] nenhum par é classificado ou ligado nesta etapa;
- [ ] A↔B aparece uma vez mesmo compartilhando vários blocos;
- [ ] motivos do par são preservados e ordenados;
- [ ] mesma entrada em ordem diferente produz a mesma saída/métricas;
- [ ] CNPJ inválido nunca cria bloco CNPJ;
- [ ] registros sem bloco são contabilizados, nunca descartados em silêncio;
- [ ] geografia aparece como cobertura ausente, não como dado estimado;
- [ ] suíte e lint verdes no CI.

## Próximos cards

F1-04 vetor de similaridade e baseline Fellegi–Sunter → F1-05 calibração dos dois limiares → F1-06 cluster versionado + operação de separação → F1-07 golden record com proveniência campo a campo → F1-08 amostra rotulada e medição formal de precisão/recall.
