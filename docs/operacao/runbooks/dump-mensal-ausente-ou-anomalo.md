# Runbook — Dump mensal da Receita ausente ou anômalo

**Por que este runbook tem prioridade máxima:** a fonte F05 é **retrato do presente** — mês não capturado é história societária perdida em caráter irreversível (diff mensal impossível, eventos `MudancaSocietariaDetectada` daquele mês nunca existirão). Nenhuma outra fonte tem essa propriedade.

## Gatilho A — dump não publicado na janela esperada

1. Confirmar no portal da fonte (atraso de publicação é comum; o monitor alerta a partir de D+3 da data típica).
2. Verificar se a URL/estrutura de publicação mudou — se sim, seguir [fonte-mudou-de-formato](fonte-mudou-de-formato.md) **imediatamente** (o custo de esperar aqui é diferente: a janela fecha).
3. Atraso confirmado da fonte → monitorar diariamente; registrar no catálogo.
4. **D+15 sem dump:** escalar — buscar espelhos oficiais/institucionais do mesmo período. Qualquer cópia íntegra do mês serve (hash + proveniência registrados).

## Gatilho B — dump publicado, volume anômalo

O gate automático bloqueia carga com desvio > limiar (referência: 30% sobre o esperado por extrapolação dos meses anteriores).

1. **Menor que o esperado:** publicação parcial é comum (arquivos faltando no lote). Conferir contra a lista de arquivos do layout; aguardar completude antes de carregar. **Não carregar parcial** — o diff mensal interpretaria ausência como baixa em massa e dispararia `MudancaSocietariaDetectada` espúrios aos milhares.
2. **Maior que o esperado:** mudança de layout (colunas explodidas) ou republicação acumulada — inspecionar antes de qualquer carga.
3. Fonte republicou corrigido → **as duas versões ficam na zona bruta** (ADR-002); a carga usa a corrigida; o manifesto registra qual e por quê.

## Regra permanente

O arquivamento do dump é **independente** de qualquer pendência (inclusive as do [RIPD](../../conformidade/lgpd/ripd.md), que bloqueiam o *tratamento analítico* de PF, não a *preservação*). Baixar e guardar acontece sempre, primeiro, sem exceção — o resto do pipeline pode esperar; a janela não.
