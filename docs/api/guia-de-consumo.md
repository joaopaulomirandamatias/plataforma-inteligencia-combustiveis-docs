# Guia de Consumo da API

Regras transversais do contrato [openapi.yaml](openapi.yaml). O contrato é a fonte; este guia explica como usá-lo sem tropeçar.

Boa parte do que está descrito aqui é **desenho alvo, não runtime**. Um integrador real construiu contra a versão anterior deste documento e tropeçou quatro vezes na mesma classe de defeito — o texto descrevia um sistema que não é o que roda. Por isso **cada seção abre declarando o próprio estado**, e não só esta introdução: quem chega pelo índice ou por link direto de uma seção precisa ver o estado onde está lendo, não três telas acima.

| Marca da seção | O que significa |
|---|---|
| **no ar** | Verificável hoje no runtime público, anônimo. Programe contra isto. |
| **desenho, não implementado** | Declarado porque é para onde o sistema vai. Não existe nenhum pedaço disso em produção; a seção diz qual é o efeito prático hoje. |

Não há prazo declarado para nada que esteja marcado como desenho. Quando existir, quem muda primeiro é o `openapi.yaml` — o estado de cada operação mora lá, neste guia só é explicado.

## O que está no ar — e como derivar isso do contrato

> **Estado: no ar.** Seis das treze operações do contrato respondem; as outras sete devolvem 404.

A base fica na **raiz do host** — `https://pic-api-production.up.railway.app` —, as rotas de negócio carregam `/v1` no próprio path e `/saude` responde na raiz, fora do versionamento, porque fala do processo e não do contrato de negócio (é o alvo do health check da plataforma). Somar a base a `/v1` e depois pedir `/v1/saude` dá 404: foi um dos quatro tropeços.

As seis operações servidas hoje, no caminho efetivo:

| Operação | Caminho | `operationId` |
|---|---|---|
| Saúde e frescor | `GET /saude` | `getSaude` |
| Coleção de postos | `GET /v1/postos` | `listarPostos` |
| Pontos para mapa | `GET /v1/postos/mapa` | `listarPostosMapa` |
| Ficha do posto | `GET /v1/postos/{posto_id}` | `getPosto` |
| Preço do posto × média regional | `GET /v1/postos/{posto_id}/contexto-regional` | `getContextoRegional` |
| Série de preços SLP | `GET /v1/precos` | `getPrecos` |

Todas são `GET` e todas são **anônimas** — não existe operação de escrita servida.

Não decore essa lista: **derive-a do contrato**. Toda operação carrega `x-estado`, e a allowlist do seu cliente é `x-estado in (implemented, deprecated)` — exatamente o que o runtime responde:

```python
import yaml
METODOS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
SERVIDAS = {"implemented", "deprecated"}

contrato = yaml.safe_load(open("openapi.yaml", encoding="utf-8"))
allowlist = [
    (metodo.upper(), caminho)
    for caminho, item in contrato["paths"].items()
    for metodo, operacao in item.items()
    if metodo in METODOS and operacao.get("x-estado") in SERVIDAS
]
```

O caminho aí é o do documento; o efetivo é `servers[].url` + path, e os dois `servers` do contrato concordam no prefixo (a raiz) justamente para que essa soma seja unívoca.

**`restricted` nunca entra na allowlist — nem depois.** É a distinção que separa fila de trabalho de decisão de arquitetura, e ler as duas como "ainda não" leva a planejar um recurso que não vai existir:

- `planned` é fila: desenhado, sem implementação. `getHistorico`, as três operações de webhook e `listarDatasets` estão aí.
- `restricted` é decisão: **existe por desenho e não pode ser servido ao público**. `getRanking` porque [ADR-005](../arquitetura/adr/adr-005-score-restrito-a-orgaos.md) proíbe score em resposta de API sem papel de órgão — não é permissão faltando, é contrato. `getGrupo` porque vínculo societário tem camada de pessoa física, e o [cofre de identidade](../seguranca/cofre-de-identidade.md) ([ADR-004](../arquitetura/adr/adr-004-cofre-de-identidade.md)) mantém pessoa física fora da borda pública. Implementar seria publicar o que a decisão proíbe.

Enquanto papel de órgão não existir no runtime, as duas seguem em 404 — o mesmo 404 de rota inexistente, sem 401 e sem 403, porque não há autenticação para negar coisa alguma.

## O que o contrato garante — e o que não garante

> **Estado: no ar** para as seis `implemented`; o resto desta seção é justamente sobre o que *não* está.

Esta é a distinção mais importante do documento, porque schema de operação servida e schema de operação no papel são visualmente idênticos e valem coisas opostas.

**Para as seis `implemented`, o schema é verificado contra a resposta real.** A suíte do backend (`tests/test_conformidade_contrato.py`) sobe a API, chama cada uma delas e valida o corpo devolvido contra o schema deste arquivo — `Saude`, `PaginaPostos`/`PostoResumo`, `MapaPostos`/`PontoMapa`, `Posto`/`Fato`, `ContextoRegional`/`ItemContextoRegional`/`MediaRegional`, `PaginaPrecos`/`PrecoSemanal`/`FiltrosPrecos` — e também os corpos de erro contra `Problem`. O CI do backend faz checkout deste repositório no **SHA fixado** em `.github/contrato.sha` e roda essa suíte contra PostgreSQL real. Então, para essas seis, derivar projeção, tipos e validação a partir do documento é seguro: o que diverge fica vermelho antes do merge.

**Para `planned` e `restricted`, o schema é desenho nunca exercido.** `PaginaHistorico`, `GrupoSocietario`, `PaginaRanking`, `Assinatura`, `Dataset` jamais foram produzidos por código nenhum. São a forma pretendida, não a forma observada — nenhum teste os confronta com uma resposta, porque não existe resposta. Gerar cliente, migração ou tabela a partir deles é repetir exatamente o erro que este documento corrige: tratar o desenho como se fosse o sistema.

A verificação é **bidirecional**, e não era. Até 2026-08 a suíte só provava "rota servida está documentada" — e por isso o contrato acumulou operações que existiam apenas no papel sem nada ficar vermelho. Hoje ela cobra os dois sentidos: `implemented` sem rota servida reprova; rota servida marcada `planned`/`restricted` reprova; operação sem `x-estado` conhecido reprova. E a comparação é sobre o caminho efetivo, não sobre o nome do path — comparar nomes deixava passar `servers` em `/v1` com path `/saude`.

**Não gere cliente a partir do `/openapi.json` do runtime.** O serviço é FastAPI e publica o documento que ele mesmo deriva do código, em `/openapi.json` e `/docs`. Ele lista os seis caminhos servidos, o que o torna tentador, mas **não** carrega `x-estado`, **não** declara `servers` e **não** descreve os corpos de resposta (as rotas devolvem `dict`, então o schema gerado tem apenas os erros de validação do próprio framework). Serve para confirmar que uma rota existe; não serve para saber o que ela devolve. O contrato canônico é o arquivo deste repositório.

## Autenticação

> **Estado: desenho, não implementado.** O runtime público é **anônimo**. Não há OIDC, não há chave, não há 401. Efeito prático: não envie `Authorization`, não construa fluxo de credencial, e não bloqueie sua integração esperando receber uma.

As seis operações servidas declaram `security: []` no contrato — e o backend reprova `implemented` sem `security: []`, justamente para que um gerador de cliente não passe a exigir credencial que não existe. Este era o quarto tropeço do integrador: `security` global pedindo `oidc`/`apiKey` num runtime que não pede nada.

O que segue declarado, como desenho das operações `restricted` e `planned`:

| Cliente | Mecanismo pretendido |
|---|---|
| Órgão, distribuidora, frota, posto | OIDC (Keycloak) — authorization code para humanos, client credentials para M2M |
| Consumo público / datasets | `X-Api-Key` com quota |

O papel e o **escopo** (UF, órgão, rede) viajariam no token, avaliados no gateway (ABAC), e é esse papel que destrava `getRanking` e `getGrupo`. Enquanto ele não existe, as duas não são servidas — e nenhuma resposta de hoje é mascarada por papel, porque a superfície pública já é, por construção, a que não depende de papel nenhum.

## Consulta temporal (`as_of`)

> **Estado: no ar** nas operações servidas que aceitam o parâmetro.

Os recursos históricos aceitam `?as_of=2026-03-12T00:00:00Z`, sem credencial:

```bash
curl "https://pic-api-production.up.railway.app/v1/postos/0000f496-39a8-5133-983f-73979b6e0ce0?as_of=2026-03-12T00:00:00Z"
```

O `posto_id` é **opaco** e vem da coleção (`GET /v1/postos`) ou de uma resposta anterior — não o construa nem presuma formato. Os exemplos do contrato usam identificadores ilustrativos que não têm a forma dos reais; a autoridade é [ADR-003](../arquitetura/adr/adr-003-posto-id-canonico.md), e a fonte prática é a própria API.

- Omitido → o instante corrente da chamada; a resposta ecoa o `as_of` que foi aplicado.
- `as_of` anterior ao primeiro dado da base **devolve coleção vazia, não erro** — e vazio aí é verdade, não defeito: fonte-retrato tem histórico que começa na primeira coleta ([armadilha 7 do modelo bitemporal](../dados/modelo-bitemporal.md)).
- `as_of` é ortogonal a filtro de recorte. Em `/v1/precos`, quem escolhe semana é `semana`/`semana_de`/`semana_ate`; `as_of` é a viagem no tempo.

> **Divergência conhecida.** O contrato descreve `as_of` como a dimensão de **validade**, e o runtime aplica o mesmo instante também no **tempo de transação** — a versão viva é a que estava viva naquele instante. Na prática isso é mais forte do que o contrato promete (aproxima-se de as-of bitemporal completo), mas é comportamento observado, não contratado: a descrição do parâmetro no `openapi.yaml` precisa de card próprio. Até lá, programe contra o que o contrato promete.
>
> O runtime também aceita `as_of` em `GET /v1/postos`, que o contrato **não** declara entre os parâmetros dessa operação (embora `PaginaPostos` declare o campo `as_of` na resposta). Parâmetro não declarado é comportamento não contratado — pode sumir sem quebrar nada formalmente.

Sobre reprodutibilidade: `versao_snapshot` é um **rótulo ecoado, não um parâmetro**. Nenhuma operação o aceita na entrada, e ele só aparece em `Saude`, `Posto` e `PaginaPrecos` — não em `PaginaPostos` nem em `MapaPostos`. O formato de hoje é provisório (`cargas/F01:9,F02:2,F03:3,GEO-ANP:6`), resolvível contra `ingestao.carga`, e serve para você registrar **contra qual estado da base** um número foi lido. A alavanca que de fato reproduz um resultado é fixar `as_of`. Snapshot materializado e versionado — o `SnapshotPublicado` do plano diretor — é desenho; enquanto não existir, a resposta é servida da base.

## Paginação

> **Estado: no ar.**

Cursor keyset opaco — **não** interprete nem construa cursores. `offset` não existe neste contrato, porque com offset uma carga que insere linhas entre duas páginas faz o cliente pular ou repetir registros.

```
GET /v1/precos?municipio=MACAPA&limit=100
→ { "itens": [...], "proximo_cursor": "MjAyNi0w...", "filtros": { ... } }
GET /v1/precos?municipio=MACAPA&limit=100&cursor=MjAyNi0w...
```

- A chave é **por coleção**: `/v1/precos` pagina sobre (semana, posto, produto) e `/v1/postos` sobre uma chave só. Cursor de outra coleção é recusado com `400 cursor_invalido` — a aridade não bate, e a alternativa seria uma página silenciosamente errada, que é pior que erro.
- `limit` tem teto **duro**: 200 nas coleções paginadas, 1000 em `/v1/postos/mapa`. Pedir acima é `422`, nunca um corte silencioso.
- `municipio` e `produto` são o **texto** como a ANP publica, não código IBGE — a PIC não tem código IBGE em nenhuma fonte. A entrada é normalizada (caixa alta, sem acento) e o valor efetivamente aplicado volta em `filtros` (e o termo de busca em `busca`, na coleção de postos). Esse eco é o contrato antifalha-silenciosa: quem recebe lista vazia lê qual recorte produziu o vazio, em vez de supor que o filtro não pegou.
- `/v1/postos/mapa` **não pagina**: devolve no máximo um ponto por posto dentro do recorte e sinaliza `truncado=true` quando há mais postos que o limite. A resposta a `truncado` é reduzir viewport ou raio, não varrer o universo de pontos.

> **Expiração de cursor: desenho, não implementado.** O runtime não expira cursor, não emite `cursor_expirado` e não tem janela de 24h. O que ele já recusa, com `400 cursor_invalido`, é cursor ilegível ou de outra coleção. Efeito prático: um cursor guardado continua válido enquanto a chave que ele ancora existir — o que não é promessa de contrato, é ausência de expiração.

## Erros

> **Estado: no ar.**

RFC 9457 (`application/problem+json`) em **todo** erro, inclusive rota inexistente (404) e método errado (405) — duas formas de erro na mesma API obrigariam todo consumidor a tratar as duas, e a esquecida seria a que quebra em produção.

Programe contra **`codigo`**, nunca contra `title` ou `detail`, que são prosa e mudam. O campo `type` é um identificador opaco: hoje ele aponta para um host `.invalid`, deliberadamente não resolvível — não tente dereferenciá-lo. O corpo traz `correlation_id`, repetido no cabeçalho `X-Request-ID`; é o que correlaciona sua chamada com os logs do serviço, e vale registrar do seu lado.

Códigos que o runtime emite hoje:

| `codigo` | Status | Quando | Ação do cliente |
|---|---|---|---|
| `posto_nao_encontrado` | 404 | Nenhum cadastro vigente para o `posto_id` no `as_of` | Não re-tentar; conferir id e `as_of` |
| `rota_nao_encontrada` | 404 | Caminho inexistente — inclui toda operação `planned`/`restricted` | Conferir a allowlist por `x-estado` |
| `metodo_nao_permitido` | 405 | Método errado no caminho certo | Corrigir o método |
| `cursor_invalido` | 400 | Cursor ilegível ou de outra coleção | Reiniciar a paginação sem cursor |
| `busca_curta` | 422 | `q` com menos de 3 caracteres | Alongar o termo; `%a%` varreria a tabela para devolver ruído |
| `parametro_invalido` | 422 | Falha de validação do parâmetro (formato, faixa, `limit` acima do teto) | Corrigir o pedido |
| `filtro_espacial_ausente` · `filtro_espacial_ambiguo` · `bbox_incompleto` · `bbox_invalido` · `raio_incompleto` · `versao_provedor_sem_provedor` | 422 | Recorte de `/v1/postos/mapa` mal formado | Informar exatamente um modo, completo |
| `semana_nao_e_domingo` · `filtro_semana_ambiguo` · `intervalo_de_semanas_invalido` | 422 | Recorte de semana de `/v1/precos` mal formado | A semana ANP abre no domingo; `semana` não se mistura com `semana_de`/`semana_ate` |
| `banco_indisponivel` | 503 | A base não respondeu | Re-tentar com backoff |
| `erro_interno` | 500 | Falha não prevista, já registrada com o `correlation_id` | Re-tentar; reportar o `correlation_id` |

> **Desenho, não implementado:** `escopo_negado`, `quota_excedida`, `cursor_expirado`, `cobertura_insuficiente` e `as_of_anterior_a_base` pertencem a autenticação, quota, expiração de cursor e score — nada disso existe no runtime, e **nenhum** desses códigos é emitido hoje. Não escreva tratamento para eles esperando exercitá-lo. Em particular, `as_of` antes do primeiro dado devolve `200` com lista vazia, e não um erro.

Ausência nunca é zero: lista vazia significa "nada no recorte", e `valor_venda: null` significa "a fonte publicou a observação sem preço de venda". Zero seria um preço, e a API não o inventa.

## Idempotência

> **Estado: desenho, não implementado.** Não existe operação de escrita servida — as seis `implemented` são todas `GET`, e `POST` numa delas devolve `405 metodo_nao_permitido`.

O contrato declara `Idempotency-Key` (UUID) obrigatória em POST com efeito, com replay seguro para mesma chave + mesmo corpo e `409` para mesma chave + corpo diferente. O único POST do documento é `criarAssinatura`, que é `planned`. Efeito prático hoje: não há chave a enviar nem replay a testar.

## Rate limiting e quota

> **Estado: desenho, não implementado.** Não há token bucket, não há `X-RateLimit-Limit`, `X-RateLimit-Remaining` ou `Retry-After`, e a API não devolve `429`. Não existe credencial contra a qual contar consumo.

Efeito prático: **o cuidado de carga é combinado, não imposto**. O que existe mecanicamente é o teto duro de página (200, ou 1000 no mapa) e o `truncado` do mapa; o resto depende de quem consome — pagine com cursor em vez de pedir tudo, recorte por UF/município/semana, e respeite backoff em `503`/`500`. O [despachante de webhooks](webhooks.md), que existiria justamente para você não precisar de polling, também é `planned`: hoje polling é o único caminho, o que é mais uma razão para espaçá-lo por conta própria.

## Versionamento e depreciação

> **Estado: parcialmente no ar** — o versionamento existe; a maquinaria de depreciação, não.

No ar:

- Major na URL (`/v1/`), e `/saude` fora do versionamento porque responde sobre o processo, não sobre o contrato de negócio.
- O `openapi.yaml` deste repositório é a fonte, e é contra ele que o backend valida. O consumidor real fixa o contrato por **SHA de commit** (é o que o backend faz em `.github/contrato.sha`); faça o mesmo. Não existe tag publicada neste repositório — apontar um gerador para "a última versão da branch" é apontar para algo que pode mudar entre duas execuções.
- Mudança aditiva não avisa; remoção ou renomeação só em major novo.

> **Desenho, não implementado:** convivência de **12 meses** e cabeçalho `Sunset`. Nenhuma operação está hoje em `x-estado: deprecated`, o runtime não emite `Sunset`, e não há changelog de depreciação a acompanhar. Quando houver, o sinal aparece primeiro no `x-estado` da operação — que é por isso que a allowlist inclui `deprecated`: operação depreciada ainda responde, e sumir com ela do seu cliente cedo demais quebra a integração sem necessidade.

## O que a API não faz — por desenho

> **Estado: no ar.** Estas não são lacunas de implementação; são recusas.

- Não retorna score nem ranking sem papel de órgão ([ADR-005](../arquitetura/adr/adr-005-score-restrito-a-orgaos.md)) — por isso `getRanking` é `restricted`, e não `planned`.
- Não retorna CPF nem dado do cofre, para nenhum papel — resolução de identidade é fluxo do cofre, fora da API. É a mesma razão de `getGrupo` ser `restricted`.
- Não afirma fraude em nenhum campo de nenhuma resposta — descrições são factuais, datadas e com fonte.
- Não funde coordenadas nem calcula posição canônica: `/v1/postos/mapa` **escolhe** uma evidência por posto, por regra determinística, e devolve a proveniência inteira dela. Escolher não é declarar verdade geográfica — a auditoria continua possível pelo `evidencia_id`.
- Não deflaciona, não converte e não arredonda preço: `valor_venda` sai nominal, na unidade da fonte, com a semana de referência ao lado para você casar com a série externa que quiser.
- Não sintetiza cobertura: `/v1/precos` devolve observações individuais e não declara amostra; quem tem noção de cobertura é `getContextoRegional`, onde `amostras` conta postos **distintos** por trás de uma média.
