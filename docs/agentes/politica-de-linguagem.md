# Política de Linguagem

O documento mais curto e mais importante da pasta: o que **nenhuma saída do sistema pode afirmar**, e como isso é verificado por software (Guardião), não por estilo. Versionada; mudança segue rito de ADR.

## O princípio

> A plataforma mostra o que aconteceu, quando, segundo qual fonte — e recomenda verificação. Quem conclui é o órgão competente, pelo procedimento dele.

Isso não é modéstia: é a fronteira entre apoio à fiscalização e instrumento legalmente relevante, e é a defesa jurídica do projeto inteiro.

## Escada de afirmação — o que cada nível de evidência permite dizer

| Nível de evidência | Pode dizer | Não pode dizer |
|---|---|---|
| Fato de fonte oficial | "Amostra não conforme em 12/03/2026 — fonte ANP/PMQC, ensaio X" | "O posto adultera combustível" |
| Score/ranking | "Prioridade elevada de verificação; principais fatores: …" | "Alto risco de fraude" |
| Anomalia (preço, comportamento) | "Padrão fora do esperado para região e período" | "Indício de irregularidade" *(sem confirmação cruzada)* |
| Vínculo societário T1/T2 | "Mesmo grupo societário aparente" | "Grupo econômico" *(termo com definição legal)* |
| Vínculo T3/T4 | "Possível vínculo, confiança N%" | Qualquer formulação que soe conclusiva |
| Caso publicado | "Conjunto de evidências que recomenda verificação; hipóteses alternativas testadas: …" | "Fraude constatada/provável" |

## Léxico bloqueado em qualquer saída

A lista normativa é **[`lexico-bloqueado.json`](lexico-bloqueado.json)**, neste repositório. Ela não é reproduzida aqui de propósito: uma lista em prosa ao lado da lista executável é uma terceira cópia, e cópias divergem — foi exatamente o que aconteceu (ver abaixo).

O arquivo é a **fonte**, não mais uma cópia. O backend (`src/pic/politica.py`) e o site (`src/lib/politica.ts`) mantêm espelhos nas linguagens deles, e o CI de cada um fica vermelho quando o espelho diverge da fonte. Como este repositório é público, os dois CIs leem o arquivo **sem credencial nenhuma** — o arranjo anterior exigia um token de leitura do backend privado, e era ele que travava a promoção do site.

O formato é JSON, e cada termo carrega a flexão que ele alcança (`fraudad` → fraudado, fraudada). O arquivo também carrega, como campo normativo, **por que** o léxico é de radicais sem a vogal final e **por que** a comparação exige fronteira de início de palavra. Não é comentário decorativo: as duas propriedades são o que impede alguém de "simplificar" o detector para casamento por palavra inteira e reabrir o buraco. Mudança segue rito de ADR.

### Divergências herdadas, registradas e não resolvidas aqui

Até 2026-08-28 existiam **três** listas — esta prosa, o Python e o TypeScript — e nenhuma batia com as outras. A prosa listava `impossível` (de burlar), que **nunca** esteve em nenhuma das duas listas executáveis; e não listava `adulterado`, `irregular` nem `suspeito`, que estavam nas duas. A unificação feita aqui adotou a lista **executável** como canônica, porque é a que estava efetivamente barrando saída em produção.

`impossível` fica, portanto, como decisão pendente do coordenador: incluí-lo é mudar a política (e derruba os dois espelhos até serem atualizados), não é uma correção de transcrição. Não foi incluído por conta própria.

Permitidos com uso obrigatoriamente qualificado: `indício` (só com evidência cruzada e caso sobrevivente à refutação) · `não conformidade` (só como fato de fonte) · `divergência` · `padrão atípico` · `prioridade de verificação`.

## Elementos obrigatórios por tipo de saída

| Saída | Obrigatório conter |
|---|---|
| Ficha pública | Fonte + data em **cada** afirmação; direito de resposta do posto quando exista |
| Alerta | O que disparou, cobertura, e o que o destinatário deve fazer (verificar — nunca "autuar") |
| Dossiê | As 7 seções do [pipeline](pipeline-do-caso.md), incluindo "o que não se pode afirmar" |
| Agregado público | Cobertura + supressão de célula pequena (RIPD §5) |

## Verificação pelo Guardião — como se aplica

1. **Gate léxico:** varredura do bloqueado (com tratamento de contexto: citar a *palavra* num texto normativo é permitido; *afirmá-la* sobre alguém, não).
2. **Casamento afirmação×evidência:** cada sentença afirmativa mapeada ao nível da escada; nível acima do que a evidência anexada sustenta → veto.
3. **Resolução de citações:** todo localizador é resolvido contra a base — existe e diz aquilo. Citação que não resolve = alucinação = veto.
4. **Estrutura:** seções obrigatórias presentes.
5. **Destinatário:** afirmações restritas (score, PF) só para papel/escopo compatível.

Veto sempre com motivo, registrado na trilha. **A política vale para humanos também:** texto de analista publicado pela plataforma passa pelo mesmo gate.

## Entrada tolerante, saída restrita (decisão 2026-08-08)

Duas fronteiras opostas, riscos opostos:

- **Ingestão (entrada):** *tolerante a coluna nova* — fonte pública muda de esquema sozinha, e recusar um campo novo custaria a janela de coleta. Coluna extra é ignorada e reportada, nunca bloqueia (política do catálogo de fontes).
- **Saída ao cliente (API pública, payload do frontend):** *lista de permissão* — campo a campo, explícito. Campo novo que a API passe a expor **não** atravessa para o navegador até alguém decidir conscientemente incluí-lo. O oposto da tolerância, e de propósito: na entrada, tolerância evita perder dado; na saída, tolerância vira vazamento.

O caso que fixou a regra: em React Server Components, `key={fato.localizador}` promoveu um dado de auditoria (caminho de arquivo + hash) ao payload de hidratação — "não renderizado ≠ não enviado". A defesa robusta não foi remover o campo (um `delete` que a próxima adição fura), mas **separar o tipo da API do tipo da aplicação**: o campo sensível não existe no tipo que os componentes veem, então o compilador barra qualquer rota de vazamento — texto, atributo ou `key`. Corolário escrito no componente: **`key` se monta com dado que já está na tela** (fonte + data + índice), nunca com dado de auditoria.

**Duas camadas, cada uma cobre o que a outra não cobre (calibragem 2026-08-08):** a separação de tipo garante que **nenhum caminho acidental** vaza — quem escreve `{fato.localizador}` ou `key={fato.localizador}` recebe erro de compilação, e é assim que morre a rota que ninguém previu. Ela **não** resiste a um cast deliberado (`as unknown as Fato` compila — o TypeScript obedece o cast). Contra cast forçado, biblioteca de terceiros ou caminho não imaginado, a defesa é o **verificador de payload** que passa o pente no HTML servido e não pode ser convencido por tipo nenhum. Nenhuma das duas basta sozinha: o tipo pega o erro honesto na hora de escrever; o verificador pega o resto. Corolário para o próximo card que exponha dado sensível ao cliente: exigir AS DUAS — tipo na borda + varredura no HTML servido.

**Como provar o verificador, barato (desenho 2026-08-08):** NÃO versionar uma sabotagem que muta o fonte e roda `next build` — teste que estraga a árvore de trabalho quando falha é pior que o buraco que fecha. Em vez disso, **separar o pente do encanamento**: extrair a busca de vestígios para uma **função pura** (recebe HTML, devolve as ocorrências) e provar com dois testes de unidade instantâneos — um HTML sabotado de amostra (ex.: `["$","li","cadastro.csv@sha256:aaaa:2",{...}]`) deve acusar 3 ocorrências; um HTML limpo deve acusar zero. O script de ponta a ponta passa a ser só quem liga essa função ao servidor real. Prova versionada, milissegundos, sem build, sem tocar no fonte.

## Casos de fronteira já decididos

- **Imprensa pergunta "o posto X frauda?"** → resposta padrão: os fatos públicos com fonte e data, mais: "a plataforma não faz essa afirmação; verificação é competência do órgão".
- **Fiscal escreve "fraude" no campo livre do caso** → o campo é dele (registro do órgão); a plataforma armazena, não republica.
- **Selo de transparência** → afirmação positiva permitida porque é verificável por critérios publicados; a ausência do selo **não** é publicada como negativa.
