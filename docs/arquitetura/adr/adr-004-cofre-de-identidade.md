# ADR-004 — CPF completo só no cofre segregado

**2026-08 · Aceito · Decisores: arquitetura + DPO**

## Contexto
O CPF vem mascarado na base pública da Receita por decisão deliberada do controlador. Vínculos T3 (sócio PF) são probabilísticos e homônimos geram grupo falso — e grupo falso gera fiscalização indevida. Resolver identidade exige o dado real em algum ponto; tê-lo espalhado pela base analítica é passivo LGPD e alvo de exfiltração.

## Decisão
CPF completo existe apenas no cofre (banco próprio, rede segregada, envelope encryption). A base analítica opera com `pessoa_id = HMAC(sal_do_cofre, CPF)`. Resolução de identidade pelas rotas R1/R2/R3; reconstrução técnica do mascaramento é vedada em qualquer hipótese.

## Consequências
(+) Vazamento da base analítica não expõe CPF por construção. (+) Toda consulta ao dado real é logada com finalidade — auditável por terceiros. (−) Joins que precisam de identidade real passam pelo fluxo do cofre, com latência e cerimônia. **(Proibido)** CPF em evento, log, feature, dossiê ou payload de webhook — mesmo truncado.

## Alternativas rejeitadas
- **Criptografia de coluna na base única:** segrega logicamente, mas não fisicamente — um comprometimento da aplicação lê tudo.
- **Não tratar identidade PF:** mantém homônimos como falso vínculo, e a ferramenta de priorização passa a produzir injustiça — inaceitável para o propósito do sistema.
