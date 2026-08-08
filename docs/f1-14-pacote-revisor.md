# F1-14 — pacote cego individual e proveniência do julgamento humano

## Problema

F1-12 congela a população candidata e F1-13 congela quem são os dois revisores independentes. Ainda faltava uma ligação explícita entre o rótulo humano e **o artefato de evidências que aquele revisor efetivamente recebeu**.

Sem esse vínculo, a base consegue responder “quem rotulou este item?”, mas não consegue demonstrar de forma determinística “qual versão do pacote cego estava associada àquele julgamento?”.

F1-14 fecha essa lacuna sem criar rótulos, parâmetros estatísticos ou decisões automáticas.

## Fluxo

```text
pacote cego F1-12
        ↓
atribuição F1-13 já congelada
        ↓
filtrar somente item_id atribuídos ao revisor
        ↓
validar cegamento estrutural
        ↓
serializar JSON canônico
        ↓
calcular SHA-256 do pacote individual
        ↓
registrar hash + mapa exato de item_id antes do primeiro rótulo
        ↓
entregar artefato ao revisor
        ↓
lote de rótulos cita o mesmo SHA-256
        ↓
PostgreSQL verifica experimento + revisor + pacote
```

## Artefato do revisor

Schema atual: `f1-14-v1`.

O pacote contém somente:

- `schema_versao`;
- `experimento_id`;
- `revisor_id` opaco;
- `codebook_versao`;
- `manifesto_sha256`;
- labels permitidos;
- `item_id` opacos atribuídos ao revisor;
- evidências factuais já permitidas pelo pacote cego F1-08a v2.

O pacote não pode conter chaves internas como:

- `referencia_interna`;
- `estrato_primario` ou `estratos`;
- score/pontuação;
- motivos ou famílias de blocking;
- versão de modelo/calibração;
- thresholds/limiares;
- `populacao_sha256`.

## Hash canônico

A serialização é determinística (`sort_keys` e separadores canônicos). O SHA-256 é calculado sobre os bytes do pacote individual.

O banco registra:

- experimento;
- revisor;
- `pacote_sha256`;
- manifesto;
- codebook;
- quantidade de itens;
- mapa exato dos `item_id` que formam o pacote.

O hash sozinho não é tratado como assinatura digital. Sua função é identificar de maneira reproduzível o artefato e permitir comparação com o registro imutável do experimento.

## Defesa em profundidade no PostgreSQL

A migração `015_pacote_revisor_entity_resolution.sql` adiciona:

### `identidade.pacote_revisor_er`

Cabeçalho append-only do pacote individual por `(experimento_id, revisor_id)`.

### `identidade.pacote_revisor_item_er`

Mapa append-only dos IDs cegos que efetivamente compõem aquele pacote.

O banco exige:

1. experimento previamente registrado;
2. manifesto e codebook iguais aos do experimento;
3. revisor previamente atribuído pela F1-13;
4. pacote registrado antes do primeiro rótulo daquele revisor;
5. quantidade igual à atribuição;
6. no `COMMIT`, mapa completo e exatamente correspondente ao conjunto atribuído;
7. rótulo F1-14 citando exatamente o SHA registrado para aquele revisor.

Assim, um `INSERT` direto com somente um SHA arbitrário e uma contagem correta não satisfaz o contrato.

## Compatibilidade

Rótulos históricos não recebem hash retroativamente.

Quando não existe registro F1-14 para o revisor, o contrato F1-08c anterior continua permitindo `pacote_revisor_sha256 = NULL`.

Quando um pacote F1-14 foi registrado, o hash passa a ser obrigatório e precisa coincidir exatamente.

Essa distinção evita inventar proveniência para dados anteriores ao novo protocolo.

## Operação

Enquanto as PRs permanecem empilhadas, a operação está isolada no módulo:

```text
python -m pic.operacao_pacote_revisor_entity_resolution exportar ...
python -m pic.operacao_pacote_revisor_entity_resolution validar ...
python -m pic.operacao_pacote_revisor_entity_resolution importar-rotulos ...
```

`validar` recalcula a integridade interna do arquivo. Para provar que o arquivo corresponde ao pacote oficialmente associado ao experimento, o SHA também precisa ser comparado ao registro persistido.

## Critérios de aceite

- [x] pacote individual é determinístico para mesma entrada/atribuição;
- [x] pacote contém somente itens atribuídos ao revisor;
- [x] pacote base precisa coincidir exatamente com os itens registrados do experimento;
- [x] pacote continua estruturalmente cego;
- [x] alteração do conteúdo sem atualizar o hash é detectada;
- [x] registro do pacote ocorre antes do primeiro rótulo;
- [x] mapa de itens é obrigatório e corresponde exatamente à atribuição;
- [x] SQL direto com hash/contagem sem mapa completo falha no `COMMIT`;
- [x] rótulo no modo F1-14 precisa citar o SHA registrado;
- [x] hash inexistente ou divergente falha alto;
- [x] tabelas novas são append-only para o papel da aplicação;
- [x] experimento legado sem F1-14 continua compatível sem backfill inventado;
- [x] lint, PostgreSQL 16, suíte completa e contrato OpenAPI ficam verdes no Railway CI Sandbox;
- [ ] merge/promoção permanecem condicionados ao GitHub Actions oficial.

**Evidência técnica (2026-08-08):** PR #10, head de produto `08e098d6a23012edc43f7ef8f22f54ecbda77da8`; branch de CI reconstruída diretamente desse head com apenas runner/marker; deployment Railway CI Sandbox `966a7853-0476-46d5-96ad-90198ba8236d`; `ruff` aprovado; **359 passed, 1 skipped, 2 deselected**; testes F1-14 7/7; invariantes da migração 015 5/5; OpenAPI 8/8; `CI_RESULT=PASS`.

## O que F1-14 não prova

F1-14 não prova:

- que a pessoa realmente examinou as evidências com atenção;
- que o rótulo está correto;
- concordância/Kappa;
- precisão, recall ou especificidade do Entity Resolution;
- parâmetros `m/u`;
- thresholds de produção;
- autenticidade criptográfica de identidade humana.

Essas propriedades permanecem dependentes do protocolo humano, adjudicação e avaliação empírica posterior.
