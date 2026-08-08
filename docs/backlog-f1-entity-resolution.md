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

## F1-03 — blocking mensurável ✅

**Objetivo:** reduzir o universo de comparações antes de qualquer score, registrando por que cada par foi candidato e quanto trabalho foi eliminado. **Compartilhar bloco significa somente “vale comparar”, nunca “é o mesmo posto”.**

### Blocos disponíveis sem geocodificação

1. **CNPJ raiz** — oito primeiros dígitos de um CNPJ validado. É bloco, não evidência de ponto físico: matriz e filiais podem compartilhar raiz.
2. **CEP + tipo de logradouro** — só quando CEP válido e o tipo do primeiro token do endereço está reconhecido.
3. **Nome normalizado por tokens** — bloco textual conservador para recuperar casos sem identificador forte; não é chamado de “fonético” até existir algoritmo/validação próprios.

O bloco geográfico da especificação (`geohash + vizinhas`) fica **indisponível e reportado como tal** até GEO-01 produzir coordenadas. A ausência não é mascarada por um substituto inventado.

### Critérios de aceite

- [x] nenhum par é classificado ou ligado nesta etapa;
- [x] A↔B aparece uma vez mesmo compartilhando vários blocos;
- [x] motivos do par são preservados e ordenados;
- [x] mesma entrada em ordem diferente produz a mesma saída/métricas;
- [x] CNPJ inválido nunca cria bloco CNPJ;
- [x] registros sem bloco são contabilizados, nunca descartados em silêncio;
- [x] geografia aparece como cobertura ausente, não como dado estimado;
- [x] suíte e lint verdes no CI.

**Evidência de fechamento (2026-08-08):** módulo `pic.blocking_identidade`; suíte `test_blocking_identidade.py`; CI completo com PostgreSQL 16 aprovou 200+ testes e contrato canônico.

## F1-04 — vetor de similaridade + Fellegi–Sunter parametrizado ✅

**Objetivo:** separar evidência observável do modelo estatístico. O sistema pode calcular similaridades sem fingir que já conhece parâmetros `m/u`, pesos ou limiares de produção.

### Entrega

- vetor explícito para CNPJ raiz, razão social, endereço, número, CEP e bandeira;
- Jaccard por tokens e Jaro/Jaro-Winkler implementados sem dependência externa;
- valor ausente permanece `None`/estado `ausente`, nunca vira discordância;
- distância geográfica permanece ausente até GEO-01;
- discretização explícita (`forte`, `parcial`, `discordante`, `ausente`);
- núcleo Fellegi–Sunter calcula `log2(m/u)` **somente** quando recebe parâmetros explícitos e versionados;
- parâmetro ausente para evidência observada falha alto, em vez de receber peso zero silencioso;
- nenhum limiar ou auto-match embutido no módulo.

### Critérios de aceite

- [x] similaridade simétrica e determinística;
- [x] ausência não é tratada como evidência negativa;
- [x] parâmetros `m/u` precisam estar estritamente em `(0,1)`;
- [x] versão do modelo é obrigatória;
- [x] score é decomposto em contribuições por campo/estado;
- [x] nenhum vínculo de identidade é alterado;
- [x] lint e suíte completos verdes no CI.

**Evidência de fechamento (2026-08-08):** módulo `pic.similaridade_identidade`, suíte própria de similaridade/FS e validação novamente incluída no CI verde da F1-05.

## F1-05 — calibração dos dois limiares ✅ engenharia / ⏳ calibração empírica

**Objetivo:** tornar mensurável a decisão em três vias sem fabricar rótulos: `aceitar`, `revisar`, `rejeitar`.

### Entrega de engenharia concluída

- matriz binária `VP/FP/VN/FN`, precisão, recall e especificidade;
- métricas da política em três vias, incluindo cobertura automática, erros de aceite e falsos rejeitados;
- busca de limiar de aceite sujeita a precisão/recall mínimos;
- busca conjunta de `limiar_aceite` e `limiar_rejeicao`;
- aceite automático limitado por **precisão mínima declarada**;
- rejeição automática limitada pela **taxa máxima declarada de ligações verdadeiras rejeitadas**;
- a busca retorna `None` quando a amostra não sustenta as restrições — nunca relaxa a meta;
- exige as duas classes na amostra para calibrar os dois lados;
- métricas por estrato impedem uma média global de esconder casos difíceis;
- thresholds candidatos vêm dos scores observados, não de casas decimais inventadas.

### O que continua bloqueado por evidência

Os valores de produção dos dois limiares **não estão definidos**. Para isso é obrigatória a amostra rotulada e estratificada da F1-08. Dados sintéticos servem para testar a matemática, não para alegar precisão ≥ 0,98 ou recall ≥ 0,95.

### Critérios de aceite de engenharia

- [x] nenhum rótulo é criado pelo código;
- [x] meta impossível retorna ausência de calibração;
- [x] os dois limiares são calibrados em conjunto;
- [x] custo assimétrico de falso aceite e falso rejeite é parametrizado explicitamente;
- [x] ordem da amostra não muda o resultado;
- [x] testes próprios cobrem casos válidos, impossíveis e estratificados;
- [x] CI verde antes da promoção para a branch `deploy`.

**Evidência de fechamento de engenharia (2026-08-08):** módulo `pic.calibracao_identidade`, suíte `test_calibracao_identidade.py`, pipeline `main → CI → deploy`. O fechamento **empírico** permanece dependente da F1-08.

## F1-06 — cluster versionado + separação reversível 🔄

**Objetivo:** representar agrupamentos aceitos sem editar história e permitir desfazer uma fusão errada como operação de primeira classe. **Nenhum fato será atualizado ou movido.**

### Contrato proposto

Cada alteração de cluster é um **snapshot imutável**:

1. `identidade.cluster_versao`
   - `cluster_id` estável entre versões do mesmo ponto reconciliado;
   - `versao` monotônica por cluster;
   - `registrado_em` pelo banco — quando a base passou a conhecer aquela versão;
   - `tipo ∈ {criar, revisar, separar}`;
   - `revisor_id` e `justificativa` obrigatórios;
   - referência opcional à versão da qual o snapshot deriva.
2. `identidade.cluster_membro_versao`
   - snapshot dos `posto_id` membros daquela versão;
   - intervalo de **validade no mundo** por membro, para sucessão/renumeração poder ser retroativa sem alterar fatos;
   - membro aparece uma vez por versão;
   - extremos e intervalos são validados pelo banco.

A consulta `as-of` escolhe primeiro a versão conhecida no instante de transação e depois aplica a validade de cada membro. Uma correção posterior pode carregar uma validade passada sem apagar o snapshot que antes era conhecido.

### Operações internas

- criar cluster a partir de pelo menos dois `posto_id` existentes;
- versionar um cluster copiando explicitamente o snapshot anterior e suas alterações;
- separar um subconjunto em novo `cluster_id`, criando simultaneamente nova versão do cluster original;
- recusar membro inexistente, duplicado, subconjunto vazio, separação de todos os membros e intervalos inválidos;
- impedir que o papel da aplicação faça `UPDATE`/`DELETE` nas tabelas de cluster;
- nenhuma operação altera `fatos.*` ou `posto_chave_fonte` nesta etapa.

### Critérios de aceite

- [ ] migração aditiva/idempotente;
- [ ] primeira versão exige ≥ 2 membros;
- [ ] versões anteriores permanecem consultáveis;
- [ ] split gera dois snapshots novos sem apagar o anterior;
- [ ] split nunca move nem regrava fatos;
- [ ] intervalos de validade permitem correção retroativa explícita;
- [ ] papel de escrita continua append-only;
- [ ] execução determinística para o mesmo comando lógico;
- [ ] suíte e lint verdes antes de `deploy`;
- [ ] Railway aplica a migração e `/saude` permanece 200.

## Próximos cards

F1-07 golden record com proveniência campo a campo → F1-08 amostra rotulada e medição formal de precisão/recall. O bloco geográfico de F1-03/F1-04 será ampliado quando GEO-01 disponibilizar coordenadas verificáveis.
