# ADR-012 — Planejar app de verificação com relatos segregados

**Data:** 2026-11-12 · **Status:** proposto (não aprovado) · **Decisores pendentes:** Produto, Arquitetura, Jurídico/DPO, Domínio/Metrologia, Segurança, parceiros.

## Contexto
A PIC v1 agrega e apresenta fatos institucionais oficiais bitemporais. O roadmap já reserva aplicativo cliente (G6), equipamentos (G7), integrações ERP/ATG (G8), além de espaço para atendimento/contraditório. A Portaria Inmetro 227/2022 e documentação técnica relacionada apontam possibilidade de leitura Bluetooth metrológica **em bombas compatíveis**. O usuário pediu também um **canal de envio de relatos de possíveis irregularidades**, recebido na plataforma e visualizado apenas por pessoas com acesso específico. Essas manifestações **não têm natureza de fato oficial ou detecção confirmada**.

## Decisão proposta
Ampliar o app cliente existente, com **três superfícies distintas:** `Consulta pública`, `Verificação opcional de abastecimento` e `Relatar ocorrência`. O cliente envia registros de ocorrência a um **serviço privado e isolado**; uma **fila de triagem humana restrita** usa permissões por papel + finalidade + escopo. A coleta Bluetooth é exclusivamente **read-only**, compatível e autorizada; integração contínua via controlador/IFSF exige contrato próprio. **Nenhuma denúncia ou registro de bomba é automaticamente publicado ou qualificado como fraude**.

## Consequências e limites
- Mantém uma UX mobile integrada, mas backend público e privado ficam segregados por BFF, autorização e dados.
- Não altera o contrato da API pública nem o catálogo F01–F11 por simples decisão documental.
- Receber denúncia não equivale a receber reclamação de Procon/ANP, e não cria rotulagem ou pontuação automática do estabelecimento.
- O acesso do gestor de posto à denúncia bruta é negado; contraditório é fluxo formal minimizado.
- Exige novos contratos, RIPD, revisão de segurança, gestão de incidentes/abuso, retenção, auditoria e aceite institucional antes de disponibilização.
- Retorno do protocolo ao cidadão utiliza token seguro não enumerável ou sessão autenticada; decisão pendente de UX e segurança.
- O módulo de relatos é independente da existência de bomba inteligente: recebe descrição e anexos **sem Bluetooth**.

## Alternativas
1. **Criar segundo aplicativo exclusivo de denúncia:** rejeitar preliminarmente, pois gera duplicação de identidade, suporte e UX; reavaliar se exigência institucional separar canais.
2. **Denúncia como conteúdo público associado ao posto:** rejeitada, por risco de divulgação de alegação não verificada, exposição de terceiros e violação da política de linguagem.
3. **Encaminhar automaticamente denúncia para órgão/funcionário do posto:** rejeitada; requer acordo e supervisão, no interesse da confidencialidade e da cadeia de custódia.
4. **Acesso direto do celular ao banco de gestão:** rejeitada; sempre API de ingestão segregada e BFF/gateway com políticas de autorização.

## Validação e governança
Detalhes de requisitos, estados, dados e testes: [PIC Verifica — app](../../produto/pic-verifica-app.md) e [contrato de evidências](../contrato-evento-bomba-e-relato.md). Este ADR permanece **proposto**, aguardando aprovação dos decisores. Não substitui ADRs 003, 004, 005, 006, 008 nem compromissos atuais de produção.
