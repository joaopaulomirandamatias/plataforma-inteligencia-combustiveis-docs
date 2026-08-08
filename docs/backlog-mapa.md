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

## Cuidados herdados do projeto

- **Qualidade da geocodificação é dado, não verdade:** endereço mal geocodificado põe o pino no lugar errado; a evidência precisa preservar origem e método.
- **Política de linguagem no popup:** fato com fonte, nunca juízo.
- **Cobertura declarada:** postos não geocodificados não somem em silêncio — contam como “sem localização”, não como “não existe”.
- **Custo:** a produção do dataset real deve ter orçamento e protocolo próprios.
- **Sem PostGIS por padrão:** pinos, bbox e raio cabem no desenho atual; PostGIS só entra se surgirem geometrias complexas.

## Sequência atual

`GEO-01 ✅` → `GEO-02 ✅` → `GEO-03 ✅` → `GEO-04 ✅` → `WEB-02 ✅` → `GEO-05 🟡`

Depois da primeira carga GEO-ANP, o próximo gate é medir cobertura, registros sem vínculo, divergências de CNPJ e necessidade real do fallback GEO-01 antes de ativar qualquer provedor externo.
