# PIC Verifica — aplicativo móvel de abastecimento e relatos

**Situação:** proposta incorporada ao escopo futuro da Plataforma de Inteligência de Combustíveis (PIC), **sem implementação, piloto, aprovação metrológica ou disponibilização nas lojas**.  
**Data:** 12/11/2026. **Versão do desenho:** 0.1.  
**Dono de produto proposto:** PIC Gestão; contratos, segurança, pesquisa e governança em `plataforma-inteligencia-combustiveis-docs`.

## Visão do produto

O **PIC Verifica** é um canal mobile único, com três capacidades complementares:

1. **Consultar** ficha de posto e informações públicas existentes na PIC, com fonte, data, cobertura e natureza do dado.
2. **Verificar abastecimento** com leitura **somente autorizada** de bombas compatíveis, via interface metrológica Bluetooth ou integração contratada com controlador/sistema de pista. Comparar registros **quando houver correspondência explícita** com a PIC. O pacote assinado do último abastecimento não garante telemetria contínua nem veracidade do volume físico.
3. **Relatar ocorrência / possível irregularidade**, enviando relato, evidências opcionais e vínculo com posto/abastecimento para uma **fila privada de manifestações** na PIC. A equipe de análise com acesso específico revisa o caso; o relato nunca vira automaticamente fato oficial, fraude comprovada, pontuação de risco ou conteúdo da ficha pública.

**Princípio:** o aplicativo não substitui medição independente, fiscalização, perícia, decisão regulatória ou canal oficial do órgão; deve orientar o usuário quanto aos canais oficiais e aos limites da análise feita pela PIC.

## Personas e permissão

| Perfil | Pode fazer | Não pode |
| --- | --- | --- |
| Pessoa usuária / consumidor | Ver ficha, solicitar conexão manual a bomba compatível, enviar relato e acompanhar seu próprio protocolo | Ver relatos de terceiros, acessar dados privados de postos, alterar bomba |
| Analista de manifestações PIC | Ler relatos **atribuídos por função/finalidade**, pedir complementação, classificar evidências e registrar triagem | Declarar fraude comprovada ou publicar conteúdo sensível |
| Supervisor responsável | Revisar escalonamento, liberar encaminhamento a órgão competente nos termos institucionais e registrar decisão auditada | Expor denunciante a posto/parceiro ou remover trilha |
| Fiscal/órgão parceiro | Acessar caso **apenas com concessão expressa**, finalidade e prazo; consultar evidências pertinentes | Acessar fila geral por ser parceiro; obter dados além do acordo |
| Gestor do posto | Consultar **somente** eventual comunicação formal permitida pelo rito de contraditório | Acessar identidade/anexos do denunciante ou fila da plataforma |
| Administrador técnico | Operar infra e métricas agregadas sem acesso ao conteúdo por padrão | Autoatribuir leitura de manifestações sem autorização |

## Jornada A — consulta da bomba (planejada)

1. Usuário escolhe posto (não deduzir associação pela proximidade), escolhe `Verificar abastecimento` e vê aviso de compatibilidade e limites.
2. App solicita permissões Bluetooth apropriadas somente após ação explícita. Identifica dispositivo e confirma visualmente modelo/identificador físico; impede conexão automática ambígua.
3. Adaptador em modo leitura usa apenas comandos publicamente documentados e autorizados pelo fabricante/protocolo. Perfil Bluetooth clássico serial e BLE/GATT **não são intercambiáveis**.
4. Salva pacote **bruto**, hash, fonte, identificador do instrumento, instante local/recebimento, estado de verificação de assinatura/certificado e versão do decodificador. Falha de verificação é exibida, nunca silenciosamente tratada como sucesso.
5. Exibe `volume informado no instrumento`, `registro íntegro/verificável ou não verificável`, sem afirmar que volume físico foi entregue.
6. Faz comparação **contextual** com F01 (identidade autorizada), F02 (ensaio PMQC), F03 (preços), F08/F09 (atos/metrologia, quando disponíveis), explicitando **diferença de granularidade, datas e cobertura**; não calcular coincidência de transação com amostra PMQC.

**Tempo real (canal separado):** apenas integração por API/controlador de pista com permissão contratual, capacidade do equipamento e provas em bancada. Se indisponível, somente leitura pós-abastecimento; jamais prometer streaming Bluetooth por padrão.

## Jornada B — relato de ocorrência (funcionalidade solicitada)

1. Usuário seleciona `Relatar problema` a partir da ficha do posto, da verificação do abastecimento ou do menu principal.
2. Informa tipo autoidentificado: **quantidade**, **qualidade**, **preço/cobrança**, **conduta/atendimento**, **outro**. São categorias de **relato**, não rótulos oficiais de fraude.
3. Escolhe posto por `posto_id` confirmado ou informa dados mínimos para vínculo **pendente**; indica data aproximada e, opcionalmente, bomba/bico, produto, valor e volume **declarados pelo usuário**, descrição e anexos.
4. Pode anexar comprovante, foto/vídeo e **referência explícita ao pacote da bomba capturado pelo próprio app**; manter original, hash e proveniência, mas declarar que imagem/anexo pode ser incorreto, incompleto ou manipulado.
5. Antes do envio, app informa finalidade, tratamento de dados, canais oficiais e limites; oferece **identificação opcional quando viável juridicamente** ou contato para retorno, separando anonimato, confidencialidade e notificação. Não prometer sigilo absoluto.
6. Submete via **endpoint privado de ingestão** `POST /v1/manifestacoes` **(contrato proposto, não implementado)**; API valida tamanho, tipo, malware, rate limit, antiabuso, consentimento/base legal e idempotência. Retorna protocolo opaco aleatório e recibo.
7. Plataforma grava `manifestacao_id`, conteúdo em armazenamento segregado, vínculo canônico quando validado, estado e **trilha de auditoria**; **não** insere relato como fato oficial na base pública e não envia texto bruto a ML/IA automaticamente.
8. **Fila reservada** no console/sala institucional: analista designado recebe casos por escopo; realiza triagem humana e registra justificativas, evidências, hipótese alternativa, pedido de complementação e escalonamento.
9. Titular acompanha apenas seu protocolo (com autenticação ou token de acompanhamento de uso restrito, a decidir) e recebe status neutros: `recebido`, `em análise`, `necessita informações`, `encaminhado`, `concluído`. Não revelar identidade de analistas, conclusões protegidas ou dados de terceiros.
10. Encaminhamento externo **não automático**, apenas a órgão efetivamente autorizado com finalidade, política, base legal/convênio e registro de transferência. A PIC não se apresenta como canal oficial sem acordo formal.

### Fluxo de análise e estados internos propostos

`recebida → validacao_inicial → triagem → (complementacao | em_analise) → (encaminhada | concluida | arquivada_fundamentada)`.

- `validacao_inicial`: separar spam, conteúdo vedado, ameaça imediata e anexo suspeito; registrar bloqueios e possibilidade de reenvio sem apagar trilha.
- `triagem`: vincular posto/instrumento apenas por dados validados; classificar `relato_sem_corroboração`, `relato_com_evidencia_anexa`, `evidencia_correspondente` **sem converter em fraude**.
- `encaminhada`: identificar destinatário, acordo, escopo, base legal, data e recibo do órgão; a análise fiscalizatória pertence à autoridade.
- `concluida`/ `arquivada_fundamentada`: conservar razões, restrições de retenção e ciência ao usuário quando aplicável; permitir revisão controlada.

### Modelo mínimo da manifestação

| Campo | Observação |
| --- | --- |
| `manifestacao_id`, `protocolo_publico`, `schema_version`, `criado_em` | IDs não enumeráveis, UTC e versão |
| `categoria_relato`, `descricao`, `data_evento_aproximada` | Declarações do usuário **sem validação de mérito** |
| `posto_id?`, `vinculo_estado`, `dispositivo_id?`, `bico?` | Associação segura e justificada, ou `nao_confirmada` |
| `evento_bomba_id?`, `pacote_assinado_ref?`, `resultado_verificacao?` | Referência ao evento, não prova automática do fato alegado |
| `anexos[]` | ID de objeto privado, hash, MIME real, antivírus, tamanho; metadados EXIF minimizados |
| `reportante_ref?`, `canal_retorno?`, `preferencia_contato` | Protegidos em cofre/domínio privado separado |
| `fonte=usuario`, `status`, `historico[]`, `politica_retencao` | Natureza do registro, decisões humanas e trilha |

**Nunca incluir** texto livre, anexos ou dados do reportante em endpoints públicos, indexação, alertas de massa, telemetry de frontend, indexação de busca ou dados analíticos sem base legal e tratamento específico.

## Segurança, privacidade, prevenção de abuso

- **Deny-by-default**, papéis explícitos `analista_manifestacoes`, `supervisor_manifestacoes` e `auditor_manifestacoes`, com decisão ABAC por finalidade, território, órgão, caso e vigência; **auditoria de leitura**, pesquisa, exportação, encaminhamento e mudança de estado.
- Segregar conteúdo da manifestação do núcleo oficial e do `posto_id` público: vínculo é referência autenticada, não duplicação e publicidade. Contato do denunciante é separado do texto e de anexos.
- Retenção, exclusão, legal hold, controlador/operador, canal de exercício de direitos e regras de compartilhamento dependem de **RIPD e parecer jurídico adicionais** antes de produção.
- Proteção contra reportes massivos/falsos, instruções maliciosas em anexos, exploração de arquivos, vazamento por tokens de protocolo, solicitação indevida de localização e material pessoal excessivo. Desabilitar geolocalização em segundo plano.
- Usuário não deve registrar pessoa identificável desnecessariamente; oferecer orientação para ocultar dados de terceiros. Para urgência ou risco imediato, orientar procurar o órgão competente.
- A plataforma apresenta **`relato enviado por usuário; não verificado`**, e mantém o histórico privado. A eventual mensagem ao posto/órgão usa contraditório e minimização, sem revelar identidade do reportante por padrão.
- Rate limit e CAPTCHA proporcional, validação robusta de conteúdo, escaneamento de anexos, armazenamento com criptografia e URLs temporárias, idempotência/antirreplay e trilha de acesso.

## Telas e funcionalidades previstas

| Tela | Conteúdo | Status |
| --- | --- | --- |
| Início, mapa e ficha | Fonte, data, filtros, histórico público, acesso a verificação e relato | Planejada no app G6 |
| Verificar abastecimento | Compatibilidade, Bluetooth, captura, integridade, comparação contextual | Pesquisa/PoC autorizada, sem implementação |
| Relatar ocorrência | Categoria, posto, data, descrição, comprovante, pacote opcional, privacidade | **Planejado** |
| Protocolo e acompanhamento | Recibo, status neutro, solicitação de complemento, cancelamento quando cabível | **Planejado** |
| Fila de manifestações (console) | Triagem, atribuição, RBAC/ABAC, revisão, encaminhamento, auditoria | **Planejado, restrito** |

## Critérios de aceite (a comprovar em testes)

- [ ] Anonimato/confidencialidade e tratamentos jurídicos claros; nenhuma promessa técnica sem evidência.
- [ ] Reporte sem dispositivo Bluetooth deve funcionar, com posto confirmado ou vínculo pendente.
- [ ] Somente ações de leitura permitidas para bombas; sem comando de parametrização, reparo ou reset.
- [ ] Falha de assinatura, modelo não suportado, Bluetooth desligado e rede indisponível não geram `validado`.
- [ ] Reporte sem anexos pode ser recebido; com anexos passa por quarentena e controle de tamanho/MIME.
- [ ] Vínculo posto/manifestação não gera publicação no portal público; nenhum relato muda F02/F04 nem pontuação do posto.
- [ ] Testes negativos: consumidor A não lê protocolo B; gestor do posto não acessa denúncias; parceiro sem concessão não vê a fila; admin técnico não lê conteúdo por padrão.
- [ ] Auditoria de acesso e mudança de estado; justificativa humana e consentimento/base legal documentados.
- [ ] Simulações de spam, anexos maliciosos, token de protocolo descoberto, duplicação e falha de rede.
- [ ] Critério de encaminhamento a órgão parceiro validado por jurídico e acordo institucional; sem encaminhamento automático.

## Implantação por gates

- **G6-A:** app consulta pública, ficha, mapa; saída sem conta obrigatória.
- **G6-B (novo):** módulo relato/protocolo com backend privado e console de triagem; pode evoluir sem Bluetooth.
- **G8-M (novo):** módulo de observação metrológica read-only Bluetooth / gateway quando compatível, com laboratório e contrato de equipamento. Operação online é escopo separado e condicional.
- **G9-P (proposto):** piloto institucional de triagem e evidência associada; exige governança, operador responsável, procedimento de resposta, treinamento e testes de privacidade.

**Próximas decisões:** titularidade e privacidade dos dados; quem recebe denúncias; se aceitamos envio anônimo; prazos de atendimento; critérios de parceria com órgãos; fabricante/modelo para laboratório; avaliação de viabilidade Android Bluetooth serial vs BLE.
