# Adendo ao investimento — APP, segurança e operação de manifestações

**Data:** 12/11/2026 · **Natureza:** revisão qualitativa de escopo financeiro, **não** orçamento revisado ou cotação de mercado atualizada.

## 1. Referência histórica

O documento-fonte *Levantamento de investimento para o desenvolvimento completo da plataforma* (14/09/2026, 4 páginas) apresenta quatro cenários, com premissas explícitas de equipe, duração e custos. Os totais **com contingência de 20%** são:

| Cenário original | Duração | Estimativa histórica em R$ milhões, com contingência |
| --- | --- | --- |
| A — equipe CLT enxuta | 19 meses | 4,8–8,7 |
| A′ — equipe PJ enxuta | 19 meses | 3,9–7,1 |
| B — equipe CLT robusta (1,5×) | 19 meses | 7,1–12,8 |
| C — equipe enxuta PJ assistida por IA | 12 meses | 1,1–2,0 |

O documento também estabelece **premissa de sustentação** de R$ 0,8–1,7 milhão/ano (3 FTE + infraestrutura escalada + DPO + 1 pentest/ano + IA). Os valores refletem **preços e escolhas de 14/09/2026**; não foram recalculados aqui. Números não significam recursos disponíveis, propostas firmes nem custo aprovado.

**Fora do total original expressamente identificado no levantamento:** vendas/marketing, honorários jurídicos para convênios, compra de dados privados de parceiros, impostos sobre notas PJ, escritório e equipamentos. Ver fontes e premissas no documento histórico.

## 2. Novas frentes com necessidade de custo explícito

| Centro de custo adicional | Gatilho e entregáveis | Driver de custo | Informação faltante |
| --- | --- | --- | --- |
| Mobile Android/iOS | G6-A/B, fluxo de consulta, relato, protocolo | Desenvolvimento, testes em aparelhos, CI mobile, publicação/conta de loja, suporte | Escopo final, suporte a BLE/SPP e dispositivos |
| Backend de manifestações | G6-B, recepção, fila, histórico, reencaminhamento e antispam | API privada, modelo de dados, filas, armazenamento e monitoramento | Volume esperado de casos, anexos e retenção |
| Segurança & privacidade | P0/P1 do [modelo de ameaças](../seguranca/modelo-ameacas-pic-verifica-2026.md) | Pentest **mobile + API + Bluetooth** em laboratório, DPO/jurídico, auditorias, gestão de incidentes | Fornecedor, escopo, ciclos e avaliação de risco |
| Evidências e custódia | Cofre, hash original, retenção/backup, auditoria de leitura | Object storage, criptografia/gestão de chaves, recuperação, registro independente | Tamanho de imagem/vídeo por caso, frequência de acesso |
| Hardware/integração | G8-M, pacote de bomba e gateway opcional | Fabricante, bancadas, equipamento homologado, instrumentação, formação e seguro | Modelos compatíveis, preço, autorização e custo de laboratório |
| Operação humana | G9-P, triagem, atendimento, incidentes e encaminhamento | Equipe de atendimento/analistas, treinamento, SLA e jurídico institucional | Demanda mensal, tempos médios e capacidade |
| Integrações de terceiros | F09/F10, cartões-frota, automação, ERP/ATG | Convênios, contratos, APIs, integração, limites de uso | Termos, preço por chamada/arquivo e cobertura |
| Sustentação | Releases, SBOM, patches, monitoramento, backups | Hospedagem, licenças/serviços, revisão de segurança recorrente | Infra real, SLOs, RPO/RTO e tráfego |

**Não gerar um novo total ainda.** O cenário C de setembro não dedica FTE próprio de QA ou segurança e supõe que automação/CI/pentest contratado cubram parte do trabalho; para dados pessoais, Bluetooth e evidência institucional, essa é **hipótese de capacidade a reavaliar**, não garantia de suficiência.

## 3. Método para atualização orçamentária reproduzível

Para cada centro: `quantidade × custo unitário × duração`, manter **piso, base e teto**, origem do preço e data; separar `CAPEX/desenvolvimento`, `OPEX/sustentação`, `custos jurídicos/convênios`, `licenças/dados` e `contingência`. Não somar custo já coberto pelo orçamento inicial (dupla contagem).

Etapas: (1) congelar escopo G6-A, G6-B, G8-M, G9-P; (2) estimar volume de casos, arquivos e equipes; (3) obter cotações para testes, consultoria jurídica e bancada; (4) recalcular quatro cenários e registrar quais premissas foram alteradas; (5) comparar cenário de app **sem** Bluetooth contra app **com** laboratório; (6) submeter investimento incremental a aceite.

## 4. Decisão recomendada de sequenciamento

**Separar MVP de consulta/relato do laboratório Bluetooth.** A primeira fase só exige infra privada e jurídico/segurança dos relatos; hardware e integração com controladores entram após evidência de compatibilidade e acordos. Isso reduz dependência de aquisição e permite validação de utilidade e custos de triagem antes da expansão.

**Revisão dependente:** jurídico, DPO, engenheiro de metrologia, arquiteto, gerente de produto e responsável financeiro. **Nenhum valor novo ou economia efetiva foi demonstrado por esta revisão.**

Links internos: [oportunidades](../produto/oportunidades-priorizadas-2026.md), [app](../produto/pic-verifica-app.md), [status](../status-projeto.md).
