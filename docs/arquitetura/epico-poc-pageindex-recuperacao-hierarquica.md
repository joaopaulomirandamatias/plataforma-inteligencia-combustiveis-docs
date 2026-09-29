# Épico — POC de recuperação documental hierárquica (PageIndex)

**Status:** pronto para implementação  
**Data:** 2026-09-29  
**ADR de origem:** [ADR-011](adr/adr-011-recuperacao-documental-hierarquica-pageindex.md)  
**Runtime alvo:** PHN / ReguHub (`harmonizacao normativa` no Railway)  
**Serviço Railway:** `pageindex` (experimental, rede privada)

## 1. Objetivo

Transformar a decisão do ADR-011 em um POC mensurável: instalar o PageIndex
como implementação de referência do `HierarchicalRetrievalProvider`, indexar
um dataset regulatório controlado, emitir evidências no contrato PHN e
comparar o resultado com a busca vetorial/lexical já existente — sem alterar
a autoridade de decisão normativa.

## 2. Fora de escopo

- substituir pgvector, ontologia, Knowledge Graph ou regras de aplicabilidade;
- publicação automática de conclusão jurídica;
- UI de produto;
- promoção do PageIndex a componente oficial (só ocorre após o benchmark);
- OCR cloud gerenciado (fica para avaliação posterior).

## 3. Fatias de entrega

| Fatia | Entrega | Critério de pronto |
| --- | --- | --- |
| F0 | Serviço Railway `pageindex` com PageIndex instalado, `/health` e status do provider | deployment Online; status declara `pageindexInstalled` e `llmConfigured` |
| F1 | Contrato `HierarchicalRetrievalProvider` + adaptador `PageIndexProvider` | interface estável no monorepo PHN; zero import direto do PageIndex fora do adaptador |
| F2 | Dataset regulatório de 20–50 normas reais (café/soja/UE/BR prioritários) | manifesto versionado com CELEX/URL/sha; árvores indexadas reproduzíveis |
| F3 | Contrato de evidência hierárquica alinhado ao evidence PHN | JSON Schema + exemplos; `decisionAuthority=NONE` |
| F4 | Benchmark automatizado (vetorial × hierárquico × híbrido) | job CI/local com métricas e relatório; gate de promoção documentado |

## 4. `HierarchicalRetrievalProvider`

### 4.1 Responsabilidade

Responder **onde** está a evidência no documento e qual é o **caminho
estrutural**. Não decide aplicabilidade.

### 4.2 Interface conceitual

```text
HierarchicalRetrievalProvider
├── health() -> ProviderHealth
├── index_document(doc: NormativeDocumentRef, bytes|uri) -> TreeIndexReceipt
├── get_tree(doc_id) -> DocumentTree
└── retrieve(query: HierarchicalQuery) -> list[HierarchicalEvidence]
```

```text
HierarchicalQuery
├── text: str
├── documentIds?: list[str]     # candidatos já escolhidos pelo PHN
├── jurisdiction?: str
├── limit: int
└── requireStructuralPath: bool # exige artigo/§/inciso quando existir
```

```text
HierarchicalEvidence
├── documentId
├── documentVersion
├── structuralPath[]          # ex.: Título > Cap. > Art. 12 > §1º
├── deviceHints               # article / paragraph / item / annex (se detectados)
├── pageRange?
├── excerpt
├── score / confidence?
├── provider = "pageindex"
├── executionId
└── decisionAuthority = "NONE"
```

### 4.3 Isolamento

- único módulo autorizado a importar o SDK PageIndex:
  `services/pageindex/provider_pageindex.py` (ou equivalente);
- demais consumidores falam só com a interface HTTP/interna do serviço;
- falha do PageIndex degrada para “provider indisponível”, nunca para decisão.

## 5. Dataset regulatório de teste

### 5.1 Tamanho e composição

- **20–50** normas/versões reais;
- prioridade inicial alinhada ao piloto PHN: café torrado, soja, higiene/LMR UE,
  atos BR correlatos já presentes no ledger (0112–0114 e vizinhos);
- misturar: regulamento longo, diretiva, anexo tabular, republicação/alteração.

### 5.2 Manifesto (`dataset/manifest.json`)

Cada entrada:

| Campo | Obrigatório | Nota |
| --- | --- | --- |
| `docId` | sim | estável no POC |
| `title` | sim | |
| `jurisdiction` | sim | UE / BR / … |
| `officialIdentifier` | sim | CELEX, URN LEX, etc. |
| `versionLabel` | sim | |
| `sourceUri` | sim | URL oficial ou artefato versionado |
| `contentSha256` | sim | do PDF/HTML indexado |
| `language` | sim | |
| `notes` | não | peculiaridades (anexo escaneado, etc.) |

### 5.3 Golden questions (mínimo 40)

Cobrir os tipos do ADR-011 §9: obrigação, exceção, sujeito, prazo, atividade,
anexo, alteração entre versões, trechos que sustentam conclusão.

Cada pergunta liga a `expectedDevices[]` (artigo/§/inciso) e `acceptableDocIds[]`.

## 6. Contrato de evidência

Estender o espírito do evidence-retrieval atual:

- `schemaVersion`: `phn-hierarchical-evidence/v1`;
- `decisionAuthority`: sempre `NONE`;
- proveniência: `documentId`, `contentSha256`, `treeReceiptId`, `provider`,
  `providerVersion`, `executionId`, `structuralPath`, `excerpt`, `pageRange?`;
- proibido: campos de “aplicável / não aplicável”, score de conformidade ou
  ranking regulatório.

O consumidor canônico no POC é o benchmark e, depois, o `Retrieval Router`
(SEL / evidence-retrieval), nunca o motor de regras.

## 7. Benchmark automatizado

### 7.1 Braços

1. **baseline lexical/vetorial** — evidence-retrieval / eval RAG já existente;
2. **hierárquico** — `pageindex` isolado;
3. **híbrido** — candidatos pelo baseline + refino hierárquico.

### 7.2 Métricas (ADR-011 §9)

| Métrica | Como medir no POC |
| --- | --- |
| precisão / recall de evidências | hit@k nos `expectedDevices` |
| precisão da citação | path estrutural bate com golden |
| acerto artigo/§/inciso | match normalizado de dispositivo |
| alucinação | excerpt não contido no documento-fonte |
| latência | p50/p95 por braço |
| custo / tokens | contabilizado no adaptador LLM |
| cobertura | % docs do manifesto com árvore válida |
| estabilidade | taxa de erro / timeout do provider |

### 7.3 Artefatos

- `benchmark/report.json` + `.md` (commitável ou CI artifact);
- limiar de promoção (documentado, não automático): hierárquico deve
  **complementar de forma mensurável** o baseline em documentos longos,
  com latência/custo aceitáveis e fallback intacto.

## 8. Instalação Railway (F0)

Serviço `pageindex` no projeto `harmonizacao normativa`:

- imagem a partir de `services/pageindex/Dockerfile`;
- config-as-code: `railway.pageindex.json`;
- healthcheck: `GET /health`;
- rede: **privada** (sem domínio público na F0);
- volume: `pageindex-data` montado em `/data` (árvores e manifesto);
- variáveis:
  - `PAGEINDEX_SERVICE_TOKEN` — bearer interno;
  - `OPENAI_API_KEY` ou rota via `AI_GATEWAY_*` quando disponível;
  - `PAGEINDEX_DATA_DIR=/data`;
  - `PORT` (Railway).

Enquanto a chave LLM não estiver configurada, o serviço permanece Online com
`llmConfigured=false` e os endpoints de index/retrieve respondem `503` com
código explícito — a instalação do runtime não depende do benchmark.

## 9. Plano de implementação no monorepo PHN

```text
services/pageindex/
├── Dockerfile
├── requirements.txt
├── app.py                      # FastAPI: health, status, index, retrieve
├── provider.py                 # protocolo HierarchicalRetrievalProvider
├── provider_pageindex.py       # único adaptador PageIndex
├── evidence_contract.py
├── dataset/manifest.example.json
├── benchmark/
│   ├── run_benchmark.py
│   └── questions.example.json
└── README.md
railway.pageindex.json
```

Atualizar `scripts/railway-config-drift.mjs` para declarar o serviço.

## 10. Critérios de aceite do épico

1. PageIndex instalado e saudável no Railway (`/health` + status).
2. Adaptador isolado atrás de `HierarchicalRetrievalProvider`.
3. Manifesto com ≥20 normas reais e sha dos artefatos.
4. Contrato de evidência versionado com `decisionAuthority=NONE`.
5. Benchmark reproduzível comparando os três braços, com relatório.
6. Nenhuma promoção implícita a componente oficial sem passar pelos critérios
   do ADR-011 §10.

## 11. Riscos herdados do ADR

Acoplamento à biblioteca, interpretação indevida, OCR fraco, divergência
árvore×estrutura jurídica, uso como decisão automática — controles do
ADR-011 §11 aplicam-se integralmente a este épico.

## 12. Próxima ação imediata

1. aterrissar F0 (`pageindex` Online no Railway);
2. preencher `OPENAI_API_KEY` (ou gateway real) para destravar indexação;
3. montar o manifesto das primeiras 20 normas do piloto;
4. fechar F1–F4 em PRs pequenas e mensuráveis.
