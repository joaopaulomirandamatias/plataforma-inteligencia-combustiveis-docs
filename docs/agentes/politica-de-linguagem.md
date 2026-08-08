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

`fraude` (como afirmação sobre agente identificado) · `fraudador` · `criminoso` · `culpado` · `comprovado/provado` · `certeza` · `impossível` (de burlar) · `garantido` · `grupo econômico` · `sonegação` · `máfia/quadrilha`

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

## Casos de fronteira já decididos

- **Imprensa pergunta "o posto X frauda?"** → resposta padrão: os fatos públicos com fonte e data, mais: "a plataforma não faz essa afirmação; verificação é competência do órgão".
- **Fiscal escreve "fraude" no campo livre do caso** → o campo é dele (registro do órgão); a plataforma armazena, não republica.
- **Selo de transparência** → afirmação positiva permitida porque é verificável por critérios publicados; a ausência do selo **não** é publicada como negativa.
