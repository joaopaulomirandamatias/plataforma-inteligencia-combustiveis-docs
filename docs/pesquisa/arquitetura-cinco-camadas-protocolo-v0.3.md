# Arquitetura ciberfísica de cinco camadas — adendo conceitual v0.3

**Data da revisão:** 12/11/2026  
**Natureza:** atualização documental para pesquisa acadêmica, ainda sujeita à revisão metodológica e orientação.  
**Base:** protocolo de pesquisa conceitual v0.2 (24/07/2026, Poli-USP).  
**Estado:** **não implementado**. Não é autorização para teste em bombas, certificação, parecer jurídico ou demonstração de desempenho.

> **Separação de escopos:** a Plataforma de Inteligência de Combustíveis (PIC) v1 agrega dados institucionais, resolve identidades e versiona evidências documentais. A pesquisa das cinco camadas investiga uma arquitetura **ciberfísica futura** que poderia dialogar com a PIC, mas não modifica contratos, funcionalidades, prioridades ou estado operacional da v1. Ver [status canônico](../status-projeto.md), [projeto v1](../projeto-v1.md) e [política de linguagem](../agentes/politica-de-linguagem.md).

## 1. Objetivo científico

**Pergunta:** que evidências científicas, técnicas, metrológicas e normativas sustentam as funções, limitações e interfaces de uma arquitetura conceitual em cinco camadas para identificar possíveis irregularidades na dispensação de combustíveis?

O produto desta fase é uma **síntese rastreável** da literatura e das normas, não um equipamento ou algoritmo testado. A relação de interesse é:

`modalidade → fenômeno observável → grandeza/sinal → método → evidência → incerteza → limites → dependências → requisito`.

**Distinções obrigatórias:** fraude implica intencionalidade demonstrada; não conformidade é desvio de requisito; anomalia é indício para apuração. Integridade criptográfica comprova propriedades do registro após captura, não a veracidade física da origem. Sombra digital e gêmeo digital exigem definições técnicas distintas.

## 2. Matriz de investigação (L1–L5)

| Camada | Função de pesquisa | Evidência candidata | Limite crítico | Material acrescentado |
| --- | --- | --- | --- | --- |
| **L1 — medição independente** | Comparar quantidade indicada e referência apropriada | Volume/massa, vazão, temperatura, incerteza, rastreabilidade | Desvio não identifica autoria ou intenção; a cadeia metrológica legal tem requisitos próprios | [OIML R 117:2019](https://www.oiml.org/en/publications/recommendations/117/2019/) |
| **L2 — comportamento** | Estudar intermitência e mudanças de regime | Sequências temporais, mudanças de parâmetro, eventos de manutenção | Variação legítima, deriva de processo e viés de seleção | Inspeções eletrônicas e literatura de detecção multivariada |
| **L3 — físico-química** | Comparar assinaturas e propriedades de combustíveis | Raman, FTIR, densidade, destilação, sensores ópticos/dielétricos, ensaio de referência | Dependência de combustível, lote, adulterante, faixa de concentração e mistura | Revisão ACS Sensors 2026; Raman/FTIR 2026 |
| **L4 — sombra/gêmeo digital** | Analisar consistência de estoque, entrega, abastecimento e contexto | Conservação, histórico, previsão e residual de modelo | Erro do modelo pode produzir alerta sem irregularidade; PIC v1 não possui telemetria de bomba | Modelos conceituais e fontes institucionais como **contexto**, não dados de sensor |
| **L5 — auditoria verificável** | Tornar intervenções, versões e vínculos entre eventos verificáveis | Identidades, sequência, timestamps, hashes/assinaturas, vínculo de evidências | Log íntegro pode conter dado errado; falhas de relógio, chave e origem são possíveis | OIML D 31, Okamoto 2026, Kamada 2026 |

**Fusão de evidências** é uma função transversal de análise e decisão, **não** uma sexta camada. A L5 deve oferecer proveniência desde a aquisição até o relatório, e não apenas no final da cadeia.

## 3. Requisitos a investigar (não implementados)

| ID | Requisito conceitual | Justificativa |
| --- | --- | --- |
| PESQ-01 | Distinguir evento de abastecimento, amostra, ensaio, instrumento e processo de fiscalização | Evita juntar unidades de análise diferentes |
| PESQ-02 | Carregar, se disponíveis, origem, instrumento, método, UTC, período de referência, versão e incerteza | Necessário à interpretação e rastreabilidade |
| PESQ-03 | Preservar a **evidência de ligação** entre sinais atribuídos ao mesmo evento; horário semelhante não basta | Transferência conceitual do modelo de Kamada (2026), ainda não validado em bombas |
| PESQ-04 | Modelar falhas comuns por energia, rede, relógio, firmware, operador, calibrador e fonte de dados | Concordância entre canais correlacionados pode ser enganosa |
| PESQ-05 | Separar integridade e autenticidade digital da exatidão da observação física | Limite de logs e assinaturas |
| PESQ-06 | Representar ausência de dados, atraso, revisão retroativa, mudança de formato e incerteza de vinculação | Ausência de registro não comprova conformidade |
| PESQ-07 | Exigir referência independente e revisão humana para alegações com consequência fiscalizatória | A PIC não declara fraude nem substitui autoridade |
| PESQ-08 | Verificar segurança e metrologia legal antes de qualquer ensaio futuro | Fase documental não autoriza intervenção física |

## 4. Método para atualização da revisão (ainda a executar)

1. **Protocolo pré-registrado:** adotar revisão de escopo segundo JBI, relato PRISMA-ScR, busca PRISMA-S e revisão da busca PRESS; para engenharia, classificação/mapeamento sistemático. Congelar perguntas, critérios e data antes da triagem.
2. **Três corpora distintos:** A = pesquisa científica; B = normas e documentos oficiais; C = patentes, datasets e documentação técnica. Norma, patente ou material comercial não é validação empírica.
3. **Busca reprodutível:** estratégia geral `("fuel dispenser" OR "fuel pump" OR "filling station" OR "liquid measuring system") AND (fraud OR tamper* OR adulterat* OR "short delivery" OR nonconform*)`; buscas especializadas para Raman/FTIR, software metrológico, verificação de logs, medição de líquidos e sombra digital. Adaptar sintaxe por Scopus, WoS, IEEE Xplore, SciELO e CAPES. Documentar consulta literal, data, filtro, resultados e deduplicação.
4. **Sementes 2026:** utilizar os artigos com DOI e boletins listados em [bibliografia e fontes](referencias-e-fontes-2026.md); executar busca retrospectiva e prospectiva de citações. Essas sementes **não** são corpus exaustivo.
5. **Extração padronizada:** fonte/DOI, área, combustível, matriz, laboratório/campo, unidade independente, referência, tamanho, validação fora da amostra, limitações, custo quando relatado, licença, tipo de evidência, camada e maturidade.
6. **Risco de viés:** distinguir apreensões de amostra representativa, mistura de laboratório de campo, imagens de PCB de séries de dispensação e resultados de pesagem de resultados em bombas. Não generalizar acurácia publicada sem validação independente.
7. **Síntese:** produzir taxonomia de modalidades, matriz fraude × camada × método × evidência × falha comum e agenda experimental futura.
8. **Revisão da orientação:** registrar críticas e decisões de escopo antes de formalizar artigo/dissertação.

## 5. Integração documental com as fontes atuais

- **F02/PMQC:** já existe na PIC e tem grão de ensaio/amostra, não abastecimento. A ANP publicou em 13/10/2026 pacotes ZIP com CSV/JSON e dados de 2016 a set/2026. **Isso não significa que todas as competências estejam ingeridas**; o [catálogo F02](../dados/catalogo-fontes.md) mantém fatos, hashes, backfill e limitações operacionais.
- **F03/SLP:** preço é apenas contexto econômico; valor atípico não prova adulteração.
- **F04/fiscalização:** autuação não é decisão definitiva. A ANP explicita contraditório e ampla defesa; a fonte publicada inclui blocos 1998–2018 e 2019–2025 na consulta deste adendo.
- **F08/F09/Inmetro:** preservar vigência, proveniência, restrições de convênio e a distinção entre dados públicos e dados por instrumento.
- **FD-TamperBoard:** dataset acadêmico de imagens de placas, útil à revisão forense, **não** fonte operacional FXX nem diagnóstico automático de postos.

## 6. Entregáveis e critérios de aceite

**Entregáveis propostos:** protocolo registrado, estratégias de busca reproduzíveis, taxonomia, matriz de evidência e ameaça, revisão crítica, requisitos conceituais, lacunas e agenda de validação. **Fora do escopo atual:** hardware, treinamento de modelos, teste de campo, integração em bomba, certificação, alegação de patenteabilidade ou eficácia comercial.

- [ ] Bibliografia com DOI/URL, edição, data e tipo de evidência
- [ ] Critérios e strings de busca previamente congelados
- [ ] Fontes/datasets com licença, proveniência e unidade de análise
- [ ] Matriz L1–L5 com vieses e falhas comuns
- [ ] Normas com edição, vigência e status de minuta
- [ ] Avaliação de especialistas registrada sem confundir opinião com validação
- [ ] Revisão do orientador antes de publicar o protocolo definitivo

**Leitura complementar:** [Bibliografia, datasets e manuais — 2026](referencias-e-fontes-2026.md). Para o estado **implementado** do produto, usar exclusivamente [status-projeto.md](../status-projeto.md).

## Desdobramento de produto independente da revisão científica — PIC Verifica (12/11/2026)

O projeto passou a prever um [APP de consulta, verificação digital e relatos](../produto/pic-verifica-app.md) como canal futuro da PIC. Esse plano **não altera a natureza conceitual desta pesquisa**: nenhuma bomba, leitura Bluetooth, sensor ou resultado de denúncia foi testado ou validado. A NIT-Sinst-020, a Portaria Inmetro 227/2022 (e alterações) e certificados de Objetos Metrológicos serão pesquisados para verificar se e como dados assinados podem ser coletados **legalmente e em modo leitura**. Relatos do cidadão são **declarações não verificadas**, sob governança privada, e não entram como rótulos de fraude ou como substitutos de evidência laboratorial/metrológica.
