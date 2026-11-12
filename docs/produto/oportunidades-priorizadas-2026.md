# Carteira de oportunidades — segurança, evidência e novos recursos da PIC

**Data:** 12/11/2026 · **Status:** recomendações e hipóteses de produto, **não implementadas**.  
**Fonte interna 1:** *Mapa de integrações — PIC (2026-09-28)*, elaborado com verificação principal em 14/09/2026 (páginas 1–6); versão documental do GitHub: [mapa de integrações](../dados/mapa-de-integracoes.md).  
**Fonte interna 2:** *Levantamento de investimento — PIC (14/09/2026)*, quatro cenários originais e premissas de custeio, disponível no acervo de planejamento (não foi copiado ao repositório por este adendo).  
**Fontes complementares:** [projeto v1](../projeto-v1.md), [PIC Verifica](pic-verifica-app.md), [modelo de ameaças](../seguranca/modelo-ameacas-pic-verifica-2026.md).

## 1. Escopo: seis perguntas, mais evidências transacionais

O mapa original organiza a inteligência por seis perguntas: **quem é; quanto cobra; quanto entrega; o que entrega; o que o Estado constatou; demanda e território**. São perguntas de dados institucionais e parceiros, integradas por `posto_id`. A nova frente de app responde uma pergunta complementar **sem alterar o modelo v1**: *que evidências do abastecimento particular foram apresentadas, como foram obtidas e quais verificações são legítimas?*

Medição de bomba, comprovante fiscal, relato do consumidor, amostra PMQC e autuação pertencem a **unidades de análise diferentes**. A vinculação entre elas exige identificadores, temporização e validação próprios; não pode ser baseada apenas em CNPJ, produto e data.

## 2. Recursos propostos e ordem recomendada

| ID | Recurso | Valor esperado | Dependências / limites | Prioridade |
| --- | --- | --- | --- | --- |
| R-01 | **Cofre de evidências e dossiê verificável** | Facilitar reconstrução e compartilhamento autorizado de casos | Segregação, hash/original, trilha de acesso, retenção e validação humana; não concluir fraude | **P0** |
| R-02 | **PIC Verifica — relato, protocolo e triagem** | Participação do consumidor sem publicar alegações não verificadas | Segurança, DPO, antimalware, revisão jurídica, equipe de atendimento | **P0** |
| R-03 | **Meu Abastecimento — histórico pessoal e recibos** | Permitir anexar comprovante, data, produto, valor, volume e eventual pacote assinado | Sem acesso presumido a NFC-e; controle de titular; dados declarados separados | **P1** |
| R-04 | **Passaporte digital da bomba** | Vincular marca, modelo, aprovação de modelo, série, manutenção, lacres, certificados e posto | Depende de fontes verificadas, instrumento/certificado e potencial F09/F11; documento inexistente não equivale a falha | **P1** |
| R-05 | **Inteligência para frotas** | Cruzar transações contratuais, telemetria e consumo com contexto | Contratos, LGPD, placa/usuário, incerteza do combustível pré-existente, limitações da capacidade nominal | **P1** |
| R-06 | **Reconciliação de estoque e abastecimento** | Analisar balanço de LMC, ATG, vendas e entregas | Adesão do posto, dados de tanque, reconciliação temporal, perdas técnicas e incerteza | **P2** |
| R-07 | **Integração metrológica Bluetooth em laboratório** | Verificar registros digitais e identidade de bomba compatível | Fabricante, modelo, protocolo, certificados e ensaio autorizado; **sem controle da bomba** | **P1** |
| R-08 | **Gateway operacional/IFSF** | Observar dados de pista em tempo real onde disponíveis | Contrato por fabricante/controlador, isolamento OT/IT; não confundir com Bluetooth de verificação | **P2** |
| R-09 | **Dossiê institucional** | Apoio a análise por fiscais e parceiros mediante concessão | Acordo, finalidade, contraditório, análise humana, proibição de divulgação indevida | **P1** |

**Observação:** P0–P2 são prioridades propostas. Ainda faltam validação com usuários, métricas de valor, custos e documentação institucional.

## 3. Integrações que mais ampliam a evidência

| Trilha | Fonte | Situação no levantamento de setembro/2026 | Cautela |
| --- | --- | --- | --- |
| F09 | IPEM/Inmetro — medições por bico, intervenção, lacres e modelos | Restrita, por convênio/LAI; mapa de campos existente | É a referência metrológica que falta; verificar cobertura e permissão, sem prometer acesso |
| F10 | SEFAZ — NFC-e / NF-e | Restrita por sigilo/base legal | **Registro fiscal da transação não equivale à medição física independente** |
| F04 | ANP — ações de fiscalização | Disponibilidade pública identificada, conector pendente na fotografia de setembro | Autuação não é decisão definitiva; datas do fato e decisão distintas |
| F11 | Inmetro — oficinas permissionárias e modelos | Pública/candidata no mapa | Associação com instrumento/posto pode ser incompleta; não inferir manutenção realizada |
| F03/F02 | ANP — preço e qualidade | Já disponíveis na PIC v1 | Preço anômalo não prova fraude; PMQC é amostra/ensaio, não transação individual |
| Frota | Cartões-frota e telemetria embarcada | Contrato/parceria | Geolocalização, capacidade, volume inicial e diferenças de abastecimento são fatores de confusão |
| Pista e tanque | Automação, ATG e LMC por adesão | Integração futura, condicionada | Desvios podem ser perda/temperatura/operação; não classificar intenção |

**Atualização de status:** a fotografia dos PDFs é histórica. Usar [status-projeto.md](../status-projeto.md) e o [catálogo de fontes](../dados/catalogo-fontes.md) para estado de implantação datado; nova integração só é considerada ativa após evidência de execução.

## 4. Duas correções científicas obrigatórias

**COR-01 — capacidade nominal do tanque não é gabarito de fraude.** O mapa de setembro (páginas 5–6) sugere usar abastecimento acima da capacidade nominal como evidência direta de bomba fora de medida. Isso precisa ser reclassificado como **alerta para verificação**, pois a capacidade real, o volume prévio, alterações do veículo, dados de identificação e erro da transação influenciam a comparação. Nunca atribuir fraude por essa regra isolada.

**COR-02 — reconciliação de NFC-e não é medição física.** O mapa (página 4) descreve NFC-e como registro autoritativo de venda e sua utilização para reconciliação comprado × vendido. A fonte é **autoritativa para o registro fiscal** nos limites do sistema, mas não verifica independentemente o volume físico dispensado. Um balanço fiscal/contábil não substitui ensaio metrológico.

Revisar enunciados técnicos em especificações e apresentações futuras; preservar o mapa PDF original como fotografia histórica, **sem reescrevê-lo silenciosamente**.

## 5. Sequência de iniciativas e critérios de passagem

1. **P0 Segurança da manifestação e evidências:** modelo de ameaças, RIPD, chaves, acesso por caso, anexos, auditoria e gestão de incidentes. Saída: testes negativos e parecer de segurança/jurídico.
2. **P0 Integração institucional de baixo risco:** revisar F04/F11 e preparar pedidos F09 sem criar rótulos indevidos. Saída: esquema verificado, fonte, licença/competência e plano de reconciliação.
3. **P1 App de consulta/relato:** formulário, recibo e acompanhamento, sem Bluetooth obrigatório. Saída: piloto com humanos, proteção do denunciante e operação da fila.
4. **P1 Instrumento e comprovante:** estudo NIT-Sinst-020 e PoC autorizada; comprovante pessoal sem presumir acesso a NFC-e. Saída: teste por fabricante/modelo e falhas demonstradas.
5. **P1/P2 Produtos comerciais/institucionais:** dossiê verificável, passaporte do equipamento, frotas e reconciliação, cada qual com business case, contrato e dados.

## 6. Indicadores de desempenho para futuras fases

- Segurança: **0** vazamentos de caso entre papéis e tenants em testes, 100% leituras sensíveis auditadas em escopo testado, tempo de revogação medido, restauração executada.
- Evidência: proporção de pacotes com origem/versão/hash completos; proporção com assinatura verificada; taxa de vínculo de instrumento/estabelecimento confirmada, sem confundir com acurácia metrológica.
- Denúncias: volume recebido, duplicações tratadas, tempo para primeira triagem, backlog, taxa de pedido de complemento e taxa de encaminhamento **como estatística operacional**, não prevalência de fraude.
- Integrações: cobertura temporal, atualizado_em, carga válida versus pendente, amostra abrangida, tipos de evento e falhas.
- Produto: conclusão da jornada do app, utilidade sem Bluetooth, retenção consentida, disponibilidade e custo por caso tratado.

**Não apresentar metas numéricas ainda não medidas como resultados alcançados.**
