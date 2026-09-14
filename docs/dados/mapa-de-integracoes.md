# Mapa de integrações — o que falta, por órgão e empresa

*Verificação de existência na fonte em 2026-09-14. Convenção do [catálogo de fontes](catalogo-fontes.md): ✔ verificado na fonte (página ou recurso existe; o layout só quando dito) · ⚠ conhecido, ainda não verificado · 🔒 restrito (convênio, contrato, adesão ou base legal). Versão para compartilhar: [PDF](../apresentacao/mapa-de-integracoes.pdf).*

## As seis perguntas que uma plataforma completa responde

| Pergunta | O que é | Quem detém o dado |
|---|---|---|
| **Quem é** | identidade do posto e de quem o controla | ANP cadastro · Receita CNPJ · Juntas · GEO |
| **Quanto cobra** | preço e sua posição na cadeia de custo | ANP SLP · produtores · distribuição · apps |
| **Quanto entrega** | quantidade — metrologia e volume | Inmetro/Ipem · SEFAZ NF-e/NFC-e · cartões-frota · telemetria · automação |
| **O que entrega** | qualidade do produto | ANP PMQC · auditorias das distribuidoras |
| **O que o Estado já constatou** | conformidade e sanções | ANP fiscalização · Ipem autos · SEFAZ cassações · CGU · Procon |
| **Demanda e território** | denominadores | SENATRAN frota · IBGE · ANP vendas |

Cada fonte abaixo serve a pelo menos uma dessas perguntas; o valor de uma integração é medido por quantas perguntas ela fecha para o mesmo `posto_id`.

## Estado atual

No ar, com API pública e site: F01 cadastro, F02 PMQC, F03 preços e GEO-ANP. Catalogadas sem conector: F04 fiscalização ANP, F07 IBGE, F08 normativo, F09 Ipem (convênio), F10 SEFAZ (fase 3). Conector pronto com carga desligada: F05 Receita. Quebrada: F06 Sindec (host fora do ar). Candidata: F11 oficinas permissionárias do Inmetro.

## 1. Órgãos federais

| Órgão / empresa | Dados | Integração | Acesso | Destrava | Na plataforma hoje |
|---|---|---|---|---|---|
| **ANP** | Cadastro de revendedores, PMQC (qualidade), SLP (preços semanais), georreferenciamento dos revendedores | Pull versionado de dados abertos | Público — em produção ✔ | Identidade, preço e qualidade do posto | No ar: F01, F02, F03, GEO-ANP |
| **ANP** | Ações de fiscalização do abastecimento (autos por agente econômico) e multas aplicadas | Dados abertos mensais, defasagem de 2 meses; arquivos brutos 1998–2018 e 2019–2025 | Público — página e recursos existem; layout não lido ✔ | Rótulo de conformidade e reincidência. Auto não é julgamento: registrar data do fato e da decisão | Catalogada (F04), sem conector |
| **ANP** | Distribuidores autorizados (filiais), contratos de cessão de espaço, pontos de abastecimento, TRR | Dados abertos (CSV) | Público — recursos existem ✔ | Cadeia de oferta: quem abastece quem | Não |
| **ANP** | Vendas de derivados por UF e município; movimentação de derivados; preços de produtores e importadores | Dados abertos | Público — páginas existem; layout não lido ✔ | Denominadores de volume e primeiro elo da cadeia de custo | Não |
| **ANP** | Sistema de Transparência na Distribuição (STD, Decreto 12.930/2026): operações agregadas a cada 14 dias | Painel dinâmico | Público — página existe; dados brutos a confirmar ⚠ | Contexto de oferta sob regime emergencial | Não |
| **ANP** | SIMP — movimentação de produtos declarada por cada agente | Convênio | Restrito 🔒 | Volume por distribuidora e base; reconciliação com o varejo | Não |
| **ANP** | Reclamações e denúncias contra postos (canal próprio) | Não estruturado; LAI agregada | Restrito 🔒 | Sinal precoce | Não |
| **Inmetro / RBMLQ-I (Ipem)** | Verificações de bomba por bico: erro, resultado, lacres, oficina executora, intervenções, ano de fabricação; autos de infração; preços de campo do SGI | Convênio; LAI agregada por CNPJ; consulta pública do PDA 2026–2028 | Restrito — confirmado ausente do público 🔒 | Gabarito metrológico — a fonte mais valiosa do sistema | Catalogada (F09) |
| **Inmetro / RBMLQ-I** | Oficinas permissionárias (JSON por UF); Portarias de Aprovação de Modelo (SIL-PAM); consolidado de execução por UF | Pull mensal / diário | Público — medido na fonte ✔ | Quem intervém em bomba; dimensão marca/modelo; intensidade fiscalizatória | F11 candidata; F08 |
| **Inmetro / PSIE** | Validação de certificado de verificação por número | Consulta pontual | Público — existe; comportamento não testado ⚠ | Posto idôneo sobe o próprio certificado e a plataforma confere — gabarito de baixo para cima | Não |
| **Receita Federal** | Dados Públicos CNPJ: empresas, estabelecimentos, QSA, situação, CNAE, Simples/MEI | Dump mensal | Público ✔ | Grafo societário — só o presente | Conector existe (F05); carga cheia desligada |
| **Receita Federal** | CPF completo do sócio; NF-e modelo 55 (compras do posto à distribuidora) | Via órgão parceiro; base legal escrita | Restrito 🔒 | Identidade da pessoa; volume comprado por posto | Não — o RIPD prevê a dimensão PF |
| **Senacon / MJ** | Sindec (Procons) e consumidor.gov.br, por CNPJ | Pull do catálogo | Sindec: host não resolve. consumidor.gov.br: página existe; layout não lido ⚠ | Sinal precoce de reclamação | F06 quebrada; substituto a verificar |
| **CGU** | CEIS, CNEP e CEPIM — empresas sancionadas ou inidôneas, por CNPJ | Dados abertos do Portal da Transparência | Público — página de download existe; layout não lido ✔ | Flag de conformidade administrativa | Não |
| **SENATRAN** | Frota de veículos por município e tipo | Dados abertos mensais | Público — página existe; layout não lido ✔ | Denominador de demanda: litros esperados por município | Não |
| **IBGE** | Malha municipal, população, renda, PIB municipal | Anual | Público  | Território; estratos de fairness | Catalogada (F07) |
| **Imprensa Nacional** | Atos normativos ANP e Inmetro (DOU) | Varredura diária | Público  | RAG regulatório; vigência de cada regra | Catalogada (F08) |
| **CADE** | Processos de cartel em revenda de combustíveis | Documental, não estruturado | Público  | Contexto de mercado local — preço uniforme não é concorrência | Não — contexto |

## 2. Órgãos estaduais

| Órgão / empresa | Dados | Integração | Acesso | Destrava | Na plataforma hoje |
|---|---|---|---|---|---|
| **SEFAZ (cada UF)** | NFC-e modelo 65 — cada venda na bomba: volume, produto, valor, hora | Base legal escrita (sigilo fiscal) | Restrito 🔒 | Registro autoritativo de venda; reconciliação comprado × vendido × capacidade de tanque | Catalogada (F10, fase 3) |
| **SEFAZ-SP e congêneres** | Cassação da inscrição estadual de postos por combustível fora de especificação (lei estadual) | DOE e lista pública | Público — endereço não localizado nesta verificação ⚠ | Rótulo público forte em SP, sem convênio | Não |
| **SEFAZ / Sintegra** | Situação cadastral da inscrição estadual por CNPJ | Consulta pontual | Público por consulta ⚠ | Posto com IE suspensa ou cassada operando | Não |
| **Procons estaduais** | Reclamações e rankings próprios | PDF / HTML | Público, pouco estruturado  | Complemento à F06 | Não |
| **Órgãos ambientais (CETESB e congêneres)** | Licença de operação; idade e troca de tanques subterrâneos | Consulta pública | Público ⚠ | Integridade física; posto operando sem licença | Não |
| **Corpo de Bombeiros** | AVCB vigente | Consulta | Público ⚠ | Conformidade de segurança — baixa prioridade | Não |
| **Juntas Comerciais** | Histórico societário — o que a Receita não dá (só o presente) | Certidão paga ou convênio | Pago 🔒 | Rotatividade societária real | Não |

## 3. Empresas do setor (por contrato)

| Órgão / empresa | Dados | Integração | Acesso | Destrava | Na plataforma hoje |
|---|---|---|---|---|---|
| **Distribuidoras / bandeiras** | Contratos de bandeira e desembandeiramentos; volume entregue por posto; auditorias de qualidade da rede; lacres de tanque | API ou arquivo por contrato | Parceria — clientes pagantes no projeto v1 🔒 | Volume do lado da oferta sem esperar a SEFAZ; monitoramento da rede | Não |
| **Cartões-frota (Ticket Log/Edenred, Sem Parar, Alelo Frota e outros)** | Transações na bomba: litros, preço, CNPJ do posto, placa, hora | API por contrato | Parceria 🔒 | O sinal privado mais rico de quantidade: abastecimento acima da capacidade do tanque do veículo é evidência direta de bomba fora de medida | Não |
| **Telemetria embarcada (Sascar, Omnilink e outros)** | Nível de tanque e GPS por veículo | Stream por contrato | Parceria 🔒 | Litros recebidos × litros pagos por abastecimento — gatilho do ADR-006 (streaming) | Não |
| **Instituto Combustível Legal, IBP, sindicatos** | Estudos, canal de denúncia, estimativas setoriais | Documental; parceria | Misto  | Legitimidade setorial; calibração de estimativas | Não |
| **Petrobras e demais produtores** | Preço de venda às distribuidoras por base e data | Página pública | Público — página existe; estrutura não lida ⚠ | Primeiro elo da cadeia de custo | Não |
| **Apps de preço e de mapas** | Preço promocional relatado por consumidores | API comercial | Pago, termos restritivos 🔒 | Terceiro critério do método de seleção de alvos do Ipem-SP | Lacuna registrada |

## 4. Dado do próprio posto (por adesão)

| Órgão / empresa | Dados | Integração | Acesso | Destrava | Na plataforma hoje |
|---|---|---|---|---|---|
| **Automação de pista (Companytec, Sinergy, Gilbarco/Wayne e outros)** | Encerrantes por bico, vendas por bico, alarmes | API ou exportação por adesão | Adesão do posto 🔒 | Quantidade medida na origem; base do selo de transparência auditável | Não |
| **Medição eletrônica de tanque** | Nível, entradas, perdas | Idem | Adesão do posto 🔒 | Reconciliação estoque × entrada × venda | Não |
| **LMC — Livro de Movimentação de Combustíveis** | Estoque diário, entradas e vendas por produto | Arquivo por adesão (ou via ANP) | Adesão do posto 🔒 | Balanço volumétrico oficial do posto | Não |
| **Certificados de verificação do Inmetro em papel** | Número, data, resultado | Upload + validação no PSIE | Adesão do posto 🔒 | Gabarito parcial vindo do posto idôneo | Não |

## 5. Referência e apoio

| Órgão / empresa | Dados | Integração | Acesso | Destrava | Na plataforma hoje |
|---|---|---|---|---|---|
| **OpenStreetMap / malha viária** | Rotas e vias | Público (ODbL) | Público  | Setor de frotas: posto na rota | Não |
| **Base de CEP (ViaCEP / DNE)** | Normalização de endereço | API pública ou base paga | Público / pago  | Resolução de entidade — a F11 não tem CNPJ | Não |
| **Catálogo de veículos** | Capacidade de tanque por modelo | Referência | Público ⚠ | Regra: abasteceu mais que o tanque | Não |
| **RAIS / CAGED** | Empregados por CNPJ | Agregado público; microdado restrito | Misto  | Porte do posto | Não |

## Ordem de prioridade

1. **Ipem/Inmetro por convênio (F09)** — sem ele não há gabarito de quantidade; o pedido já está afiado no catálogo.
2. **SEFAZ: NF-e e NFC-e (F10)** — a reconciliação comprado × vendido é o único fechamento volumétrico autoritativo; exige base legal antes do primeiro byte.
3. **Cartões-frota** — o mesmo fechamento pelo lado privado, sem sigilo fiscal, com o sinal “acima da capacidade do tanque”; é também o setor de frotas pagando.
4. **ANP fiscalização e multas (F04), CGU CEIS/CNEP, SEFAZ-SP cassações** — três rótulos públicos — os dois primeiros com páginas e recursos confirmados nesta verificação.
5. **SENATRAN frota por município** — denominador de demanda; barato e público.
6. **consumidor.gov.br no lugar do Sindec; F11 oficinas como conector pequeno** — restaura o sinal precoce e abre o único dado do Inmetro por estabelecimento.
7. **Distribuidoras** — volume entregue e monitoramento da rede, por contrato.
8. **Telemetria e automação de pista** — só com adesão real; é o gatilho de streaming previsto no ADR-006.

## Fila de verificação na fonte

Itens ⚠ acima, na ordem em que valem o esforço: layout e granularidade por CNPJ dos dados de fiscalização e multas da ANP; lista de cassações da SEFAZ-SP (o endereço tentado respondeu 404); layout do consumidor.gov.br; CEIS/CNEP; frota SENATRAN; validação de certificado no PSIE; STD; preços de produtores; licenças ambientais. Cada item verificado sobe para o catálogo com data, como as fontes do Inmetro em [fontes-inmetro](fontes-inmetro.md).

## O que não muda com nenhuma integração

Nenhuma fonte, pública ou restrita, autoriza a plataforma a afirmar conduta: ela mostra fato, fonte e data e recomenda verificação; quem conclui é o órgão competente ([ADR-005](../arquitetura/adr/), [política de linguagem](../agentes/politica-de-linguagem.md)). Fontes restritas entram só com base legal escrita e desenho de minimização antes do primeiro byte ([RIPD](../conformidade/lgpd/ripd.md)).
