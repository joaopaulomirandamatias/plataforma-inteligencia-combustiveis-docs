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
4. **Timezone.** Fontes publicam em horário de Brasília sem offset; normalizar para UTC na ingestão, nunca na consulta.
5. **Snapshot desatualizado ≠ bug.** Snapshot é versão com identidade; a ficha pública declara a versão que exibe. "Atual" é o snapshot mais recente, não `now()`.
6. **`'infinity'` não é "sem limite" para todas as funções.** Com a convenção deste documento, `upper_inf(transacao)` devolve **false** — o extremo existe e é `infinity`. O predicado correto para "versão viva" é `upper(transacao) = 'infinity'` ou `transacao @> now()`. Já derrubou teste em implementação; vai derrubar o próximo que assumir `upper_inf`. A armadilha alcança também o **driver**: `psycopg` não materializa `'infinity'` em `datetime` (`DataError: timestamp too large`) — leitura em Python projeta `lower(validade)` e o predicado `upper(validade) = 'infinity'`, nunca `SELECT` cru da coluna de range. (`NULL` teria carregado como `None` silencioso — mais um motivo da proibição.)
7. **Fonte-retrato sem data de referência.** Fonte que publica o estado corrente sem declarar a que data o retrato se refere (ex.: cadastro de revendedores da ANP — sem `Last-Modified`/`ETag`) tem `validade` iniciada na **data da coleta**, a melhor aproximação disponível. Consequência assumida: o histórico dessa fonte começa na primeira coleta; as-of anterior devolve vazio — e isso é **verdade**, não defeito. Datas de sub-fatos do payload (ex.: `DATAPUBLICACAO` = data da autorização) **não retroagem** a validade do retrato: retroagir fabricaria história para atributos mutáveis (bandeira, endereço). Se o sub-fato importar como fato próprio ("autorização publicada em D"), ele vira tipo de fato separado com a validade dele. **Corolário para reprocessamento:** ao recarregar da zona bruta, a referência temporal vem do manifesto (data da coleta original), nunca do relógio corrente — reprocessar não é recoletar. E o instante é **carimbado uma única vez**: o `coletado_em` gravado no manifesto é a fonte de verdade da validade tanto na carga original quanto no reprocessamento — duas chamadas de relógio "quase iguais" divergem por milissegundos e quebram a equivalência de reconstrução da forma mais traiçoeira: pequena demais para parecer erro, exata o bastante para reprovar.

## Interação com a trilha de auditoria

Toda operação de escrita grava fato **e** registro de auditoria na mesma transação (Unit of Work — plano diretor §2.2). Se a corrente de auditoria não gravar, o fato não existe. Isso faz da trilha um espelho completo da dimensão de transação — e é o que permite ao auditor reconstruir qualquer estado publicado sem acesso privilegiado.
