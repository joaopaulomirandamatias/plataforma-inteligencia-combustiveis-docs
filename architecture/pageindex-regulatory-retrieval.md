# PageIndex como motor complementar de recuperação documental no PIC

**Status:** proposta para PoC  
**Referência:** https://github.com/VectifyAI/PageIndex  
**Data:** 2026-09-29

## Objetivo

Avaliar o PageIndex como componente de recuperação documental da Plataforma de Inteligência de Combustíveis (PIC), com foco em normas, resoluções, relatórios técnicos, procedimentos, estudos científicos e documentos relacionados a fiscalização e fraude.

O PageIndex constrói uma representação hierárquica dos documentos e usa raciocínio para localizar seções relevantes. Essa abordagem pode complementar a busca vetorial tradicional em situações nas quais a resposta depende de contexto normativo ou da estrutura interna de um documento longo.

## Papel no PIC

A arquitetura do PIC deve separar claramente três classes de informação:

```text
Dados operacionais        Conhecimento documental       Relações semânticas
     |                              |                            |
     v                              v                            v
Analytics / ML              Retrieval Router              Knowledge Graph
                                    |
                         +----------+----------+
                         |                     |
                         v                     v
                    Vector Search           PageIndex
                         |                     |
                         +----------+----------+
                                    |
                                    v
                              PIC Intelligence
```

O PageIndex entra apenas na camada de **conhecimento documental**.

## Casos de uso prioritários

### 1. Inteligência regulatória

Perguntas como:

- quais requisitos regulatórios se aplicam a determinada irregularidade?
- qual seção de uma resolução estabelece um procedimento de fiscalização?
- quais obrigações recaem sobre determinado agente econômico?
- quais limites, critérios ou exceções constam na norma aplicável?

podem se beneficiar da navegação hierárquica do documento.

### 2. Pesquisa sobre fraude em combustíveis

Para a linha de pesquisa sobre fraude em postos, o PageIndex pode apoiar leitura profunda de:

- artigos científicos;
- relatórios de fiscalização;
- estudos técnicos;
- documentos de órgãos de controle;
- normas e regulamentos;
- materiais sobre adulteração, fraude metrológica e evasão.

A recuperação deve diferenciar claramente:

- hipótese;
- método;
- resultado;
- indicador de fraude;
- evidência empírica;
- limitação do estudo.

### 3. Explicação de alertas

Um alerta gerado por Analytics/ML pode ser enriquecido com evidência documental:

```text
Anomalia detectada
       |
       v
classificação do evento
       |
       +--> dados históricos
       +--> regras estruturadas
       +--> normas/documentos via PageIndex
       |
       v
explicação auditável
```

Exemplo: o modelo detecta comportamento atípico; a camada documental recupera normas ou procedimentos relacionados, sem afirmar automaticamente que houve infração.

## Estratégia híbrida

### Vector Search

Usar para descoberta, similaridade conceitual e busca ampla em corpus grande.

### PageIndex

Usar para leitura profunda, localização de requisito, seção, método ou evidência dentro de documentos longos.

### Knowledge Graph

Usar para relacionar posto, agente econômico, produto, evento, norma, obrigação, infração e evidência.

### Analytics / ML

Usar para padrões quantitativos, anomalias, séries temporais e predição.

Nenhum desses mecanismos substitui os demais.

## Controle de versão regulatória

A seleção de documentos deve considerar vigência e versionamento fora do PageIndex:

```text
RegulatoryDocument
- id
- authority
- identifier
- publicationDate
- effectiveFrom
- effectiveUntil
- status
- supersedes
- supersededBy
- sourceUrl
- contentHash
```

O PageIndex recupera conteúdo dentro da versão selecionada; o PIC decide qual versão é válida para a data e contexto da consulta.

## Proveniência

Toda evidência documental utilizada em uma análise deve guardar:

- identificador do documento;
- autoridade/fonte;
- versão e vigência;
- seção/capítulo;
- página;
- trecho recuperado;
- mecanismo de retrieval;
- consulta realizada;
- modelo utilizado;
- timestamp;
- trace id.

## Segurança

Documentos internos, autos, relatórios e dados de fiscalização podem ser sensíveis. Aplicar:

- segregação por tenant/projeto;
- controle de acesso antes do retrieval;
- opção de indexação local;
- secrets fora do código;
- logging sem conteúdo sensível;
- trilha de auditoria.

## Benchmark proposto

### Corpus

Montar corpus contendo:

- normas e resoluções relevantes ao setor;
- documentos técnicos;
- artigos sobre fraude/adulteração;
- relatórios públicos;
- exemplos sintéticos ou autorizados de documentos internos.

### Configurações

Comparar:

1. busca lexical;
2. vector RAG;
3. PageIndex;
4. Vector + PageIndex;
5. Vector + PageIndex + Knowledge Graph.

### Métricas

- precisão da seção/página;
- retrieval precision/recall;
- citation faithfulness;
- completude do requisito recuperado;
- custo;
- latência;
- taxa de uso da norma vigente;
- explicabilidade da resposta.

## Limitações e riscos

- o SDK PageIndex ainda é classificado como Alpha;
- benchmarks do projeto devem ser reproduzidos internamente;
- raciocínio documental não substitui validação jurídica/regulatória;
- OCR e documentos ricos em imagem exigem testes específicos;
- respostas do sistema devem separar evidência observada de inferência.

## Decisão atual

**Adicionar PageIndex ao roadmap técnico do PIC como motor complementar de recuperação estruturada de documentos.**

A adoção deve ocorrer somente após PoC comparativa. O desenho preferido é híbrido, combinando analytics/ML, busca vetorial, PageIndex, consultas estruturadas e grafo de conhecimento.

## Próximos passos

- [ ] selecionar corpus regulatório e científico;
- [ ] definir perguntas com ground truth;
- [ ] criar adaptador `PageIndexRetrievalProvider`;
- [ ] implementar versionamento/vigência documental;
- [ ] comparar com vector baseline;
- [ ] validar rastreabilidade das respostas;
- [ ] avaliar integração com alertas e investigação assistida.
