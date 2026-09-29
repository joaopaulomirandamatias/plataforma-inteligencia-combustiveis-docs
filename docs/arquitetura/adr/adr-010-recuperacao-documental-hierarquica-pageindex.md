# ADR-010 — Recuperação documental hierárquica como capacidade complementar

**Status:** Proposta para POC  
**Data:** 2026-09-29  
**Contexto:** PHN / ReguHub — inteligência regulatória, busca normativa, radar e evidências

## 1. Decisão

Adotar uma capacidade de **recuperação estruturada e hierárquica de documentos** como complemento aos mecanismos já previstos na plataforma, avaliando o **PageIndex** como primeira implementação de referência.

Essa capacidade **não substitui**:

- busca vetorial / pgvector;
- ontologia regulatória;
- Knowledge Graph;
- regras de aplicabilidade;
- normalização normativa;
- rastreabilidade e evidências do PHN;
- mecanismos determinísticos de consulta e classificação.

Ela será usada como uma camada especializada para localizar e recuperar conteúdo em documentos longos e estruturados, preservando contexto hierárquico e permitindo que agentes raciocinem sobre a organização interna da fonte.

## 2. Motivação

Normas, regulamentos, manuais e documentos técnicos possuem estrutura semântica própria. Um requisito pode depender da relação entre capítulo, seção, artigo, parágrafo, inciso, alínea e anexo. A segmentação tradicional em chunks pode perder parte desse contexto.

Uma abordagem hierárquica permite representar documentos de forma semelhante a:

```text
Norma
├── Título
│   ├── Capítulo
│   │   ├── Seção
│   │   │   ├── Artigo
│   │   │   │   ├── Parágrafo
│   │   │   │   └── Inciso
│   │   └── Seção
│   └── Capítulo
└── Anexos
```

O PageIndex utiliza um índice em árvore e recuperação orientada por raciocínio, em vez de depender exclusivamente de similaridade vetorial. Esse modelo é especialmente promissor para documentos profissionais longos, incluindo documentos jurídicos, regulatórios e técnicos.

## 3. Papel arquitetural

A capacidade deve ser isolada atrás de uma abstração própria da plataforma, evitando dependência irreversível de um fornecedor ou biblioteca específica.

Interface conceitual:

```text
DocumentRetrievalProvider
├── VectorRetrievalProvider
├── HierarchicalRetrievalProvider
│   └── PageIndexProvider
└── NativeDocumentRetrievalProvider
```

O PHN deve continuar sendo responsável por decidir **quais normas são candidatas e por que elas se aplicam**. A recuperação hierárquica deve responder principalmente **onde está a evidência relevante no documento e qual é o contexto estrutural dessa evidência**.

## 4. Arquitetura recomendada

```text
                   Fontes normativas
                         │
                 PDF / HTML / XML
                         │
                         ▼
              Normalização documental
               OCR / parsing / versões
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
     Recuperação hierárquica     Busca vetorial
       (ex.: PageIndex)           (pgvector)
             │                       │
             └───────────┬───────────┘
                         ▼
                  Retrieval Router
                         │
             ┌───────────┼───────────┐
             │           │           │
             ▼           ▼           ▼
         Ontologia   Knowledge   Dados/SQL
                     Graph
             │           │           │
             └───────────┼───────────┘
                         ▼
                  Evidence Fusion
                         │
                         ▼
                 Regulatory Agent
                         │
          resposta + fundamento + evidência
```

## 5. Casos de uso prioritários

### 5.1 Busca normativa explicável

Exemplo:

> Quais requisitos sanitários se aplicam ao armazenamento deste produto?

Fluxo proposto:

1. identificar atividade, produto, jurisdição e contexto;
2. selecionar normas candidatas usando ontologia, regras e metadados;
3. usar recuperação hierárquica para localizar artigos, parágrafos, incisos e anexos relevantes;
4. fundir a evidência com o modelo semântico do PHN;
5. produzir resposta com origem rastreável.

### 5.2 Evidência e auditoria

A resposta regulatória deve poder ser vinculada a uma cadeia verificável:

```text
Documento
→ estrutura
→ dispositivo
→ trecho
→ conceito regulatório
→ requisito
→ regra de aplicabilidade
→ decisão apresentada ao usuário
```

A recuperação hierárquica deve preservar, quando disponível:

- identificador da norma;
- versão da norma;
- página;
- caminho hierárquico;
- artigo / parágrafo / inciso / anexo;
- trecho recuperado;
- confiança ou score interno;
- identificador da execução que produziu a evidência.

### 5.3 Radar de Inteligência Regulatória

A capacidade também pode apoiar análise estrutural de mudanças entre versões:

```text
Norma v1 → árvore v1
Norma v2 → árvore v2
              │
              ▼
       comparação estrutural
              │
              ▼
Art. alterado / inciso incluído / anexo substituído
              │
              ▼
       análise de impacto PHN
              │
              ▼
empresas / CNAEs / produtos / requisitos afetados
```

Essa abordagem deve complementar, e não substituir, o diff textual e os mecanismos formais de versionamento.

### 5.4 DPP / Passaporte Digital do Produto

Pode ser usada para recuperar evidências em:

- regulamentos aplicáveis;
- certificados;
- relatórios técnicos;
- documentos de conformidade;
- especificações de produto;
- documentos de rastreabilidade.

O motor documental localiza a evidência; a ontologia e o Knowledge Graph conectam essa evidência ao produto, processo, requisito, ator e jurisdição.

### 5.5 Agentes regulatórios

A capacidade deve poder ser exposta como ferramenta para agentes, por exemplo:

```text
Regulatory Agent
├── identify_activity()
├── map_cnae()
├── find_applicable_regulations()
├── retrieve_document_structure()
├── retrieve_document_evidence()
├── map_requirements_to_ontology()
└── generate_regulatory_evidence()
```

## 6. Estratégia híbrida

A decisão arquitetural é utilizar recuperação **híbrida**, combinando mecanismos conforme a natureza da consulta.

| Mecanismo | Uso principal |
|---|---|
| pgvector | descoberta semântica ampla e similaridade |
| recuperação hierárquica | contexto estrutural em documentos longos |
| Knowledge Graph | relações entre normas, requisitos, atividades, produtos e jurisdições |
| ontologia | significado formal e interoperabilidade semântica |
| SQL | fatos estruturados e filtros determinísticos |
| LLM / agentes | raciocínio, composição e explicação |

O `Retrieval Router` deverá escolher uma ou mais estratégias e combinar seus resultados.

## 7. PageIndex como implementação de referência

O PageIndex foi identificado como candidato adequado porque oferece:

- recuperação baseada em árvore hierárquica;
- operação sem dependência obrigatória de vector database;
- raciocínio sobre a estrutura do documento;
- SDK Python;
- modo local;
- integração com agentes;
- licença MIT para o projeto open source.

Entretanto, o pacote deve ser tratado como **componente experimental até validação**, pois seu SDK ainda declara estágio Alpha. Portanto, nenhuma regra de negócio central do PHN deve depender diretamente de classes ou formatos internos do PageIndex.

## 8. Local vs. Cloud

### Local / self-hosted

Preferido inicialmente para o POC e para documentos públicos com camada textual.

Vantagens:

- maior controle arquitetural;
- menor dependência externa;
- possibilidade de isolamento da biblioteca atrás do provider;
- compatibilidade com infraestrutura própria.

### Cloud

Pode ser avaliado posteriormente quando houver necessidade comprovada de:

- OCR gerenciado;
- documentos digitalizados;
- compreensão de imagens;
- metadados avançados;
- organização por folders;
- citações mais granulares;
- escala gerenciada de corpus.

A adoção de Cloud deve passar por avaliação própria de segurança, privacidade, custo, retenção, localização dos dados e disponibilidade.

## 9. POC obrigatório antes de produção

Executar benchmark com conjunto controlado de aproximadamente 20 a 50 normas reais.

Comparar ao menos:

1. busca vetorial atual;
2. recuperação hierárquica com PageIndex;
3. estratégia híbrida: PageIndex + pgvector + ontologia PHN.

### Tipos de perguntas

- qual artigo define a obrigação X?;
- a obrigação possui exceções?;
- quem é o sujeito obrigado?;
- qual prazo se aplica?;
- quais dispositivos regulam determinada atividade?;
- qual anexo complementa o artigo?;
- qual dispositivo foi alterado entre versões?;
- quais trechos sustentam determinada conclusão regulatória?.

### Métricas

- precisão da resposta;
- recall de evidências;
- precisão da citação;
- acerto do artigo/parágrafo/inciso;
- taxa de alucinação;
- latência;
- custo por consulta;
- uso de tokens;
- cobertura de documentos;
- estabilidade operacional.

## 10. Critérios para promoção a componente oficial

A solução somente deve ser promovida de experimental para oficial se:

- superar ou complementar de forma mensurável a busca vetorial em documentos estruturados;
- produzir evidências rastreáveis;
- possuir latência aceitável;
- ter custo operacional sustentável;
- não introduzir dependência proprietária obrigatória;
- possuir fallback para outros providers;
- manter a separação entre recuperação documental e decisão regulatória.

## 11. Riscos e controles

### Risco: acoplamento à biblioteca

Controle: encapsular via `HierarchicalRetrievalProvider`.

### Risco: recuperação correta, interpretação errada

Controle: separar `retrieval` de `regulatory reasoning` e exigir evidências explícitas.

### Risco: documentos digitalizados ou de baixa qualidade

Controle: pipeline OCR e quality gate antes da indexação.

### Risco: divergência entre árvore documental e estrutura jurídica real

Controle: validação contra parser normativo canônico do PHN e identificação explícita de artigo/parágrafo/inciso.

### Risco: uso indevido do resultado como decisão jurídica automática

Controle: manter políticas de governança, rastreabilidade, revisão e indicação de origem da evidência.

## 12. Evolução futura: Regulatory Tree

A árvore documental pode ser enriquecida pelo PHN e transformada conceitualmente em um `Regulatory Tree`:

```text
Norma
├── requisitos
├── obrigações
├── exceções
├── definições
├── sanções
└── anexos
```

Com ligações semânticas como:

```text
appliesTo → CNAE
appliesTo → Product
requires → Requirement
exceptionOf → Rule
supersedes → Regulation
equivalentTo → InternationalRule
```

Essa evolução deve alimentar o Regulatory Knowledge Graph, sem confundir a estrutura recuperada do documento com fatos já validados no grafo.

## 13. Decisão resumida

A plataforma deverá suportar **Vector + Hierarchical Tree + Knowledge Graph + Ontology + Agentic Reasoning** como estratégia de recuperação e interpretação regulatória.

O PageIndex será avaliado como primeira implementação do motor hierárquico por meio de POC e benchmark. Seu uso inicial será complementar e isolado, preservando a independência arquitetural do PHN/ReguHub.

## 14. Referências

- PageIndex — https://github.com/VectifyAI/PageIndex
- Documentação PageIndex — https://docs.pageindex.ai/

