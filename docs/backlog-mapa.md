# Backlog — Mapa de postos (épico)

Ideia do usuário (2026-08-08): a ficha pública deve ter um mapa mostrando os postos.

## Por que é épico, não card

O mapa precisa de **coordenadas (lat/long)**; o cadastro ANP (F01) traz **endereço em texto livre**, sem geocodificação. A ordem obrigatória:

1. **Geocodificação (dados/backend) — pré-requisito.** Converter os ~45.653 endereços em lat/long. Opções: Nominatim/OSM (gratuito, rate-limited, exige respeitar política de uso), serviço pago (Google/Mapbox — custo por chamada), ou base do IBGE/CEP. Cada endereço geocodificado é um FATO com fonte e data (bitemporal, como tudo) — geocodificação erra, e reprocessar precisa ser possível.
2. **Armazenamento geoespacial.** PostGIS (já previsto no plano diretor; NÃO está na imagem atual do Railway — exige troca de imagem, ver nota de infra). Coluna `geometry(Point,4326)` + índice GiST.
3. **API.** Endpoint que devolve postos com coordenadas, com bounding-box/raio (não a lista inteira — mapa carrega por viewport). Cursor não serve aqui; é consulta espacial.
4. **Frontend.** Biblioteca de mapa (Leaflet+OSM é leve e sem chave; MapLibre para vetorial). Clusterização de pinos (45k pontos não renderizam soltos). Popup do pino → ficha.

## Cuidados herdados do projeto

- **Qualidade da geocodificação é dado, não verdade:** endereço mal geocodificado põe o pino no lugar errado; a confiança da geocodificação acompanha o ponto (como a confiança de vínculo T1–T4).
- **Política de linguagem no popup:** mesmo léxico, mesma regra — fato com fonte, nunca juízo.
- **Cobertura declarada:** postos não geocodificados não somem do mapa em silêncio — contam como "sem localização", não como "não existe".
- **Custo:** geocodificar 45k endereços tem custo (tempo em Nominatim, dinheiro em serviço pago) — decisão do usuário sobre a fonte.

## Sequência proposta (quando priorizado)

GEO-01 conector de geocodificação (bitemporal, reprocessável) → GEO-02 PostGIS no Railway (troca de imagem) + coluna/índice → GEO-03 endpoint espacial (bbox) → WEB-02 mapa no frontend (Leaflet + clusterização).

Não iniciado. Priorização é do usuário; hoje o foco é WEB-01c (localizador no payload + bump Next).
