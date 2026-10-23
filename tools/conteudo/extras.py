# -*- coding: utf-8 -*-
"""Quiz, guia de artefatos e dados do site — todos derivados das afirmações verificadas."""

# ----------------------------------------------------------------------------- ARTEFATOS
ARTEFATOS = dict(
    itens=[
        dict(nome="Grãos de pólen", confundidaCom="Ovos de helmintos, em especial o ovo fértil de Ascaris lumbricoides",
             comoDiferenciar="O CDC registra que o pólen é muito comum nas fezes e pode se parecer muito com o ovo fértil de Ascaris. As fontes lidas não trazem critérios de diferenciação; compare as medidas e estruturas com a ficha de Ascaris e peça confirmação a um profissional experiente.",
             refs=["dpdx_art"], status="ressalva",
             evidencia="\"Pollen spores are very common in stool and may be confused for a variety of helminth eggs.\" · \"This grain looks very similar to the fertile egg of Ascaris lumbricoides\""),
        dict(nome="Pelos vegetais", confundidaCom="Larvas de ancilostomídeo ou de Strongyloides stercoralis",
             comoDiferenciar="O CDC registra a confusão possível. Como critério de comparação, use as características verificadas das larvas: S. stercoralis L1 tem canal bucal curto e primórdio genital proeminente; a larva rabditoide de ancilostomídeo tem canal bucal longo e primórdio genital inconspícuo (veja as fichas).",
             refs=["dpdx_art", "dpdx_stro", "dpdx_hook"], status="ressalva",
             evidencia="\"Plant hairs can be common in stool and may be confused for the larvae of hookworm or Strongyloides stercoralis.\""),
        dict(nome="Material vegetal (restos de planta)", confundidaCom="Ovos e larvas de helmintos, por exemplo o ovo de ancilostomídeo",
             comoDiferenciar="O CDC registra que o material vegetal é muito comum nas fezes e pode ser confundido com vários ovos e larvas. As fontes lidas não trazem critérios de diferenciação; compare com a ficha da espécie suspeita (ovo de ancilostomídeo: casca fina, incolor, 60–75 × 35–40 µm).",
             refs=["dpdx_art", "dpdx_hook"], status="ressalva",
             evidencia="\"Plant material is very common in stool and may be confused for a variety of helminth eggs and larvae.\" · \"This material can be confused for a hookworm egg.\""),
        dict(nome="Leveduras e outros elementos fúngicos", confundidaCom="Giardia, em preparações a fresco",
             comoDiferenciar="O CDC registra que leveduras são comuns nas fezes e, em preparações a fresco, podem ser confundidas com Giardia. As fontes lidas não trazem critérios de diferenciação; compare com as medidas e estruturas da ficha de Giardia (trofozoíto piriforme de 10–20 µm; cisto de 8–19 µm).",
             refs=["dpdx_art", "dpdx_giar"], status="ressalva",
             evidencia="\"Yeast and other fungal elements are common in stool.\" · \"Yeast in wet mounts may be confused for Giardia.\""),
        dict(nome="Esporos de fungos", confundidaCom="Ovos de helmintos (especialmente ancilostomídeo), cistos de Entamoeba e protozoários como Giardia ou Chilomastix",
             comoDiferenciar="O CDC registra as três confusões possíveis. As fontes lidas não trazem critérios de diferenciação; compare com as fichas das espécies.",
             refs=["dpdx_art"], status="ressalva",
             evidencia="\"Such spores may be confused for helminth eggs, especially hookworm.\" · \"Such spores may be confused for the cysts of Entamoeba spp.\" · \"Such spores may be confused for protozoa such as Giardia or Chilomastix.\""),
    ],
    dica="Em caso de dúvida entre artefato e parasita, compare estruturas e medidas com as fichas verificadas do atlas e peça confirmação a um profissional experiente. Esta dica é uma orientação geral dos autores; não foi extraída de uma fonte.",
    removidos=[
        dict(item="Bolhas de ar", antes="Bordas escuras espessas; mudam de foco ao menor toque; confundidas com cistos/Taenia.",
             motivo="Não consta na página de artefatos do CDC (única fonte lida sobre o tema); nenhuma fonte lida sustenta a descrição."),
        dict(item="Grânulos de amido", antes="Coram-se em azul-marinho/roxo com Lugol; 'cruz de malta' sob luz polarizada.",
             motivo="Não consta na página de artefatos do CDC; nenhuma fonte lida sustenta a descrição. Pode ser reincluído se houver referência."),
        dict(item="Critérios de diferenciação do pólen e das fibras vegetais", antes="Espinhos geométricos/poros de germinação; canais ocos; espessamento helicoidal.",
             motivo="Detalhes sem fonte lida."),
        dict(item="Dica 'gire o micrométrico: o parasita mantém a consistência das membranas internas'", antes="Dica geral de bancada.",
             motivo="Sem fonte lida; substituída por orientação geral claramente identificada como dos autores."),
    ],
)

# ----------------------------------------------------------------------------- QUIZ
# (id, módulo, categoria, título, pergunta, correta, [erradas x3], explicação, pérola, refs)
Q = []


def q(id_, mod, cat, titulo, pergunta, certa, erradas, expl, perola, refs):
    Q.append(dict(id=id_, module=mod, category=cat, title=titulo, question=pergunta,
                  correct=certa, wrong=erradas, explanation=expl, pearl=perola, refs=refs))


q("q01", "nematelmintos", "Ascaris", "Tamanho do ovo fértil", "Qual é a faixa de comprimento do ovo fértil de Ascaris lumbricoides segundo o CDC?",
  "45 a 75 µm", ["10 a 20 µm", "100 a 140 µm", "20 a 30 µm"],
  "O CDC DPDx informa que os ovos férteis medem de 45 a 75 µm de comprimento; os inférteis são alongados e maiores, até 90 µm.", "Ovo infértil: alongado e maior (até 90 µm).", ["dpdx_asc"])
q("q02", "nematelmintos", "Ascaris", "Ovo decorticado", "O que caracteriza um ovo decorticado de Ascaris?",
  "A camada externa está ausente", ["Possui dois tampões polares", "Tem seis ganchos refráteis", "Apresenta filamentos polares"],
  "Segundo o CDC DPDx, ovos decorticados são aqueles em que a camada externa está ausente.", "Decorticado = sem a camada externa.", ["dpdx_asc"])
q("q03", "nematelmintos", "Artefatos", "Pólen", "Qual ovo de helminto pode ser muito parecido com um grão de pólen presente nas fezes, segundo o CDC?",
  "O ovo fértil de Ascaris lumbricoides", ["O ovo de Trichuris trichiura", "O ovo de Schistosoma mansoni", "A larva de Strongyloides stercoralis"],
  "A página de artefatos do CDC mostra um grão de pólen que se parece muito com o ovo fértil de Ascaris.", "Pólen é comum nas fezes e pode imitar ovos de helmintos.", ["dpdx_art"])
q("q04", "nematelmintos", "Ancilostomídeos", "Ovos de Ancylostoma e Necator", "É possível distinguir ao microscópio óptico o ovo de Ancylostoma do de Necator?",
  "Não; os ovos dos dois gêneros não são diferenciáveis ao microscópio", ["Sim, pelo tamanho, que é o dobro em Ancylostoma", "Sim, pela presença de filamentos polares", "Sim, pelo opérculo duplo de Necator"],
  "O CDC DPDx afirma que os ovos de Ancylostoma e Necator não podem ser diferenciados microscopicamente.", "Diferenciar os gêneros exige outros recursos além do ovo.", ["dpdx_hook"])
q("q05", "nematelmintos", "Ancilostomídeos", "Fezes não refrigeradas", "Se fezes com ovos de ancilostomídeo não forem refrigeradas e examinadas em poucas horas, o que pode ocorrer?",
  "Os ovos podem eclodir e as larvas ser confundidas com as de Strongyloides stercoralis", ["Os ovos se tornam maiores e coram-se melhor", "Os ovos perdem a casca e viram cistos", "Surgem filamentos polares nos ovos"],
  "O MSD Manual alerta que os ovos podem eclodir e liberar larvas, confundíveis com larvas de S. stercoralis.", "Exame rápido ou refrigeração evitam a eclosão.", ["msd_hook"])
q("q06", "nematelmintos", "Strongyloides", "Larva rabditoide", "Qual par de características distingue a larva rabditoide L1 de Strongyloides da de ancilostomídeo?",
  "Strongyloides: canal bucal curto e primórdio genital proeminente; ancilostomídeo: canal bucal longo e primórdio genital inconspícuo",
  ["Strongyloides: canal bucal longo e primórdio genital inconspícuo; ancilostomídeo: o oposto", "Ambas têm canal bucal curto; só diferem no tamanho", "Strongyloides tem dois núcleos visíveis; ancilostomídeo tem quatro"],
  "O CDC DPDx descreve L1 de S. stercoralis com canal bucal curto e primórdio genital proeminente, e a larva rabditoide de ancilostomídeo com canal bucal longo e primórdio genital inconspícuo.", "Canal bucal + primórdio genital: a dupla-chave.", ["dpdx_stro", "dpdx_hook"])
q("q07", "nematelmintos", "Strongyloides", "Sensibilidade do exame de fezes", "Segundo o CDC DPDx, qual método coprológico é o mais sensível para detectar larvas de Strongyloides?",
  "Cultura em placa de ágar", ["Esfregaço direto único", "Exame de fita adesiva perianal", "Coloração de Gram"],
  "O CDC DPDx descreve a cultura em placa de ágar como o método coprológico mais sensível; a microscopia de fezes tem baixa sensibilidade. O MSD estima que uma única amostra detecta larvas em cerca de 25% dos casos.", "Uma amostra só não basta: use técnicas específicas e amostras seriadas.", ["dpdx_stro", "msd_stro"])
q("q08", "nematelmintos", "Strongyloides", "Triagem antes de imunossupressão", "Em qual situação o CDC orienta considerar Strongyloides ao avaliar um paciente?",
  "Em quem usa ou vai iniciar corticosteroides ou outros imunossupressores", ["Somente em quem tem febre alta", "Apenas em crianças menores de um ano", "Somente em quem já completou tratamento com ivermectina"],
  "A página do CDC para profissionais de saúde lista pacientes em uso (ou prestes a usar) corticosteroides ou imunossupressores, com HTLV-1, entre outros.", "Corticosteroides em altas doses são fator de hiperinfecção.", ["cdc_stro_hcp", "dpdx_stro"])
q("q09", "nematelmintos", "Enterobius", "Coleta com fita adesiva", "Quando deve ser feita a coleta com fita adesiva para pesquisar Enterobius vermicularis?",
  "Pela manhã, antes de evacuar e de lavar a região", ["À noite, após o banho", "Logo após a refeição principal", "Qualquer hora, desde que após evacuar"],
  "O CDC DPDx indica coleta pela manhã, antes da defecação e da lavagem.", "Fezes são menos úteis que a fita adesiva para Enterobius.", ["dpdx_ent"])
q("q10", "nematelmintos", "Enterobius", "Forma do ovo", "Qual é a forma do ovo de Enterobius vermicularis?",
  "Transparente, de alongado a oval, ligeiramente achatado de um lado", ["Esférico, com estrias radiais", "Em barril, com tampões polares", "Com espículo lateral"],
  "O CDC DPDx descreve os ovos como transparentes, alongados a ovais e ligeiramente achatados de um lado (50–60 × 20–30 µm).", "Achatamento unilateral: marca do ovo de Enterobius.", ["dpdx_ent"])
q("q11", "nematelmintos", "Enterobius", "Infectividade do ovo", "Em quanto tempo, em condições ótimas, os ovos de Enterobius se tornam infectantes?",
  "Em 4 a 6 horas", ["Em 15 a 30 dias", "Em 18 dias a várias semanas", "Em 2 a 3 meses"],
  "O CDC DPDx informa 4 a 6 horas em condições ótimas. (15–30 dias é o tempo do ovo de Trichuris; 18 dias a várias semanas, o de Ascaris.)", "Ovos de Enterobius ficam infectantes rapidamente.", ["dpdx_ent", "dpdx_tri", "dpdx_asc"])
q("q12", "nematelmintos", "Trichuris", "Ovo em barril", "Qual conjunto descreve o ovo de Trichuris trichiura?",
  "Forma de barril ou limão, casca espessa e um tampão polar em cada extremidade", ["Esférico, com seis ganchos e estrias radiais", "Grande, com espículo lateral", "Oval com filamentos polares"],
  "O CDC DPDx descreve ovos em barril, de casca espessa, com um par de tampões polares, medindo 50–55 × 20–25 µm; o MSD descreve ovos em forma de limão com opérculos claros nas duas pontas.", "Tampões polares nas duas pontas.", ["dpdx_tri", "msd_tri"])
q("q13", "platelmintos", "Taenia", "Ovos de Taenia", "É possível diferenciar ovos de T. solium e T. saginata pelo exame microscópico do ovo?",
  "Não; os ovos de todas as Taenia são morfologicamente idênticos e a espécie é definida pelas proglotes grávidas", ["Sim, pelo tamanho do ovo", "Sim, pelo número de núcleos", "Sim, pela presença de filamentos polares"],
  "O CDC DPDx afirma que os ovos são idênticos e que a identificação da espécie exige o exame das proglotes grávidas.", "Laudo de ovos: 'Taenia sp.'", ["dpdx_taen"])
q("q14", "platelmintos", "Taenia", "Ramos uterinos", "Quantos ramos uterinos laterais primários tem a proglote grávida de T. solium, segundo o CDC?",
  "7 a 13", ["12 a 30", "2 a 4", "Mais de 40"],
  "O CDC DPDx informa 7–13 em T. solium e 12–30 em T. saginata.", "Poucos ramos: T. solium; muitos: T. saginata.", ["dpdx_taen"])
q("q15", "platelmintos", "Taenia", "Origem da cisticercose", "Como o ser humano desenvolve cisticercose por Taenia solium?",
  "Ingerindo ovos de T. solium", ["Comendo carne bovina malcozida", "Por penetração de larvas pela pele", "Pela picada de caramujos"],
  "O MSD Manual descreve que a cisticercose resulta da ingestão de ovos de T. solium (de fezes de infectados ou do próprio verme).", "Ingestão de ovos pode causar cisticercose: cuidado na bancada.", ["msd_taen", "dpdx_taen"])
q("q16", "platelmintos", "Taenia", "Cozimento de carne suína", "Qual é a temperatura mínima citada pelo MSD Manual para cozinhar cortes inteiros de carne suína na prevenção da teníase por T. solium?",
  "63 °C (145 °F)", ["45 °C", "80 °C", "100 °C"],
  "O MSD Manual cita cozinhar cortes inteiros de carne suína a ≥ 63 °C (≥ 145 °F).", "Valor citado para cortes inteiros de carne suína (sem dose/tempo de cocção especificados).", ["msd_taen"])
q("q17", "platelmintos", "Hymenolepis", "Filamentos polares", "Qual característica distingue o ovo de H. nana do de H. diminuta?",
  "H. nana tem 4–8 filamentos polares; H. diminuta não tem e é maior (70–85 × 60–80 µm)", ["H. nana tem estrias radiais; H. diminuta tem tampões polares", "Ambos têm filamentos polares, mas H. diminuta é menor", "H. nana tem espículo lateral"],
  "O CDC DPDx descreve 4–8 filamentos polares em H. nana (ovo de 30–50 µm) e ausência deles em H. diminuta.", "Filamentos polares = H. nana.", ["dpdx_hym"])
q("q18", "platelmintos", "Hymenolepis", "Hospedeiro artrópode", "O que o CDC afirma sobre o hospedeiro intermediário artrópode em Hymenolepis?",
  "É necessário para H. diminuta, mas não para H. nana", ["É necessário para H. nana, mas não para H. diminuta", "É necessário para ambas", "Não existe em nenhuma das duas"],
  "O CDC DPDx afirma que o hospedeiro artrópode é necessário para H. diminuta, mas não para H. nana.", "H. nana pode se autoinfectar internamente.", ["dpdx_hym"])
q("q19", "platelmintos", "Schistosoma", "Hospedeiro intermediário", "Quais caramujos são hospedeiros intermediários de Schistosoma mansoni?",
  "Os do gênero Biomphalaria", ["Os do gênero Lymnaea", "Os do gênero Helix", "Nenhum; a transmissão é direta"],
  "O CDC DPDx cita caramujos do gênero Biomphalaria para S. mansoni.", "Larvas liberadas por caramujos penetram a pele.", ["dpdx_schi"])
q("q20", "platelmintos", "Schistosoma", "Espículo do ovo", "Qual é a posição do espículo no ovo de S. mansoni e no de S. haematobium?",
  "S. mansoni: lateral; S. haematobium: terminal", ["S. mansoni: terminal; S. haematobium: lateral", "Ambos terminal", "Nenhum dos dois tem espículo"],
  "O CDC DPDx descreve espículo lateral proeminente em S. mansoni e espículo terminal conspícuo em S. haematobium (ovos eliminados na urina).", "Lateral = mansoni; terminal = haematobium.", ["dpdx_schi"])
q("q21", "platelmintos", "Schistosoma", "Américas", "Segundo a OPAS, quais países das Américas são endêmicos para esquistossomose?",
  "Brasil, Venezuela, Suriname e Santa Lúcia", ["Apenas Brasil", "Brasil, Argentina, Chile e Peru", "México, Cuba, Haiti e Colômbia"],
  "A ficha da OPAS lista quatro países endêmicos: Brasil, Venezuela, Suriname e Santa Lúcia.", "O Brasil é endêmico.", ["paho_schisto"])
q("q22", "platelmintos", "Schistosoma", "Tratamento", "Qual medicamento a OMS recomenda contra todas as formas de esquistossomose?",
  "Praziquantel", ["Ivermectina", "Albendazol", "Metronidazol"],
  "A OMS afirma que o praziquantel é o tratamento recomendado contra todas as formas de esquistossomose.", "Ivermectina é a droga da estrongiloidíase.", ["who_schisto"])
q("q23", "protozoarios", "Giardia", "Núcleos do cisto", "Quantos núcleos tem o cisto maduro de Giardia duodenalis?",
  "4", ["1", "2", "8"],
  "O CDC DPDx informa que cistos maduros têm 4 núcleos e os imaturos, 2.", "Cistos medem 8–19 µm (média 10–14 µm).", ["dpdx_giar"])
q("q24", "protozoarios", "Giardia", "Trofozoíto", "Como o CDC descreve o trofozoíto de Giardia duodenalis?",
  "Piriforme, de 10–20 µm, com dois núcleos grandes visíveis em preparações coradas e discos de sucção", ["Esférico, de 50 µm, com 8 núcleos", "Alongado, com um único núcleo e cauda longa", "Em forma de limão com um botão hialino"],
  "O CDC DPDx descreve trofozoítos piriformes com 10–20 µm e 2 grandes núcleos usualmente visíveis em preparações permanentes coradas.", "Dois núcleos + disco de sucção.", ["dpdx_giar"])
q("q25", "protozoarios", "Entamoeba", "E. histolytica x E. dispar", "O que o CDC afirma sobre distinguir E. histolytica, E. dispar e E. moshkovskii?",
  "Não são distinguíveis pela morfologia; métodos moleculares são recomendados", ["São distinguíveis pelo número de núcleos do cisto", "São distinguíveis pelo tamanho do trofozoíto", "São distinguíveis apenas pela cor na coloração de Gram"],
  "O CDC DPDx afirma que as três espécies não são distinguíveis pela morfologia e que métodos moleculares são recomendados; PCR é o método de escolha para separar E. histolytica de E. dispar.", "Microscopia sozinha não separa as espécies.", ["dpdx_amoeb"])
q("q26", "protozoarios", "Entamoeba", "Cisto de E. coli", "Quantos núcleos tem tipicamente o cisto maduro de Entamoeba coli?",
  "8 (podendo chegar a 16 ou mais)", ["1", "2", "Sempre exatamente 4"],
  "O CDC DPDx afirma que os cistos maduros costumam ter 8 núcleos, podendo ter 16 ou mais. O cisto de E. histolytica tem 4.", "E. coli: 8 núcleos; E. histolytica: 4.", ["dpdx_intam", "dpdx_amoeb"])
q("q27", "protozoarios", "Endolimax", "Cisto de Endolimax nana", "Qual descrição corresponde ao cisto maduro de Endolimax nana?",
  "5–10 µm, esférico a elipsoide, com quatro pequenos núcleos de cariossomos grandes", ["30 µm, esférico, com estrias radiais", "20–35 µm com oito núcleos", "Em forma de barril com tampões polares"],
  "O CDC DPDx informa cistos de 5–10 µm com quatro pequenos núcleos de cariossomos grandes, em geral centrais.", "Endolimax é uma ameba comensal, de cisto pequeno.", ["dpdx_intam"])
q("q28", "protozoarios", "Chilomastix", "Trofozoíto", "Como o CDC descreve o trofozoíto de Chilomastix mesnili?",
  "Piriforme, 6–24 µm, com extremidade anterior arredondada, um núcleo de cariossomo excêntrico e extremidade posterior afilada", ["Esférico, com 4 núcleos centrais", "Em forma de sino com dois núcleos grandes", "Ameboide, com pseudópodes e hemácias ingeridas"],
  "O CDC DPDx descreve trofozoítos piriformes de 6–24 µm, com um núcleo de cariossomo excêntrico e extremidade posterior afilada.", "Chilomastix mesnili é considerado não patogênico.", ["dpdx_chilo"])
q("q29", "protozoarios", "Artefatos", "Esporos de fungos", "Com quais organismos esporos de fungos podem ser confundidos, segundo o CDC?",
  "Ovos de helmintos (especialmente ancilostomídeo), cistos de Entamoeba e Giardia/Chilomastix", ["Somente com larvas de Strongyloides", "Somente com ovos de Taenia", "Com nenhum parasita"],
  "A página de artefatos do CDC lista essas três possibilidades de confusão.", "Esporos fúngicos imitam vários parasitas.", ["dpdx_art"])
q("q30", "nematelmintos", "Ancilostomídeos", "Via de infecção", "Segundo a OMS, como as pessoas se infectam principalmente com ancilostomídeos?",
  "Andando descalças em solo contaminado (penetração de larvas na pele)", ["Bebendo água de rios", "Comendo carne de porco malcozida", "Pela picada de mosquitos"],
  "A OMS afirma que a infecção por ancilostomídeos ocorre principalmente andando descalço em solo contaminado; as larvas podem penetrar ativamente na pele.", "Calçados são medida de barreira.", ["who_sth", "msd_hook"])


def build_quiz():
    out = []
    for i, x in enumerate(Q):
        pos = i % 4
        opts = list(x["wrong"])
        opts.insert(pos, x["correct"])
        out.append(dict(id=x["id"], category=x["category"], title=x["title"], context="", question=x["question"],
                        options=opts, correctIndex=pos, explanation=x["explanation"], fieldPearl=x["pearl"],
                        module=x["module"], refs=x["refs"]))
    return out


# ----------------------------------------------------------------------------- SITE
SITE = dict(
    title="Atlas Digital de Parasitologia Humana",
    subtitle="Laminário interativo de ensino e diagnóstico",
    institution="Universidade Federal do Amazonas (UFAM)",
    course="Disciplina de Parasitologia",
    advisor=dict(name="Profa. Dra. Jaila Dias Borges Lalwani", role="Orientadora"),
    developers=[
        dict(name="Micael Davi Lima de Oliveira", role="Desenvolvedor · Iniciação Científica"),
        dict(name="Elias de Souza Barros", role="Desenvolvedor"),
    ],
    developer="Micael Davi Lima de Oliveira e Elias de Souza Barros, sob orientação da Profa. Dra. Jaila Dias Borges Lalwani",
    references=[
        "Neves, D. P. Parasitologia Humana. Atheneu.",
        "Rey, L. Bases da Parasitologia Médica. Guanabara Koogan.",
        "Ferreira, A. W. Diagnóstico Laboratorial das Principais Doenças Infecciosas.",
        "Ministério da Saúde. Manual de Procedimentos em Coproparasitologia.",
    ],
    referencesNote="Os quatro livros acima são a bibliografia geral da disciplina e NÃO foram consultados nesta revisão; as afirmações científicas do atlas são sustentadas pelas fontes listadas em 'Referências'.",
)

MODULES = {
    "nematelmintos": dict(description="Ovos e larvas de nematódeos de importância médica em lâminas reais: ancilostomídeos, Ascaris, Enterobius, Strongyloides e Trichuris."),
    "platelmintos": dict(description="Ovos de Taenia sp. e Hymenolepis nana em lâminas reais, além de Schistosoma mansoni (imagem em revisão)."),
    "protozoarios": dict(status="ativo", description="Amebas e flagelados intestinais: Entamoeba histolytica, E. coli, Endolimax nana, Giardia duodenalis e Chilomastix mesnili, com fotografias e autoria das imagens."),
}
