# F1-08 — Validação formal de Entity Resolution

## Objetivo

Medir, com evidência empírica reproduzível, se o pipeline de Entity Resolution alcança as metas da v1:

- **precisão das ligações ≥ 0,98**;
- **recall ≥ 0,95**;
- perda causada pelo blocking medida separadamente;
- desempenho dos casos difíceis reportado por estrato, não escondido numa média global.

Esta etapa é a fronteira entre **engenharia implementada** e **alegação de desempenho**. Testes sintéticos validam código e matemática; não validam os números de produção.

---

## Unidade de avaliação

A unidade primária é o **par de registros de fontes distintas**. Cada par recebe um rótulo humano independente do score do modelo:

- `MESMO_PONTO` — as evidências sustentam que os dois registros representam o mesmo ponto físico de revenda no intervalo considerado;
- `PONTOS_DIFERENTES` — as evidências sustentam pontos físicos distintos;
- `INDETERMINADO` — evidência insuficiente ou contraditória para decisão segura.

`INDETERMINADO` nunca é convertido automaticamente em positivo ou negativo. Ele segue para adjudicação e sua frequência é reportada como métrica de qualidade da evidência.

A pergunta é sobre **ponto físico**, não apenas CNPJ, empresa ou razão social. Isso é necessário para respeitar a semântica de `posto_id`.

---

## Congelamento do experimento

Antes de rotular:

1. fixar os hashes/snapshots das fontes usadas;
2. fixar versão do normalizador;
3. fixar versão das regras de blocking;
4. fixar versão do vetor de similaridade;
5. registrar a versão do código/commit;
6. congelar o conjunto de pares selecionados para avaliação;
7. não alterar pares ou rótulos após observar a métrica final sem abrir nova versão do experimento.

O manifesto do experimento deve permitir reconstruir exatamente os dados que o revisor viu.

---

## Dois experimentos, não um

### A. Avaliação do blocking

Medir somente pares produzidos pelo blocking inflaria o recall, pois pares verdadeiros perdidos antes da classificação nunca apareceriam no denominador.

A auditoria do blocking precisa partir de uma amostra que **não dependa exclusivamente das próprias regras de blocking**. Estratégia v1:

1. amostrar registros-âncora por fonte, UF e disponibilidade de identificadores;
2. construir para cada âncora um conjunto de candidatos de auditoria com busca mais ampla que o blocking operacional, incluindo revisão manual dirigida;
3. identificar os pares `MESMO_PONTO` no conjunto de auditoria;
4. medir quantos desses pares o blocking operacional recuperaria.

Métrica:

```text
blocking_recall = verdadeiros_recuperados_pelo_blocking / verdadeiros_na_auditoria
```

Também registrar `reduction_ratio`: quanto o blocking reduz o produto cartesiano cross-source. Recall sem redução não mede utilidade operacional; redução sem recall mede apenas agressividade.

### B. Avaliação da classificação/decisão

Sobre pares que atravessam o blocking, medir o score e os destinos `aceitar`, `revisar`, `rejeitar` usando rótulos humanos congelados.

Relatar:

- precisão do aceite automático;
- recall do aceite automático;
- taxa de ligações verdadeiras rejeitadas automaticamente;
- cobertura automática;
- fração enviada à revisão humana;
- precisão/recall por fonte × fonte, faixa de dificuldade e família de blocking.

O desempenho end-to-end deve considerar a perda de blocking. Não publicar apenas a métrica condicional ao par ter chegado ao classificador.

---

## Estratificação obrigatória

A amostra não pode ser uniforme sobre todos os pares: negativos fáceis dominariam o universo e produziriam uma métrica enganosa.

Estratos mínimos:

- par de fontes (`F01×F02`, `F01×F03`, futuras combinações estruturadas);
- score/faixa de dificuldade, quando disponível;
- motivo de blocking (CNPJ raiz, CEP/logradouro, nome, futuro geográfico);
- identificador forte presente/ausente;
- mesma raiz CNPJ versus raízes distintas;
- mesmo endereço versus endereço divergente;
- casos catalogados: sucessão, matriz/filial, postos vizinhos, rodovia/km, renumeração de logradouro;
- região/UF suficiente para não medir apenas mercados com endereços mais padronizados.

A estimativa agregada deve usar pesos compatíveis com o desenho amostral ou declarar explicitamente que é uma métrica por estrato, não prevalência populacional.

---

## Revisão humana

### Blindagem

O revisor não vê:

- score final do modelo;
- destino automático sugerido;
- limiar de aceite/rejeição;
- rótulo de outro revisor antes de concluir o próprio.

Pode ver as **evidências factuais** necessárias: nomes, CNPJ quando permitido e pertinente, endereços, datas, coordenadas quando existirem, fontes e localizadores.

### Dupla revisão

Uma fração definida do conjunto — e obrigatoriamente todos os casos difíceis/limítrofes usados para decisão metodológica — recebe dois rótulos independentes.

Divergências passam por adjudicação documentada. Registrar:

- concordância bruta;
- Cohen's kappa quando aplicável;
- taxa de adjudicação;
- frequência de `INDETERMINADO`.

Kappa não substitui inspeção das discordâncias; ele é diagnóstico de consistência do codebook.

---

## Separação treino / calibração / teste

Nenhum par do teste final participa da estimativa de parâmetros `m/u`, treinamento de modelo ou escolha dos limiares.

Dividir por **unidade de identidade/grupo**, não apenas aleatoriamente por linha, para evitar que registros quase duplicados do mesmo posto apareçam em treino e teste.

Papéis:

- `treino`: estimar parâmetros/modelos;
- `calibracao`: escolher `limiar_aceite` e `limiar_rejeicao`;
- `teste`: uma única avaliação final congelada.

Se o teste final for usado para ajustar o modelo, ele deixa de ser teste e uma nova amostra final precisa ser criada.

---

## Incerteza estatística

Não basta reportar `0,98`; cada métrica deve acompanhar intervalo de confiança.

Para proporções, usar intervalo de Wilson ou método equivalente documentado. O tamanho da amostra é calculado **antes** da avaliação final a partir de:

- nível de confiança escolhido;
- largura máxima aceitável do intervalo;
- prevalência/precisão esperada apenas para planejamento, nunca como resultado.

A alegação “precisão ≥ 0,98” deve ser distinguida entre:

1. estimativa pontual ≥ 0,98;
2. limite inferior do intervalo de confiança ≥ 0,98.

A segunda é evidência substancialmente mais forte e exige amostra maior. O relatório deve dizer explicitamente qual critério foi satisfeito.

---

## Métricas mínimas

Para o teste congelado:

```text
precision = VP / (VP + FP)
recall    = VP / (VP + FN)
specificity = VN / (VN + FP)
```

Além disso:

- `blocking_recall`;
- `reduction_ratio`;
- cobertura automática;
- taxa de revisão humana;
- falso aceite por 1.000 aceites automáticos;
- verdadeiro vínculo rejeitado por 1.000 rejeições automáticas;
- métricas por estrato;
- intervalos de confiança;
- quantidade e percentual `INDETERMINADO`.

O relatório deve publicar a matriz de confusão em números absolutos junto das taxas.

---

## Artefatos executáveis da F1-08

### F1-08a — codebook e formato de amostra

- schema versionado do item de revisão;
- rótulos permitidos;
- evidências exibidas ao revisor;
- campos explicitamente ocultos para blindagem;
- hash do manifesto de dados.

### F1-08b — gerador de amostra

- seleção determinística dado `seed` + manifesto;
- estratificação declarada;
- IDs opacos para revisão;
- nunca inclui score/destino no pacote do revisor;
- exporta lista separada para reconciliação posterior com o experimento.

### F1-08c — importação/adjudicação

- dois revisores não sobrescrevem um ao outro;
- adjudicação é novo evento, não UPDATE do rótulo original;
- trilha de quem/quando/codebook-versão.

### F1-08d — relatório de avaliação

- matriz de confusão;
- métricas globais e por estrato;
- intervalos de confiança;
- perda do blocking;
- thresholds e versão do modelo usados;
- critérios de aceite satisfeitos ou não satisfeitos.

---

## Critérios para alegar meta atingida

A plataforma **não** declara precisão ≥ 0,98 / recall ≥ 0,95 enquanto todos os itens abaixo não existirem:

- [ ] amostra de teste congelada e independente de treino/calibração;
- [ ] codebook versionado;
- [ ] revisão humana documentada;
- [ ] blocking auditado fora do próprio conjunto de candidatos;
- [ ] thresholds congelados antes de abrir o teste final;
- [ ] matriz de confusão e métricas por estrato calculadas;
- [ ] incerteza estatística reportada;
- [ ] manifesto/hashes permitem reproduzir o experimento;
- [ ] resultado final satisfaz ou rejeita explicitamente as metas, sem ajustar o critério depois de ver os dados.
