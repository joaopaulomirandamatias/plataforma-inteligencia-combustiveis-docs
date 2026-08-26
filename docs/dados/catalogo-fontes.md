# Catálogo de Fontes de Dados

Um registro por fonte, no padrão do [Plano Diretor](../arquitetura/plano-diretor.md) (`docs/dados/catalogo-fontes/`). Campos fixos: o que traz, cadência, formato, acesso, papel no sistema, riscos conhecidos e cuidados de ingestão.

> [!warning] Verificação pendente antes da F0
> URLs, layouts e granularidade marcados com ⚠ precisam de confirmação na fonte oficial antes de escrever o conector — endereços de publicação de dado público brasileiro mudam sem aviso e sem redirect.

## Política de divergência de esquema (todos os conectores tabulares)

Decisão da F0-01, arbitrada de novo na verificação da F0-02: **tolerante a coluna nova, intolerante a coluna que some.**

- Coluna **extra** não declarada: ignorada e **reportada com alerta** (`colunas_novas`) — fonte pública acrescentar campo é rotina e não pode custar a janela de coleta.
- Coluna **esperada ausente**: quarentena — nada entra na base.
- O contrato de cabeçalho declara **todas** as colunas que o parser lê: coluna lida sem contrato é defeito (sumiria em silêncio como NULL em vez de ir à quarentena).

---

## F01 — ANP · Cadastro de revendedores

| Campo | Valor |
|---|---|
| O que traz | Postos autorizados: `CODIGOISIMP`, autorização, razão social, CNPJ, endereço, UF/município, bandeira, datas |
| URL vigente *(verificada em 2026-08-07)* | `https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/arquivos-dados-cadastrais-dos-revendedores-varejistas-de-combustiveis-automotivos/dados-cadastrais-revendedores-varejistas-combustiveis-automoveis.csv` |
| Formato | CSV UTF-8, separador `;`, CRLF. Colunas: `CODIGOISIMP;AUTORIZACAO;DATAPUBLICACAO;RAZAOSOCIAL;CNPJ;ENDERECO;COMPLEMENTO;BAIRRO;CEP;UF;MUNICIPIO;BANDEIRA;DATAVINCULACAO` |
| Cadência | Atualização frequente (arquivo observado com data do próprio dia); coleta agendada. O HTTP **não envia `Last-Modified` nem `ETag`** |
| Semântica temporal | **Fonte-retrato sem data de referência** — armadilha nº 7 do [modelo bitemporal](modelo-bitemporal.md): `validade` inicia na data da coleta; histórico constrói-se da primeira coleta em diante. `DATAPUBLICACAO` é a data da **autorização** (2000→hoje), fica no payload e não retroage a validade |
| Acesso | Público |
| Papel | **Semente do universo**: define o conjunto de `posto_id` candidatos; espinha dorsal cadastral |
| Riscos | Endereço em texto livre; bandeira desatualizada; defasagem entre autorização e operação real |
| Cuidados | Geocodificar com tolerância; nunca usar como prova de operação ativa — é autorização, não atividade |

## F02 — ANP · PMQC (qualidade)

| Campo | Valor |
|---|---|
| O que traz | Amostras coletadas: posto, produto, ensaios, resultado (conforme/não conforme) |
| Cadência | Mensal, com **defasagem de ~2 meses** observada (em 2026-08, o mês mais recente publicado era 2026-06) |
| URL observada *(2026-08)* | `…/dados-abertos/arquivos/pmqc/<AAAA>/pmqc_<AAAA>_<MM>.csv` |
| Formato | CSV |
| Identificador de amostra | **Não existe na fonte.** `amostra_id` é derivado (ponto + data + produto + coordenada GPS; desempate posicional nos raros casos sem coordenada — 10 em 62,6 mil em 2026-06). Republicação com linhas reordenadas pode trocar a identidade desses casos — risco registrado |
| Acesso | Público |
| Papel | **Gabarito de qualidade** (rótulo F2 da taxonomia); insumo do risco e da ficha pública |
| Riscos | Amostragem **dirigida, não aleatória** — taxa de reprovação do PMQC ≠ prevalência real; identificação do posto por nome/endereço, não por chave estável |
| Cuidados | Registrar o desenho amostral junto do dado; toda estatística derivada declara o viés de seleção; reconciliação obrigatória antes de qualquer junção |

## F03 — ANP · SLP (preços)

| Campo | Valor |
|---|---|
| O que traz | Preços coletados por posto, produto e semana |
| Cadência | Semanal. O calendário de semanas **não é publicado junto do dado** — convenção adotada: domingo–sábado (validada sem duplicata no grão em 2026-07); fonte oficial substituirá a convenção se existir |
| Nomes de arquivo | **Irregulares na origem** — exemplos reais de 2026: `02-cados-abertos-…` (typo da própria ANP), arquivo sem extensão, ano embutido no nome. O conector **descobre** a URL na página oficial casando prefixo do mês e família — nunca monta o nome por regra |
| Formato | CSV |
| Acesso | Público |
| Papel | Detecção de preço anômalo; série histórica por região |
| Riscos | Cobertura parcial (nem todo posto toda semana); municípios pequenos sub-representados |
| Cuidados | Anomalia sempre condicionada (região × produto × semana × bandeira); cobertura da semana publicada junto de qualquer agregado |

## F04 — ANP · Autuações e sanções

| Campo | Valor |
|---|---|
| O que traz | Processos administrativos e penalidades |
| Cadência | ⚠ irregular |
| Formato | ⚠ possivelmente PDF/HTML — extração necessária |
| Acesso | Público, granularidade a confirmar |
| Papel | Rótulo de conformidade; feature de reincidência |
| Riscos | Defasagem processual longa entre infração e decisão; identificação inconsistente |
| Cuidados | Registrar as duas datas (fato e decisão) — usar a errada no corte temporal é vazamento |

## F05 — Receita Federal · Dados Públicos CNPJ

| Campo | Valor |
|---|---|
| O que traz | `EMPRESAS`, `ESTABELECIMENTOS`, `SOCIOS` (QSA), situação, CNAE, endereço, telefone |
| Cadência | **Mensal — dump completo**; competências disponíveis de 2023-05 em diante (39 até 2026-07) |
| Formato | ~37 arquivos ZIP/mês, ~7,1 GB por competência; layout com histórico de mudanças |
| Acesso *(verificado em 2026-08-07)* | Público, via compartilhamento **Nextcloud** — descoberta por WebDAV `PROPFIND` em `https://arquivos.receitafederal.gov.br/public.php/webdav` (usuário = token público do share `YggdBLfdninEJX9`, senha vazia). As URLs antigas morreram: `dadosabertos.rfb.gov.br` não responde e `arquivos.receitafederal.gov.br/dados/cnpj/…` retorna 404 |
| Papel | Grafo societário (T1–T4); rotatividade; sucessão de fachada |
| Riscos | **É retrato do presente** — sócio que saiu desaparece do dump seguinte; **CPF mascarado** (`***XXXXXX**`); layout muda sem aviso |
| Cuidados | **Arquivar todo mês, começando já** — mês não capturado é história perdida em caráter irreversível; T3 sempre probabilístico com score; diff mensal gera os eventos `MudancaSocietariaDetectada` |

## F06 — Senacon / Procons · Sindec

| Campo | Valor |
|---|---|
| O que traz | Atendimentos registrados nos Procons, individualizados por fornecedor: `DataAtendimento`, `NumeroCNPJ`, tipo, assunto, grupo de assunto, problema, grupo de problema e UF |
| Cadência | **Trimestral** no portal; o conector sonda o catálogo semanalmente porque a data de publicação varia |
| Formato *(verificado em 2026-08-09)* | CSV. Recurso vigente observado: `da-fornecedor-t1-2026-01-01-a-2026-03-31.csv` |
| Acesso *(verificado em 2026-08-09)* | Público, catálogo CKAN da Senacon: [conjunto Sindec](https://dados.mj.gov.br/dataset/atendimentos-de-consumidores-nos-procons-sindec); [recurso 2026-T1](https://dados.mj.gov.br/dataset/atendimentos-de-consumidores-nos-procons-sindec/resource/359a4f79-629f-4e9e-ab79-ad1b6c0bfdb4) |
| Semântica temporal | Evento datado pela própria fonte: validade de um dia, `[DataAtendimento, DataAtendimento+1)` |
| Papel | **Sinal de contexto oficial** na linha do tempo; não é rótulo nem prova de responsabilidade do fornecedor |
| Riscos | Viés de cobertura e de quem procura o Procon; categorias podem conter linguagem acusatória; o portal pode remover ou substituir recursos; o arquivo aberto contém atributos do consumidor |
| Cuidados | Descobrir o recurso pelo catálogo, validar esquema e preservar a zona bruta; vincular **somente por CNPJ exato**, nunca por nome aproximado; persistir no fato apenas data e classificações do atendimento — sexo, faixa etária, CEP e texto de consumidor não entram; a borda pública aplica a política de linguagem |

## F07 — IBGE / bases geográficas

| Campo | Valor |
|---|---|
| O que traz | Malha municipal, população, renda, logística viária |
| Cadência | Anual/estável |
| Formato | Shapefiles/CSV |
| Acesso | Público |
| Papel | Normalização territorial; denominadores de indicador; contexto de preço |
| Riscos | Baixos — fonte estável |
| Cuidados | Fixar versão da malha por ano de referência |

## F08 — Corpus normativo (ANP, Inmetro, DOU)

| Campo | Valor |
|---|---|
| O que traz | Resoluções, portarias, RTMs, consolidações — com vigência |
| Cadência | Contínua (Diário Oficial); varredura diária pelo Analista regulatório |
| Formato | HTML/PDF |
| Acesso | Público |
| Papel | RAG regulatório; vigência aplicável a cada fato (bitemporalidade da regra) |
| Riscos | Consolidação manual sujeita a erro; ato que altera ato exige encadeamento |
| Cuidados | Versionar por vigência, nunca sobrescrever; resposta do RAG sempre com citação + data; mudança de limite (ex.: E30/B15) dispara `AtoNormativoPublicado` → reavaliação de modelos |

## F09 — IPEM / Inmetro · Verificações metrológicas *(fase 2 — convênio)*

| Campo | Valor |
|---|---|
| O que traz | Aferições por bomba/bico: erro medido, aprovação/reprovação, lacres, datas |
| Cadência | Conforme convênio; alvo: carga histórica de 5 anos + incremental |
| Formato | A definir no convênio |
| Acesso | **Restrito — convênio** |
| Papel | **Gabarito metrológico** (rótulo F1) — a fonte mais valiosa do sistema; sem ela, detecção volumétrica não valida |
| Riscos | Instrumento jurídico demorado; qualidade/completude desconhecidas até a primeira carga |
| Cuidados | O pedido é específico: **série histórica com erro medido por bico**; modelar desde já o esquema-alvo para que a chegada seja carga, não redesenho |

## F10 — SEFAZ · NFC-e *(fase 3 — restrito)*

| Campo | Valor |
|---|---|
| O que traz | Cupons fiscais: volume, produto, valor, timestamp, emitente |
| Cadência | Contínua |
| Formato | XML/eventos |
| Acesso | **Restrito** — viabilidade jurídica e técnica a estudar |
| Papel | Registro autoritativo de venda; reconciliação declarado × observado |
| Riscos | Sigilo fiscal; volume alto (primeira fonte genuinamente streaming — gatilho do ADR-006 junto com telemetria) |
| Cuidados | Nenhuma ingestão sem base legal escrita; desenho de minimização antes do primeiro byte |

---

## Matriz-resumo

| # | Fonte | Acesso | Cadência | Papel-chave | Fase |
|---|---|---|---|---|---|
| F01 | ANP cadastro | Público | Mensal | Universo de postos | v1 |
| F02 | ANP PMQC | Público | Mensal | Gabarito qualidade | v1 |
| F03 | ANP SLP | Público | Semanal | Preço anômalo | v1 |
| F04 | ANP autuações | Público ⚠ | Irregular | Reincidência | v1 |
| F05 | Receita CNPJ | Público | Mensal | Grafo societário | v1 — **arquivar já** |
| F06 | Consumidor.gov/Procon | Público | Diária | Sinal precoce | v1 |
| F07 | IBGE | Público | Anual | Território | v1 |
| F08 | Normativo | Público | Diária | Vigências/RAG | v1 |
| F09 | IPEM | Convênio | — | Gabarito metrológico | 2 |
| F10 | SEFAZ NFC-e | Restrito | Contínua | Reconciliação fiscal | 3 |

---

## Adaptadores candidatos não autoritativos

Adaptadores não recebem identificador `Fxx` porque não são fontes de verdade. Eles
podem facilitar acesso ou transformação, mas cada fato continua vinculado à origem
primária.

| Adaptador | Estado | Uso permitido agora | Documento |
|---|---|---|---|
| MCP Fiscal Brasil | candidato para PoC | validação e parsing offline com fixtures sintéticas | [avaliação e controles](mcp-fiscal-adaptador-candidato.md) |

A inclusão nesta tabela não comprova implementação, autorização para dado fiscal,
homologação ou adequação para produção.
