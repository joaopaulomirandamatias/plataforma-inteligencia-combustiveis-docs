# Bibliografia e fontes verificadas — pesquisa de combustíveis (2026)

**Corte:** 12/11/2026. Registro inicial e **não exaustivo** de artigos, datasets e referenciais para o [protocolo conceitual v0.3](arquitetura-cinco-camadas-protocolo-v0.3.md). Links editoriais e institucionais verificados; **qualidade e risco de viés ainda sujeitos à leitura integral**. Nenhuma fonte abaixo representa prova de eficácia da arquitetura integrada.

## A. Literatura científica e artigos técnicos

| Código | Referência e acesso | Interesse | Limitação crítica |
| --- | --- | --- | --- |
| A01 | *FD-TamperBoard: A Tampering Features Dataset of Fuel Dispenser PCBs for Illicit Metering Detection*. **Data** 11(5), 107, 07/05/2026. [DOI 10.3390/data11050107](https://doi.org/10.3390/data11050107) | L1/L2/L5: inspeção forense de placas adulteradas; 189 imagens de 5 marcas | Apreensões em ações de fiscalização não formam amostra populacional; imagem de PCB não monitora abastecimento em tempo real |
| A02 | Zuo et al., *Gasoline Adulteration Analysis Based on Raman Spectroscopy and a Multi-Scale Convolutional Neural Network*. **ACS Omega**, publicação online 12/09/2026. [DOI 10.1021/acsomega.6c05800](https://doi.org/10.1021/acsomega.6c05800) | L3: Raman + classificação/regressão; 1.200 espectros de gasolina e quatro adulterantes em 5–30% | Matriz de laboratório e faixas não validam E30 brasileira nem limite legal de traços de metanol |
| A03 | Toledo & Rodembusch, *Optical Molecular Sensing Strategies for Fuel Quality Monitoring: From Polarity-Sensitive Probes to Emerging Portable Technologies for Adulterant Detection*. **ACS Sensors**, 22/08/2026 online. [DOI 10.1021/acssensors.6c01726](https://doi.org/10.1021/acssensors.6c01726) | L3: revisão de sondas ópticas e alternativas portáteis | É revisão secundária; investigar seletividade, custo, robustez e validação de cada estudo primário |
| A04 | Lalhruaitluanga et al., *Exploration of various chemometric methods for analysis of gasoline adulteration*. **Next Research**, jun/2026. [DOI 10.1016/j.nexres.2026.101608](https://doi.org/10.1016/j.nexres.2026.101608) | L3: FTIR, densidade, destilação ASTM D86 e quimiometria | Conferir amostragem, referências analíticas e acessibilidade do texto completo |
| A05 | Junichi Okamoto, *Checking audit trails for measuring instruments using runtime verification*. **OIML Bulletin** LXVII(3), 2026, 20260304. [Página oficial](https://www.oiml.org/en/publications/oiml-bulletin/2026/2026-03/20260304) | L5: verificação formal de sequências de eventos e modificações de parâmetros | Demonstração baseada em instrumentos de pesagem; transferência às bombas é hipótese |
| A06 | Takeaki Kamada, *Preserving Legal-Metrology Integrity in AI-Assisted Logging: Auditable Linking of Recognition and Weighing*. **OIML Bulletin** LXVII(3), 2026, 20260305. [Página oficial](https://www.oiml.org/en/publications/oiml-bulletin/2026/2026-03/20260305) | L1/L5: evidência explícita de como reconhecimento e medição são associados | Pesagem e estudo piloto não estabelecem desempenho em dispensadores de combustível |

**Observação:** outros trabalhos previamente apontados sobre sensores dielétricos, séries multivariadas e estudos de caso IPEM-SP devem ser triados com ficha completa antes da inclusão como evidência extraída. Não usar títulos e resumos isolados para reivindicar desempenho.

## B. Bases de dados e disponibilidade

| Código | Fonte | Grão correto e uso | Precaução |
| --- | --- | --- | --- |
| C01 | [ANP — PMQC](https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/pmqc-programa-de-monitoramento-da-qualidade-dos-combustiveis) | Resultados de **ensaios** de amostras; cobertura publicada 2016–set/2026, pacotes ZIP com CSV/JSON na atualização de 13/10/2026; já catalogada como F02 | Não é base de todos abastecimentos, não gera autuação e não estabelece intenção fraudulenta; confrontar atualização da página com o último mês **efetivamente ingerido** |
| C02 | [ANP — Ações de Fiscalização](https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/acoes-de-fiscalizacao) | Ações e processos, com grupos 1998–2018 e 2019–2025 consultados; candidata a complementar F04 | Autuação é acusação sujeita a contraditório/ampla defesa, não desfecho definitivo; registrar datas de fato, autuação e decisão |
| C03 | [FD-TamperBoard — ScienceDB](https://doi.org/10.57760/sciencedb.31800) e [GitHub](https://github.com/NIM-NMDC/FD-TamperBoard) | **Imagem de placa eletrônica**, anotação de adulteração; recurso científico suplementar | Verificar download real, licença, distribuição por marca e origem antes de qualquer reuso; não criar conector operacional sem projeto separado |
| C04 | [ANP — levantamento semanal de preços](https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/levantamento-de-precos-de-combustiveis-ultimas-semanas-pesquisadas) | Posto/produto/semana, **contexto** já conhecido como F03 | Preço anômalo isolado não prova adulteração |
| C05 | [Catálogo Inmetro e restrições F09](../dados/fontes-inmetro.md) | Portarias de modelo, permissionárias e instrumentos, conforme disponibilidade pública/convênio | Não inventar histórico por bico; conferir LGPD, restrições e identificadores |

**Metadados obrigatórios antes de utilizar qualquer base:** `fonte`, `url_oficial`, `data_consulta`, `versao`, `formato`, `unidade_de_observacao`, `cobertura`, `metodo_de_amostragem`, `rotulos`, `identificador`, `licenca`, `proveniencia`, `limitacoes` e `sha256` **quando efetivamente baixado**. Campo não verificado = **desconhecido**, não inferido.

## C. Normas, manuais e frameworks

| Código | Referência | Interpretação para o estudo |
| --- | --- | --- |
| B01 | [ANP — Cartilha do Posto Revendedor de Combustíveis, 7ª edição, 09/07/2026](https://www.gov.br/anp/pt-br/centrais-de-conteudo/publicacoes/cartilhas-e-guias/cartilha-do-posto-revendedor-de-combustiveis) | Fonte orientativa sobre práticas, qualidade, amostra-testemunha e fiscalização; **não substitui ato normativo** |
| B02 | [OIML R 117:2019](https://www.oiml.org/en/publications/recommendations/117/2019/) | Medição dinâmica de líquidos não aquosos, requisitos/testes; aplicar no Brasil mediante análise do RTM nacional competente |
| B03 | [OIML D 31:2023](https://www.oiml.org/en/files/pdf_d/d031-e23.pdf) | Software legalmente relevante, registro de intervenções e segurança de parâmetros |
| B04 | [NIST SP 800-82 Rev. 4 — Initial Public Draft, 21/09/2026](https://csrc.nist.gov/pubs/sp/800/82/r4/ipd) | Contexto de ameaças e mitigação OT; **minuta pública**, comentários até 30/11/2026, não versão final |
| B05 | [OIML TC8/SC3 — revisão limitada da R117, proposta aprovada em 25/07/2026](https://www.oiml.org/en/tc-sc-pg/scinfo_view?idsc=14) | Item de acompanhamento; projeto de revisão **não** altera automaticamente a edição vigente |
| B06 | [ANP — orientação de uso e metadados PMQC](https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/pmqc-programa-de-monitoramento-da-qualidade-dos-combustiveis) | Unidade de observação, desenho do monitoramento e variáveis |
| B07 | [ANP — orientações de interpretação das ações fiscalizatórias](https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/acoes-de-fiscalizacao) | Distinção entre registro administrativo, sanção e resultado definitivo |

**Portarias Inmetro/ANP brasileiras:** seguir o [catálogo F08](../dados/catalogo-fontes.md) e o [levantamento Inmetro](../dados/fontes-inmetro.md) com versão e vigência; não declarar que OIML/NIST são leis brasileiras.

## D. Próximas ações para a revisão

- [ ] Conferir textos integrais de A01–A06 e produzir fichas com método, tamanho amostral, base de comparação, métricas e risco de viés.
- [ ] Verificar permissão/licença e recuperação efetiva dos arquivos C03.
- [ ] Versionar as estratégias de busca, datas e seleção PRISMA-ScR, PRISMA-S e PRESS.
- [ ] Completar matriz `ameaça × evidência × tecnologia × incerteza × falso alarme × contexto × restrição`.
- [ ] Documentar leis, RTMs e composição de gasolina/diesel com ato, vigência e data de cada experimento futuro.
- [ ] Tratar a atualização pública de C01/C02 como **novo achado documental**, não como prova de ingestão, backfill, suporte do backend ou atualização de produção.

**Nota de governança:** a PIC v1 continua sendo a fonte canônica do que foi entregue; esta página registra fontes candidatas para **pesquisa**, sem incorporar software nem validar modelo.

## D. Protocolos e interfaces de bombas inteligentes (adendo 12/11/2026)

Estas referências complementam a revisão para a futura função do [PIC Verifica](../produto/pic-verifica-app.md). **Não** demonstram Bluetooth disponível em qualquer bomba, acesso irrestrito por aplicativo terceiro ou streaming contínuo. Antes de desenvolver, verificar edição, alteração vigente, marca, modelo e permissões.

| Documento/fonte | Tipo | Pergunta de pesquisa e cautela |
| --- | --- | --- |
| [Portaria Inmetro nº 227/2022](https://www.ipem.pr.gov.br/sites/default/arquivos_restritos/files/documento/2022-06/portaria_227_26_05_2022_bombas_medidoras_nova_julho_2022.pdf) e alterações aplicáveis | Regulamentação brasileira | Requisitos de interface de verificação, registro do último abastecimento, integridade e software; conferir o texto consolidado/alterações antes de alegar obrigação |
| [NIT-Sinst-020 — catálogo de software do Inmetro](https://www.gov.br/inmetro/pt-br/assuntos/metrologia-legal/documentos-normativos-para-metrologia-legal/assunto/software) | Procedimento técnico | Identificar protocolo serial, transporte, autenticação, pacotes e permissões; **SPP e BLE/GATT não são equivalentes** |
| [Certificação digital de objetos metrológicos — Inmetro](https://www.gov.br/inmetro/pt-br/assuntos/metrologia-legal/certificacao-digital) | Infraestrutura de confiança | Estudar certificados OM-BR, NIT-Dmtic-009 e procedimentos de validação criptográfica |
| [IFSF — International Forecourt Standards Forum](https://www.ifsf.org/) | Padronização de integração de pista | Avaliar API/controlador para dados operacionais **mediante contrato/permissão**; não confundir com interface Bluetooth metrológica |
| [Wertco Assistant na Google Play](https://play.google.com/store/apps/details?id=com.companytec.wertco_bluetooth) | Exemplo de aplicativo de fabricante | Investigar como o fabricante implementa a NIT-Sinst-020 e que serviços são públicos/restritos; não pressupor API aberta |
| [IPEM-SP — Bombas Seguras](https://www.ipem.sp.gov.br/index.php/servicos/consultas/bombas-seguras) | Serviço público | Identificação de instalações de bombas certificadas; não presumir app público já disponibilizado |

**Rastreabilidade da pesquisa:** para cada bomba, construir ficha com marca, modelo, nº da Portaria de Aprovação de Modelo, versão de firmware, data e estado da certificação, transportes, comandos **somente leitura** autorizados, tipo do pacote e certificado, limitação, riscos de área classificada, versão da norma e evidências documentais. **Teste só em bancada autorizada e com avaliação de segurança apropriada.**

A função de **manifestação** é canal separado de relato do usuário (não dado metrológico): ingresso em domínio privado e análise humana. Não utilizar relatos como rótulos positivos de fraude em treino de modelos ou como critério de reputação.
