# -*- coding: utf-8 -*-
"""Detalhamento de morfologia e doença a partir das páginas oficiais do CDC (DPDx e CDC), lidas em 06/11/2026.

Mesclado às espécies por tools/aplicar-conteudo.py (EXTRA[id] é acrescentado a sp['claims']).

Honestidade dos dados:
- Cada registro abaixo corresponde a um trecho que a página do CDC indicada afirma (leitura de 06/11/2026).
- A evidência é PARÁFRASE do leitor automático de páginas, não citação literal; por isso o campo
  'ev' diz isso expressamente. Confira o trecho literal na página antes de citá-lo em publicação.
- Quando a página não informa um dado, o registro diz "não consta" (ressalva) em vez de preencher.
- Datas de revisão indicadas em cada página (lidas em 06/11/2026):
  dpdx/hookworm 17/09/2019 · dpdx/ascariasis 19/07/2019 · dpdx/enterobiasis 05/08/2019 ·
  dpdx/strongyloidiasis 30/07/2019 · dpdx/trichuriasis 10/06/2024 · dpdx/taeniasis 07/06/2024 ·
  cysticercosis/about 04/09/2024 · dpdx/hymenolepiasis 05/06/2024 · dpdx/schistosomiasis 07/06/2024 ·
  dpdx/amebiasis 15/10/2019 · dpdx/giardiasis 05/06/2024 · dpdx/blastocystis 21/10/2019 ·
  dpdx/chilomastix 05/06/2019 · dpdx/intestinalAmebae 29/10/2019.
"""

EV = ("Paráfrase do CDC lida em 06/11/2026 (leitor automático de páginas); "
      "conferir o trecho literal na página.")


def _c(sec, text, refs, st="confirmado", nota=""):
    return dict(sec=sec, text=text, st=st, refs=list(refs), ev=EV, nota=nota, key=None, antes="")


EXTRA = {
    # ---------------------------------------------------------------- Ancylostoma / Necator
    "ancilostomideo": [
        _c("Morfologia", "Ovos: casca fina e incolores, com cerca de 60–75 µm por 35–40 µm; ao microscópio não se distinguem os ovos de Ancylostoma e de Necator.", ["dpdx_hook"]),
        _c("Morfologia", "Larva rabditoide (L1): cerca de 250–300 µm por 15–20 µm, com canal bucal longo e primórdio genital pouco evidente. Em geral não aparece nas fezes, a menos que a amostra demore a ser processada; deve ser diferenciada da L1 de Strongyloides stercoralis.", ["dpdx_hook"]),
        _c("Morfologia", "Larva filarioide (L3, infectante): 500–700 µm, com cauda pontiaguda, envolta por bainha e razão aproximada de 1:2 entre esôfago e intestino. Há diferenças sutis entre as L3 de A. duodenale e de N. americanus.", ["dpdx_hook"]),
        _c("Morfologia", "Vermes adultos são bursados (machos). Cápsula bucal com dentes afiados em Ancylostoma e com placas cortantes em Necator; nos machos de Necator, as duas espículas são fundidas na extremidade distal, o que não ocorre em Ancylostoma.", ["dpdx_hook"]),
        _c("Tamanho", "Adultos: A. duodenale, machos 8–12 mm e fêmeas 10–15 mm; N. americanus, machos 5–9 mm e fêmeas 9–11 mm.", ["dpdx_hook"]),
        _c("Clínica", "A infecção intestinal é frequentemente assintomática. A fixação dos vermes à parede intestinal pode causar dor abdominal, náusea e anorexia; em infecções intensas, pode haver sangue oculto nas fezes.", ["dpdx_hook"]),
        _c("Clínica", "Anemia ferropriva por perda sanguínea no local de fixação dos vermes adultos, sobretudo em infecções intensas; em casos graves, desnutrição proteica por perda crônica de proteínas plasmáticas.", ["dpdx_hook"]),
        _c("Clínica", "Durante a migração larvar pelos pulmões, pode ocorrer pneumonia eosinofílica; após a penetração das L3, pode surgir erupção urticariforme (ground itch) e, depois, uma segunda erupção. Após infecção oral, podem ocorrer sintomas gastrointestinais vagos e eosinofilia (síndrome de Wakana).", ["dpdx_hook"]),
    ],
    # ---------------------------------------------------------------- Ascaris lumbricoides
    "ascaris_lumbricoides": [
        _c("Morfologia", "Ovos férteis: arredondados, de casca grossa e camada externa mamilada, muitas vezes corada em marrom pela bile; podem estar decorticados, isto é, sem a camada externa.", ["dpdx_asc"]),
        _c("Morfologia", "Ovos inférteis: alongados e maiores que os férteis, com casca mais fina, camada mamilada variável e interior com massa de grânulos refráteis.", ["dpdx_asc"]),
        _c("Morfologia", "Vermes adultos têm três lábios na extremidade anterior, em ambos os sexos. A fêmea tem cauda reta; o macho, cauda curvada.", ["dpdx_asc"]),
        _c("Clínica", "Em infecções intensas, sobretudo em crianças, podem ocorrer desnutrição e crescimento atrofiado.", ["dpdx_asc"]),
        _c("Clínica", "Cargas elevadas de vermes podem causar dor abdominal e obstrução intestinal; em infecções de intensidade muito alta, pode ocorrer perfuração intestinal.", ["dpdx_asc"]),
        _c("Clínica", "Vermes migrantes podem causar oclusão sintomática das vias biliares, apendicite, ou expulsão pelo nariz ou pela garganta, sobretudo quando há uma única fêmea.", ["dpdx_asc"]),
        _c("Clínica", "Os adultos geralmente não causam sintomas agudos.", ["dpdx_asc"]),
    ],
    # ---------------------------------------------------------------- Enterobius vermicularis
    "enterobius_vermicularis": [
        _c("Morfologia", "Fêmea adulta com cauda longa e pontiaguda; macho com extremidade posterior arredondada e um espículo. Os ovos geralmente são eliminados parcialmente embrionados.", ["dpdx_ent"]),
        _c("Clínica", "A infecção é frequentemente assintomática. O sintoma mais típico é prurido perianal, sobretudo à noite, que pode levar a escoriações e superinfecção bacteriana.", ["dpdx_ent"]),
        _c("Clínica", "Ocasionalmente ocorrem vulvovaginite e granulomas pélvicos ou peritoneais. Outros sintomas citados são bruxismo, enurese, insônia, anorexia, irritabilidade e dor abdominal, que pode imitar apendicite. A colite eosinofílica é rara.", ["dpdx_ent"]),
        _c("Clínica", "Transmissão: autoinoculação (ovos levados à boca após coçar a região perianal), exposição a ovos em superfícies, roupas e roupas de cama contaminadas e, raramente, inalação de ovos suspensos no ar. A retroinfecção pode ocorrer; sua frequência é desconhecida.", ["dpdx_ent"]),
    ],
    # ---------------------------------------------------------------- Strongyloides stercoralis
    "strongyloides_stercoralis": [
        _c("Morfologia", "Larva rabditoide (L1) de 180–380 µm: esôfago rabditoide dividido em três seções, ocupando cerca de um terço do corpo; a L2 é mais longa e tem razão esôfago:intestino menor.", ["dpdx_stro"]),
        _c("Morfologia", "Fêmea parasita longa e delgada, de 2,0–3,0 mm. Não há machos parasitas; os machos de vida livre medem até 0,75 mm e as fêmeas de vida livre, até 1,0 mm.", ["dpdx_stro"]),
        _c("Morfologia", "Ovos: a página não informa as dimensões dos ovos de S. stercoralis; os ovos eclodem na mucosa do intestino delgado.", ["dpdx_stro"], st="ressalva",
           nota="Dimensões dos ovos de S. stercoralis não constam na página. Para S. fuelleborni, a seção de morfologia dá 50–60 × 30–40 µm e a de diagnóstico, 45–55 × 30–35 µm: valores discrepantes dentro da própria página."),
        _c("Clínica", "Forma aguda: rash pruriginoso e eritematoso no local de penetração da pele e tosse seca com irritação traqueal. Após deglutição das larvas, podem ocorrer diarreia, constipação, dor abdominal e anorexia.", ["dpdx_stro"]),
        _c("Clínica", "Forma crônica: geralmente assintomática. Podem ocorrer manifestações gastrointestinais e cutâneas e, raramente, artrite, arritmias, má absorção crônica, obstrução duodenal, síndrome nefrótica e asma recorrente. Até 75% dos pacientes têm eosinofilia leve ou IgE elevada.", ["dpdx_stro"]),
        _c("Clínica", "Síndrome de hiperinfecção: associada, sobretudo, a infecção subclínica em pacientes que recebem corticosteroides em altas doses; a imunidade prejudicada acelera a autoinfecção, e as larvas ficam limitadas ao trato gastrointestinal e aos pulmões. Sem tratamento, a mortalidade pode chegar a cerca de 90%.", ["dpdx_stro"]),
        _c("Clínica", "Estrongiloidíase disseminada: as larvas invadem vários órgãos, com complicações potencialmente graves. Pacientes imunocomprometidos com doença disseminada geralmente têm IgG detectável, embora possam ocorrer falsos negativos.", ["dpdx_stro"]),
    ],
    # ---------------------------------------------------------------- Trichuris trichiura
    "trichuris_trichiura": [
        _c("Morfologia", "Adultos com extremidade anterior longa, em forma de chicote, em ambos os sexos. A região posterior é enrolada nos machos e reta nas fêmeas.", ["dpdx_tri"]),
        _c("Clínica", "Na maioria das vezes assintomática. Infecções intensas, sobretudo em crianças pequenas, podem causar dor abdominal, diarreia e prolapso retal, além de possível retardo do crescimento.", ["dpdx_tri"]),
        _c("Clínica", "O prolapso retal é citado como manifestação de infecções intensas; a página não detalha seus sinais.", ["dpdx_tri"]),
    ],
    # ---------------------------------------------------------------- Taenia sp.
    "taenia_sp": [
        _c("Morfologia", "Proglotes grávidas são mais longas que largas. T. solium tem escólex com quatro ventosas grandes e rostelo com duas fileiras de ganchos; T. saginata tem quatro ventosas grandes, sem rostelo nem ganchos rostelares; T. asiatica tem acúleos rudimentares em formação verrucosa.", ["dpdx_taen"]),
        _c("Tamanho", "Escólex com 1–2 mm de diâmetro. T. saginata tem entre 1.000 e 2.000 proglotes; T. solium, em média, cerca de 1.000.", ["dpdx_taen"]),
        _c("Clínica", "Teníase por T. saginata: causa apenas sintomas abdominais leves. O achado mais marcante é a eliminação de proglotes, ativa ou passiva. Proglotes migrantes podem, ocasionalmente, causar apendicite ou colangite.", ["dpdx_taen"]),
        _c("Clínica", "Teníase por T. solium: costuma ser menos sintomática; o principal sintoma é geralmente a eliminação passiva de proglotes.", ["dpdx_taen"]),
        _c("Clínica", "Cisticercose (larva de T. solium): cistos (cisticercos) se instalam em tecidos como músculo, cérebro e olho. Os sinais dependem da localização e do número de cistos e podem surgir meses a anos após a infecção, geralmente quando os cistos começam a morrer.", ["cdc_cysti"]),
        _c("Clínica", "Neurocisticercose: é a cisticercose no cérebro ou no sistema nervoso central. A página consultada do CDC trata convulsões como sintoma controlado com medicamentos e cita o inchaço cerebral como fator na decisão cirúrgica.", ["cdc_cysti"], st="ressalva",
           nota="Lista específica de sinais da neurocisticercose, e a menção a hidrocefalia, não constam na página do CDC consultada. As outras afirmações desta seção vêm de fontes complementares."),
        _c("Clínica", "A infecção por ovos de T. solium pode causar cisticercose; comer carne de porco não causa cisticercose. Autoinfecção: a pessoa com a tênia pode infectar a si mesma e outras pessoas da família com os ovos.", ["cdc_cysti", "dpdx_taen"]),
    ],
    # ---------------------------------------------------------------- Hymenolepis nana
    "hymenolepis_nana": [
        _c("Morfologia", "Para comparação com H. nana, os ovos de H. diminuta são redondos ou levemente ovais, de 70–85 × 60–80 µm, e não têm filamentos polares.", ["dpdx_hym"]),
        _c("Morfologia", "Cisticercoide: forma-se em artrópodes intermediários (como besouros do gênero Tribolium e pulgas) a partir dos ovos ingeridos; em H. nana, também pode se desenvolver na vilosidade intestinal. Tamanho e demais características do cisticercoide não constam na página.", ["dpdx_hym"], st="ressalva",
           nota="A página não informa tamanho nem demais características morfológicas do cisticercoide."),
        _c("Tamanho", "Adulto de H. nana: 15–40 mm. Adulto de H. diminuta (comparação): 20–60 cm, com escólex de quatro ventosas.", ["dpdx_hym"]),
        _c("Clínica", "A maioria das infecções é assintomática. Infecções intensas por H. nana podem causar fraqueza, dor de cabeça, anorexia, dor abdominal e diarreia. Sinais específicos não constam na página.", ["dpdx_hym"]),
        _c("Clínica", "Autoinfecção em H. nana: o embrião (hexacanto) eclode no intestino, penetra a vilosidade e continua o ciclo sem passar pelo ambiente externo, o que pode manter a infecção por anos.", ["dpdx_hym"]),
    ],
    # ---------------------------------------------------------------- Schistosoma mansoni
    "schistosoma_mansoni": [
        _c("Morfologia", "Ovos de S. mansoni: 114–180 µm por 45–70 µm, com espinho lateral proeminente próximo à extremidade posterior; a extremidade anterior é afilada e levemente curvada. Ao serem eliminados nas fezes, já contêm miracídio maduro.", ["dpdx_schi"]),
        _c("Morfologia", "Sexos separados (dioicos). O macho é robusto e tuberculado; a fêmea é mais longa e delgada e permanece no canal ginecóforo do macho.", ["dpdx_schi"]),
        _c("Morfologia", "Miracídio: eclode do ovo e nada até penetrar o caramujo hospedeiro intermediário. Cercária: é a forma infectante; penetra a pele humana e perde a cauda bifurcada ao se transformar em esquistossômulo.", ["dpdx_schi"], st="ressalva",
           nota="A página não traz descrição morfológica detalhada do miracídio nem da cercária."),
        _c("Tamanho", "Adultos: macho de 6 a 12 mm; fêmea de 7 a 17 mm.", ["dpdx_schi"]),
        _c("Clínica", "Fase aguda (febre de Katayama): reação de hipersensibilidade sistêmica que pode ocorrer semanas após a infecção, com febre, tosse, dor abdominal, diarreia, hepatoesplenomegalia e eosinofilia. Antes, podem surgir lesões cutâneas locais, pruriginosas e maculopapulares, no local de penetração das cercárias.", ["dpdx_schi"]),
        _c("Doença", "Esquistossomose por S. mansoni: a infecção contínua pode causar reações granulomatosas e fibrose no fígado e no baço. Muitas infecções são assintomáticas.", ["dpdx_schi"]),
        _c("Clínica", "Ovos depositados em outros órgãos podem causar lesões granulomatosas; em S. mansoni, a página cita a medula espinhal.", ["dpdx_schi"], st="ressalva",
           nota="A página não rotula explicitamente a fase de infecção contínua como 'crônica'. Os sinais por fase, além dos citados, não constam."),
    ],
    # ---------------------------------------------------------------- Giardia lamblia
    "giardia_lamblia": [
        _c("Morfologia", "Número de flagelos: a página lida não informa; o valor citado no atlas em outra fonte (8) não foi confirmado nesta leitura.", ["dpdx_giar"], st="ressalva",
           nota="Número de flagelos não consta na página do CDC consultada."),
        _c("Clínica", "Incubação de 1 a 14 dias (média de 7). A doença aguda costuma durar de 1 a 3 semanas.", ["dpdx_giar"]),
        _c("Clínica", "Sintomas: diarreia, dor abdominal, distensão abdominal, náusea e vômito. Na forma crônica, os sintomas são recorrentes, podendo haver má absorção e debilitação. O quadro varia de portador assintomático a diarreia grave com má absorção.", ["dpdx_giar"]),
        _c("Clínica", "Transmissão: ingestão de cistos presentes em água ou alimentos contaminados, ou via fecal-oral pelas mãos ou por fômites. Como os cistos são infecciosos já ao serem eliminados, a transmissão pessoa a pessoa é possível. O papel de animais como reservatórios não está claro.", ["dpdx_giar"]),
    ],
    # ---------------------------------------------------------------- Entamoeba histolytica
    "entamoeba_histolytica": [
        _c("Morfologia", "Trofozoíto: citoplasma granular (aspecto 'ground-glass'), núcleo único com cariossomo central e cromatina periférica uniformemente distribuída. Trofozoítos de fezes diarreicas tendem a ser mais alongados.", ["dpdx_amoeb"]),
        _c("Clínica", "Amebíase intestinal: a maioria das infecções restritas ao lúmen é assintomática. Na colite invasiva, há disenteria grave. Infecções crônicas graves podem levar a peritonite, perfurações e granulomas amebianos (ameboma).", ["dpdx_amoeb"]),
        _c("Clínica", "Amebíase extraintestinal: o abscesso hepático amebiano é a manifestação mais comum. Também foram observados abscessos pleuropulmonares e cerebrais e lesões necróticas na pele perianal e genital.", ["dpdx_amoeb"]),
        _c("Clínica", "Sinais e sintomas específicos (como febre e dor abdominal) não constam na página do CDC consultada.", ["dpdx_amoeb"], st="ressalva",
           nota="Sinais específicos não constam na página do CDC consultada; os sintomas listados no atlas vêm de fontes complementares."),
    ],
    # ---------------------------------------------------------------- Entamoeba coli
    "entamoeba_coli": [
        _c("Morfologia", "Cisto: 10–35 µm, geralmente esférico, podendo ser alongado; geralmente 8 núcleos, podendo ter 16 ou mais. É a única espécie de Entamoeba em humanos com mais de quatro núcleos no estágio de cisto. Corpos cromatoides, quando presentes, têm forma de lasca com extremidades pontiagudas.", ["dpdx_intam"]),
        _c("Morfologia", "Trofozoíto: 15–50 µm, com um núcleo, cariossomo grande e excêntrico e cromatina periférica grossa e irregular. Citoplasma granular e vacuolizado; pseudópodes curtos e rombudos e movimento não direcional.", ["dpdx_intam"]),
        _c("Doença", "Não causa doença sintomática: a colonização é não invasiva. Trofozoítos ou cistos nas fezes indicam exposição fecal da pessoa.", ["dpdx_intam"]),
    ],
    # ---------------------------------------------------------------- Endolimax nana
    "endolimax_nana": [
        _c("Morfologia", "Cisto: 5–10 µm, de esférico a elipsoidal, com quatro núcleos pequenos, de cariossomo grande, geralmente central, e sem cromatina periférica. Os núcleos não são visíveis em preparações úmidas não coradas; não há corpos cromatoides.", ["dpdx_intam"]),
        _c("Morfologia", "Trofozoíto: 6–12 µm, com um núcleo cujo cariossomo é grande, irregular e em forma de mancha, sem cromatina periférica. Citoplasma granular, muitas vezes vacuolizado.", ["dpdx_intam"]),
        _c("Doença", "Não causa doença sintomática. Pode ser difícil de diferenciar de Iodamoeba buetschlii.", ["dpdx_intam"]),
    ],
    # ---------------------------------------------------------------- Chilomastix mesnili
    "chilomastix_mesnili": [
        _c("Morfologia", "Trofozoíto de 6–24 µm, 'pear-shaped' (em forma de pera), com extremidade anterior arredondada e posterior afilada e um único núcleo com cariossomo excêntrico.", ["dpdx_chilo"]),
        _c("Morfologia", "Número de flagelos, dimensões e forma do cisto não constam na página do CDC consultada (há apenas legendas de figuras).", ["dpdx_chilo"], st="ressalva",
           nota="A página não traz texto descritivo sobre o cisto nem o número de flagelos."),
        _c("Doença", "Considerado não patogênico; sinais e sintomas não constam na página.", ["dpdx_chilo"]),
        _c("Doença", "Cistos ou trofozoítos nas fezes podem indicar contaminação fecal de alimento ou água e não excluem outras parasitoses.", ["dpdx_chilo"]),
    ],
    # ---------------------------------------------------------------- Blastocystis sp. (em revisão)
    "blastocystis_sp": [
        _c("Morfologia", "Forma vacuolar: é a forma predominante nas fezes humanas. Tem tamanho de 5 a 40 µm, com faixa usual de 8 a 10 µm nas fezes humanas; é esférica a oval, com um vacúolo central cercado por fina borda de citoplasma com até seis núcleos. Cora de vermelho a azul pelo tricrômico.", ["dpdx_blasto"]),
        _c("Morfologia", "Forma cística: de 3 a 5 µm. É postulada como forma infectante, hipótese ainda não confirmada.", ["dpdx_blasto"]),
        _c("Morfologia", "Formas granular e amebóide: observadas em fezes e/ou cultura, sem descrição de tamanho ou características na página; seu papel biológico requer mais investigação.", ["dpdx_blasto"], st="ressalva",
           nota="A página não descreve tamanho nem características das formas granular e amebóide."),
        _c("Doença", "Potencial patogênico em debate: a página afirma que a capacidade de causar doença gastrointestinal em humanos 'continues to be debated and investigated'. Foi detectado tanto em pessoas sintomáticas quanto assintomáticas.", ["dpdx_blasto"], st="ressalva",
           nota="Sintomas atribuídos ao Blastocystis não constam na página do CDC consultada."),
    ],
    # ---------------------------------------------------------------- Iodamoeba buetschlii (em revisão)
    "iodamoeba_buetschlii": [
        _c("Morfologia", "Cisto: 5–20 µm, de quase esférico a elipsoidal, com um núcleo que não é visível em preparações não coradas nem com iodo. Característica diagnóstica principal: uma grande massa compacta de glicogênio, que aparece marrom-avermelhada com iodo e não cora com tricrômico.", ["dpdx_intam"],
           nota="Grafia 'buetschlii' conforme worldspecies (nome aceito) e a página do CDC; a página do CDC também usa o sinônimo 'bütschlii'."),
        _c("Morfologia", "Trofozoíto: 8–20 µm, com um núcleo de cariossomo grande, geralmente central, cercado por grânulos acromáticos refringentes. Citoplasma grosseiramente granular e vacuolizado, podendo conter bactérias, leveduras ou outros materiais. Movimento lento e não progressivo.", ["dpdx_intam"]),
        _c("Doença", "Não causa doença sintomática, pois a colonização é não invasiva. Pode ser difícil de diferenciar de Endolimax nana.", ["dpdx_intam"]),
    ],
}
