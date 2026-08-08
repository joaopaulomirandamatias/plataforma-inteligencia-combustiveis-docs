# ADR-010 — Estratos de amostragem não pertencem ao pacote cego

**Status:** aceito  
**Data:** 2026-08-08

## Contexto

A F1-08 estratifica a amostra por dimensões como fonte×fonte, dificuldade, faixa de score, motivo de blocking e presença de identificador forte. Esses metadados são necessários para selecionar a amostra e calcular métricas por estrato.

O codebook F1-08a v1 exportava `estratos` junto do item entregue ao revisor. Mesmo sem mostrar o score numérico, rótulos como `score_alto`, `dificil`, `sem_identificador_forte` ou o próprio motivo de blocking podem transmitir uma expectativa do modelo e influenciar a decisão humana.

Isso conflita com a regra metodológica de revisão independente do classificador.

## Decisão

A partir do codebook `f1-08a-v2`, o pacote cego entregue ao revisor contém somente:

- `item_id` opaco;
- evidências factuais necessárias à decisão, com fonte e localizador.

Permanecem fora do pacote cego:

- referência interna;
- chaves técnicas das fontes;
- score/peso/probabilidade;
- threshold e destino automático;
- versão/expectativa do classificador quando ela puder influenciar o julgamento;
- **todos os estratos de amostragem**.

Os estratos continuam no manifesto interno e nos artefatos de reconciliação para permitir desenho amostral, ponderação e relatório por estrato.

## Consequências

- a versão v1 já produzida não é reescrita; experimentos precisam registrar qual codebook utilizaram;
- novos experimentos devem preferir `f1-08a-v2`;
- UI/CLI de revisão não pode reconstruir ou exibir estratos a partir do manifesto interno;
- métricas por estrato são calculadas depois da reconciliação dos rótulos, não durante a tela de decisão do revisor.

## Invariante

**Informação necessária para selecionar/avaliar a amostra não é automaticamente informação adequada para mostrar ao revisor.**
