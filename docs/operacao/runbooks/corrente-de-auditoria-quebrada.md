# Runbook — Corrente de auditoria quebrada

**Gatilho:** a verificação (incremental diária ou completa semanal) encontrou `hash_anterior` que não confere. **Classificação: incidente de segurança maior** — este runbook não tem caminho "verificar depois".

## Princípio

A corrente quebrada significa uma de duas coisas: **bug de escrita** ou **adulteração**. O runbook trata as duas com a mesma seriedade até prova em contrário — a diferença só é conhecida no fim, e tratá-la como bug por padrão é exatamente o que um adversário esperaria.

## Passos imediatos (primeira hora)

1. **Declarar o incidente** (severidade maior) e acionar o responsável de segurança.
2. **Preservar estado:** snapshot do banco da trilha e dos WALs — antes de qualquer investigação que toque o sistema.
3. **Não parar a escrita de produção.** A trilha continua gravando (a corrente nova nasce do último registro válido conhecido + marcador de incidente); parar a auditoria seria apagar as luzes durante o roubo.
4. **Localizar o ponto de quebra:** menor `seq` inconsistente. Tudo antes dele está íntegro por construção.

## Investigação

5. **Comparar com as âncoras externas.** É para isto que elas existem: a âncora do dia D prova qual era o hash válido em D. Quebra *antes* da última âncora íntegra = adulteração retroativa (grave); quebra *depois* = janela intra-dia (bug ou adulteração recente).
6. **Cruzar com os backups WAL:** o registro divergente aparece no WAL do horário correspondente? WAL e tabela divergem → escrita fora do caminho normal (comprometimento de credencial de banco); conferem → investigar o caminho de aplicação (bug de UoW ou código malicioso).
7. **Determinar o alcance:** quais `acao`/`objeto` estão na região afetada; se envolve cofre ou publicação de caso, acionar também DPO (possível incidente com dado pessoal — prazo de comunicação da LGPD conta a partir da ciência).

## Encerramento

8. **A corrente nunca é "consertada".** Registros adulterados/perdidos são documentados num **registro de incidente apensado à própria corrente** (com o laudo), e a verificação passa a reconhecer a descontinuidade declarada. Reescrever a corrente para "ficar bonita" destruiria a única propriedade que a torna crível.
9. **Post-mortem obrigatório** com: vetor, janela de detecção real vs. esperada, e revisão do intervalo de verificação/âncora se a janela foi longa demais.
10. **Comunicação:** auditor e órgão parceiro recebem o laudo — a trilha existe para convencer o cético; esconder um incidente dela inverte o propósito do sistema.
