# Backlog — Mapa de postos (épico)

Ideia do usuário (2026-08-08): a ficha pública deve ter um mapa mostrando os postos.

## Estado executivo — 2026-08-08

| Card | Estado | Resultado atual |
|---|---|---|
| GEO-01 geocodificação | ✅ **engenharia em produção** | migração 017, cache imutável, fato bitemporal, `pic-geo`, provedor plugável e nenhuma chamada externa sem configuração explícita |
| GEO-02 armazenamento/índices espaciais | ✅ **produção** | migração 018, `cube` + `earthdistance`, B-tree de viewport, GiST para raio e view factual; 387 testes + OpenAPI 8/8 |
| GEO-03 API espacial | 🟡 **em implementação** | contrato `/postos/mapa` definido: bbox ou raio, limite duro, `as_of` e evidência com provedor/versão |
| WEB-02 mapa | ⏳ pendente | mapa client-side, clusterização e carregamento por viewport |

**Importante:** GEO-01 em produção significa que a infraestrutura para geocodificar existe. O conjunto real de coordenadas continua vazio/não produzido enquanto não for escolhido explicitamente um provedor de lote e um protocolo de execução. Nenhuma variável `PIC_GEO_*` está configurada nos serviços produtivos no fechamento do GEO-02.

## Por que é épico, não card

O mapa precisa de **coordenadas (lat/long)**; o cadastro ANP (F01) traz **endereço em texto livre**, sem geocodificação. A ordem obrigatória:

1. **GEO-01 — geocodificação auditável. ✅** Endereço F01 vira consulta determinística; respostas são cacheadas por provedor + versão + hash e vinculadas ao fato cadastral sem declarar a coordenada como verdade canônica. Resultado `nao_encontrado` também é preservado. O servidor público do Nominatim não é configurado como executor de lote; produção não possui endpoint GEO ativo até decisão explícita.
2. **GEO-02 — armazenamento geoespacial. ✅** PostGIS não é necessário para pinos do mapa v1. A coordenada continua na resposta imutável do GEO-01; o fato mantém a associação bitemporal. `cube`/`earthdistance`, índices e uma view factual preparam bounding-box e raio sem duplicar lat/lon nem escolher ponto oficial.
3. **GEO-03 — API. 🟡** Endpoint devolve evidências geográficas por bounding-box/raio, nunca a lista inteira. Cursor de lista tradicional não substitui consulta espacial por viewport. O contrato canônico foi definido antes da implementação.
4. **WEB-02 — frontend.** Biblioteca de mapa + clusterização de pinos + popup que aponta para a ficha. A busca deve ocorrer no cliente por viewport para evitar serializar dezenas de milhares de pontos no payload RSC.

## GEO-01 — o que foi entregue

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
- produção GEO-01: `main/deploy` `73ff7f4ac1918f324db14421536377f08bd81140`, migração 017 aplicada pelo startup e `/saude` HTTP 200.

### Limite de GEO-01

GEO-01 **não geocodificou o cadastro real**. Isso é deliberado. Escolher/contratar/operar o provedor de lote é uma decisão separada porque envolve política de uso, custo, taxa de chamadas, cobertura e validação amostral.

## GEO-02 — entregue em produção

GEO-02 foi validado em PostgreSQL 16 e promovido pelo fluxo oficial. Entregas:

- `cube` e `earthdistance` no mesmo schema endurecido;
- revogação explícita de `CREATE` no schema das extensões para papéis não confiáveis;
- índice B-tree parcial `(latitude, longitude)` para viewport;
- índice GiST parcial sobre `ll_to_earth(latitude, longitude)` para pré-filtro de raio;
- `earth_box(...)` para reduzir candidatos e `earth_distance(...)` para o corte circular exato;
- `fatos.vw_geocodificacao_ponto`, que expõe somente evidências com coordenadas e preserva provedor, versão, hashes e bitemporalidade;
- nenhuma duplicação de latitude/longitude no fato;
- nenhuma seleção de “coordenada oficial”.

Gate final da PR #18:

- head validado `496c926152c39c0d883ae1d157fa7e0f59392411`;
- **387 passed, 1 skipped, 2 deselected**;
- testes GEO-02 **5/5**;
- OpenAPI **8/8**;
- lint verde.

Produção:

- merge/main/deploy `c9fb84d684933224895ae5117efb6bd1b017c125`;
- migração `018_geoespacial.sql` aplicada pelo startup normal;
- `pic-api` e `pic-worker` no mesmo SHA e `SUCCESS`;
- `/saude` HTTP 200.

## GEO-03 — contrato definido

O contrato canônico agora prevê `GET /v1/postos/mapa` (em `openapi.yaml`, caminho `/postos/mapa` porque o `/v1` vive em `servers`). Regras:

- exatamente um modo por requisição:
  - bbox completo: `min_lat`, `min_lon`, `max_lat`, `max_lon`; ou
  - raio completo: `lat`, `lon`, `raio_m`;
- mistura, ausência ou grupo incompleto é 422;
- `raio_m` máximo de 100 km;
- `limit` máximo de 1.000 e padrão 500;
- consulta temporal `as_of`;
- filtros opcionais `provedor` e `versao_provedor`, sendo versão dependente de provedor;
- resposta contém `truncado`; quando verdadeiro, o cliente deve reduzir viewport/raio, não tentar paginar todo o universo;
- cada item é uma **evidência GEO-01**, com `evidencia_id`, provedor, versão, hash de resultado, fonte e localizador;
- `distancia_m` só é preenchida no modo raio;
- não existe seleção implícita de coordenada canônica.

## Cuidados herdados do projeto

- **Qualidade da geocodificação é dado, não verdade:** endereço mal geocodificado põe o pino no lugar errado; a evidência precisa preservar origem e método.
- **Política de linguagem no popup:** mesmo léxico, mesma regra — fato com fonte, nunca juízo.
- **Cobertura declarada:** postos não geocodificados não somem do mapa em silêncio — contam como “sem localização”, não como “não existe”.
- **Custo:** geocodificar dezenas de milhares de endereços pode consumir tempo ou dinheiro; a execução real deve ter orçamento e protocolo próprios.
- **Sem PostGIS por padrão:** pinos, bbox e raio cabem no desenho `double precision` + `cube`/`earthdistance`; PostGIS só entra se surgirem polígonos/interseções/geometrias complexas.

## Notas de arquitetura da borda web

1. **O payload RSC é o problema central do mapa, não um detalhe.** Numa página de servidor (RSC), pontos enviados como props entram no payload serializado. O mapa deve tender a componente de cliente buscando o endpoint espacial diretamente por viewport.
2. **A borda de dados (`lib/api.ts`) é allowlist.** Latitude/longitude só devem atravessar quando GEO-03/WEB-02 adicionarem explicitamente os campos permitidos. Isso evita ampliar o contrato público por acidente.
3. **Mapa não é fonte de verdade de atividade.** Um ponto geocodificado significa “há evidência de localização derivada deste cadastro”, não “posto ativo agora” sem o filtro temporal/cadastral correspondente.

## Sequência atual

`GEO-01 ✅` → `GEO-02 ✅` → `GEO-03 🟡` → `WEB-02`

Em paralelo, após a escolha de provedor, deve existir um protocolo separado para **produção e validação do dataset geocodificado real**, incluindo cobertura, amostra manual de qualidade, versionamento e reprocessamento.
