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

### Invariável de adjudicação

A adjudicação só é válida quando existem **pelo menos dois rótulos humanos e pelo menos dois valores distintos** para o item. Essa regra não fica apenas na camada Python: a migração F1-08c adiciona uma validação no PostgreSQL para impedir INSERT direto que tente contornar a divergência humana prévia.

Os rótulos originais permanecem append-only. Adjudicar cria outro registro; nunca executa UPDATE ou DELETE sobre a opinião dos revisores.

---

## Separação treino / calibração / teste

Nenhum par do teste final participa da estimativa de parâmetros `m/u`, treinamento de modelo ou escolha dos limiares.

Dividir por **unidade de identidade/grupo**, não apenas aleatoriamente por linha, para evitar que registros quase duplicados do mesmo posto apareçam em treino e teste.

Papéis:

- `treino`: estimar parâmetros/modelos;
- `calibracao`: escolher `limiar_aceite` e `limiar_rejeicao`;
- `teste`: uma única avaliação final congelada.

Se o teste final for usado para ajustar o modelo, ele deixa de ser teste e uma nova amostra final precisa ser criada.

O motor F1-08d reforça essa separação em runtime: ele aceita somente registros marcados como `teste`; item de `treino` ou `calibracao` faz a avaliação falhar explicitamente.

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

### Regra implementada na v1

A F1-08d usa **Wilson 95%** para precisão e recall e adota o critério conservador como gate de alegação:

```text
meta_precisao_sustentada = limite_inferior_IC95(precision) >= 0,98
meta_recall_sustentada   = limite_inferior_IC95(recall)    >= 0,95
meta_modelo_atendida     = ambas verdadeiras
```

Portanto, uma amostra pequena com precisão pontual `1,00` pode corretamente resultar em **meta não sustentada** se o intervalo ainda for largo.

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

### F1-08a — codebook e formato de amostra ✅ engenharia validada

- schema versionado do item de revisão;
- rótulos permitidos;
- evidências exibidas ao revisor;
- campos explicitamente ocultos para blindagem;
- hash do manifesto de dados.

Implementação: `pic.revisao_entity_resolution`, com IDs opacos e JSON determinístico. CI completo ficou verde antes do bloqueio de billing do Actions.

### F1-08b — gerador de amostra 🧪 implementado / CI bloqueado

- seleção determinística dado `seed` + manifesto;
- estratificação declarada;
- IDs opacos para revisão;
- nunca inclui score/destino no pacote do revisor;
- exporta lista separada para reconciliação posterior com o experimento.

Implementação: `pic.amostragem_entity_resolution`. A seleção usa ranking SHA-256 de `seed + item_id`, quotas exatas e falha quando um estrato não possui população suficiente. Validação local isolada dos módulos puros passou; falta o CI canônico após regularização do billing.

### F1-08c — importação/adjudicação 🧪 implementado / CI bloqueado

- dois revisores não sobrescrevem um ao outro;
- adjudicação é novo evento, não UPDATE do rótulo original;
- experimento, item, rótulo e adjudicação são append-only;
- migração `012_rotulos_entity_resolution.sql`;
- PostgreSQL também impede adjudicação sem divergência humana prévia.

A migração não deve ser considerada de produção antes de CI verde + promoção automática para `deploy` + confirmação Railway.

### F1-08d — relatório de avaliação 🧪 PR #1 / CI bloqueado

- matriz de confusão;
- métricas globais e por estrato;
- política operacional em três vias;
- `INDETERMINADO` excluído das classes e reportado como cobertura não resolvida;
- Wilson 95% para precisão/recall;
- holdout aceita apenas partição `teste`;
- limiares precisam ser finitos e já estar congelados;
- critérios de aceite satisfeitos ou não satisfeitos sem recalibrar o teste.

Implementação isolada em `work/f1-08d-relatorio` / PR #1. Testes puros locais passaram; merge continua bloqueado até GitHub Actions voltar a executar jobs.

---

## Bloqueio operacional atual

O GitHub Actions informa que os jobs não iniciam porque **pagamento recente falhou ou o spending limit do Actions precisa ser aumentado**. Os runs terminam antes de receber runner e não executam lint, PostgreSQL ou pytest.

A correção depende de **GitHub → Settings → Billing & plans**. Até lá:

- `deploy` não é movida manualmente;
- Railway não volta a apontar para `main`;
- migração 012 não é aplicada manualmente em produção;
- PR #1 não é mergeada sem CI verde.

---

## Critérios para alegar meta atingida

A plataforma **não** declara precisão ≥ 0,98 / recall ≥ 0,95 enquanto todos os itens abaixo não existirem:

- [ ] amostra de teste congelada e independente de treino/calibração;
- [x] codebook versionado em engenharia;
- [ ] revisão humana real documentada;
- [ ] blocking auditado fora do próprio conjunto de candidatos;
- [ ] thresholds empíricos congelados antes de abrir o teste final;
- [ ] matriz de confusão e métricas por estrato calculadas sobre amostra real;
- [ ] incerteza estatística reportada sobre amostra real;
- [ ] manifesto/hashes permitem reproduzir o experimento real;
- [ ] resultado final satisfaz ou rejeita explicitamente as metas, sem ajustar o critério depois de ver os dados.

**Importante:** a engenharia para produzir esses artefatos pode estar concluída antes da evidência empírica. Isso não autoriza transformar testes sintéticos ou locais em alegação científica de desempenho.
