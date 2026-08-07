# Entity Resolution — identidade canônica do posto

Como registros de cinco fontes viram um `posto_id`. Este é o componente onde mora o pior erro possível do sistema — **ligação errada**: atribuir a um posto o histórico de outro. Todo o desenho abaixo é assimétrico por causa disso: *deixar de ligar é recuperável; ligar errado propaga injustiça.*

## O que `posto_id` identifica

`posto_id` identifica o **ponto físico de revenda** com continuidade operacional — não a empresa. A empresa operadora é uma **relação bitemporal** (`empresa ↔ posto`, com validade). Consequência direta: na sucessão de fachada (CNPJ baixado, CNPJ novo no mesmo endereço), o `posto_id` **permanece** e a relação com a empresa muda — é exatamente isso que impede o histórico de "zerar" com a troca de CNPJ.

## Pipeline

```
normalização → blocking → similaridade → classificação → clusterização → golden record
                                                              │
                                                    fila de revisão humana
```

### 1. Normalização
Endereço (abreviaturas, logradouro, CEP), razão social (sufixos societários removidos para comparação, preservados no dado), geocodificação com tolerância declarada. Saída: registro canônico por fonte, com o original sempre preservado (ADR-002).

### 2. Blocking
Nenhum par é comparado sem passar por ao menos um bloco: **geográfico** (célula geohash + vizinhas), **CNPJ raiz**, **CEP + tipo de logradouro**, **fonético da razão social**. Métrica vigiada: taxa de pares verdadeiros perdidos pelo blocking (estimada por amostragem) — blocking que perde par verdadeiro é recall perdido silenciosamente.

### 3. Similaridade multi-campo
Vetor de características por par candidato:

| Campo | Comparação |
|---|---|
| CNPJ raiz | igualdade (peso dominante quando presente) |
| Razão social / fantasia | similaridade por tokens (Jaccard/Jaro-Winkler) |
| Logradouro normalizado + número | similaridade + igualdade de número |
| CEP | igualdade / prefixo |
| Coordenada | distância em metros |
| Bandeira | igualdade (peso baixo — muda com frequência) |

### 4. Classificação
Fellegi-Sunter probabilístico como baseline explicável; gradient boosting supervisionado quando houver rótulo suficiente da fila humana (active learning: toda decisão humana vira exemplo de treino). Modelo versionado no MLflow com dado de treino registrado.

**Dois limiares, três destinos:**

| Score do par | Destino |
|---|---|
| ≥ limiar de aceite | Liga automaticamente |
| ≤ limiar de rejeição | Descarta automaticamente |
| Entre os dois | **Fila de revisão humana** — nada ambíguo decide sozinho |

Os limiares são calibrados pela assimetria de custo: o de aceite é **conservador** (precisão manda), o de rejeição é folgado (recall recupera depois via nova evidência).

### 5. Clusterização
Fecho transitivo sobre pares aceitos, com **guarda anti-avalanche**: cluster acima de N registros (limiar operacional) é bloqueado para revisão humana antes de valer — fecho transitivo transforma um único falso positivo em fusão em cadeia.

### 6. Golden record
Melhor valor por campo com **proveniência campo a campo** e precedência por fonte declarada por campo (ex.: endereço → cadastro ANP; situação cadastral → Receita; nome fantasia → o mais recente entre fontes). A precedência é configuração versionada, não código.

## Versionamento e reversão

Cluster nunca é editado — nova versão, evento `IdentidadeReconciliada`, e a versão anterior permanece consultável as-of. Separar um cluster fundido erradamente é operação de primeira classe (`LigacaoIdentidadeRevisada`), auditada, com efeito retroativo limpo nas consultas as-of — os fatos não se movem; o que muda é o mapa registro→cluster, bitemporal como tudo.

## Métricas e metas

| Métrica | Meta v1 | Como se mede |
|---|---|---|
| Precisão das ligações | **≥ 0,98** | Amostra rotulada manualmente, estratificada por dificuldade (não aleatória uniforme — pares fáceis inflam a métrica) |
| Recall | **≥ 0,95** | Mesma amostra + estimativa de perda no blocking |
| Fila humana | idade máxima do par < 7 dias | Direto da fila |
| Clusters bloqueados pela guarda | 100% revisados antes de valer | Trilha |

## Casos difíceis catalogados

| Caso | Tratamento |
|---|---|
| Sucessão de fachada | Mesmo `posto_id`, nova relação empresa↔posto (ver acima) |
| Matriz e filial no mesmo endereço | CNPJs distintos, mesmo ponto físico → mesmo `posto_id`, duas relações |
| Postos vizinhos do mesmo dono | Coordenada + número de logradouro separam; na dúvida, fila |
| Endereço de rodovia (km) | Normalização própria de km/sentido; geocodificação decide |
| Renumeração municipal de logradouro | Evidência temporal: mesmo posto se demais campos concordam em janelas distintas |

Decisões da fila humana sobre esses casos alimentam o codebook de revisão — o manual cresce com os casos, não antes deles.
