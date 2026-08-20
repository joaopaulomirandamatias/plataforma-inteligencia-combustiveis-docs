# Backlog — Mapa de postos (épico)

Ideia do usuário (2026-08-08): a ficha pública deve ter um mapa mostrando os postos.

## Estado executivo — 2026-08-08

| Card | Estado | Resultado atual |
|---|---|---|
| GEO-01 geocodificação | ✅ **engenharia em produção** | migração 017, cache imutável, fato bitemporal, `pic-geo`, provedor plugável e nenhuma chamada externa sem configuração explícita |
| GEO-02 armazenamento/índices espaciais | ✅ **produção** | migração 018, `cube` + `earthdistance`, B-tree de viewport, GiST para raio e view factual; 387 testes + OpenAPI 8/8 |
| GEO-03 API espacial | ✅ **produção** | `/v1/postos/mapa`: bbox ou raio, `as_of`, limite duro, truncamento e proveniência; 402 testes + OpenAPI 9/9 |
| GEO-04 posição oficial ANP | ✅ **engenharia em produção** | API oficial paginada, snapshot imutável, vínculo por código SIMP e defesa por CNPJ; a carga diária entra pelo GEO-05 |
| WEB-02 mapa | ✅ **produção** | mapa client-side por viewport, proxy same-origin com allowlist, estado vazio, clusters e atribuição de tiles |
| GEO-05 operação diária | 🟡 **em promoção** | GEO-ANP após F01, cadência por livro-razão e comando isolado `pic-geo-anp` |
| GEO-06 um ponto por posto | 🟡 **em revisão** | `/v1/postos/mapa` colapsa evidências vivas por `posto_id` com regra determinística; `limite`/`truncado` passam a contar postos |

**Importante:** GEO-01 continua sendo o fallback de geocodificação por endereço e não depende de um provedor configurado em produção. A fonte primária agora é GEO-ANP, obtida diretamente da API oficial de Revendedores. O mapa permanece vazio até a primeira execução operacional de GEO-ANP concluir.

## Sequência arquitetural

1. **GEO-01 — geocodificação auditável. ✅** Endereço F01 vira consulta determinística; respostas são cacheadas por provedor + versão + hash e vinculadas ao fato cadastral sem declarar a coordenada como verdade canônica. Resultado `nao_encontrado` também é preservado. O servidor público do Nominatim não é configurado como executor de lote.
2. **GEO-02 — armazenamento geoespacial. ✅** `cube`/`earthdistance`, índices e view factual preparam bbox e raio sem duplicar lat/lon nem escolher ponto oficial.
3. **GEO-03 — API. ✅** Endpoint devolve evidências geográficas por bounding-box/raio, nunca a lista inteira. O contrato canônico foi definido antes da implementação.
4. **GEO-04 — posição publicada pela ANP. ✅** API oficial como fonte primária; GEO-01 permanece fallback explícito.
5. **WEB-02 — frontend. ✅** Mapa client-side consulta o endpoint espacial por viewport sem transformar evidência em verdade canônica.
6. **GEO-05 — operação diária. 🟡** A agenda executa GEO-ANP depois do F01 e mantém o executor isolado para reprocessamentos controlados.

## GEO-01 — entregue

- `ingestao.cache_geocodificacao`: cache imutável de resposta do provedor;
- `fatos.fato_geocodificacao`: vínculo bitemporal entre o F01 e a resposta usada;
- SHA-256 da consulta e do resultado normalizado;
- status explícito `encontrado` / `nao_encontrado`;
- latitude/longitude somente quando encontradas e dentro do domínio válido;
- confiança somente quando o provedor oferece uma medida documentada; ranking/importância não vira “confiança” por renomeação;
- trigger SQL contra posto ou validade divergentes do F01;
- privilégios append-only, inclusive sequences `IDENTITY`;
- provedor Nominatim-compatível sem endpoint padrão;
- cache antes da rede;
- CLI `pic-geo`;
- testes sem rede real;
- validação oficial: **382 passed, 1 skipped, 2 deselected + OpenAPI 8/8**;
- produção GEO-01: `73ff7f4ac1918f324db14421536377f08bd81140`, migração 017 aplicada e `/saude` HTTP 200.

### Limite de GEO-01

GEO-01 **não geocodificou o cadastro real**. Isso é deliberado. Escolher/contratar/operar o provedor de lote é uma decisão separada porque envolve política de uso, custo, taxa de chamadas, cobertura e validação amostral.

## GEO-02 — entregue em produção

- `cube` e `earthdistance` no mesmo schema endurecido;
- revogação explícita de `CREATE` no schema das extensões para papéis não confiáveis;
- índice B-tree parcial `(latitude, longitude)` para viewport;
- índice GiST parcial sobre `ll_to_earth(latitude, longitude)` para raio;
- `earth_box(...)` como pré-filtro e `earth_distance(...)` como corte circular exato;
- `fatos.vw_geocodificacao_ponto` preservando provedor, versão, hashes e bitemporalidade;
- nenhuma duplicação de latitude/longitude no fato;
- nenhuma seleção de “coordenada oficial”.

Gate final da PR #18:

- head validado `496c926152c39c0d883ae1d157fa7e0f59392411`;
- **387 passed, 1 skipped, 2 deselected**;
- testes GEO-02 **5/5**;
- OpenAPI **8/8**;
- lint verde.

Produção GEO-02:

- main/deploy `c9fb84d684933224895ae5117efb6bd1b017c125`;
- migração `018_geoespacial.sql` aplicada pelo startup normal;
- `pic-api` e `pic-worker` no mesmo SHA e `SUCCESS`;
- `/saude` HTTP 200.

## GEO-03 — entregue em produção

Contrato canônico: `GET /v1/postos/mapa` (no OpenAPI o caminho é `/postos/mapa`, pois `/v1` vive em `servers`).

### Regras

- exatamente um modo:
  - bbox completo: `min_lat`, `min_lon`, `max_lat`, `max_lon`; ou
  - raio completo: `lat`, `lon`, `raio_m`;
- mistura, ausência ou grupo incompleto → 422 Problem Details;
- `raio_m` máximo de 100 km;
- `limit` máximo 1.000, padrão 500;
- o banco busca `limit + 1` e devolve `truncado`, evitando `count(*)`;
- consulta temporal `as_of` filtra simultaneamente validade/transação da evidência GEO e do F01 de origem;
- filtros opcionais por `provedor` e `versao_provedor`;
- bbox usa latitude/longitude indexáveis;
- raio usa `earth_box` + `earth_distance`;
- cada item é uma **evidência GEO-ANP ou GEO-01**, com `evidencia_id`, provedor, versão, hash, fonte e localizador;
- `distancia_m` existe apenas no modo raio;
- não existe seleção implícita de coordenada canônica;
- bbox v1 não cruza o antimeridiano (`min_lon < max_lon`), suficiente para o recorte brasileiro.

### Gate oficial

PR #19 / head validado `a423ed0196a1c6996769f5a49a3050ddb5833141`:

- **402 passed, 1 skipped, 2 deselected**;
- `tests/test_api_geo.py`: **14/14**;
- contrato OpenAPI executável: **9/9**;
- `MapaPostos` e cada `PontoMapa` validados por JSON Schema;
- lint verde.

Produção GEO-03:

- main/deploy `700ea1e8655510410bdf2b0d17fd7def5f2a0941`;
- CI de `main` verde, inclusive promoção automática;
- deployments Railway `pic-api` e `pic-worker` no mesmo SHA e `SUCCESS`;
- startup da API confirmou **18 migrações já aplicadas**;
- `/saude` retornou HTTP 200 pelo healthcheck Railway;
- GEO-03 não executa geocodificação nem gera custo externo.

### Observação de validação HTTP externa

O ambiente de ferramentas usado durante a implementação não conseguiu resolver diretamente o domínio público Railway para uma sonda manual adicional. Isso foi tratado como limitação da ferramenta, não como evidência de sucesso ou falha do endpoint. A evidência aceita para promoção foi o CI oficial + rollout Railway + healthcheck 200. Não foi registrado um resultado externo inventado.

## WEB-02 — entregue em produção

Diretrizes implementadas:

1. componente de mapa deve ser **client-side**;
2. pontos são buscados diretamente em `/v1/postos/mapa` por viewport/raio;
3. não serializar pontos no payload RSC;
4. respeitar `truncado=true` pedindo zoom/viewport menor;
5. exibir estado vazio de cobertura geográfica de forma explícita;
6. popup deve separar fato, fonte e proveniência;
7. mapa não pode transformar coordenada geocodificada em “posto ativo” ou “localização oficial”;
8. nenhuma chamada de geocodificação é feita pelo navegador;
9. dependência/provedor de mapa e tiles deve ser escolhido com política de uso e atribuição verificadas, não por conveniência.

## GEO-06 — um ponto por posto no mapa

### O defeito, medido em produção em 2026-08-20

`GET /v1/postos/mapa?min_lat=-24&max_lat=-22&min_lon=-47&max_lon=-45` com `limit=500` devolvia **500 itens que eram 167 `posto_id` distintos** — 166 repetidos 3× e um repetido 2× — com `truncado=true`. Todas as réplicas traziam a mesma latitude/longitude e diferiam apenas na `versao_provedor`, uma por dia de coleta (`sha256:4b1539…`, `sha256:b0fc8b…`, `sha256:c60206…`, coletadas em 09, 10 e 11/08). O consumidor enxergava **um terço** dos postos que caberiam no viewport, e qualquer contagem ou cluster saía inflada 3×.

### Causa raiz

Duas coisas somadas, ambas no caminho de escrita — e **não** é fan-out de JOIN (o `JOIN` do endpoint é sobre `fato_cadastro_revendedor.fato_id`, chave primária, 1:1 comprovado por contagem):

1. `pic.fontes.anp_geo_revendedores` monta `versao_provedor` como `v1/combustivel@sha256:<snapshot>`. Como o SHA do snapshot muda a cada publicação da ANP, a chave `UNIQUE (provedor, versao_provedor, consulta_sha256)` do cache **não** reconhece a coleta do dia seguinte como repetição: nasce uma linha de cache nova, um `cache_id` novo e, portanto, o `ON CONFLICT (fato_cadastro_id, cache_id) DO NOTHING` nunca dispara.
2. `fatos.fato_geocodificacao` (migração 017) **não tem o `EXCLUDE USING gist (posto_id WITH =, validade WITH &&, transacao WITH &&)`** que o [modelo bitemporal](dados/modelo-bitemporal.md) exige de tabela de estado. Sem ele, a versão anterior não precisa ser fechada pela operação 2 (correção bitemporal) — e não é. As três linhas ficam vivas ao mesmo tempo, com validade idêntica e transação aberta.

O acúmulo é, portanto, **defeito de escrita**, não desenho: posição geográfica de um posto segundo uma fonte é **estado**, não evento. A correção do caminho de escrita (fechar a versão anterior e acrescentar o `EXCLUDE`) tem card próprio, porque exige migração e saneamento do que já está gravado.

### A decisão do endpoint

Ainda que a escrita fosse corrigida, o endpoint **precisaria** escolher: GEO-ANP e GEO-01 são fontes concorrentes legítimas e podem estar vivas para o mesmo posto ao mesmo tempo. Colapsar é a única defesa disponível a uma API somente-leitura, e passa a ser regra publicada em vez de acidente.

**Regra de colapso**, aplicada por `posto_id`, dentro do recorte pedido e depois do corte temporal `as_of`:

1. **autoridade da fonte** — `GEO-ANP` antes de `GEO-01`, por `CASE` explícito. A precedência é metodológica (posição publicada pela ANP vence coordenada inferida do endereço) e o `CASE` também evita a armadilha alfabética: `'GEO-01' < 'GEO-ANP'`, então ordenar `fonte` como texto escolheria justamente o fallback;
2. **recência** — `coletado_em` mais recente dentro da mesma autoridade;
3. **desempate endereçado por conteúdo** — `resultado_sha256`, depois `provedor`, `versao_provedor` e `consulta_sha256`, todos `COLLATE "C"`. Empatar no hash significa que as evidências carregam a mesma coordenada e os mesmos metadados; as três chaves seguintes completam uma ordem **total** sobre as linhas vivas por causa das restrições já existentes (`EXCLUDE` da 004 garante um F01 vivo por posto no `as_of`; `UNIQUE (fato_cadastro_id, cache_id)`; `UNIQUE (provedor, versao_provedor, consulta_sha256)`).

Nada de `random()`, de ordem física ou de `evidencia_id`: identificador de sequência muda com a ordem de carga e não sobrevive a uma reconstrução da base.

**A distância não desempata.** Se desempatasse, o ponto de um posto mudaria conforme o centro da busca — o mesmo posto apareceria em coordenadas diferentes para dois usuários. `distancia_m` só ordena a saída do modo raio.

### Consequências para o contrato

- `limite` e `truncado` passam a contar **postos**. O limite duro limita a unidade que o consumidor desenha; antes, o payload cheio podia ser um punhado de postos repetidos.
- A forma da resposta (`MapaPostos`, `PontoMapa`) **não muda** — nenhum campo entra ou sai. Muda a semântica: `posto_id` não se repete na lista.
- A proveniência continua inteira no item escolhido (`evidencia_id`, `fonte`, `provedor`, `versao_provedor`, `resultado_chave`, `resultado_sha256`, `coletado_em`, `localizador`). Colapsar não é anonimizar.
- A escolha é feita **entre as evidências dentro do recorte**: uma evidência fora do viewport não representa o posto no viewport.

### Ressalvas

- **Postos legitimamente distintos no mesmo endereço** (bandeira dupla, posto e conveniência com autorizações separadas) continuam sendo pontos separados: o colapso é por `posto_id`, nunca por coordenada. Dois `posto_id` diferentes com a mesma latitude/longitude produzem dois itens sobrepostos no mapa — o que é verdade, não defeito, e a distinção fica com a identidade (F1), não com a geografia.
- Enquanto o acúmulo de escrita existir, `evidencia_id` do ponto exibido **muda a cada coleta diária**, mesmo com a coordenada idêntica. Quem quiser estabilidade de identificador deve usar `posto_id`.
- O colapso não inventa cobertura: posto sem evidência geográfica viva continua ausente do mapa, e isso é "sem localização", não "não existe".

## Cuidados herdados do projeto

- **Qualidade da geocodificação é dado, não verdade:** endereço mal geocodificado põe o pino no lugar errado; a evidência precisa preservar origem e método.
- **Política de linguagem no popup:** fato com fonte, nunca juízo.
- **Cobertura declarada:** postos não geocodificados não somem em silêncio — contam como “sem localização”, não como “não existe”.
- **Custo:** a produção do dataset real deve ter orçamento e protocolo próprios.
- **Sem PostGIS por padrão:** pinos, bbox e raio cabem no desenho atual; PostGIS só entra se surgirem geometrias complexas.

## Sequência atual

`GEO-01 ✅` → `GEO-02 ✅` → `GEO-03 ✅` → `GEO-04 ✅` → `WEB-02 ✅` → `GEO-05 🟡` → `GEO-06 🟡`

Depois da primeira carga GEO-ANP, o próximo gate é medir cobertura, registros sem vínculo, divergências de CNPJ e necessidade real do fallback GEO-01 antes de ativar qualquer provedor externo.
