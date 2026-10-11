# Ficha pública do posto — conteúdo e organização

> **Estado:** especificação de produto. Este documento descreve a experiência
> alvo; não afirma que todas as seções já estejam disponíveis no portal ou na
> API. O [status canônico](../status-projeto.md) continua sendo a fonte para
> distinguir desenho, implementação local e produção.

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

### 2. Resumo factual

Um resumo curto facilita a leitura, mas não produz nota composta. Ele pode
mostrar a data do último preço, do último resultado PMQC, do último ato oficial e
o frescor de cada fonte. A ausência de uma dimensão aparece como “sem dado
público vinculado no período”, nunca como zero, aprovação ou conformidade.

### 3. Qualidade do combustível — ANP/PMQC

Esta seção é obrigatória quando existir resultado PMQC reconciliado com o posto.
A fonte F02 não fornece identificador estável da amostra física. Por isso, a API
declara `identidade_agrupamento: derivada` e organiza os ensaios por uma chave
técnica composta do identificador do ponto publicado pela F02, data, produto e
coordenadas da coleta. Esse agrupamento organiza a leitura, mas não prova que
todos os ensaios vieram da mesma amostra física. A resposta contém um recorte
de até oito agrupamentos mais recentes: `limite` é `8` e `truncado` informa se
existem resultados adicionais, sem publicar total. Cada agrupamento mostra:

- data de coleta;
- produto e grupo de produto, quando publicados;
- contagem dos ensaios `conforme`, `não conforme` e `não classificado`, sem
  produzir nota ou classificação geral que a fonte não publicou;
- fonte oficial e data de referência;
- aviso de que a amostragem do PMQC é dirigida e não mede, sozinha, a
  prevalência de problemas no posto.

Cada ensaio deve aparecer em linha própria, com:

| Campo | Apresentação |
|---|---|
| Ensaio | Nome publicado pela ANP |
| Resultado | Valor/texto publicado pela fonte, sem reinterpretar |
| Unidade | Unidade publicada; “não informada” quando ausente |
| Classificação | `conforme`, `não conforme` ou `não classificado`, conforme a fonte |
| Referência | Data da coleta e identificação pública da fonte |

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
| Nenhum agrupamento PMQC vinculado | “Sem resultado público vinculado neste período” | “Qualidade aprovada” |
| Resultado vazio na fonte | “Resultado não informado pela fonte” | “Conforme” |
| Ensaio sem classificação | “Não classificado” | Inferir pelo texto livre |
| Fonte atrasada | Exibir competência/frescor e o atraso | Tratar o dado antigo como atual |
| Ligação de identidade pendente | Não publicar o fato na ficha | Associar por semelhança e ocultar a incerteza |
| Dado restrito | Manter fora da resposta pública | Exibir parcialmente ou pseudonimizado |
| Fato corrigido | Exibir a versão aplicável e indicar a retificação | Sobrescrever o passado em silêncio |
| Fato retirado por obrigação | Tombstone sem o conteúdo, inclusive em permalink histórico | Republicar sob pretexto de reprodutibilidade |

## Matriz de conteúdo

| Fonte/dimensão | Conteúdo público elegível | Organização na ficha | Estado do requisito |
|---|---|---|---|
| F01 — cadastro ANP | CNPJ PJ, bandeira, autorização, endereço e datas | Cadastro | Já existe parcialmente |
| F02 — PMQC | Agrupamento derivado, produto, ensaio, resultado, unidade e classificação triestado | Qualidade, por agrupamento e ensaio | Contrato e implementação local concluídos; revisão, CI, promoção e produção pendentes |
| F03 — preços ANP | Valor, unidade, produto, semana e cobertura regional | Preços e médias | Já existe parcialmente |
| GEO-ANP/GEO-01 | Posição oficial ou inferida, com origem | Mapa/localização | Já existe parcialmente |
| F04 — atos ANP | Processo, ato, situação e datas, se a granularidade pública permitir | Linha do tempo oficial | Pendente de fonte/contrato |
| Inmetro/IPEM | Resultado público de aferição, erro e situação, quando publicável | Metrologia | Depende de classificação da fonte |
| F06 — Procon/Sindec | Cobertura geral; contagem por posto somente após limiar/supressão aprovados | Contexto público | **NO-GO para contagem por posto** até gate de privacidade |
| Receita/CNPJ | Situação cadastral da PJ pertinente ao estabelecimento | Cadastro/contexto | Sem pessoa física ou QSA público na ficha |

## Dependências de implementação

O portal já exibe cadastro, histórico de preços e médias recentes. Em
2026-10-15, o primeiro bloco PMQC desta especificação foi concluído **apenas em
branches de integração coordenadas**:

- o contrato passou a exigir `qualidade_combustivel.identidade_agrupamento` e
  `agrupamentos`, com objetos fechados e classificação triestado;
- o core passou a produzir agrupamentos derivados completos, limitá-los sem
  remover `fatos_recentes` e sem expor sequência ou identificador interno;
- o portal ganhou seção por agrupamento/ensaio, estados vazio e legado, allowlist de
  hidratação e avisos metodológicos;
- as suítes locais de contrato, core e portal passaram.

Isso não prova disponibilidade remota ou produção. Para cumprir esta
especificação por inteiro ainda é necessário:

1. promover contrato, core e portal na ordem coordenada, com o core fixando o
   SHA do contrato e cada repositório passando pelo próprio CI;
2. executar smoke test da resposta e da ficha implantadas, inclusive payload de
   hidratação e viewport móvel;
3. definir paginação/limites para históricos extensos e preservar `as_of` em
   todas as consultas;
4. implementar as demais dimensões públicas elegíveis e seus gates, sem
   antecipar F06 por posto enquanto o NO-GO de privacidade estiver aberto.

A reconciliação segue o contrato de
[entity resolution](../dados/entity-resolution.md): fato pendente ou ligação
sem decisão não entra na ficha. A API não recebe liberdade para “tentar” ligar
por nome/endereço na leitura.

Para atos oficiais, F04 continua fora da ficha até o contrato enumerar ao menos
`coleta`, `autuacao`, `decisao`, `sancao`, `suspenso`, `em_recurso`, `anulado` e
`definitivo`, com a fonte autoritativa e as datas de fato e decisão. Não se
infere situação processual a partir de texto livre.

“Cobertura” é específica por dimensão: em preço regional, número de postos
distintos no mesmo produto/semana/território; em PMQC, número de agrupamentos
derivados e de ensaios, com intervalo coberto — nunca contagem afirmada de
amostras físicas; em fonte, competência e instante da última coleta. Percentual
populacional só aparece quando houver denominador documentado.

## Critérios de aceite

- [ ] preço não é a única dimensão factual da ficha;
- [ ] cada agrupamento PMQC derivado é reconhecível como unidade, sem afirmar
      que representa uma amostra física identificada pela fonte;
- [ ] cada ensaio mostra resultado, unidade e classificação exatamente como
      sustentado pela fonte;
- [ ] `true`, `false` e `null` de PMQC são testados separadamente; `null` nunca
      é serializado ou renderizado como conforme/não conforme;
- [ ] fixture com um único agrupamento contendo `true`, `false` e `null` exibe
      contagem `1/1/1`, não mistura outra chave derivada e não inventa
      classificação geral;
- [ ] nove agrupamentos completos devolvem os oito mais recentes e
      `truncado: true`; até oito devolvem `truncado: false`;
- [ ] ausência, atraso, não classificação e não conformidade são estados
      distintos;
- [ ] todo fato apresenta fonte e data; todo agregado apresenta cobertura;
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
