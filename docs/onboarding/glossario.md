# Glossário — Linguagem ubíqua

Fonte única de terminologia da Plataforma de Inteligência de Combustíveis (v1). Regra do [Plano Diretor](../arquitetura/plano-diretor.md): **documento que redefine termo daqui é bug.** Termos organizados por bounded context; um termo vale para o sistema inteiro com o significado registrado aqui.

---

## Identidade & Cadastro

| Termo | Definição operacional |
|---|---|
| **`posto_id`** | Identificador canônico e estável de um posto físico, produzido pela reconciliação. Única chave aceita para integração entre contextos (ADR-003). |
| **Golden record** | O registro consolidado de um posto: melhor valor conhecido de cada campo, com proveniência campo a campo. |
| **Blocking** | Primeiro passo da reconciliação: reduzir o espaço de comparação agrupando registros por proximidade geográfica/textual antes de comparar pares. |
| **Par candidato** | Dois registros de fontes distintas que o blocking aproximou e ainda não foram julgados como mesmo posto ou postos distintos. |
| **Cluster** | Conjunto de registros julgados como o mesmo posto físico. Todo cluster tem versão; mudar um cluster gera versão nova, nunca edita a anterior. |
| **Fila de revisão humana** | Destino obrigatório de par candidato com score entre os limiares de aceite e rejeição automáticos. Nada duvidoso entra sozinho. |
| **Ligação errada** | Atribuir a um posto o histórico de outro. O pior erro do sistema — pior que deixar de ligar. |

## Vínculo Societário

| Termo | Definição operacional |
|---|---|
| **Aresta T1–T4** | Ligação entre entidades com nível de certeza: T1 filial (determinística), T2 sócio PJ (determinística), T3 sócio PF (probabilística — CPF mascarado), T4 coincidência operacional (indiciária — endereço/telefone). Nunca se misturam. |
| **Grupo societário aparente** | Componente conexo do grafo de vínculos. "Aparente" é obrigatório: não é afirmação de grupo econômico em sentido legal. |
| **`pessoa_id`** | Pseudônimo estável de pessoa física: `HMAC(sal_do_cofre, CPF)`. É o único identificador de PF que circula fora do cofre (ADR-004). |
| **Cofre de identidade** | Único componente autorizado a conter CPF completo. Banco próprio, rede segregada, acesso com finalidade logada. |
| **Rotas R1/R2/R3** | Vias legítimas de resolução de identidade: R1 — o órgão confirma com meios próprios; R2 — convênio/contrato formal; R3 — requisição em caso concreto. Não existe R4. |
| **Sucessão de fachada** | Padrão: CNPJ baixado após autuação e novo CNPJ aberto no mesmo endereço em seguida. Detectável só com histórico próprio dos dumps. |
| **Reincidência migrante** | Mesmo grupo aparente autuado em municípios/UFs diferentes ao longo do tempo. |

## Temporalidade (transversal)

| Termo | Definição operacional |
|---|---|
| **Bitemporalidade** | Todo fato carrega dois tempos: **validade** (quando foi verdade no mundo) e **transação** (quando entrou na base). Escrita sempre aditiva (ADR-001). |
| **As-of** | Modo de consulta que responde "o que era verdade em <data>, segundo o que sabíamos em <data>". Toda consulta de produto é as-of. |
| **Snapshot** | Materialização versionada de leituras quentes em uma data. É cache com identidade — nunca fonte de verdade. |
| **Corte temporal** | Fronteira de data que separa o que um modelo pode ver do que ele tenta prever. Violá-la é vazamento. |
| **Zona bruta** | Camada imutável com todo arquivo baixado como chegou, com data e hash (ADR-002). |
| **Linhagem** | Cadeia rastreável do número publicado até o byte de origem na zona bruta. |

## Qualidade & Preços

| Termo | Definição operacional |
|---|---|
| **PMQC** | Programa de Monitoramento da Qualidade dos Combustíveis (ANP). Fonte do rótulo de qualidade: amostra, ensaio, resultado. |
| **Não conformidade** | Desvio de requisito técnico ou regulatório registrado por fonte oficial. **Não** é sinônimo de fraude — intencionalidade não está demonstrada. |
| **SLP** | Levantamento Semanal de Preços da ANP. Base da detecção de preço anômalo. |
| **Preço anômalo** | Preço fora da distribuição regional **condicionada** (região, produto, semana, bandeira). Sinal, nunca veredito. |
| **Semana ANP** | Janela de coleta do SLP — a unidade temporal do contexto de Preços. |

## Risco & Priorização

| Termo | Definição operacional |
|---|---|
| **Feature** | Variável de entrada de modelo, registrada no feature store com definição, corte temporal e fonte. |
| **Vazamento** | Feature que usa informação posterior à data da predição, ou que inclui o próprio alvo (ex.: taxa do grupo sem excluir o próprio posto). Invalida o backtest. |
| **Backtesting temporal** | Protocolo de validação: treina até T, prevê T+1, compara com o que de fato foi encontrado. Congelado antes de rodar. |
| **Precision@k** | Das k fiscalizações recomendadas, quantas resultaram em achado — comparada ao critério atual do órgão. A métrica que decide o projeto. |
| **Lift** | Quanto uma condição (ex.: pertencer a grupo com posto autuado) multiplica a probabilidade base. |
| **Score** | Saída de modelo com intervalo, razões e cobertura. Restrito a órgãos (ADR-005). |
| **Cobertura** | Fração do parque com dado suficiente para a afirmação feita. Todo número sai acompanhado dela. |

## Investigação & Agentes

| Termo | Definição operacional |
|---|---|
| **Caso** | Unidade de investigação aberta por gatilho (`LimiarDeRiscoCruzado` etc.), com linha do tempo, evidências e estado. |
| **Indício** | Evidência compatível com desvio. Nunca "prova", nunca "fraude" — a política de linguagem proíbe. |
| **Refutação** | Tentativa sistemática de derrubar um indício (dono mudou? norma mudou? amostra pequena? erro de ligação?) antes de qualquer publicação. |
| **Dossiê** | Relatório final ao órgão: achado, evidência com linhagem, hipóteses alternativas testadas, o que **não** se pode afirmar. |
| **Sentinela / Investigador / Refutador / Relator / Curador / Analista regulatório / Guardião** | Os sete agentes. Definições completas em `agentes/catalogo` do repositório de docs; o Guardião é barreira de saída obrigatória (ADR-008). |
| **Política de linguagem** | Conjunto verificável de afirmações permitidas por nível de evidência. Aplicada por software, não por estilo. |

## Entrega & Produto

| Termo | Definição operacional |
|---|---|
| **Ficha do posto** | Visão pública: fatos datados com fonte e direito de resposta. Sem score, sem rótulo pejorativo. |
| **Selo de transparência** | Reconhecimento positivo, auditável, de posto com histórico limpo e dados completos. O público vê selo, não nota de risco. |
| **Contraditório** | Canal do posto para ver indício que pesa sobre ele e registrar explicação (manutenção, aferição recente, troca de bomba). |
| **Escopo** | Atributo ABAC que limita o que um papel vê (UF, órgão, rede, rota). Fiscal de SP não vê o Pará. |

## Normativo & Metrologia

| Termo | Definição operacional |
|---|---|
| **Vigência** | Intervalo em que um ato normativo vale. Toda regra citada carrega vigência; "a norma" sem data é bug. |
| **RTM** | Regulamento Técnico Metrológico (Inmetro) aplicável a bombas medidoras. |
| **Aferição / verificação** | Ato do IPEM que mede o erro da bomba contra o limite. Fonte do rótulo metrológico (fase 2). |
| **Bico** | Unidade mínima de medição fiscalizável de uma bomba. O erro do IPEM é por bico. |
| **Gabarito** | Verdade de referência para treino/validação: quem estava de fato fora do limite, e por quanto. IPEM (metrológico) e PMQC (qualidade). |
| **Wetstock** *(fase 2)* | Gestão de estoque molhado: conciliação tanque × bombas × entregas. Vocabulário da literatura de forecourt. |
