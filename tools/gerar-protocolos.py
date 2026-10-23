#!/usr/bin/env python3
"""Gera public/data/referencias.json e public/data/protocolos.json (revisão de 17/10/2026).
Regra: só entram valores encontrados nas fontes listadas. O que não foi conferido é retirado
ou marcado explicitamente em 'verification'.
Uso (na raiz do projeto): python3 tools/gerar-protocolos.py ."""
import json, sys, pathlib
ROOT = pathlib.Path(sys.argv[1])
DATE = "2026-10-17"

REFS = [
 dict(id="levecke2011", short="Levecke et al., 2011", citation="Levecke B, Behnke JM, Ajjampur SSR, Albonico M, Ame SM, Charlier J, et al. A comparison of the sensitivity and fecal egg counts of the McMaster egg counting and Kato-Katz thick smear methods for soil-transmitted helminths. PLoS Negl Trop Dis. 2011;5(6):e1201.", doi="10.1371/journal.pntd.0001201", pmid="21695104", access="texto completo lido"),
 dict(id="requena2013", short="Requena-Méndez et al., 2013", citation="Requena-Méndez A, Chiodini P, Bisoffi Z, Buonfrate D, Gotuzzo E, Muñoz J. The laboratory diagnosis and follow up of strongyloidiasis: a systematic review. PLoS Negl Trop Dis. 2013;7(1):e2002.", doi="10.1371/journal.pntd.0002002", pmid="23350004", access="texto completo lido"),
 dict(id="rodrigues2024", short="Rodrigues et al., 2024", citation="Rodrigues JGM, Miranda GS, Camelo GMA, Rodrigues VF, Silva JKAO, Gouveia CBG, et al. Modifications to the parasitological technique of Rugai increase the diagnostic sensitivity for strongyloidiasis. Parasitol Res. 2024;123(1):101.", doi="10.1007/s00436-023-08111-y", pmid="38233532", access="resumo lido"),
 dict(id="goncalves2023", short="Gonçalves et al., 2023", citation="Gonçalves AAS, Lopes CA, Levenhagen MA, Gonzaga HT, Oliveira LCM, Costa-Cruz JM. Multiple stool sampling and specific parasitological technique are crucial to diagnose strongyloidiasis in alcoholic patients. Acta Parasitol. 2023;68(3):718-722.", doi="10.1007/s11686-023-00700-2", pmid="37531007", access="resumo lido"),
 dict(id="ines2016", short="Inês et al., 2016", citation="Inês EJ, et al. Concordance between the zinc sulphate flotation and centrifugal sedimentation methods for the diagnosis of intestinal parasites. Biomédica. 2016;36(4):519-524.", url="https://www.redalyc.org/pdf/843/84348515005.pdf", access="texto lido via leitor automático (trechos de métodos e resultados)"),
 dict(id="barretto1962", short="Barretto, 1962", citation="Barretto MP. Diagnóstico da amebíase crônica. II. Estudo comparativo da eficiência do método da centrífugo-flutuação no sulfato de zinco, em amostras sucessivas de fezes normalmente emitidas, e do exame de fezes obtidas mediante catártico, usados sós ou combinadamente. Rev Inst Med Trop São Paulo. 1962;4:1-11.", pmid="13865253", url="https://revistas.usp.br/rimtsp/article/download/202337/186388/578731", access="texto lido via leitor automático (trechos de métodos e resultados)"),
 dict(id="katz1972", short="Katz et al., 1972", citation="Katz N, Chaves A, Pellegrino J. A simple device for quantitative stool thick-smear technique in Schistosomiasis mansoni. Rev Inst Med Trop São Paulo. 1972;14(6):397-400.", pmid="4675644", access="registro conferido no PubMed (resumo indisponível; texto não lido)"),
 dict(id="santos2010", short="Santos et al., 2010", citation="Santos HLC, Bandea R, Martins LAF, de Macedo HW, Peralta RHS, Peralta JM, et al. Differential identification of Entamoeba spp. based on the analysis of 18S rRNA. Parasitol Res. 2010;106(4):883-888.", doi="10.1007/s00436-010-1728-y", pmid="20169364", access="resumo lido"),
 dict(id="roshdy2017", short="Roshdy et al., 2017", citation="Roshdy MH, Abd El-Kader NM, Ali-Tammam M, Fuentes I, Mohamed MM, El-Sheikh NA, Rubio JM. Molecular diagnosis of Entamoeba spp. versus microscopy in the Great Cairo. Acta Parasitol. 2017;62(1):188-191.", doi="10.1515/ap-2017-0022", pmid="28030342", access="resumo lido"),
 dict(id="cdc_pinworm", short="CDC DPDx (oxiúro)", citation="CDC. DPDx — Laboratory Identification of Parasites of Public Health Concern: Pinworm (diagnostic procedure). Centers for Disease Control and Prevention.", url="https://www.cdc.gov/dpdx/diagnosticProcedures/other/pinworm.html", access="página lida em 17/10/2026"),
 dict(id="cdc_concentration", short="CDC DPDx (concentração)", citation="CDC. DPDx — Stool specimens: concentration procedures (centrifugal flotation). Centers for Disease Control and Prevention.", url="https://www.cdc.gov/dpdx/diagnosticprocedures/stool/specimen_cf.html", access="página lida em 17/10/2026"),
 dict(id="pho_enterobius", short="Saúde Pública de Ontário (Enterobius)", citation="Public Health Ontario. Enterobius (Pinworm) — Microscopy. Test Information Index.", url="https://www.publichealthontario.ca/en/Laboratory-Services/Test-Information-Index/Enterobius", access="página lida em 17/10/2026"),
 dict(id="pop_ufgd", short="POP.UACAP.049 (2025)", citation="Hospital Universitário (UACAP). POP.UACAP.049 — Parasitologia: exame parasitológico de fezes (EPF), versão 03, 04/11/2025. EBSERH/Gov.br.", url="https://www.gov.br/hubrasil/pt-br/hospitais-universitarios/regiao-centro-oeste/hu-ufgd/acesso-a-informacao/pops-protocolos-e-processos/gad/pop-uacap-049-parasitologia-exame-parasitologico-de-fezes-epf-v-3.pdf", access="documento lido via leitor automático (apenas a seção de sedimentação foi extraída)"),
 dict(id="chaves2014", short="Chaves, 2014", citation="Chaves LA. Comparação dos métodos parasitológico, imunológico e molecular em amostras de fezes de ratos (Rattus norvegicus Wistar) imunossuprimidos experimentalmente infectados por Strongyloides venezuelensis. Dissertação (Mestrado), Universidade Federal de Uberlândia; 2014.", url="https://repositorio.ufu.br/bitstream/123456789/16707/1/ComparacaoMetodosParasitologico.pdf", access="trecho de métodos lido via leitor automático"),
 dict(id="sop_katzkatz", short="SOP Kato-Katz", citation="SOP on Kato-Katz technique (procedimento operacional institucional). Disponível em med.uwu.ac.lk.", url="https://med.uwu.ac.lk/wp-content/uploads/2026/06/SOP-on-kato-katz-technique.pdf", access="documento lido via leitor automático"),
 dict(id="who_bench2019", short="OMS, 2019", citation="Genchi M, Potters I, Kaminsky RG, Montresor A, Magnino S. Bench aids for the diagnosis of intestinal parasites, 2nd ed. Genebra: Organização Mundial da Saúde; 2019. ISBN 9789241515344.", url="https://research.itg.be/en/publications/bench-aids-for-the-diagnosis-of-intestinal-parasites-2nd-ed/", access="apenas o registro bibliográfico foi conferido; o conteúdo do documento NÃO foi lido"),
 dict(id="classicos", short="Métodos clássicos (não conferidos)", citation="Referências históricas dos métodos (Lutz; Hoffman, Pons e Janer; Faust et al.; Graham; Rugai, Mattos e Brizola, Rev Inst Adolfo Lutz 14:5-8, 1954). Citadas apenas como atribuição de autoria: os artigos originais NÃO foram localizados nem lidos nesta revisão (a referência de Rugai et al. foi vista na lista bibliográfica de um artigo secundário).", access="atribuição histórica; não conferida"),
]

def V(item, status, note, refs=()):
    return dict(item=item, status=status, note=note, refs=list(refs))

PROTOCOLS = [
 dict(
  id="lutz-hoffmann",
  title="Sedimentação espontânea (Hoffmann, Pons e Janer / Lutz)",
  popularName="Método de sedimentação espontânea em água (HPJ)",
  indication="Exame parasitológico de fezes qualitativo por sedimentação em água, sem centrifugação, para formas parasitárias que sedimentam (ovos e larvas de helmintos, cistos de protozoários).",
  principle="A suspensão fecal é filtrada e deixada em repouso em cálice cônico; as formas parasitárias, mais densas que a água, sedimentam por gravidade e são coletadas do fundo.",
  reagentsAndMaterials=[
   "Cálice de sedimentação cônico (o POP consultado usa cálice de 200 mL)",
   "Copo descartável e bastão para macerar",
   "Gaze dobrada em quatro e peneira",
   "Água",
   "Pipeta Pasteur, lâminas e lamínulas; Lugol (opcional, conforme o POP local)",
  ],
  stepByStep=[
   "Coletar cerca de 2 g de fezes e macerar em copo com cerca de 5 mL de água.",
   "Acrescentar cerca de 20 mL de água e homogeneizar.",
   "Filtrar a suspensão através de gaze dobrada em quatro, sobre peneira, para o cálice de 200 mL.",
   "Lavar os detritos retidos na peneira com cerca de 20 mL de água e completar o volume do cálice com água.",
   "Deixar em repouso por 2 horas (pode chegar a 24 horas; com pouca amostra, sedimentar por mais de 2 horas e usar menos água).",
   "Sem agitar, coletar com pipeta uma gota do sedimento do fundo, montar entre lâmina e lamínula (a fresco e/ou com Lugol, conforme o POP local) e examinar ao microscópio.",
  ],
  advantages=[
   "Não exige centrífuga nem reagentes de flutuação.",
  ],
  limitations=[
   "Sensibilidade baixa para larvas de Strongyloides stercoralis: em 60 etilistas e 60 não etilistas (12 positivos), a sedimentação HPJ detectou 36,4% dos positivos na 1ª amostra e 72,7% com três amostras, contra 63,6% e 100% do cultivo em placa de ágar.",
   "Resultado qualitativo: não estima a carga parasitária (para isso, ver Kato-Katz).",
   "Uma única amostra pode ser insuficiente; a recomendação de várias amostras vale para a detecção de larvas (ver evidência).",
  ],
  keyParasitesDetected=["Ovos de helmintos que sedimentam em água", "Larvas de Strongyloides stercoralis (com sensibilidade baixa)", "Cistos de protozoários"],
  evidence=[
   dict(text="Sensibilidade da sedimentação HPJ para S. stercoralis em etilistas: 36,4% (IC95% 12,4–68,4) na 1ª amostra e 72,7% (IC95% 39,3–92,7) com três amostras; cultivo em placa de ágar: 63,6% e 100%. Estudo pequeno (12 casos positivos).", refs=["goncalves2023"]),
   dict(text="Em 68 amostras humanas, a sedimentação espontânea detectou larvas em 2 dos 6 indivíduos positivos (33,3%), contra 3 (50%) do cultivo em placa de ágar e 6 (100%) da técnica de Rugai modificada.", refs=["rodrigues2024"]),
  ],
  verification=[
   V("Massa de fezes e volumes de água", "corrigido", "O texto anterior indicava 2 a 4 g e 10 a 20 mL. O POP consultado usa cerca de 2 g, 5 mL + 20 mL e lavagem com mais 20 mL; os valores foram trocados pelos do POP.", ["pop_ufgd"]),
   V("Tempo de sedimentação", "confirmado", "2 horas, podendo chegar a 24 horas (POP). O texto anterior dizia 'mínimo 2 a 4 horas'.", ["pop_ufgd"]),
   V("Última etapa (coleta do sedimento e montagem)", "ressalva", "Prática usual; o trecho do POP extraído não detalha a montagem da lâmina. Siga o POP do seu laboratório.", ["pop_ufgd"]),
   V("'Excelente sensibilidade para Ascaris, Schistosoma, Trichuris e ancilostomídeos'", "removido", "Afirmação sem fonte entre as consultadas; retirada. Não há comparação de sensibilidade para ovos nas fontes lidas.", []),
   V("'Não deforma ovos por não centrifugar'", "removido", "Sem fonte; retirada.", []),
   V("Lista de parasitos detectáveis", "ressalva", "Orientação geral de livro-texto (ovos/larvas/cistos que sedimentam); não conferida espécie a espécie nesta revisão.", []),
   V("Autoria histórica (Hoffman, Pons e Janer; Lutz)", "ressalva", "Artigos originais não localizados; o POP consultado grafa 'Hoffmann'.", ["classicos"]),
  ],
  refs=["pop_ufgd", "goncalves2023", "rodrigues2024", "classicos"],
 ),

 dict(
  id="graham-fita-gomada",
  title="Fita adesiva perianal (Graham)",
  popularName="Teste da fita / swab perianal para Enterobius vermicularis",
  indication="Diagnóstico de enterobíase (Enterobius vermicularis). O exame de fezes não é recomendado para essa finalidade.",
  principle="Os ovos e, às vezes, vermes adultos presentes na região perianal aderem à superfície adesiva da fita (ou do swab/paddle adesivo) e são vistos ao microscópio.",
  reagentsAndMaterials=[
   "Fita adesiva transparente de celulose, ou swab/paddle adesivo",
   "Lâmina de microscopia",
   "Microscópio",
  ],
  stepByStep=[
   "Coletar logo ao acordar, antes de defecar e antes de lavar a região perianal.",
   "Aplicar a face adesiva da fita (ou do swab/paddle) na região perianal.",
   "Fixar a fita sobre a lâmina, com a face adesiva voltada para o vidro, e identificar a lâmina.",
   "Examinar ao microscópio em busca de ovos (e, eventualmente, vermes adultos).",
   "Repetir a coleta em dias consecutivos: o CDC indica três manhãs consecutivas; a Saúde Pública de Ontário recomenda 4 a 6 dias consecutivos para excluir a infecção.",
  ],
  advantages=[
   "Muito mais sensível que o exame de fezes, que tem sensibilidade inferior a 10%.",
   "Fita e swab/paddle têm desempenho sem diferença relatada.",
  ],
  limitations=[
   "Uma única amostra tem sensibilidade estimada em menos de 60%; com três coletas diárias chega a cerca de 90%; com seis, perto de 100%.",
   "Depende da coleta correta (antes de evacuar e de lavar a região).",
   "Um resultado negativo em amostra única não exclui a infecção.",
  ],
  keyParasitesDetected=["Enterobius vermicularis"],
  evidence=[
   dict(text="Sensibilidade estimada: <60% com uma amostra; ~90% com três amostras diárias; próxima de 100% com seis; exame de fezes <10%. Coletar diariamente por 4 a 6 dias consecutivos para excluir infecção.", refs=["pho_enterobius"]),
   dict(text="Coleta logo pela manhã, em três manhãs consecutivas, antes do banho; o material aderido à fita pode conter ovos e, às vezes, vermes adultos.", refs=["cdc_pinworm"]),
  ],
  verification=[
   V("'Sensibilidade superior a 90%' (amostra única)", "corrigido", "Era a afirmação mais problemática do texto anterior. A fonte indica <60% com uma amostra e ~90% com três.", ["pho_enterobius"]),
   V("'Menos de 5% no exame de fezes'", "corrigido", "Fonte: sensibilidade do exame de fezes <10% (não há valor de 5% nas fontes lidas).", ["pho_enterobius"]),
   V("'Padrão-ouro absoluto'", "corrigido", "Termo retirado; as fontes o descrevem como o método recomendado, não como 'padrão-ouro absoluto'.", ["pho_enterobius", "cdc_pinworm"]),
   V("Coleta ao acordar, antes de banho/evacuação", "confirmado", "Confirmado por Saúde Pública de Ontário (antes de defecar e lavar) e CDC (primeira coisa pela manhã, antes do banho).", ["pho_enterobius", "cdc_pinworm"]),
   V("Número de dias de coleta", "corrigido", "O texto anterior não indicava repetição. Fontes: 3 manhãs consecutivas (CDC) e 4 a 6 dias (Saúde Pública de Ontário).", ["cdc_pinworm", "pho_enterobius"]),
   V("Fita de 10 cm, suporte em tubo/espátula, gota de xilol ou tolueno", "removido", "Detalhes sem fonte entre as consultadas; retirados. O CDC cita fita de celulose ou 'swube'; a Saúde Pública de Ontário cita fita ou paddle.", ["cdc_pinworm"]),
   V("Detecção de ovos de Taenia na pele perianal", "removido", "Não conferido nas fontes consultadas; retirado da lista de parasitos.", []),
   V("Aumento de leitura (10× e 40×)", "removido", "As fontes lidas não especificam o aumento; use o POP local.", []),
  ],
  refs=["cdc_pinworm", "pho_enterobius", "classicos"],
 ),

 dict(
  id="rugai-baermann",
  title="Rugai, Mattos e Brizola / Baermann-Moraes",
  popularName="Pesquisa de larvas por termo-hidrotropismo",
  indication="Pesquisa de larvas de Strongyloides stercoralis em fezes frescas.",
  principle="As larvas vivas migram das fezes para a água morna (termo-hidrotropismo positivo) e sedimentam no fundo do cálice, de onde são coletadas.",
  reagentsAndMaterials=[
   "Fezes frescas, não refrigeradas (quantidade conforme o POP do laboratório)",
   "Gaze dobrada para formar a 'trouxinha'",
   "Cálice de sedimentação",
   "Água aquecida a 40–45 °C",
   "Pipeta Pasteur, lâminas, lamínulas; Lugol (opcional)",
  ],
  stepByStep=[
   "Usar fezes frescas e não refrigeradas (requisito apontado na revisão sistemática).",
   "Envolver a amostra em gaze dobrada, formando uma trouxinha.",
   "Encher o cálice de sedimentação com água aquecida a 40–45 °C.",
   "Apoiar a trouxinha de modo que as fezes fiquem em contato com a superfície da água.",
   "Manter em repouso por cerca de 1 hora.",
   "Retirar a gaze, coletar o sedimento do fundo, montar entre lâmina e lamínula (a fresco para ver a motilidade; Lugol opcional) e examinar.",
   "Confirmar a espécie pela morfologia da larva (ver a página de Strongyloides stercoralis).",
  ],
  advantages=[
   "O método de Baermann detectou 3,6 a 4 vezes mais casos que a concentração formol-éter ou o esfregaço direto, nos estudos revistos.",
   "A técnica de Rugai modificada deu sedimento mais limpo e maior recuperação de larvas que a original em ratos infectados experimentalmente.",
  ],
  limitations=[
   "Exige fezes frescas e não refrigeradas.",
   "A eliminação de larvas é intermitente e pode ser baixa na infecção crônica: um único esfregaço direto deixa de detectar cerca de 70% dos casos, e coletas em dias diferentes aumentam a sensibilidade.",
   "A sensibilidade dos métodos parasitológicos é insuficiente na infecção crônica; a sorologia (com reação cruzada com outros nematódeos) e a PCR são alternativas descritas na revisão.",
   "Os dados de sensibilidade da técnica de Rugai modificada vêm de estudo pequeno (68 pessoas, 6 positivas) e de modelo animal.",
  ],
  keyParasitesDetected=["Strongyloides stercoralis (larvas)"],
  evidence=[
   dict(text="Baermann: aumenta a detecção em 3,6–4× em relação à concentração formol-éter ou ao esfregaço direto; requer fezes frescas e não refrigeradas; coletar várias amostras em dias diferentes melhora a detecção; um esfregaço direto único deixa de detectar cerca de 70% dos casos.", refs=["requena2013"]),
   dict(text="Rugai original aplicado com água a 40–45 °C e repouso de 1 hora.", refs=["chaves2014"]),
   dict(text="Em 68 amostras humanas (6 positivas): Rugai modificada 100% (6/6), cultivo em placa de ágar 50% (3/6), sedimentação espontânea 33,3% (2/6).", refs=["rodrigues2024"]),
  ],
  verification=[
   V("Temperatura da água", "corrigido", "O texto anterior dava 40–42 °C (e '>45 °C mata as larvas'). A fonte consultada usa 40–45 °C; a afirmação sobre morte acima de 45 °C não foi encontrada e foi retirada.", ["chaves2014"]),
   V("Tempo de repouso", "corrigido", "O texto anterior dizia 60 a 90 minutos. A fonte consultada indica 1 hora.", ["chaves2014"]),
   V("'8 a 10 g de fezes'", "removido", "Massa não encontrada nas fontes consultadas; use o POP local.", []),
   V("Uso de gaze/trouxinha", "ressalva", "Descrição clássica do método; não confirmada textualmente nas fontes lidas (o trecho da dissertação descreve cálice e água aquecida).", ["chaves2014"]),
   V("'Padrão-ouro de escolha obrigatória'", "corrigido", "Fontes descrevem Baermann/placa de ágar como mais sensíveis que esfregaço e formol-éter, mas sem sensibilidade perfeita; terminologia suavizada.", ["requena2013"]),
   V("Larvas de ancilostomídeo em fezes com mais de 24–48 h", "removido", "Não conferido nas fontes consultadas.", []),
   V("Critérios morfológicos (vestíbulo bucal curto, primórdio genital)", "ressalva", "Não revistos nesta rodada (conteúdo das páginas de espécie fora do escopo desta revisão).", []),
   V("Autoria (Rugai, Mattos e Brizola, 1954; Baermann-Moraes)", "ressalva", "Referência original vista apenas em lista bibliográfica de artigo secundário; artigo original não lido.", ["classicos"]),
  ],
  refs=["requena2013", "rodrigues2024", "chaves2014", "classicos"],
 ),

 dict(
  id="faust-zinc",
  title="Centrífugo-flutuação em sulfato de zinco (Faust)",
  popularName="Método de Faust e colaboradores",
  indication="Concentração por flutuação de cistos de protozoários e de ovos leves de helmintos em exame qualitativo de fezes.",
  principle="Após lavagem por centrifugação, o sedimento é ressuspendido em solução hipertônica de sulfato de zinco (cerca de 1,18 g/mL); as formas menos densas flutuam e são coletadas da superfície.",
  reagentsAndMaterials=[
   "Solução de sulfato de zinco com densidade de cerca de 1,18 g/mL (conferir com densímetro)",
   "Centrífuga e tubos de 15 mL",
   "Gaze, água, bastão",
   "Alça ou pipeta; lâminas e lamínulas; Lugol (opcional)",
  ],
  stepByStep=[
   "Homogeneizar cerca de 2 g de fezes em cerca de 10 mL de água e filtrar em gaze.",
   "Centrifugar em tubo de 15 mL por 2 minutos a 400 g, duas vezes (lavagem, como no estudo de Inês et al.).",
   "Ressuspender o sedimento na solução de sulfato de zinco (1,18 g/mL).",
   "Centrifugar a solução de flutuação. Valor de referência do CDC: 500 × g por 5 minutos, sem usar o freio da centrífuga (CDC usa solução de densidade ~1,2; confirme a rotação e o tempo no POP local).",
   "Coletar o material da superfície (alça ou pipeta); na variante do CDC, preencher o tubo até formar menisco e deixar uma lamínula de 15 × 15 mm por 10 minutos.",
   "Montar entre lâmina e lamínula (Lugol opcional) e examinar logo: o CDC recomenda a leitura em até 15 minutos.",
  ],
  advantages=[
   "Em 330 amostras, a flutuação em sulfato de zinco diagnosticou mais casos de Trichuris trichiura que a sedimentação centrífuga (39 contra 13; p<0,001).",
   "Detectou Enterobius vermicularis (5 casos) e Strongyloides stercoralis (3 casos) que a sedimentação centrífuga não detectou (diferença significativa só para E. vermicularis: p=0,025; para S. stercoralis p=0,083).",
  ],
  limitations=[
   "Várias amostras aumentam a sensibilidade: na amebíase crônica, 67,1% na 1ª amostra e 91,8% acumulado com três amostras (85 infectados; estudo de 1962).",
   "A solução hipertônica pode não ser adequada para Blastocystis spp.; para Giardia e Blastocystis não houve diferença significativa em relação à sedimentação.",
   "Menor sensibilidade que a flutuação em solução de açúcar para Cryptosporidium (relato do mesmo estudo).",
   "A densidade da solução deve ser conferida com densímetro (CDC: semanalmente ou a cada novo lote).",
   "Formas mais densas flutuam mal em soluções hipertônicas: em estudo com flutuação em salmoura (McMaster, densidade ~1,2), ovos inférteis de Ascaris foram raramente detectados; o dado não foi medido para sulfato de zinco.",
  ],
  keyParasitesDetected=["Giardia (cistos)", "Complexo Entamoeba histolytica/dispar/moshkovskii (cistos; indistinguíveis ao microscópio)", "Trichuris trichiura (ovos)"],
  evidence=[
   dict(text="Faust (zinco 1,18 g/mL) vs sedimentação centrífuga em 330 amostras: T. trichiura 39 vs 13 (p<0,001); E. vermicularis 5 vs 0 (p=0,025); S. stercoralis 3 vs 0 (p=0,083); sem diferença significativa para Giardia e Blastocystis.", refs=["ines2016"]),
   dict(text="Sensibilidade do método em amebíase crônica: 67,1%, 69,4% e 63,5% nas amostras 1, 2 e 3; 78,8% com duas e 91,8% com três amostras sucessivas (85 infectados).", refs=["barretto1962"]),
   dict(text="E. histolytica, E. dispar e E. moshkovskii são morfologicamente idênticas e só se diferenciam por métodos moleculares; entre 194 amostras de pacientes com disenteria diagnosticadas como E. histolytica por microscopia, apenas 10,3% foram positivas para E. histolytica na PCR nested.", refs=["santos2010", "roshdy2017"]),
   dict(text="Parâmetros do CDC para centrifugação e leitura: 500 × g por 5 minutos sem freio; leitura em até 15 minutos; verificar a densidade com densímetro.", refs=["cdc_concentration"]),
  ],
  verification=[
   V("Densidade da solução", "ressalva", "Inês et al. usam 1,18 g/mL; o quadro do CDC lista sulfato de zinco a 330 g/L com densidade 1,2. Ambos citados; usar o valor do POP local e conferir com densímetro.", ["ines2016", "cdc_concentration"]),
   V("Centrifugação '2.500 rpm por 1 minuto'", "removido", "Valor não encontrado nas fontes consultadas. Substituído pelas forças centrífugas relatadas (g), que não dependem do rotor; converta para rpm conforme a sua centrífuga.", ["ines2016", "cdc_concentration"]),
   V("Massa de fezes e volume de água", "confirmado", "Cerca de 2 g em cerca de 10 mL de água, filtrados em gaze (Inês et al.).", ["ines2016"]),
   V("Leitura 'em até 15–20 minutos'", "corrigido", "CDC: em até 15 minutos.", ["cdc_concentration"]),
   V("'Ovos de S. mansoni e inférteis de Ascaris não flutuam'", "ressalva", "Só há dado sobre ovos inférteis de Ascaris em flutuação em salmoura (McMaster); nada sobre S. mansoni em sulfato de zinco. Texto reescrito com esse escopo.", ["levecke2011"]),
   V("'Excelente visualização de núcleos e axóstilos'", "removido", "Sem fonte entre as consultadas; retirada.", []),
   V("'Entamoeba histolytica' como achado microscópico", "corrigido", "Cistos de E. histolytica, E. dispar e E. moshkovskii são indistinguíveis ao microscópio; o nome foi trocado por 'complexo'.", ["santos2010", "roshdy2017"]),
   V("Autoria histórica (Faust et al.)", "ressalva", "Inês et al. citam Faust et al. (1939); o artigo original não foi localizado nem lido.", ["ines2016", "classicos"]),
  ],
  refs=["ines2016", "barretto1962", "cdc_concentration", "santos2010", "roshdy2017", "levecke2011", "classicos"],
 ),

 dict(
  id="kato-katz",
  title="Kato-Katz (esfregaço espesso)",
  popularName="Exame quantitativo de ovos por grama de fezes (OPG)",
  indication="Detecção e contagem de ovos de helmintos transmitidos pelo solo (Ascaris lumbricoides, Trichuris trichiura, ancilostomídeos) e de Schistosoma mansoni, para estimar a intensidade da infecção.",
  principle="Um volume padronizado de fezes peneiradas (modelo de furo de 6 mm de diâmetro e 1,5 mm de espessura, que amostra cerca de 41,7 mg) é espalhado entre lâmina e papel celofane embebido em glicerol com verde de malaquita; os ovos são contados e multiplicados por 24.",
  reagentsAndMaterials=[
   "Modelo (placa perfurada) de 6 mm × 1,5 mm (cerca de 41,7 mg de fezes), tela de nylon ou aço e espátula",
   "Celofane hidrofílico embebido em glicerol/verde de malaquita",
   "Solução: 100 mL de glicerol, 100 mL de água destilada e 1 mL de verde de malaquita a 3% (SOP consultado); celofane imerso por, no mínimo, 24 horas antes do uso",
   "Lâminas e papel absorvente",
  ],
  stepByStep=[
   "Pressionar a tela sobre a amostra e coletar, com a espátula, as fezes que atravessam a malha.",
   "Posicionar o modelo sobre a lâmina e preenchê-lo com as fezes peneiradas.",
   "Retirar o modelo com cuidado, deixando o cilindro de fezes sobre a lâmina.",
   "Cobrir as fezes com o celofane embebido na solução de glicerol e verde de malaquita.",
   "Pressionar a lâmina contra uma superfície lisa para espalhar as fezes em camada uniforme.",
   "Examinar os ovos de ancilostomídeo em 30 a 60 minutos (depois desse tempo eles clareiam e podem desaparecer) e reexaminar a mesma lâmina após cerca de 2 horas para os demais ovos.",
   "Contar os ovos por espécie na lâmina inteira e multiplicar por 24 para obter OPG.",
  ],
  advantages=[
   "Permite estimar a intensidade da infecção (OPG) e classificá-la pelos pontos de corte da OMS.",
   "É o método recomendado pela OMS para quantificar ovos de helmintos transmitidos pelo solo em fezes humanas e para monitorar programas de tratamento em massa.",
  ],
  limitations=[
   "O fator fixo 24 é uma aproximação: a massa real de fezes variou bastante (fator ajustado médio 23,7; IC95% 14,3–66,7; amplitude individual de 11 a 100), e o fator fixo superestimou levemente a contagem para Ascaris e Trichuris.",
   "O tempo entre o preparo e a leitura é crítico para ancilostomídeos (leitura após mais de 30 minutos pode causar falso-negativo) e difícil de padronizar.",
   "A sensibilidade varia com o local e com a intensidade da infecção: em 1.543 pessoas de cinco países, 88,1% para Ascaris, 82,6% para Trichuris e 78,3% para ancilostomídeos (referência: combinação de Kato-Katz e McMaster).",
   "A probabilidade de detecção aumenta com o número de ovos excretados; a sensibilidade é menor nas infecções leves.",
  ],
  keyParasitesDetected=["Ascaris lumbricoides", "Trichuris trichiura", "Ancilostomídeos", "Schistosoma mansoni"],
  intensity=dict(
   source="Pontos de corte da OMS como relatados em Levecke et al. (2011), em ovos por grama (OPG)",
   refs=["levecke2011"],
   rows=[
    ["Ascaris lumbricoides", "1–4.999", "5.000–49.999", "≥ 50.000"],
    ["Trichuris trichiura", "1–999", "1.000–9.999", "≥ 10.000"],
    ["Ancilostomídeos", "1–1.999", "2.000–3.999", "≥ 4.000"],
   ],
   header=["Parasito", "Leve", "Moderada", "Intensa"],
   note="Os pontos de corte para Schistosoma mansoni não foram conferidos nesta revisão e foram omitidos.",
  ),
  evidence=[
   dict(text="Modelo de 6 mm × 1,5 mm (≈ 41,7 mg); leitura de ancilostomídeos em 30–60 min e reexame após ~2 h para os demais; multiplicar por 24 para OPG.", refs=["levecke2011"]),
   dict(text="Sensibilidade global do Kato-Katz: Ascaris 88,1%, Trichuris 82,6%, ancilostomídeos 78,3%; no Brasil, 100% (Ascaris) e 95,2% (ancilostomídeos). Valores dependem da intensidade e do local; a referência foi a combinação dos dois métodos.", refs=["levecke2011"]),
   dict(text="Fator de multiplicação ajustado pela massa real: média 23,7 (IC95% 14,3–66,7); concordância quase perfeita na classificação de intensidade entre fator fixo e ajustado (κ = 0,89–0,93).", refs=["levecke2011"]),
   dict(text="Procedimento institucional: solução de glicerol + água + verde de malaquita 3%; celofane imerso por ≥ 24 h; leitura em 30–60 min para ancilostomídeos.", refs=["sop_katzkatz"]),
   dict(text="Descrição original do dispositivo (modelo de furo calibrado) para esquistossomose mansônica.", refs=["katz1972"]),
  ],
  verification=[
   V("Volume de 41,7 mg e fator 24", "confirmado", "Modelo de 6 mm × 1,5 mm ≈ 41,7 mg; ×24 (Levecke et al.; SOP).", ["levecke2011", "sop_katzkatz"]),
   V("Tempos de clarificação ('60 min para Schistosoma; 30 min para Ascaris e ancilostomídeos')", "corrigido", "Fontes: ancilostomídeos devem ser lidos em 30–60 min e as demais espécies reexaminadas após ~2 h. Os tempos por espécie do texto anterior não foram encontrados.", ["levecke2011", "sop_katzkatz"]),
   V("'Ovos de ancilostomídeos desaparecem se lidos após 2 h'", "corrigido", "Fonte: leitura após mais de 30 min pode causar falso-negativo para ancilostomídeos; o SOP fala em 30–60 min.", ["levecke2011", "sop_katzkatz"]),
   V("Malha 100 e composição da solução", "ressalva", "A malha não foi especificada nas fontes lidas e foi omitida; a composição da solução vem de um SOP institucional (não da descrição original de Katz et al.).", ["sop_katzkatz"]),
   V("Classes de intensidade da OMS", "confirmado", "Ascaris, Trichuris e ancilostomídeos conforme relatado em Levecke et al.; classes de S. mansoni não conferidas e omitidas.", ["levecke2011"]),
   V("'Não adequado para fezes diarreicas'", "removido", "Não conferido nas fontes lidas (o estudo apenas exclui diarreia do recrutamento); retirado.", []),
   V("'Inapropriado para cistos e trofozoítos de protozoários'", "removido", "Não conferido nas fontes lidas; retirado. O método foi descrito e avaliado para ovos de helmintos.", []),
   V("'Padronizado internacionalmente'", "corrigido", "Os autores descrevem o método como difícil de padronizar (tempo de leitura, massa de fezes); texto invertido.", ["levecke2011"]),
   V("Gestos de preparo (peneirar, preencher o modelo, cobrir com celofane, comprimir a lâmina)", "ressalva", "Descrição clássica do método; as fontes lidas confirmam modelo, celofane, tempos de leitura e fator de multiplicação, não cada gesto.", ["sop_katzkatz"]),
   V("Texto original de Katz, Chaves e Pellegrino (1972)", "ressalva", "Referência confirmada no PubMed, mas o resumo não está disponível e o artigo não foi lido.", ["katz1972"]),
  ],
  refs=["levecke2011", "sop_katzkatz", "katz1972"],
 ),
]

REVIEW = dict(
  reviewedOn=DATE,
  status="conferido-na-literatura",
  scope="Os cinco protocolos foram comparados com as fontes listadas. Cada valor numérico do texto foi mantido, corrigido ou retirado conforme a seção “Conferência”.",
  notValidation="Isto é uma conferência bibliográfica, não uma validação analítica. Antes de uso em rotina ou em diagnóstico, o procedimento precisa ser adotado e validado no POP do laboratório (controles positivo e negativo, equipamentos calibrados, aprovação da responsável).",
  notReviewed=["Conteúdo clínico, morfologia e ciclo das espécies (páginas de espécie)", "Banco de questões do quiz", "Guia de artefatos"],
  sourceAccessNote="Fontes lidas por ferramentas automáticas (PubMed e leitor de páginas); onde só o resumo ou trechos foram lidos, isso consta em cada referência (“acesso nesta revisão”). Dois itens de acesso indisponível: artigos originais dos métodos clássicos e o documento da OMS (Bench Aids).",
)

(ROOT / "public/data/referencias.json").write_text(json.dumps(dict(review=REVIEW, items=REFS), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "public/data/protocolos.json").write_text(json.dumps(PROTOCOLS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("ok", len(REFS), "refs", len(PROTOCOLS), "protocolos")
