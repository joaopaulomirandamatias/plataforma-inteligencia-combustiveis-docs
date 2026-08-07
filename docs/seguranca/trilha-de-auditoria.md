# Trilha de Auditoria — corrente imutável

Registro append-only, encadeado por hash, de toda ação auditável do sistema. Herança direta da camada de auditoria criptográfica do estudo que originou o projeto: **protege o registro após a captura** — e o documento é honesto sobre o limite simétrico: não prova que a origem estava certa; prova que ninguém mexeu depois.

## Estrutura do registro

```
registro_n = {
  seq            sequência monotônica global
  timestamp_utc  relógio do sistema (fonte declarada)
  ator           quem (usuário, serviço ou agente)
  papel          com qual papel/escopo
  acao           tipo tipado (catálogo fechado, versionado)
  objeto         sobre o quê (posto_id, caso_id, cluster_id, ...)
  justificativa  obrigatória para ações sensíveis (consulta ao cofre, override)
  hash_payload   SHA-256 do conteúdo da ação
  hash_anterior  SHA-256 do registro n-1
}
hash_n = SHA-256(registro_n)
```

Qualquer alteração retroativa quebra a corrente do ponto alterado em diante. O primeiro registro (gênesis) contém o hash do commit de implantação.

## O que é auditável (catálogo mínimo)

| Classe | Exemplos |
|---|---|
| Identidade | Fusão/separação de cluster, decisão da fila humana |
| Cofre | **Toda** consulta, com finalidade; tentativa negada |
| Fatos | Toda escrita bitemporal (op. 1–4 do [modelo](../dados/modelo-bitemporal.md)) |
| Modelos | Promoção, rollback, mudança de limiar |
| Casos | Abertura, refutação, publicação, veto do Guardião |
| Acesso | Dossiê aberto por fiscal; export; mudança de papel |
| Config | Precedência do golden record, limiares, políticas ABAC |

Ações de sistemas do posto (preço, estoque — fase ERP) entram como novos tipos de `acao` no mesmo catálogo, sem mudança estrutural.

## Escrita

Regra única: **mesma transação do fato** (Unit of Work). Se a trilha não grava, o fato não existe — não há caminho de escrita "rápido" que pule a corrente. `UPDATE`/`DELETE` na tabela da trilha são negados por permissão de banco *e* detectáveis pela verificação (defesa em profundidade: permissão pode ser mal configurada; a corrente não mente).

## Verificação e âncora externa

- **Verificação interna:** job agendado re-percorre a corrente (completa semanalmente, incremental diária). Corrente quebrada = incidente de segurança maior, com runbook próprio — não é "investigar depois".
- **Âncora externa diária:** o hash do último registro do dia é publicado fora do controle operacional da plataforma. Opções em ordem de preferência: (1) carimbo do tempo qualificado / OpenTimestamps sobre blockchain pública — custo zero e verificável por terceiros; (2) commit assinado em repositório público; (3) publicação ao órgão parceiro. A âncora torna a adulteração retroativa detectável **até por quem não confia na plataforma** — que é o ponto: a trilha existe para convencer o cético, não o operador.

## Consulta

Perfil `auditor` (leitura de tudo, escrita de nada — matriz IAM do plano diretor §4.1). Consultas típicas: linha do tempo de um objeto (`objeto = posto_id X`), atividade de um ator, todas as consultas ao cofre num período, todos os overrides com justificativa. A leitura da trilha **também é registrada** na trilha (auditoria da auditoria) — exceto a própria verificação agendada, marcada como tal.

## Retenção e LGPD

A trilha contém dado pessoal de operadores e fiscais (ator). Retenção longa é justificada por obrigação de auditoria e legítimo interesse documentado no [RIPD](../conformidade/lgpd/ripd.md); o que expira é o **acesso amplo**, não o registro — após o prazo operacional, consulta só por auditor com justificativa. Pedido de titular sobre a trilha não apaga registros (integridade prevalece, art. 16 LGPD — cumprimento de obrigação); o RIPD documenta essa ponderação.

## Limites declarados

1. A corrente prova integridade **a partir da captura** — sensor errado ou fonte adulterada antes da ingestão produzem registro íntegro de dado errado (por isso existem validação de chegada e o Refutador).
2. O relógio é o do sistema; disputa fina de ordem entre eventos de fontes distintas se resolve pela dimensão de transação da base, não pela trilha.
3. A âncora é diária: adulteração no mesmo dia, antes da âncora, é detectável apenas pela verificação interna — janela declarada e aceita.
