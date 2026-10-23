# Notas de migração e de dados

## Fase 2 — banco de imagens reais (PDF “Resumo de lâminas — Nematelmintos”)
Substituímos **todas as ilustrações geradas por script** pelas fotos reais do PDF (23 lâminas, cada uma com *campo* e *detalhe ampliado*).

| Espécie (módulo) | Lâminas publicadas | Confiança no PDF |
|---|---|---|
| Ancilostomídeo (Nematelmintos) | #3, #15, #16 | confirmada ×2, alta |
| *Ascaris lumbricoides* | #5, #8, #11, #13, #19 | confirmada ×2, alta ×3 |
| *Enterobius vermicularis* | #7, #21 | alta ×2 |
| *Strongyloides stercoralis* | #9, #10, #18 | alta, média ×2 |
| *Trichuris trichiura* | #20 | alta |
| *Taenia* sp. (Platelmintos) | #2, #4, #23 | média, alta ×2 |
| *Hymenolepis nana* | #6, #12, #17, #22 | confirmada, alta, média ×2 |

- **Fora do site** (`acervo-nao-publicado/`): #1 (estrutura não identificada) e #14 (*H. nana* provável, confiança baixa).
- A identificação e o grau de confiança são **os do PDF**; o site os exibe em cada foto (“confirmada”, “alta confiança”, “média — a confirmar”). Não foram reavaliados taxonomicamente por mim; a inspeção visual das miniaturas foi coerente com os rótulos.
- Lâmina #6 foi atribuída a *H. nana* (ovo central); o ovo de *Taenia* no topo do campo é citado na legenda.
- **Modelo de dados**: de “uma lâmina = um registro” para “uma espécie = um registro com galeria `images[]`”. Isso fundiu os três registros de *Enterobius* e os dois de *H. nana* (10×/40×) em um cada; o texto mantido é o do registro mais completo (nos demais havia, p. ex., a orientação de repetir a coleta de Graham por 3–5 dias, ver `legacy/specimens.original.json`).
- **Marcadores estruturais removidos de todas as espécies**: as coordenadas pertenciam às ilustrações. Recomenda-se refazê-los sobre as fotos reais (suporte por imagem já existe).
- **Aumento (10×/40×) removido**: o PDF não registra a objetiva usada.
- **Dimensão de ancilostomídeo** atualizada para “60 a 70 × 40 µm”, conforme o guia do PDF.
- **Guia de artefatos**: o estudo de caso “bolha de ar × ovo” era baseado em ilustração gerada e foi removido; os 4 itens e a dica permanecem. Será reilustrado quando houver foto real.
- **Limitações**: o PDF só tem miniaturas (360×360 e 480×640; os originais chegam a 6000×8000 px). O zoom mostra pixels. Substitua pelos originais com `tools/preparar-imagem.py`.
- **Crédito** (atualizado em 17/10/2026): as lâminas com arquivo de câmera (`2026MMDD_HHMMSS.jpg`: #2–#19) estão creditadas a “Micael Davi Lima de Oliveira — prática de Parasitologia”, com a data tirada do nome do arquivo (`creditStatus: informado`; o autor declarou serem fotos próprias). As #20–#23 (imagens do post de Instagram do autor) receberam o mesmo crédito com `creditStatus: a-confirmar`, porque a autoria de cada fotografia não está documentada nos arquivos; o site exibe “Autoria a confirmar”. As 3 imagens externas (*Schistosoma*, *Giardia*, *Entamoeba*) continuam **sem crédito** (“origem a confirmar”). Nenhuma licença de reuso foi atribuída: o campo `license` está vazio até o autor decidir.

## Fase 1 — migração do projeto original (AI Studio / React + Firestore)
Conteúdo textual migrado programaticamente (verificado campo a campo contra o original); dado bruto em `legacy/specimens.original.json`, alterações em `legacy/migration-report.json`.

### Mantido como “em revisão” (imagens externas, não eram ilustrações)
- ***Schistosoma mansoni***: imagem é MEV de vermes adultos; o texto descreve o ovo.
- ***Giardia*** e ***Entamoeba*** (módulo Protozoários, “em construção”): imagens de origem desconhecida; a de *Entamoeba* tem coloração tipo tricrômico e um organismo pouco nítido, enquanto o texto descrevia cisto tetranucleado corado por Lugol. *E. histolytica* não se distingue de *E. dispar*/*E. moshkovskii* só pela morfologia.

### Removido (e por quê)
- Ranking/votos, selos de gamificação, `photographerName/Role/photoDate` (dependiam do Firestore e atribuíam autoria fotográfica a pessoas nomeadas em imagens geradas por script), `fieldNotes` (descreviam preparo de lâmina inexistente).
- Troca de objetiva 10×/40×/100×, filtros “Lugol/azul de metileno” e grade micrométrica do visualizador (simulações sobre a mesma imagem; escala sem calibração).
- Firebase/Firestore, painel de curadoria, senha de docente, Gemini API e servidor de upload.
- Atribuições nominais em dicas (“Dica da Dra. Jaila: …”): texto preservado como “Dica de bancada”; restaure o nome em `benchTip` se forem de fato dela.

### Corrigido
- “Hymenolpeis” e “Enterobius vermiculares” (grafia). Quiz: 10 de 15 questões tinham a resposta certa na posição B; as alternativas agora são embaralhadas.

### Segurança (motivo de não usar o Firestore)
`firestore.rules` permitia criar/editar/apagar a **qualquer visitante, sem autenticação**, e a “senha de docente” (`parasito2025`, `jaila2025`) estava em código no navegador. Se o projeto Firebase antigo (`gen-lang-client-0447277814`) continuar ativo, convém desativá-lo. Lâminas cadastradas depois no Firestore **não estão** no zip original.

### Não auditado
O conteúdo clínico/diagnóstico (prevalências, letalidade, sensibilidade de métodos etc.), os 15 itens do quiz e os 5 protocolos foram **carregados como estavam**, sem revisão contra a literatura. Recomenda-se revisão docente antes de divulgar amplamente.
