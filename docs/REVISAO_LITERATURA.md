# Revisão da literatura dos protocolos (17/10/2026)

Objetivo: conferir cada parâmetro dos cinco protocolos de `public/data/protocolos.json` contra fontes que puderam ser lidas, e registrar tudo o que foi corrigido ou retirado. O resultado aparece em **Protocolos** (seção “Conferência”) e nos dados `public/data/protocolos.json` e `public/data/referencias.json` (gerados por `tools/gerar-protocolos.py`).

> **Isto é uma conferência bibliográfica, não uma validação analítica.** Validar um método significa demonstrar, no seu laboratório, desempenho com controles (amostra positiva e negativa, repetibilidade, equipamentos calibrados) e aprovação do responsável. O texto do site deve ser comparado com o POP oficial da disciplina antes de uso em rotina.

## Como a revisão foi feita (reprodutível)
Ferramentas: PubMed (busca e recuperação de registros e textos completos do PubMed Central) e leitor de páginas web. O acesso direto a PMC/NCBI/EuropePMC pelo terminal estava bloqueado; páginas foram lidas por leitor automático que devolve resumo ou trechos, o que limita o que pode ser citado. Cada referência traz o campo `access` com o que foi de fato lido.

Buscas no PubMed (consulta → o que foi usado):
- **Kato-Katz thick smear soil-transmitted helminths diagnostic accuracy** → 8 registros; usado: PMID 21695104.
- **Strongyloides stercoralis diagnosis Baermann agar plate culture sensitivity comparison** → 4 registros.
- **laboratory diagnosis and follow up of strongyloidiasis systematic review** → PMID 23350004 (texto completo lido).
- **Rugai Strongyloides** → 13 registros; usado: PMID 38233532 (resumo).
- **Hoffman Pons Janer** → 32 registros; usado: PMID 37531007 (resumo).
- **Entamoeba histolytica dispar moshkovskii morphologically identical microscopy differentiate** → PMIDs 20169364 e 28030342 (resumos).
- Consultas sem resultado (por serem muito específicas no PubMed): “Enterobius … cellulose tape test sensitivity consecutive days”; “spontaneous sedimentation Hoffman Pons Janer Lutz … zinc sulfate … Faust”; “zinc sulfate flotation Giardia centrifugation specific gravity 1.18 …”; “Rugai method … Baermann-Moraes evaluation”.
- Citações conferidas por `lookup`: Katz et al. 1972 (PMID 4675644) e Barretto 1962 (PMID 13865253). **Não encontrados** no PubMed: Graham 1941 e Faust et al. 1938 (artigos clássicos).

Páginas web lidas: CDC DPDx (procedimento do oxiúro; procedimentos de concentração), Saúde Pública de Ontário (Enterobius), POP.UACAP.049 v3 (hospital universitário, EPF), dissertação UFU (Chaves, 2014), SOP institucional de Kato-Katz, registro bibliográfico do “Bench Aids” da OMS (2019), artigo de Inês et al. (Biomédica, 2016) e de Barretto (1962) via leitor.

Tentativas sem sucesso (para que não se repitam): a página CDC DPDx de enterobíase não pôde ser aberta (permissão negada; foi lida a página do procedimento do oxiúro); o PDF do Ministério da Saúde (Diretrizes de vigilância da esquistossomose, 2014) não devolveu o procedimento do Kato-Katz (o texto extraído trazia só títulos de seção); uma apostila da USP e uma aula prática (e-Disciplinas) só devolveram a página de login; o PMC não pôde ser lido diretamente por captcha.

## Resultado em uma tabela
| Protocolo | Principais correções em relação ao texto anterior |
|---|---|
| Sedimentação (Hoffmann) | massa de fezes/volumes de água ajustados ao POP (≈2 g; 5 + 20 mL; cálice de 200 mL; 2 a 24 h); afirmações de “excelente sensibilidade” retiradas; sensibilidade baixa para larvas documentada (36,4% → 72,7% em 3 amostras) |
| Fita adesiva (Graham) | “sensibilidade >90%” corrigida para **<60% (1 amostra) / ~90% (3) / ~100% (6)**; exame de fezes <10% (não “<5%”); coleta em 3 a 6 dias; xilol/tolueno, 10 cm e Taenia retirados |
| Rugai / Baermann | água 40–45 °C e repouso de ~1 h (antes: 40–42 °C, 60–90 min); “mata acima de 45 °C” e “8–10 g” retirados; sensibilidade comparada (33,3% / 50% / 100%) e limites documentados |
| Faust (sulfato de zinco) | “2.500 rpm por 1 min” retirado (não achado nas fontes) e substituído por forças centrífugas relatadas; leitura em até 15 min (CDC); complexo *E. histolytica/dispar/moshkovskii* indistinguível ao microscópio |
| Kato-Katz | tempos corrigidos (ancilostomídeos 30–60 min; demais após ~2 h); fator 24 com sua variabilidade; classes de intensidade da OMS (Ascaris, Trichuris, ancilostomídeos); “padronizado internacionalmente” invertido (o método é difícil de padronizar); afirmações sem fonte sobre diarreia e protozoários retiradas |

## Limites desta revisão
- O conteúdo clínico, morfológico e de ciclo das **páginas de espécie**, o **quiz** e o **guia de artefatos** não foram revisados nesta rodada.
- Os artigos originais dos métodos clássicos (Lutz; Hoffman, Pons e Janer; Faust; Graham; Rugai, Mattos e Brizola) e o documento da OMS **não foram lidos**; a autoria histórica está marcada como “não conferida”.
- Dois estudos citados são pequenos (Gonçalves 2023: 12 positivos; Rodrigues 2024: 6 positivos em 68) e um é de 1962 (Barretto). As porcentagens foram transcritas com esse contexto; não devem ser lidas como desempenho geral dos métodos.
- Os pontos de corte da OMS foram citados como relatados em Levecke et al. (2011), não do documento da OMS.
- Parâmetros não encontrados nas fontes (por exemplo, rpm do Faust, massa de fezes do Rugai) foram **removidos**, não substituídos por valores de memória. Siga o POP do laboratório.

## Como atualizar
1. Edite os dados em `tools/gerar-protocolos.py` (cada afirmação numérica precisa de `refs`; o que não tem fonte vai para `verification` como `removido` ou `ressalva`).
2. `python3 tools/gerar-protocolos.py .` (na raiz do projeto) e `node tools/validar-dados.mjs`.
3. O validador falha se uma evidência não tem fonte, se uma conferência “confirmado/corrigido” não cita fonte, se um DOI/PMID está malformado ou se uma URL não é https.
