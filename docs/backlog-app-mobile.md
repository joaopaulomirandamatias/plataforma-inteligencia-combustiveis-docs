# Backlog do aplicativo móvel — o que o app precisa e o sistema ainda não tem

**Atualizado em:** 2026-11-12

**Escopo:** aplicativo do consumidor (`plataforma-inteligencia-combustiveis-mobile`)
e as entregas de backend das quais ele depende.

**Função deste documento:** o app não tem regra de negócio própria. Quando uma
tela do mockup pede algo que a API ainda não serve, o app mostra o recurso como
indisponível e a necessidade entra **aqui**, como item de backend. Este
documento é a fila dessas necessidades; não é evidência de entrega.

> Para o estado do projeto como um todo, o ponto de entrada continua sendo o
> [status canônico](status-projeto.md). O roadmap por gates da gestão
> (`docs/roadmap-gates.md`, no repositório de gestão) trata o aplicativo como
> **G6**, depois da projeção pública (G4).

> **Relação com o PIC Verifica.** O que este documento descreve é o gate
> **G6-A** (consulta pública, mapa e ficha) do produto PIC Verifica,
> acompanhado em
> [gestao#48](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis-gestao/issues/48).
> Cada item abaixo é uma sub-issue dela, no repositório que precisa fazer o
> trabalho. Relato de ocorrência (G6-B) e leitura de bomba (G8-M) **não** fazem
> parte do app implementado e não aparecem nele. O app usa hoje a marca do
> portal, “Combustível em Dia”; a escolha entre esse nome e “PIC Verifica” está
> em aberto.

## 1. Como ler

Os estados seguem o status canônico e não são promovidos por inferência:
**implementado** (existe código), **validado tecnicamente** (gates automatizados
passaram), **ativo em produção** e **aceito operacionalmente**.

Cada item de backend traz o repositório responsável, a tela do mockup que o
motivou e o que precisa existir. Os nomes de campo e de rota são **proposta**:
o contrato só muda pelo `openapi.yaml`, com o rito de sempre.

## 2. O que o app já faz

Implementado e validado tecnicamente (typecheck, lint, 83 testes, exportação
web e empacotamento para iOS e Android) em 2026-11-12. **Não** está em produção
nem em loja.

Em 2026-11-12 o app foi executado contra a API de produção pela prévia web
(mesmo código das telas nativas, com um servidor que repassa as chamadas, já
que a API não aceita chamada direta de navegador). Busca, ficha
`00097ff8-98c0-5d16-823e-66edb77c334c` (6 grupos e 48 ensaios, como no status
canônico), contexto regional e proximidade responderam `200` e renderizaram.
Isso é evidência datada de compatibilidade com o contrato, não teste em
aparelho.

| Tela | Operação da API (`x-estado: implemented`) |
|---|---|
| Início e busca | `GET /saude` |
| Resultados | `GET /v1/postos` |
| Ficha do posto: resumo, qualidade, preços, cadastro, fontes | `GET /v1/postos/{posto_id}`, `GET /v1/postos/{posto_id}/contexto-regional` |
| Perto de mim, em lista e em mapa | `GET /v1/postos/mapa` (modo raio) |
| Visão em outra data (seletor e link com `as_of`) | as mesmas da ficha, com `as_of` |
| Compartilhar (ficha sempre atual ou link permanente do recorte) | nenhuma — monta o endereço do portal |
| Canais oficiais e “como ler um resultado” | nenhuma — conteúdo mínimo embutido, sem citação de norma |
| Favoritos, consultas recentes, preferências | nenhuma — guardado só no aparelho |
| Offline | cópia da última resposta da API, por até 7 dias, com a data à vista |

Telas presentes no app, mas **sem função** por falta de backend: aba “Do posto”
da ficha, Alertas e a parte de conta. Elas dizem isso ao usuário em vez de
simular o recurso.

## 3. Itens de backend — API pública (núcleo)

Repositório: `plataforma-inteligencia-combustiveis`.

| Id | Necessidade | Tela do mockup | O que precisa existir |
|---|---|---|---|
| [APP-01](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis/issues/83) | Cartão de lista com endereço e disponibilidade de dado | 04 Resultados, 05 Mapa | `PostoResumo` com `endereco`, data da última coleta PMQC vinculada e data da última pesquisa de preço. Hoje a coleção devolve só nome, bandeira, município e UF, e o app não mostra as etiquetas “Qualidade · coleta em…” do mockup. |
| [APP-02](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis/issues/84) | Filtros e ordenação declarados | 06 Filtros | Parâmetros `produto`, `bandeira`, “com resultado de qualidade”, “com preço na última pesquisa”, “com posição publicada pela ANP”; ordenação por nome; eco dos filtros aplicados, como já existe em `/v1/precos`. Sem ordem por preço ou por resultado. |
| [APP-03](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis/issues/85) | Série de preços de um posto | 09 Ficha · Preços | Observações estruturadas por posto e produto (por exemplo `posto_id` em `/v1/precos`). Hoje `/v1/precos` não filtra por posto, então o gráfico de oito semanas com lacunas não tem dado. |
| [APP-04](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis/issues/86) | Histórico estruturado | 07 a 10 | `GET /v1/postos/{posto_id}/historico` (já `planned`) com campos próprios por tipo de fato. Hoje `fatos_recentes[].descricao` é texto, que o portal interpreta por expressão regular e o app exibe como veio. |
| [APP-05](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis/issues/87) | Posição do posto na ficha | 10 Ficha · Cadastro | `Posto.localizacao` com latitude, longitude, origem (`GEO-ANP` ou `GEO-01`) e data. Hoje a ficha não traz coordenada: a aba Cadastro não tem mapa e a rota usa o endereço. |
| [APP-06](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis/issues/88) | Rótulos de apresentação vindos da API | todas | Rótulo canônico de produto e de fonte, e o juízo “cobertura suficiente” da média regional. Hoje portal e app mantêm cada um a sua tabela (`NOMES_PRODUTOS`, piso de 5 postos), e duas cópias divergem. |
| [APP-07](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis/issues/89) | Data do dado por fonte | 11 Ficha · Fontes | Competência, semana ou data de publicação por fonte, além de `coletado_em`. Hoje só existe a data em que a plataforma leu. |
| [APP-08](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis/issues/90) | Lista de municípios por UF | 03 Início | Coleção de municípios com a grafia da fonte, para o seletor de cidade. Hoje a cidade é texto livre. |
| [APP-09](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis/issues/91) | Situação cadastral | 07, 10 | `situacao_cadastral`, já previsto no contrato como “fase Entrega”. |
| [APP-10](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis/issues/92) | Conteúdo do guia do consumidor | 24 a 27 | Conteúdo versionado e servido pela API (testes que o consumidor pode pedir, o que conferir no local, canais oficiais por UF, explicador do PMQC), com a referência de cada afirmação. Depende de revisão jurídica: as referências do mockup foram conferidas só por busca. |
| [APP-11](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis/issues/93) | Etanol × gasolina | 28 | Nova fonte (tabela PBE Veicular do Inmetro) e cálculo no backend. O app não faz a conta. |
| [APP-12](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis/issues/94) | Ordem declarada no modo raio | 05 Mapa | O contrato de `GET /v1/postos/mapa` não diz em que ordem os itens voltam nem quais ficam de fora quando `truncado` é verdadeiro. O app apresenta a lista pela `distancia_m` recebida e, no truncamento, só orienta a reduzir o raio. |

## 4. Itens de backend — gestão

Repositório: `plataforma-inteligencia-combustiveis-gestao`.

| Id | Necessidade | Tela do mockup | O que precisa existir |
|---|---|---|---|
| [APP-20](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis-gestao/issues/55) | Dados declarados pelo posto na API pública | 12 Ficha · Declarado | É o gate **G4** da gestão: projeção pública de horário, serviços, formas de pagamento, preço informado e conteúdo promocional, cada um com data da declaração e sem se misturar ao dado oficial. O app já tem a aba e as três etiquetas (oficial, declarado, promoção). |
| [APP-21](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis-gestao/issues/56) | Correção e resposta do posto | 29 | Entrada do pedido no console, identificação de quem representa o CNPJ, estado “em revisão” na ficha e uso do campo `contraditorio`, que já existe no contrato. |

## 5. Serviços que ainda não existem

| Id | Necessidade | Tela do mockup | O que precisa existir |
|---|---|---|---|
| [APP-30](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis-gestao/issues/57) | Conta do consumidor | 18 Conta | Serviço próprio de conta e preferências (decisão registrada em `apps/mobile/README.md`, na gestão): autenticação, sincronização de favoritos, exportação e exclusão de dados. Exige política de consentimento, retenção e exclusão, e atualização do RIPD. |
| [APP-31](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis-gestao/issues/58) | Alertas | 15, 16 | Registro de aparelho, assinatura por posto e tipo de aviso, detecção de publicação nova a partir do [catálogo de eventos](dados/eventos/README.md), envio de notificação e central de alertas. Todo alerta passa pelo Guardião e segue a [política de linguagem](agentes/politica-de-linguagem.md): diz o que disparou, a cobertura e o que fazer. |
| [APP-32](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis-gestao/issues/59) | Estatísticas de uso | 18 | Telemetria minimizada e opt-in. O interruptor existe no app e hoje não envia nada. |
| [APP-33](https://github.com/joaopaulomirandamatias/plataforma-inteligencia-combustiveis-web/issues/43) | Links universais | 17 Compartilhar | Domínio próprio e os arquivos de associação servidos pelo portal, para `/postos/{posto_id}` abrir direto no app. A rota já é a mesma nas duas pontas. |

## 6. Próximos passos só do app

Não dependem de backend novo, mas dependem de decisão ou de aparelho:

1. chave do Google Maps para o build de Android — sem ela o modo mapa fica
   oculto no Android, porque o SDK fecha o app;
2. identificadores de loja, ícone e tela de abertura próprios, e o primeiro
   build de desenvolvimento;
3. abrir o app num aparelho: o mapa e a permissão de localização só foram
   conferidos por teste de componente e no navegador;
4. conferência com leitor de tela em aparelho real.

As telas “testes que você pode pedir” e “o que conferir no local” (24 e 25 do
mockup) **não** foram implementadas de propósito: cada frase delas cita uma
norma, e as referências só foram conferidas por busca. Elas entram quando o
conteúdo vier da plataforma, já revisado (APP-10). O mesmo vale para os
contatos por estado na tela de canais oficiais, que hoje traz só o telefone da
ANP.

## 7. Condições do gate G6 ainda abertas

O roadmap da gestão define, para o G6, “protótipo visual selecionado, testes em
dispositivos, privacy review”. Situação em 2026-11-12:

- **Protótipo visual:** existe um mockup com 29 telas; falta a escolha formal
  de produto sobre ele.
- **Testes em dispositivos:** não feitos. A conferência visual foi no
  navegador, com a exportação web do mesmo código.
- **Revisão de privacidade:** não feita. O app não cria conta, não envia
  localização exata à API e não grava coordenada, mas isso precisa de parecer
  do encarregado antes de publicação em loja. O modo mapa acrescenta um ponto
  novo a avaliar: a área exibida é enviada ao provedor de mapas do aparelho
  (Apple no iOS, Google no Android).
- **Sobreposição com o aplicativo da ANP:** a pesquisa de 2026-11-12 indicou
  que a ANP lançou em julho de 2026 um aplicativo próprio, com nota de 0 a 5
  por posto. A informação veio de resultados de busca e precisa ser confirmada
  na fonte. Se confirmada, o posicionamento do app (várias fontes, origem e
  data de cada fato, sem nota) deve ser decidido em ADR.
