# Modelo Bitemporal — semântica e uso

Como o [ADR-001](../arquitetura/adr/adr-001-bitemporalidade.md) vira esquema, escrita e consulta. Leitura obrigatória antes de tocar qualquer tabela de fato.

## As duas dimensões de tempo

| Dimensão | Pergunta que responde | Quem controla |
|---|---|---|
| **Validade** (`validade`) | Quando isto foi verdade *no mundo*? | O mundo (a fonte, o fato) |
| **Transação** (`transacao`) | Quando a base *soube* disto? | O sistema — sempre `now()` na gravação |

As duas juntas respondem a pergunta que uma só não responde: *"o que sabíamos em C sobre o que era verdade em D?"* — a defesa contra "esse número não era esse quando vocês publicaram".

## Padrão de esquema

```sql
-- Pré-requisito: o EXCLUDE abaixo mistura operador de igualdade (btree)
-- com sobreposição (GiST) no mesmo índice — sem esta extensão, não compila.
CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE fato_qualidade (
    fato_id      bigint GENERATED ALWAYS AS IDENTITY,
    posto_id     text        NOT NULL,   -- SEMPRE o canônico (ADR-003)
    -- ... payload do fato (produto, ensaio, resultado ...) ...
    validade     tstzrange   NOT NULL,   -- quando foi verdade no mundo
    transacao    tstzrange   NOT NULL DEFAULT tstzrange(now(), 'infinity'),
    fonte        text        NOT NULL,   -- F01..F10
    localizador  text        NOT NULL,   -- linhagem: arquivo@hash:linha
    PRIMARY KEY (fato_id),
    -- duas versões "vivas" do mesmo fato não podem coexistir:
    EXCLUDE USING gist (
        posto_id  WITH =,
        validade  WITH &&,
        transacao WITH &&
    )
);
```

Convenções: extremo aberto é `'infinity'` (nunca `NULL`); todo timestamp é `timestamptz` em UTC; `fonte` + `localizador` são obrigatórios — fato sem linhagem não é persistível (invariante do domínio).

> **Estado vs. evento.** O DDL acima é de tabela de **estado** — um fato vivo por entidade (ex.: cadastro). Em tabela de **evento**, onde várias ocorrências do mesmo posto são legítimas (amostras, preços), o **grão do evento entra na chave de exclusão** junto de `posto_id` — ex.: `(posto_id, amostra_id, …)` ou `(posto_id, semana, produto, …)`. Sem o grão, o `EXCLUDE` rejeitaria a segunda ocorrência real. (Lacuna encontrada na implementação F0-02.)
>
> O grão cresce também numa tabela de **estado**, quando FONTES diferentes
> afirmam legitimamente o mesmo tipo de estado sobre a mesma entidade. Posição
> geográfica de um posto é estado — um ponto vivo por vez —, mas GEO-ANP (posição
> publicada pela ANP) e GEO-01 (geocodificação por endereço) são evidências
> concorrentes que podem coexistir; a chave é `(posto_id, fonte, …)`. Com
> `posto_id` sozinho, a segunda fonte seria rejeitada como duplicata. A pergunta
> que decide o grão não é "estado ou evento?", e sim **"o que pode ser verdade ao
> mesmo tempo sem se contradizer?"**. (Migração 022.)

## As quatro operações permitidas

Não existe quinta. `UPDATE` de payload e `DELETE` são proibidos por ADR-001 (e negados por permissão de banco).

| # | Operação | Como |
|---|---|---|
| 1 | **Afirmar** um fato novo | `INSERT` com `transacao = [now, ∞)` |
| 2 | **Corrigir** um fato (soubemos que estava errado) | Fecha a transação da versão antiga (`transacao = [t0, now)`) **e** insere a versão nova — na mesma transação de banco |
| 3 | **Encerrar validade** (deixou de ser verdade no mundo) | Fecha `validade` da versão corrente via correção (op. 2) |
| 4 | **Superar** (fonte reemitiu o dado) | Igual à correção, com `localizador` da nova emissão |

A operação 2 é a única forma de "mudar" algo — e ela **preserva** a versão anterior consultável: quem perguntar "o que sabíamos ontem?" recebe o valor de ontem, errado como era.

> **Mecanismo canônico da operação 2.** Com o `REVOKE UPDATE` do ADR-001, fechar a transação da versão antiga é fisicamente um `UPDATE` — que o papel de aplicação não pode executar. A resolução é uma **função `SECURITY DEFINER` do owner**, restrita ao par fechar+inserir na mesma transação: o privilégio mora no código auditado, não no papel. (Decisão do coordenador em 2026-08-07, a partir da tensão identificada na implementação F0-01; implementação em card próprio.)

## Consulta as-of

```sql
-- O que era verdade em :D, segundo o que sabíamos em :C
SELECT *
FROM   fato_qualidade
WHERE  posto_id = :posto
  AND  validade  @> :D::timestamptz
  AND  transacao @> :C::timestamptz;

-- Visão corrente = as-of(now, now)
-- "Como estava a ficha quando o dossiê foi emitido" = as-of(D = data do fato, C = data do dossiê)
```

Regra de produto: **rota quente não consulta bitemporal cru** — lê snapshot versionado (`SnapshotPublicado`), que é as-of materializado com identidade. A API expõe `?as_of=` resolvendo contra snapshot quando existir, contra a base quando não.

## Armadilhas conhecidas

1. **Fato vs. decisão.** Autuação tem duas datas (infração e decisão — catálogo F04). A `validade` é a do *fato*; usar a da decisão desloca o fato no tempo e **vaza futuro para o passado** em features de ML.
2. **Retrato do presente.** O dump da Receita não traz histórico — a bitemporalidade aqui é construída **por nós** via diff mensal. Mês não arquivado = buraco permanente na dimensão de validade.
3. **Corte temporal de ML.** Feature calculada para prever em T usa `transacao @> T` — o que a base *sabia* em T — e não `validade`. Usar validade é vazamento sutil: incorpora correções feitas depois de T.
4. **Timezone.** Fontes publicam em horário de Brasília sem offset; normalizar para UTC na ingestão, nunca na consulta. E a terceira cara da armadilha: `::date` sobre `timestamptz` converte **no fuso da sessão** — fato gravado em `2026-06-01T00:00Z` aparece como `2026-05-31` numa sessão em −03. Nada quebra; o relatório sai plausível com a data errada. Conferência de data é sempre com `AT TIME ZONE 'UTC'`.
5. **Snapshot desatualizado ≠ bug.** Snapshot é versão com identidade; a ficha pública declara a versão que exibe. "Atual" é o snapshot mais recente, não `now()`.
6. **`'infinity'` não é "sem limite" para todas as funções.** Com a convenção deste documento, `upper_inf(transacao)` devolve **false** — o extremo existe e é `infinity`. O predicado correto para "versão viva" é `upper(transacao) = 'infinity'` ou `transacao @> now()`. Já derrubou teste em implementação; vai derrubar o próximo que assumir `upper_inf`. A armadilha alcança também o **driver**: `psycopg` não materializa `'infinity'` em `datetime` (`DataError: timestamp too large`) — leitura em Python projeta `lower(validade)` e o predicado `upper(validade) = 'infinity'`, nunca `SELECT` cru da coluna de range. (`NULL` teria carregado como `None` silencioso — mais um motivo da proibição.)
7. **Fonte-retrato sem data de referência.** Fonte que publica o estado corrente sem declarar a que data o retrato se refere (ex.: cadastro de revendedores da ANP — sem `Last-Modified`/`ETag`) tem `validade` iniciada na **data da coleta**, a melhor aproximação disponível. Consequência assumida: o histórico dessa fonte começa na primeira coleta; as-of anterior devolve vazio — e isso é **verdade**, não defeito. Datas de sub-fatos do payload (ex.: `DATAPUBLICACAO` = data da autorização) **não retroagem** a validade do retrato: retroagir fabricaria história para atributos mutáveis (bandeira, endereço). Se o sub-fato importar como fato próprio ("autorização publicada em D"), ele vira tipo de fato separado com a validade dele. **Corolário para reprocessamento:** ao recarregar da zona bruta, a referência temporal vem do manifesto (data da coleta original), nunca do relógio corrente — reprocessar não é recoletar. E a referência é **carimbada uma única vez e preservada no manifesto** (`referencia_validade`): ela é a fonte de verdade da validade na carga original **e** no reprocessamento. Quando a fonte não declara data — o caso desta armadilha — a referência é o próprio `coletado_em`, e os dois coincidem por construção; quando a fonte declara (`Last-Modified`), a referência é a data declarada e diverge de `coletado_em` **legitimamente**. A regra universal é `lower(validade) = referencia_validade` do manifesto nos dois caminhos; `lower(validade) = coletado_em` é propriedade do caminho sem data declarada, não regra geral. O motivo do carimbo único: duas chamadas de relógio "quase iguais" divergem por milissegundos e quebram a equivalência de reconstrução da forma mais traiçoeira — pequena demais para parecer erro, exata o bastante para reprovar.

8. **Comparação entre ambientes: fixe a collation.** `ORDER BY` textual segue a collation do banco — `C` no local e `en_US.utf8` no gerenciado ordenam diferente sobre dados **idênticos**, e uma impressão digital que agrega linhas ordenadas diverge parecendo defeito de dado. Hash de equivalência entre ambientes ordena com `COLLATE "C"` explícito. (Da verificação F0-02: os três recortes "divergiam" até a consulta fixar a collation — o dado estava certo; a comparação é que mentia.)

9. **`EXCLUDE` proíbe sobreposição em TODO o tempo de transação — não só
   "duas vivas agora".** É a armadilha mais cara desta lista, porque só aparece
   quando já é tarde: na hora de acrescentar a restrição a uma tabela que foi
   escrita sem ela.

   Suponha um caminho de escrita que afirma sem nunca fechar a versão anterior.
   Depois de N execuções, existem N linhas com transação `[t1, ∞)`, `[t2, ∞)`,
   …, `[tN, ∞)`. O reflexo é "fecho as perdedoras agora e pronto" — e ele está
   errado: fechar em `now()` produz `[t1, now)`, que **continua contendo**
   `[tN, now)` e portanto continua sobreposta à sobrevivente. Não existe
   instante de fechamento no presente que desfaça uma sobreposição do passado.

   Só duas formas satisfazem a restrição, e nenhuma é de graça:

   - **encadear retroativamente** — `[t1,t2)`, `[t2,t3)`, …, `[tN,∞)`, a cadeia
     que a operação 2 teria produzido. Restaura o invariante e torna `as_of`
     unívoco em todo o passado, mas reescreve `transacao` de linhas antigas:
     apaga da base o episódio em que ela afirmou várias coisas ao mesmo tempo;
   - **restrição parcial** (`WHERE upper(transacao) = 'infinity'`) — não toca em
     nada, impede o defeito de voltar, e deixa a anomalia consultável **para
     sempre** num `as_of` dentro da janela ruim.

   Corolário prático: **o `EXCLUDE` não é item para "acrescentar depois". Ele
   pertence à primeira migração da tabela.** Ele não é otimização nem detalhe de
   integridade — é a única coisa que obriga a escrita a passar pela operação 2, e
   sem ele o caminho de escrita erra em silêncio por tempo indeterminado.

   Precedente: `fatos.fato_geocodificacao` nasceu na 017 sem a restrição e
   acumulou três evidências vivas por posto até 2026-08-20. A migração 022
   acrescentou o `EXCLUDE`, e a decisão do coordenador foi encadear
   retroativamente **com arquivo de evidência obrigatório** — o estado anterior,
   linha a linha e com hash, gravado antes do commit, para que o episódio
   continue provável fora do banco. Runbook `docs/operacao-saneamento-geo.md`,
   no repositório de código.

   E como a restrição não aceita `NOT VALID` (só `CHECK` e `FK` aceitam), não há
   como acrescentá-la desligada e validar depois: a migração que a adiciona ou
   encontra o dado já saneado, ou falha. Prefira falhar com uma guarda explícita
   que rode o mesmo predicado e nomeie o runbook, em vez de deixar o
   `ADD CONSTRAINT` estourar apontando uma linha qualquer.

## Interação com a trilha de auditoria

Toda operação de escrita grava fato **e** registro de auditoria na mesma transação (Unit of Work — plano diretor §2.2). Se a corrente de auditoria não gravar, o fato não existe. Isso faz da trilha um espelho completo da dimensão de transação — e é o que permite ao auditor reconstruir qualquer estado publicado sem acesso privilegiado.
