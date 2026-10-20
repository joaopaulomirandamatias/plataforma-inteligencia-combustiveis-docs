# F1-09 — Pipeline executável de candidatos de Entity Resolution

> **Status do `f1-09-f02-contexto-v1`: implementação experimental concluída,
> ainda bloqueada para produção.** Os gates estruturais de lote homogêneo,
> execução obrigatoriamente sem modelo, proveniência GEO e semântica temporal
> estão cobertos no contrato e em testes. O único gate operacional restante é o
> dry-run integral das 801 pendências, com revisão do relatório. Portanto, isto
> ainda não autoriza execução produtiva.

## Objetivo

Fechar a lacuna entre os componentes já implementados da F1 e a fila auditável de revisão:

```text
representação normalizada
        ↓
blocking mensurável
        ↓
vetor de similaridade
        ↓
Fellegi–Sunter opcional
        ↓
fila candidato_ligacao
        ↓
revisão F1-08
```

O pipeline **termina na fila**. Ele não contém threshold, auto-match, auto-reject, merge de cluster, alteração de `posto_id` ou remapeamento de fatos.

## Escala de pontuação

A F1-01 original criou `score` limitado a `[0,1]`. Isso não comporta o peso Fellegi–Sunter `log2(m/u)`. A decisão normativa está no ADR-009.

A migração 013, em validação, preserva o legado e adiciona:

- `pontuacao_escala`;
- `pontuacao_valor`;
- `calibracao_id`.

Escalas:

- `legado_score_01`;
- `similaridade_01`;
- `peso_log2`;
- `probabilidade_01`;
- `sem_modelo`.

`probabilidade_01` exige `calibracao_id` no domínio e no PostgreSQL. Peso log₂ nunca sofre sigmoid/min-max implícito para parecer probabilidade.

## Envelope de entrada

`RepresentacaoIdentidade` contém apenas a projeção comparável. Para revisão humana isso não basta, pois a evidência precisa ser citável.

A F1-09 usa `RegistroComparavel`:

- `representacao`: projeção F1-02;
- `localizador`: origem factual verificável;
- `campos_revisao`: valores factuais que podem ser exibidos posteriormente.
- `pontos_geograficos`: zero ou mais pontos com latitude, longitude, tipo de
  evidência, fonte, localizador, SHA-256 e datas semanticamente separadas;
- datas de contexto: observação, início da validade cadastral, vinculação
  publicada e criação do alias, quando existirem.

Localizador é obrigatório. O pipeline não fabrica proveniência.

## Envelope de evidências

Novos candidatos F1-09 gravam JSON versionado com cinco blocos comuns:

1. `normalizacao` — versão de normalização de cada lado;
2. `blocking` — motivos pelos quais o par foi comparado;
3. `similaridade` — vetor e estados discretizados;
4. `pontuacao` — escala, valor, versão do modelo e contribuições quando houver;
5. `revisao` — campos factuais com fonte e localizador de A/B.

O contrato-base continua sendo:

```text
metodo         = blocking-similaridade-f1-09
schema_versao  = f1-09-v1
```

O experimento exclusivo `F01↔F02` adiciona, sem substituir o contrato-base:

```text
metodo         = blocking-similaridade-f1-09-f02-contexto-v1
schema_versao  = f1-09-f02-contexto-v1
contexto_f02   = contexto-f02-v1
```

O par de fontes escolhe o contrato. Somente o conjunto exato `{F01, F02}` usa
o envelope contextual. `F01↔F03` permanece em `f1-09-v1`; candidatos antigos,
inclusive os de F03, não são reescritos nem reinterpretados. Se o mesmo par
F01/F02 já tiver um candidato legado, o candidato contextual pode coexistir
com ele sob método e schema próprios. Essa evolução é append-only.

Esse envelope é **interno**. Score/peso, motivo de blocking e estratos não devem ser enviados automaticamente ao revisor. O ADR-010 determina que estratos de amostragem ficam fora do pacote cego `f1-08a-v2`.

## Modo sem modelo

Sem parâmetros Fellegi–Sunter validados, o pipeline ainda pode produzir pares auditáveis:

```text
pontuacao_escala = sem_modelo
pontuacao_valor  = NULL
```

Isso permite construir a primeira amostra humana sem inventar parâmetros `m/u` ou probabilidade.

## Modo Fellegi–Sunter

Quando um `ModeloFellegiSunter` explicitamente versionado é fornecido:

```text
pontuacao_escala = peso_log2
pontuacao_valor  = soma log2(m/u)
```

As contribuições por campo/estado ficam no envelope interno. Parâmetro ausente faz a execução falhar antes do INSERT.

## Integração com F02/F03

### Contrato contextual experimental F01↔F02

O `f1-09-f02-contexto-v1` existe para entregar ao revisor os fatos que ajudam a
avaliar uma possível continuidade do ponto físico sem transformar proximidade
em identidade. O envelope preserva toda evidência disponível no corte.

#### Evidência geoespacial

F01 consulta **todos** os fatos geográficos encontrados e válidos nos cortes
`validade_em` e `transacao_em`, ligados ao fato cadastral comparado. Cada ponto
preserva:

- latitude e longitude;
- `tipo_evidencia`;
- fonte do fato geográfico;
- localizador do resultado bruto e localizador do vínculo factual;
- `hash_conteudo`, lido de `cache_geocodificacao.resultado_sha256`;
- `validade_inicio`, início da validade bitemporal do fato geográfico;
- `coletado_em`, data em que o resultado entrou no cache;
- `observado_em`, somente quando a fonte declara uma data de obtenção.

As três datas não são intercambiáveis. Para GEO-ANP, `observado_em` vem de
`metadados.data_obtencao`; para GEO-01 fica `null`, porque a geocodificação não
declara quando a posição existia no mundo. O início de validade e a coleta
continuam disponíveis em seus campos próprios, sem serem promovidos a data de
observação.

Para F02, a coordenada publicada pelo PMQC vira um ponto
`tipo_evidencia = posicao_pmqc`, com fonte F02, localizador e SHA-256 da linha
na zona bruta, `coletado_em` do depósito e `observado_em` igual à data de
coleta declarada pelo PMQC. `validade_inicio` não é inventada.

O ponto só existe quando latitude e longitude estão presentes, são numéricas e
caem no domínio geográfico. Caso contrário, a observação continua candidata,
mas a evidência F02 fica `status = ausente`, sem coordenada sintética, e registra
uma razão explícita:

- `f02_coordenada_ausente_ou_invalida`; ou
- `f02_coordenada_fora_do_dominio`.

O bloco `contexto_f02.geoespacial` registra contagens de pontos F01/F02, o
produto cartesiano de comparações e, para cada combinação, ambos os pontos
completos e a distância Haversine em metros, arredondada a 0,001 m. Nenhum
ponto é descartado para conservar apenas o “mais próximo”.

Fonte, localizador e hash de cada ponto GEO atravessam o envelope contextual e
o F1-12 v2. O manifesto precisa declarar cada par `fonte + hash_conteudo` usado;
o localizador GEO precisa conter um SHA-256 completo e igual ao
`hash_conteudo` do ponto. O artefato registra a tripla completa em
`proveniencias_usadas`, exige igualdade entre os snapshots GEO declarados e os
efetivamente usados e inclui o digest canônico do envelope em
`populacao_sha256`.

As razões de cobertura são explícitas:

- `f01_sem_evidencia_geografica_no_corte`;
- `f02_coordenada_ausente_ou_invalida` ou
  `f02_coordenada_fora_do_dominio` na releitura F02;
- `f02_sem_coordenada_publicada` como fallback fechado para um registro F02
  sem ponto nem razão mais específica;
- `distancia_geografica_calculada`, quando há ao menos uma comparação.

Ausência de ponto produz cobertura zero e razão de ausência; nunca distância
zero, localização inferida ou reprovação implícita.

#### Evidência temporal

O bloco `contexto_f02.temporal` preserva, quando disponíveis:

- data de coleta F02;
- início da validade do cadastro F01;
- data de vinculação publicada no cadastro F01;
- data em que o alias F01 foi registrado na plataforma;
- dias entre a coleta F02 e o início da validade F01;
- dias entre a coleta F02 e a data de vinculação F01.

Além dos valores, o envelope registra cobertura booleana e razões legíveis por
máquina. O vocabulário completo desta versão é:

- `f02_sem_data_coleta` / `data_coleta_f02_disponivel`;
- `f01_sem_inicio_validade_cadastral` /
  `inicio_validade_cadastral_f01_disponivel`;
- `f01_sem_data_vinculacao_publicada` /
  `data_vinculacao_f01_disponivel`;
- `f01_sem_data_registro_alias` / `data_registro_alias_f01_disponivel`;
- `coleta_f02_no_ou_apos_inicio_validade_f01` /
  `coleta_f02_anterior_ao_inicio_validade_f01`;
- `coleta_f02_no_ou_apos_vinculacao_f01` /
  `coleta_f02_anterior_a_vinculacao_f01`.

Os intervalos em dias só existem quando os dois extremos existem. Data ausente
permanece `null` e recebe razão própria; não é imputada.

#### Blindagem da revisão humana

O experimento F02 roda sem modelo: `pontuacao_escala = sem_modelo`,
`pontuacao_valor = NULL` e versão `f1-09-f02-contexto-v1-sem-modelo`. O motor
genérico F1-09 pode receber modelo em outros contratos, mas o caminho
F01↔F02 — inclusive a preparação F1-12 — rejeita modelo explícito antes de
gerar ou persistir candidatos.

Os campos contextuais são copiados para `revisao.campos` com as fontes e os
localizadores de ambos os lados, para atravessarem a ponte F1-10. O revisor não
recebe score, faixa, threshold, contribuição do modelo, destino sugerido ou
autoaceite. A política gravada no contexto é
`somente_revisao_humana_sem_autoaceite`.

O pipeline pode apenas acrescentar um `candidato_ligacao` auditável. Ele não
cria ou altera `posto`, alias, fato, `decisao_ligacao`, cluster ou vínculo
temporal. Qualquer decisão humana posterior pertence a outro fluxo e deixa sua
própria trilha.

### Por que reler a zona bruta

F02 e F03 armazenam em `ingestao.pendencia_vinculo` apenas a chave tentada, motivo, contagem e um localizador de exemplo. Isso é suficiente para operar o vínculo determinístico, mas não preserva no registro agregado todos os campos de nome/endereço necessários para Entity Resolution.

Os bytes originais permanecem na zona bruta imutável. A F1-09 usa essa fonte como evidência, sem alterar os fatos F02/F03.

### Recorte inicial

A implementação em validação aceita somente:

```text
motivo = cnpj_sem_posto
fonte ∈ {F02, F03}
```

O fluxo recebe um `carga_id` explícito:

1. lê `ingestao.carga`;
2. seleciona as chaves `cnpj_sem_posto` da mesma carga;
3. abre `caminho_bruto`;
4. confere manifesto e SHA-256;
5. usa o **parser original do conector** para determinar quais linhas eram válidas;
6. relê somente essas linhas para recuperar nome/endereço e demais evidências;
7. aplica validação de dígitos verificadores da F1-02;
8. compara as observações contra F01.

CNPJ de 14 dígitos que passa pelo parser antigo mas falha no DV da F1 é contabilizado e não usado como identificador forte.

## Chave da observação pendente

Uma mesma carga pode repetir o posto em vários produtos/ensaios. Para não gerar uma entidade por linha nem colapsar diferenças factuais em silêncio, a chave interna da observação usa:

```text
cnpj:<cnpj>:obs:<sha256-da-identidade-factual>
```

Linhas com identidade factual idêntica colapsam; alteração factual produz outra observação. Essa chave serve apenas ao pipeline/fila e não cria `posto_id` nem alias.

## F01 bitemporal

O universo F01 é consultado com dois cortes obrigatórios:

- `validade_em` — quando o dado deveria valer no mundo;
- `transacao_em` — o que a plataforma já sabia naquele instante de conhecimento.

Nenhum `now()` escondido define o resultado da comparação.

## Gate das 801 pendências F02 de maio/2026

A auditoria canônica está no [catálogo da F02](dados/catalogo-fontes.md#f02--anp--pmqc-qualidade):
o CSV registrado na carga tem SHA-256
`18ade9a457aea3c5bd28947a21a4be88d3fcaa92f7a6eb60739f6929d610206a` e o ZIP
oficial preservado tem SHA-256
`c675f9e654edb5625a4340b83b991d06187299f7991f71bb72b954f2f60b56cd`.
A carga leu 65.226 linhas, vinculou 64.425 fatos e deixou 801 pendências em 23
CNPJs válidos, com motivo exclusivo `cnpj_sem_posto` e zero linha descartada.
Dez casos têm candidato espacial forte, sem que isso autorize vínculo automático.

### Ambiente obrigatório do ensaio

`pic-er preparar-experimento` **não possui modo dry-run**. O comando abre
`PIC_DATABASE_URL_APP`, insere em `identidade.candidato_ligacao` e, quando
termina sem erro, confirma a transação. É proibido apontá-lo para produção ou
tratar um rollback como isolamento suficiente: sequências PostgreSQL não são
transacionais e podem avançar mesmo quando as linhas são revertidas.

Neste gate, “dry-run” significa exclusivamente um ensaio em
**restauração/clone descartável e isolado**, nunca uma transação descartada no
banco produtivo. A restauração precisa estar acompanhada da mesma zona bruta e
dos respectivos manifestos, porque o pipeline abre o caminho registrado em
`ingestao.carga.caminho_bruto` e confere o SHA-256 antes de reler o CSV.

Antes de conectar, o operador registra e compara nominalmente host, banco e
usuário do DSN com a restauração aprovada; qualquer coincidência com o endpoint
produtivo bloqueia o ensaio. Prefere-se usar duas restaurações do mesmo estado
limpo: a primeira para descobrir estratos e proveniências efetivamente usadas;
a segunda para reproduzir o manifesto aprovado e produzir a evidência final.
Reutilizar um clone já alterado exige restauração ao estado inicial antes da
reprodução.

O ensaio precisa usar os hashes comprovados acima e cortes bitemporais
explicitamente aprovados. `validade_em`, `transacao_em`, seed, quotas e o
conjunto exato de hashes F01/GEO **não estão definidos por esta baseline** e não
podem ser preenchidos por inferência. Em particular, snapshots GEO declarados e
não usados também invalidam o manifesto.

### Asserções e relatório de liberação

Antes de executar o pipeline, o preflight precisa confirmar na restauração:

- `sum(ingestao.pendencia_vinculo.ocorrencias) = 801` para a carga;
- 23 chaves/CNPJs distintos, todos com motivo `cnpj_sem_posto`;
- SHA-256 do CSV e do ZIP iguais à baseline acima;
- zona bruta e manifesto legíveis nos caminhos esperados.

Após a releitura, o relatório precisa provar ainda:

- `linhas_relevantes = 801`, 23 CNPJs pendentes e
  `linhas_cnpj_sem_dv_valido = 0`;
- reconciliação explícita entre linhas, CNPJs, observações factuais e candidatos,
  mantendo contabilizadas as observações que não atravessarem o blocking;
- escrita restrita à fila contextual F02 do clone, com deltas zero em `posto`,
  aliases, fatos e decisões;
- estabilidade da F03 e dos candidatos legados.

O relatório de liberação deve registrar ao menos:

- carga e hashes de ZIP/CSV usados;
- cortes `validade_em` e `transacao_em`;
- total de linhas, CNPJs, observações e candidatos gerados;
- cobertura de pontos F01/F02, comparações de distância e razões de ausência;
- cobertura de cada data e razões temporais;
- confirmação de `sem_modelo`/valor nulo em todos os candidatos;
- deltas zero em `posto`, aliases, fatos e decisões;
- estabilidade da F03 e dos candidatos legados.

O lote gerador F02 aceita exatamente as fontes de entidade `{F01, F02}` e
falha antes do blocking se F03 ou outra fonte de entidade estiver presente. O
manifesto do experimento também não mistura F02 com F03; snapshots GEO podem
ser declarados apenas como proveniência das evidências usadas, sem virarem
entidades do lote. O conjunto `fonte + hash_conteudo` dos snapshots GEO
declarados precisa ser exatamente igual ao conjunto GEO efetivamente usado
pelos candidatos; sobra ou ausência falha alto.

Sem esse relatório revisado, o contrato permanece experimental e não deve ser
executado nas tabelas produtivas. O dry-run mede e expõe a fila; não aceita
pares, não cria identidade e não corrige a cobertura pública.

## Casos ainda fora do escopo

### `cnpj_ausente`

Pode exigir matching apenas por nome/endereço/geografia. Ainda não existe uma chave de entidade publicada pela fonte que permita agrupar observações sem risco de sobreagrupar.

### `cnpj_invalido`

Pode representar erro recuperável, mas a reconstrução precisa ser evidenciada. O pipeline não corrige dígitos automaticamente.

Esses dois motivos serão tratados em card posterior com chave de observação e política próprias.

## Critérios de aceite do contrato contextual F02

- [x] pipeline sem modelo grava NULL, não score fictício;
- [x] F02 é relida da zona bruta com hash conferido;
- [x] `f1-09-f02-contexto-v1` só é selecionado para F01↔F02;
- [x] contrato F03 e candidatos legados permanecem imutáveis;
- [x] todas as evidências geográficas e temporais preservam proveniência e
      explicam ausência sem imputação;
- [x] hashes GEO são declarados, validados e entram no fingerprint F1-12 v2;
- [x] localizador GEO contém SHA-256 completo e coerente com `hash_conteudo`;
- [x] snapshots GEO declarados e efetivamente usados formam o mesmo conjunto;
- [x] `observado_em` GEO tem semântica verificável e não deriva indevidamente
      da validade cadastral;
- [x] lote e manifesto F02 recusam mistura com F03 antes de gerar candidatos;
- [x] protocolo F02 roda sem modelo e sem score, threshold ou autoaceite;
- [ ] dry-run das 801 pendências prova deltas zero fora da fila de candidatos;

A blindagem do pacote humano continua a cargo do F1-10 e do codebook
`f1-08a-v2`: estratos, score e referências internas não atravessam essa ponte.
