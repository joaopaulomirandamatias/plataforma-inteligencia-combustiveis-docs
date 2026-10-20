# Ficha pública do posto — conteúdo e organização

> **Estado:** especificação de produto com o contrato estruturado de qualidade
> em produção. A organização dos detalhes em cartões cronológicos, descrita
> abaixo, é a próxima iteração do portal e só deve ser tratada como ativa depois
> de validação e promoção registradas no
> [status canônico](../status-projeto.md). Este documento ainda contém dimensões
> alvo que não estão no portal ou na API.
>
> **Recorte observado em 2026-10-20:** a seção visual **Qualidade do
> combustível** e o payload estruturado estão em produção. A ficha
> `00097ff8-98c0-5d16-823e-66edb77c334c` foi observada com 6 agrupamentos e 48
> ensaios reais, incluindo data, fonte, resultado, unidade e classificação. A
> ficha `304d2b1e-e655-5f50-8db9-b8445179ce25` retornou agrupamentos vazios em
> produção, embora 72 linhas PMQC tenham sido localizadas na competência
> `2026-05` publicada pela fonte. Essa competência ainda não havia sido carregada
> após a entrega da F02 mudar de CSV direto para ZIP e o backfill permanecer
> pendente. Portanto, esse vazio é uma lacuna de cobertura, não evidência de
> inexistência de ensaios na fonte.

## Objetivo

A ficha pública reúne, de forma legível e rastreável, os fatos públicos ligados
ao mesmo `posto_id`. Preço é somente uma das dimensões. Cadastro, qualidade do
combustível, resultados de ensaios, atos oficiais, contexto público e cobertura
das fontes devem aparecer organizados, com data, origem e limites de
interpretação.

A ficha não atribui reputação, culpa, intenção ou uma nota pública de risco. Ela
reproduz fatos oficiais e explica o que eles significam — e o que não
significam.

## Regra para entrada de dados públicos

Um campo ou fato entra na ficha apenas quando satisfaz todos estes critérios:

1. a fonte é pública e oficial, e sua possibilidade de republicação foi
   verificada;
2. o dado é pertinente ao estabelecimento e foi reconciliado com o `posto_id`;
3. a validade do fato e o instante em que a plataforma o conheceu estão
   preservados;
4. a apresentação informa fonte, data de referência e cobertura;
5. o dado não expõe pessoa física, segredo, atributo interno, texto livre de
   consumidor ou informação reservada a órgão;
6. a redação respeita a
   [política de linguagem](../agentes/politica-de-linguagem.md).

A autorização para republicar precisa estar registrada no
[catálogo de fontes](../dados/catalogo-fontes.md), com responsável, evidência e
data da última verificação. Fonte com licença, termos ou classificação incertos
fica fora da ficha até nova decisão documentada.

Ser público na origem não basta, por si só, para republicação na ficha. Dados
de sócios pessoas físicas, CPF ainda que mascarado, contatos pessoais,
identificadores internos, localização de arquivo e score de fiscalização ficam
fora da borda pública. Score e ranking continuam restritos por
[ADR-005](../arquitetura/adr/adr-005-score-restrito-a-orgaos.md).

## Arquitetura da informação

A página deve funcionar em tela ampla, celular, zoom de 200% e navegação por
teclado. As seções seguem uma ordem estável; dentro delas, fatos são agrupados
por assunto e ordenados do mais recente para o mais antigo.

### 1. Identificação e recorte temporal

O cabeçalho apresenta:

- nome/razão social publicada, CNPJ de pessoa jurídica, bandeira e endereço;
- situação cadastral e início de validade do cadastro exibido;
- data de corte (`as_of`) e versão do estado consultado;
- indicação inequívoca de “visão atual” ou “visão histórica”;
- link permanente que reproduz exatamente o mesmo recorte temporal.

Na ficha pontual, o mesmo instante `T = as_of` corta as duas dimensões: a base
já precisava conhecer a versão (`transacao @> T`) e o cadastro exibido precisava
estar vigente (`validade @> T`). Os fatos históricos da ficha precisam ter sido
conhecidos em `T` e ter validade iniciada até `T`; nada aprendido depois pode
vazar para a visão antiga. Todas as seções recebem exatamente o mesmo `T`.

`as_of` é RFC 3339 com offset explícito. A API normaliza o instante para UTC; o
portal preserva e propaga sem recalcular a representação canônica devolvida na
resposta. Intervalos seguem `[início, fim)`: versão que começa exatamente em `T`
entra; versão cujo fim é exatamente `T` não entra. Instantes equivalentes com
offsets diferentes precisam produzir o mesmo estado e a mesma URL canônica.

### 2. Resumo factual superior

Um resumo curto facilita a leitura, mas não produz nota composta. Para PMQC,
ele apresenta apenas fatos calculados sobre o payload exibido: quantidade de
agrupamentos derivados, ensaios e produtos, período observado, contagens
separadas de `conforme`, `não conforme` e `não classificado`, além de limite e
estado de truncamento. Os ensaios individuais ficam na linha do tempo; não são
duplicados no resumo.

O resumo também pode mostrar a data do último preço, do último resultado PMQC,
do último ato oficial e o frescor de cada fonte. A ausência de uma dimensão
aparece como “sem dado público vinculado no período”, nunca como zero,
aprovação ou conformidade.

### 3. Qualidade do combustível — ANP/PMQC

O bloco superior de qualidade aparece mesmo quando não há agrupamento, pois é
ele que comunica o estado do recorte de maneira honesta. A fonte F02 não
fornece identificador estável da amostra física. Por isso, a API declara
`identidade_agrupamento: derivada` e organiza os ensaios por uma chave técnica
composta do identificador do ponto publicado pela F02, data, produto e
coordenadas da coleta. Esse agrupamento organiza a leitura, mas não prova que
todos os ensaios vieram da mesma amostra física. A resposta contém um recorte
de até oito agrupamentos mais recentes: `limite` é `8` e `truncado` informa se
existem resultados adicionais, sem publicar total.

#### Cartões cronológicos no histórico oficial

Cada agrupamento derivado vira **um cartão** na linha do tempo **Histórico
oficial**, intercalado com preços e os demais fatos públicos pela data de
referência. Não se cria um cartão por ensaio e não se reúne agrupamentos de
datas diferentes. O cartão mostra, sem exigir expansão:

- data de coleta;
- produto e grupo de produto, quando publicados;
- contagem dos ensaios `conforme`, `não conforme` e `não classificado`, sem
  produzir nota ou classificação geral que a fonte não publicou;
- fonte oficial e data de referência;
- aviso de que a amostragem do PMQC é dirigida e não mede, sozinha, a
  prevalência de problemas no posto.

Os ensaios ficam em um controle de divulgação (*disclosure*) dentro do cartão,
para manter a cronologia escaneável sem esconder o detalhe. O controle é
operável por teclado, anuncia seu estado expandido/recolhido e não depende
somente de cor ou de ícone. Cada ensaio aparece em linha própria, com:

| Campo | Apresentação |
|---|---|
| Ensaio | Nome publicado pela ANP |
| Resultado | Valor/texto publicado pela fonte, sem reinterpretar |
| Unidade | Unidade publicada; “não informada” quando ausente |
| Classificação | `conforme`, `não conforme` ou `não classificado`, conforme a fonte |
| Referência | Data da coleta e identificação pública da fonte, ainda que coincidam com a procedência do agrupamento |

Fonte e data aparecem em dois níveis deliberadamente: no cartão, para dar
procedência ao agrupamento ainda recolhido; em cada ensaio, para que o detalhe
continue autocontido quando lido isoladamente por tecnologia assistiva ou
extraído para outra apresentação.

Quando a fonte vier a publicar valor medido, limite ou faixa normativa de forma
estruturada, a ficha pode acrescentar **valor medido**, **limite/faixa** e
**norma vigente na data**, sem calcular retroativamente um limite não fornecido.
Até lá, a interface mostra somente os campos efetivamente publicados e
preservados (`ensaio`, `resultado`, `unidade` e `conforme`).

O contrato estruturado usa `conforme: boolean | null`, com mapeamento fechado:
`true` → `conforme`, `false` → `não conforme`, `null` → `não classificado`.
Coerção por valor truthy/falsy é proibida. A classificação geral de um agrupamento
só pode aparecer se a própria fonte a publicar e o contrato preservar esse
campo separadamente.

#### Indicadores factuais do recorte

No bloco superior, a seção apresenta uma faixa compacta intitulada
**Indicadores factuais do recorte**. A faixa resume somente os agrupamentos
presentes em `qualidade_combustivel.agrupamentos` na resposta corrente; ela não
consulta outro período, não completa o recorte por inferência e não substitui a
leitura dos ensaios nos cartões cronológicos.

| Indicador | Cálculo e apresentação |
|---|---|
| Agrupamentos exibidos | Quantidade de objetos em `agrupamentos`. A unidade continua sendo o agrupamento derivado, não uma amostra física identificada. |
| Ensaios exibidos | Soma da quantidade de objetos em `agrupamento.ensaios`. É contagem de linhas de ensaio no recorte, não quantidade de abastecimentos ou de amostras físicas. |
| Produtos no recorte | Quantidade de rótulos públicos canônicos distintos entre os agrupamentos exibidos. O portal aplica somente a tabela versionada de equivalências de apresentação (por exemplo, caixa e aliases textuais do mesmo combustível), preserva o valor original nos dados de origem e não usa `grupo_produto` para criar produto adicional. Agrupamentos que chegam ao mesmo rótulo canônico são reunidos na mesma seção. |
| Período observado | Menor e maior `data_coleta` entre os agrupamentos exibidos. Uma única data aparece uma vez; lista vazia não produz período. |
| Resultados por classificação | Recontagem dos objetos em `agrupamento.ensaios` pelos valores `conforme: true`, `false` e `null`, em três números separados. As contagens agregadas recebidas no agrupamento não são a fonte desse resumo; assim, a faixa permanece coerente com os ensaios realmente exibidos e a soma coincide com **Ensaios exibidos**. |
| Cobertura do recorte | `truncado: false` → “recorte exibido sem truncamento”; `truncado: true` → “há agrupamentos mais antigos fora deste recorte exibido”, acompanhado do `limite` recebido. Não se publica total nem “X de Y”. |

Esses números são contagens descritivas do payload exibido. **Não são nota,
taxa, índice de desempenho, score, ranking ou classificação do posto.** Também
não calculam percentual de conformidade/não conformidade: a coleta do PMQC é
dirigida, o recorte pode estar truncado e a fonte não sustenta esse denominador
como estimativa do estabelecimento.

Quando `agrupamentos` estiver vazio, a faixa dá lugar ao estado neutro “Sem
resultado público vinculado neste período”. Ela não mostra `0%`, não cria um
período e não traduz ausência como aprovação. Quando `truncado` for verdadeiro,
o aviso acompanha as contagens e o período; todos os valores continuam
qualificados como **exibidos neste recorte**, nunca como totais históricos.

Regras de linguagem:

- “ensaio com resultado não conforme” é permitido quando reproduz a fonte;
- “posto não conforme”, “combustível adulterado” ou equivalentes são
  proibidos sem ato oficial que sustente exatamente essa afirmação;
- não haver agrupamento no período não significa que o posto foi aprovado;
- resultado conforme numa coleta não garante qualidade futura ou de todo o
  estoque.

### 4. Preços e contexto regional

Os preços permanecem agrupados por data/semana e produto. Cada observação
mostra valor, unidade, fonte e data da pesquisa. Médias do município e da UF
ficam ao lado do mesmo produto e da mesma semana, sempre com o número de postos
que sustenta o agregado. Preço ausente não vira zero, e a ficha não se apresenta
como comparador de preços.

### 5. Cadastro e localização

Cadastro mostra somente atributos públicos da pessoa jurídica e da autorização
do estabelecimento. O mapa usa a posição com a precedência metodológica
documentada; coordenada inferida do endereço é identificada como tal e não é
apresentada como ponto oficial.

### 6. Fiscalizações, aferições e atos oficiais

Autuações, sanções, verificações metrológicas e aferições entram apenas quando
o registro for público, possuir granularidade suficiente para o posto e puder
ser exibido com sua situação processual. A interface distingue coleta,
autuação, decisão e sanção; ato ainda sujeito a recurso não é apresentado como
decisão definitiva.

Dados obtidos por convênio e classificados para uso restrito permanecem no
painel do órgão. A existência de uma fonte institucional não autoriza sua
publicação automática.

### 7. Outros contextos públicos

Atendimentos de consumidor, quando vinculados por CNPJ exato, podem aparecer
como contexto estatístico oficial. Não entram texto livre, sexo, faixa etária,
CEP ou qualquer atributo do consumidor. Categorias da fonte passam pela
política de linguagem e não se tornam prova de responsabilidade do posto.

Contagens por categoria permanecem fora da borda pública até produto, jurídico
e DPO aprovarem um limiar mínimo de célula, a supressão de cruzamentos raros e
testes contra reidentificação. Enquanto esse gate estiver aberto, a ficha pode
informar apenas que a fonte existe e sua cobertura geral, sem número por posto.

Vínculo societário com pessoa física, score de risco, ranking de fiscalização,
hipóteses dos agentes e evidências ainda não publicadas pelo órgão nunca
aparecem nesta ficha.

### 8. Fontes, frescor e metodologia

A ficha encerra com um painel de transparência contendo:

- fonte de cada seção e data da coleta mais recente;
- URL pública do conjunto, versão/competência e data de publicação, quando a
  fonte as fornecer;
- período efetivamente coberto;
- aviso de atraso conhecido ou indisponibilidade da fonte;
- link para metodologia, catálogo de fontes e significado de cada estado;
- versão do recorte e forma de reproduzi-lo.

Frescor da ingestão e data do fato são conceitos diferentes e devem ser
rotulados separadamente.

Dentro de cada seção, a ordenação usa a data de validade do fato. Quando o
schema publicar uma chave estável, ela decide empates. Nos agrupamentos PMQC, a
chave derivada é deliberadamente interna; o servidor garante desempate técnico
determinístico sem expô-la nem alegar identidade física. Data de ingestão não
decide a ordem visual: ela fica no painel de transparência para explicar quando
a plataforma conheceu o fato.

## Correção, retirada e direito de resposta

Correção ordinária fecha a versão anterior na dimensão de transação e cria uma
nova versão. A visão corrente exibe a correção e identifica a data da
retificação. Uma visão histórica mantém seu **payload factual congelado em
`T`**. Aviso de correção, retirada ou direito de resposta publicado depois de
`T` aparece numa camada separada, identificada como “informação posterior ao
recorte”; o conteúdo novo não é inserido retroativamente na lista factual do
snapshot antigo.

Retirada legal, mudança para classificação restrita ou publicação indevida
prevalece sobre a reprodutibilidade histórica: o conteúdo deixa de ser servido
também em permalinks antigos e dá lugar a um tombstone factual, sem repetir o
dado retirado. A decisão, fundamento, alcance e data ficam na trilha de
auditoria. Direito de resposta integra o snapshot se já existia em `T`; quando
posterior, aparece somente na camada atual pós-recorte, sem reescrever o payload
histórico.

## Estados de ausência e incerteza

| Situação | Texto esperado | Texto proibido |
|---|---|---|
| `qualidade_combustivel.agrupamentos` presente e vazio, com cobertura conhecida | “Sem resultado público vinculado neste período” | “Qualidade aprovada” ou “o posto não possui testes” |
| Campo estruturado ausente ou `null` numa resposta legada | Estado de compatibilidade: dados estruturados de qualidade indisponíveis nesta versão da resposta | Converter a ausência do campo em lista vazia ou afirmar que a fonte não tem resultado |
| Competência da fonte não ingerida ou backfill pendente | Informar a competência/frescor conhecido e a lacuna de cobertura | Tratar o payload vazio como retrato completo da fonte |
| Resultado vazio na fonte | “Resultado não informado pela fonte” | “Conforme” |
| Ensaio sem classificação | “Não classificado” | Inferir pelo texto livre |
| Fonte atrasada | Exibir competência/frescor e o atraso | Tratar o dado antigo como atual |
| Ligação de identidade pendente | Não publicar o fato na ficha | Associar por semelhança e ocultar a incerteza |
| Dado restrito | Manter fora da resposta pública | Exibir parcialmente ou pseudonimizado |
| Fato corrigido | Exibir a versão aplicável e indicar a retificação | Sobrescrever o passado em silêncio |
| Fato retirado por obrigação | Tombstone sem o conteúdo, inclusive em permalink histórico | Republicar sob pretexto de reprodutibilidade |

Esses estados não são intercambiáveis. A lista estruturada vazia descreve o
que a API conseguiu vincular **no recorte servido**. Campo ausente ou `null`
indica fallback de uma versão legada do contrato. Competência não ingerida é
uma lacuna operacional entre fonte e snapshot. Somente uma verificação da
cobertura permite afirmar qual dos três casos se aplica; nenhum deles autoriza
inferir aprovação, reprovação ou inexistência de coleta.

Em 2026-10-20, o posto
`304d2b1e-e655-5f50-8db9-b8445179ce25` demonstrou essa diferença: o payload de
produção trouxe `agrupamentos: []`, mas a competência `2026-05` da fonte continha
72 linhas PMQC associáveis ao estabelecimento. A publicação havia mudado de
CSV direto para ZIP e essa competência ainda não tinha sido retrocarregada.
Até o conector aceitar a nova embalagem e o backfill ser validado, a ficha deve
identificar o vazio como cobertura incompleta, não como ausência na fonte.

## Matriz de conteúdo

| Fonte/dimensão | Conteúdo público elegível | Organização na ficha | Estado do requisito |
|---|---|---|---|
| F01 — cadastro ANP | CNPJ PJ, bandeira, autorização, endereço e datas | Cadastro | Já existe parcialmente |
| F02 — PMQC | Agrupamento derivado, produto, ensaio, resultado, unidade e classificação triestado | Resumo factual superior; um cartão por agrupamento no histórico oficial; ensaios em disclosure | Contrato/core e primeiro bloco visual **em produção**; organização cronológica em validação antes da promoção |
| F03 — preços ANP | Valor, unidade, produto, semana e cobertura regional | Preços e médias | Já existe parcialmente |
| GEO-ANP/GEO-01 | Posição oficial ou inferida, com origem | Mapa/localização | Já existe parcialmente |
| F04 — atos ANP | Processo, ato, situação e datas, se a granularidade pública permitir | Linha do tempo oficial | Sem contrato público aprovado; não exibir |
| Inmetro/IPEM | Resultado público de aferição, erro e situação, quando publicável | Metrologia | Sem contrato público e dependente de classificação/convênio; não exibir |
| F06 — Procon/Sindec | Cobertura geral; contagem por posto somente após limiar/supressão aprovados | Contexto público | **NO-GO para contagem por posto** até gate de privacidade |
| Receita/CNPJ | Situação cadastral da PJ pertinente ao estabelecimento | Cadastro/contexto | Sem pessoa física ou QSA público na ficha |

## Dependências de implementação

O portal já exibe cadastro, histórico de preços e médias recentes. Em
2026-10-15, o primeiro bloco PMQC desta especificação foi concluído em branches
de integração coordenadas:

- o contrato passou a exigir `qualidade_combustivel.identidade_agrupamento` e
  `agrupamentos`, com objetos fechados e classificação triestado;
- o core passou a produzir agrupamentos derivados completos, limitá-los sem
  remover `fatos_recentes` e sem expor sequência ou identificador interno;
- o portal ganhou seção por agrupamento/ensaio, estados vazio e legado, allowlist de
  hidratação e avisos metodológicos;
- as suítes locais de contrato, core e portal passaram.

A iteração seguinte separa a faixa factual do detalhe: mantém as contagens no
topo e move cada agrupamento derivado para um cartão cronológico no Histórico
oficial, com os ensaios em disclosure. Até haver evidência de testes, merge,
deploy e smoke dessa iteração, a descrição acima é especificação de produto,
não afirmação sobre o HTML servido em produção.

Em 2026-10-19, a camada do portal foi promovida primeiro. Os PRs #35/#36 foram
mesclados, `main` e `deploy` ficaram em
`d9b93a36e5f0afb1b2f2eb43a274b3496e577bc9`, o pipeline Woodpecker #47 passou em
CI e promoção e o deployment Railway
`c8513d09-6802-440a-bee7-a31368e2fd74` terminou com `SUCCESS`. O smoke retornou
`HTTP 200` e confirmou visualmente a ficha
`304d2b1e-e655-5f50-8db9-b8445179ce25` no estado legado neutro.

Depois, o PR #72 do núcleo isolou o bloco PMQC das migrações GEO bloqueadas,
passou pelos pipelines Woodpecker #10 e #11 e promoveu `main`/`deploy` para
`8f46c869bcd956dab30ec903d24da8cbfddfebb3`. O Migrator Railway
`11efd3fe-c865-4ed6-a921-3c4e1bba2f1e` confirmou 22 migrações aplicadas e nada
pendente; a API `33982e35-b1ec-4344-b5af-c1a2cb547903` terminou com `SUCCESS`.
O smoke da ficha `00097ff8-98c0-5d16-823e-66edb77c334c` confirmou 6 agrupamentos
e 48 ensaios e a interface exibiu contagens triestado, resultado, unidade,
fonte e data sem erros no console.

Para cumprir esta especificação por inteiro ainda é necessário:

1. adaptar e provar a ingestão F02 para a entrega ZIP e executar backfill
   controlado da competência `2026-05`, reconciliando as 72 linhas do posto
   `304d2b1e-e655-5f50-8db9-b8445179ce25` sem duplicar fatos;
2. remover o NO-GO de backup/PITR do núcleo e executar com segurança a sequência
   das migrações 023/024 do PR #70;
3. ampliar o smoke automatizado do bloco PMQC para payload de hidratação,
   viewport móvel, zoom e leitor de tela;
4. definir paginação/limites para históricos extensos e preservar `as_of` em
   todas as consultas;
5. implementar as demais dimensões públicas elegíveis e seus gates, sem
   antecipar F06 por posto enquanto o NO-GO de privacidade estiver aberto.

A reconciliação segue o contrato de
[entity resolution](../dados/entity-resolution.md): fato pendente ou ligação
sem decisão não entra na ficha. A API não recebe liberdade para “tentar” ligar
por nome/endereço na leitura.

Para atos oficiais, F04 continua fora da ficha até o contrato enumerar ao menos
`coleta`, `autuacao`, `decisao`, `sancao`, `suspenso`, `em_recurso`, `anulado` e
`definitivo`, com a fonte autoritativa e as datas de fato e decisão. Não se
infere situação processual a partir de texto livre.

Todo fato novo entra por **allowlist de apresentação e contrato público
fechado**. Acrescentar um campo no banco, na API interna ou numa fonte não o
torna publicável automaticamente. F04 e IPEM permanecem fora da ficha enquanto
não houver contrato e decisão de publicação; F06 continua bloqueada pelo gate
de privacidade. O fallback legado aceita respostas anteriores sem quebrar a
página, mas não promove campos desconhecidos nem fabrica a semântica do estado
estruturado.

“Cobertura” é específica por dimensão: em preço regional, número de postos
distintos no mesmo produto/semana/território; em PMQC, número de agrupamentos
derivados e de ensaios, com intervalo coberto — nunca contagem afirmada de
amostras físicas; em fonte, competência e instante da última coleta. Percentual
populacional só aparece quando houver denominador documentado.

## Critérios de aceite

- [x] preço não é a única dimensão factual da ficha;
- [x] cada agrupamento PMQC derivado é reconhecível como unidade, sem afirmar
      que representa uma amostra física identificada pela fonte;
- [x] cada ensaio mostra resultado, unidade e classificação exatamente como
      sustentado pela fonte;
- [x] `true`, `false` e `null` de PMQC são testados separadamente; `null` nunca
      é serializado ou renderizado como conforme/não conforme;
- [x] fixture com um único agrupamento contendo `true`, `false` e `null` exibe
      contagem `1/1/1`, não mistura outra chave derivada e não inventa
      classificação geral;
- [x] nove agrupamentos completos devolvem os oito mais recentes e
      `truncado: true`; até oito devolvem `truncado: false`;
- [x] ausência, não classificação e não conformidade são estados distintos;
- [ ] atraso/frescor possui estado e limiar documentados, separados da data do
      ensaio e da ausência de resultado;
- [x] todo ensaio PMQC apresenta fonte e data; cada agrupamento apresenta suas
      contagens e o recorte declara limite/truncamento;
- [x] a faixa **Indicadores factuais do recorte** deriva agrupamentos, ensaios,
      produtos, período e triestado somente dos agrupamentos exibidos;
- [x] `truncado: true` mantém todas as contagens qualificadas como recorte,
      informa que há agrupamentos adicionais e não inventa total ou “X de Y”;
- [x] testes de conteúdo e de interface provam que a faixa não publica
      percentual, nota, taxa, índice de desempenho, score, ranking ou
      classificação do posto;
- [ ] o portal promovido mantém somente o resumo factual no bloco superior e
      apresenta exatamente um cartão cronológico por agrupamento derivado;
- [ ] cada cartão traz data/fonte e contagens triestado antes da expansão, e
      cada ensaio repete data/fonte dentro de disclosure acessível;
- [ ] os testes distinguem lista vazia, resposta legada sem o campo e
      competência conhecida ainda não ingerida;
- [ ] a visão histórica usa o mesmo `as_of` em todas as seções e possui link
      permanente;
- [ ] teste bitemporal prova que fato aprendido após `as_of` não aparece e que
      fato corrigido aparece somente no recorte aplicável;
- [ ] testes de fronteira provam `[início, fim)`, inclusive versão iniciada em
      `T`, versão encerrada em `T` e equivalência de offsets RFC 3339;
- [ ] correção e direito de resposta posteriores a `T` aparecem somente como
      camada pós-recorte, sem alterar o payload factual congelado;
- [ ] nenhum score/ranking restrito, dado pessoal, localizador interno ou texto
      livre de consumidor alcança HTML, JSON público ou hidratação;
- [ ] enquanto o gate de privacidade do F06 estiver aberto, nenhuma contagem
      total ou por categoria vinculada ao posto alcança HTML, JSON público ou
      hidratação ou metadados públicos;
- [ ] retirada legal substitui o conteúdo por tombstone em visão atual e
      permalink histórico, invalida cache/CDN e não deixa o dado retirado em
      HTML, JSON, hidratação ou metadados públicos;
- [ ] teclado percorre todos os controles em ordem, foco nunca fica oculto,
      zoom 200% e viewport de 320 px não criam rolagem horizontal no conteúdo,
      e axe não acusa violações WCAG A/AA aplicáveis em navegador real;
- [ ] leitura manual com um leitor de tela suportado, versão e sistema
      registrados, confirma títulos, tabelas, estados e fonte/data sem perda de
      significado;
- [ ] testes negativos provam que dado interno ou campo novo da API não entra
      automaticamente na ficha;
- [ ] a documentação e a interface deixam explícito que PMQC é amostragem
      dirigida, que a identidade do agrupamento é derivada e que ausência de
      resultado não equivale a aprovação.

Aqui, **amostragem dirigida** significa que a seleção das coletas segue o plano
operacional do programa, sua cobertura e seus critérios de monitoramento; não é
uma amostra probabilística aleatória de todos os abastecimentos do posto. Por
isso a taxa observada nas amostras não estima automaticamente a prevalência no
estabelecimento.
