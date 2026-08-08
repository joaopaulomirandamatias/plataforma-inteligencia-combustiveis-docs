# GEO-04 — posição geográfica publicada pela ANP

A tela de mapa foi entregue antes de existir um conjunto real de coordenadas. O resultado correto era um mapa-base sem pinos. A investigação da fonte oficial identificou que a própria ANP mantém a **API de Revendedores**, cujo contrato documenta latitude, longitude, latitude/longitude ANP4C, validação geográfica, estimativa de acurácia, SRID/SRC, data de obtenção e origem da informação.

## Decisão

A API oficial da ANP passa a ser a **fonte geográfica primária**. GEO-01 (geocodificação de endereço) permanece como fallback para registros sem coordenada publicada pela Agência.

Isso reduz erro de inferência, custo externo e dependência de fornecedor. Ainda assim, a plataforma preserva a coordenada como **evidência com proveniência**, e não como verdade canônica escolhida silenciosamente.

## Vínculo

1. `codigoSIMP` da API é reconciliado com a chave F01 no contexto de Identidade;
2. CNPJ funciona como defesa adicional: divergência não é ligada automaticamente;
3. o par `latitude/longitude` principal é preferido quando válido;
4. `latitude_ANP4C/longitude_ANP4C` é fallback explícito e fica marcado em `par_usado`;
5. registro sem nenhum par válido permanece `nao_encontrado`, sem inventar ponto.

## Temporalidade

- GEO-01 mantém validade exatamente igual à do F01 que originou a consulta;
- GEO-ANP pode começar na `dataObtencao` publicada pela ANP (ou no instante da coleta quando ausente), mas seu intervalo deve permanecer contido na validade do F01;
- nenhuma nova evidência sobrescreve a anterior.

## Operação

A fonte `GEO-ANP` entra na agenda diária depois de F01. A coleta é paginada, congela as páginas na zona bruta e produz um snapshot determinístico; o livro-razão torna a repetição do mesmo snapshot idempotente.

## Critério para o mapa

O mapa só mostra linhas com coordenadas efetivamente presentes. Registros sem coordenada oficial não desaparecem do processo: permanecem contabilizados e podem seguir posteriormente para o protocolo de fallback GEO-01.
