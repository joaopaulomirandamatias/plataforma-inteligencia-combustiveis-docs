# Protocolo de Backtesting

*(especificação inicial — congela o protocolo antes do primeiro modelo, que é o único momento em que um protocolo pode ser congelado com credibilidade)*

## A pergunta que o backtest responde

> Com o mesmo número de fiscalizações, o ranking do modelo encontra mais irregularidades do que o critério vigente do órgão?

Não é acurácia, não é AUC. É **precision@k contra baseline**, porque é a única métrica que se traduz em decisão de alocação — e é o critério de saída da fase F2 do projeto.

## Desenho

```
para cada safra T em {T1, T2, ..., Tn}:          # cortes trimestrais
    treinar com dados de transacao @> T           # o que a base SABIA em T
    prever o conjunto elegível em T
    comparar top-k do modelo × baseline em T
    verdade = resultados reais de inspeção em (T, T + janela]
```

Regras não negociáveis:

1. **Corte pela dimensão de transação**, não de validade — armadilha nº 3 do [modelo bitemporal](../dados/modelo-bitemporal.md). Correções feitas depois de T não existem para o modelo em T.
2. **Protocolo congelado antes de rodar:** k, safras, janela, baseline e critério de vitória ficam registrados neste arquivo (versionado) *antes* da primeira execução. Mudança posterior = novo protocolo declarado, nunca edição silenciosa.
3. **k operacional, não estatístico:** k = capacidade real de fiscalização do órgão parceiro no período (a obter na fase de convênio). Reportar também k/2 e 2k para sensibilidade.
4. **Sem reuso do teste:** cada safra é avaliada uma vez por versão de protocolo. Iteração de modelagem usa validação interna às safras de treino — o conjunto de avaliação não vira conjunto de desenvolvimento.
5. **Controle negativo:** permutação dos rótulos deve levar precision@k ao nível da base. Se não levar, há vazamento — procurar antes de comemorar.

## Baseline

O critério vigente do órgão, reconstruído do histórico: quais postos **foram de fato inspecionados** em cada período. Vantagem: é o comparador honesto (inclui o conhecimento tácito do fiscal). Limite declarado: o histórico de inspeção é a política antiga — o ganho medido é *incremental sobre ela*, não absoluto.

## O viés que este protocolo não elimina — declarado

O gabarito (reprovações) só existe **onde houve inspeção**, e a inspeção não é aleatória. Precision@k medida sobre inspecionados é estimável; recall verdadeiro não é. Consequências:

- Nenhuma afirmação de "detecta X% das fraudes" — não é mensurável com este dado.
- A afirmação permitida é: *"entre os fiscalizáveis, o ranking concentra mais achados por visita que o critério atual"*.
- Mitigação de longo prazo: sorteio de uma fração pequena de inspeções aleatórias no piloto (a negociar com o órgão) — único caminho para estimar taxa-base.

## Relato

Por safra: precision@k (modelo × baseline), intervalo por bootstrap, cobertura média do top-k, lift. Agregado: mediana entre safras (não média — uma safra atípica não pode carregar o resultado). Tudo reproduzível: versão de modelo, protocolo, snapshot e seed registrados no MLflow.
