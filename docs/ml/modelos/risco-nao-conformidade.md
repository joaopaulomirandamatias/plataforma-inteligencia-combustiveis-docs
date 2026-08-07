# Risco de não conformidade — especificação inicial

*(pré-implementação: fixa alvo, gabarito e limites antes da primeira linha de treino)*

## Objetivo e unidade de decisão

Prever, por **posto** (`posto_id`), a probabilidade de reprovação em inspeção numa janela futura — para ordenar o [ranking de fiscalização](../../api/openapi.yaml). A unidade de decisão é a visita de fiscalização; a saída operacional é o top-k com razões.

## Gabarito

Reprovações PMQC (rótulo F2) na v1; erro metrológico IPEM (rótulo F1) quando o convênio entregar. **Viés estrutural declarado:** o gabarito só existe onde houve inspeção, e a inspeção é dirigida — ver a seção correspondente do [protocolo de backtesting](../backtesting.md), incluindo o que isso proíbe afirmar.

## Features (categorias — o feature store detalha)

| Categoria | Exemplos | Cuidado específico |
|---|---|---|
| Histórico próprio | taxa/recência PMQC, ensaio reprovado, autuações | Data do **fato**, não da decisão (armadilha F04) |
| Grupo societário | `taxa_nao_conformidade_do_grupo`, `distancia_no_grafo_ate_posto_autuado`, `rotatividade_societaria_12m` | **Exclui o próprio posto**; respeita corte; disponível só quando a dimensão PF do RIPD liberar — versão só-T1/T2 até lá |
| Preço | desvio persistente abaixo da distribuição regional condicionada | Condicionamento completo (região × produto × semana × bandeira) |
| Cadastro | idade do CNPJ, mudanças recentes, situação | — |
| Contexto | densidade de risco na vizinhança, porte do município | Não pode virar proxy puro de região pobre — ver fairness |
| Reclamações | volume/teor (NLP) | Contexto, jamais dominante — relato não é fato |

## Exclusões anti-vazamento

Resultado de inspeção da própria janela-alvo; qualquer feature com `validade` posterior ao corte; features derivadas de snapshot mais novo que T.

## Saída

`AvaliacaoDeRisco {score, intervalo, cobertura, razoes_topk}` — sem cobertura mínima, **não emite** (evento [`LimiarDeRiscoCruzado`](../../dados/eventos/limiar-de-risco-cruzado.md)).

## Fairness e cobertura

Risco concreto: postos de regiões com mais fiscalização histórica têm mais rótulo — o modelo pode aprender "onde o fiscal já vai", não "onde há problema". Controles: reportar precision@k **por estrato** (capital/interior, porte); monitorar participação de cada estrato no top-k vs. na base; a fração aleatória de inspeções do piloto é o corretor de longo prazo.

## Limites conhecidos (herdam a política de linguagem)

O score ordena prioridade de verificação entre postos fiscalizáveis. Não é probabilidade de fraude, não atribui intenção, não sustenta sanção — e o [Guardião](../../agentes/politica-de-linguagem.md) bloqueia qualquer texto que diga o contrário.
