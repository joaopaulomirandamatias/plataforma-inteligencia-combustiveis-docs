# Backlog — Mapa de postos (épico)

Ideia do usuário (2026-08-08): a ficha pública deve ter um mapa mostrando os postos.

## Estado executivo — 2026-08-08

| Card | Estado | Resultado atual |
|---|---|---|
| GEO-01 geocodificação | ✅ **engenharia em produção** | migração 017, cache imutável, fato bitemporal, `pic-geo`, provedor plugável e nenhuma chamada externa sem configuração explícita |
| GEO-02 armazenamento/índices espaciais | 🟡 **PR #18 em validação** | `cube` + `earthdistance`, B-tree de viewport, GiST para raio e view factual |
| GEO-03 API espacial | ⏳ pendente | endpoint `bbox`/raio, limites de payload e semântica temporal |
| WEB-02 mapa | ⏳ pendente | mapa client-side, clusterização e carregamento por viewport |

**Importante:** GEO-01 em produção significa que a infraestrutura para geocodificar existe. O conjunto real de coordenadas continua vazio/não produzido enquanto não for escolhido explicitamente um provedor de lote e um protocolo de execução. Nenhuma variável `PIC_GEO_*` está configurada nos serviços produtivos no fechamento do GEO-01.

## Por que é épico, não card

O mapa precisa de **coordenadas (lat/long)**; o cadastro ANP (F01) traz **endereço em texto livre**, sem geocodificação. A ordem obrigatória:

1. **GEO-01 — geocodificação auditável. ✅** Endereço F01 vira consulta determinística; respostas são cacheadas por provedor + versão + hash e vinculadas ao fato cadastral sem declarar a coordenada como verdade canônica. Resultado `nao_encontrado` também é preservado. O servidor público do Nominatim não é configurado como executor de lote; produção não possui endpoint GEO ativo até decisão explícita.
2. **GEO-02 — armazenamento geoespacial. 🟡** PostGIS não é necessário para pinos do mapa v1. A coordenada continua na resposta imutável do GEO-01; o fato mantém a associação bitemporal. `cube`/`earthdistance`, índices e uma view factual preparam bounding-box e raio sem duplicar lat/lon nem escolher ponto oficial.
3. **GEO-03 — API.** Endpoint que devolve postos com coordenadas por bounding-box/raio, nunca a lista inteira. Cursor de lista tradicional não substitui consulta espacial por viewport.
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
- produção: `main/deploy` `73ff7f4ac1918f324db14421536377f08bd81140`, migração 017 aplicada pelo startup e `/saude` HTTP 200.

### Limite de GEO-01

GEO-01 **não geocodificou o cadastro real**. Isso é deliberado. Escolher/contratar/operar o provedor de lote é uma decisão separada porque envolve política de uso, custo, taxa de chamadas, cobertura e validação amostral.

## GEO-02 — desenho em validação

A PR #18 propõe:

- `cube` e `earthdistance` no mesmo schema endurecido;
- revogação explícita de `CREATE` no schema das extensões para papéis não confiáveis;
- índice B-tree parcial `(latitude, longitude)` para viewport;
- índice GiST parcial sobre `ll_to_earth(latitude, longitude)` para pré-filtro de raio;
- `earth_box(...)` para reduzir candidatos e `earth_distance(...)` para o corte circular exato;
- `fatos.vw_geocodificacao_ponto`, que expõe somente evidências com coordenadas e preserva provedor, versão, hashes e bitemporalidade;
- nenhuma duplicação de latitude/longitude no fato;
- nenhuma seleção de “coordenada oficial”.

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

`GEO-01 ✅` → `GEO-02 🟡 PR #18` → `GEO-03` → `WEB-02`

Em paralelo, após a escolha de provedor, deve existir um protocolo separado para **produção e validação do dataset geocodificado real**, incluindo cobertura, amostra manual de qualidade, versionamento e reprocessamento.
