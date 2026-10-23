#!/usr/bin/env node
// Valida a integridade dos dados do atlas. Uso: node tools/validar-dados.mjs
// Sai com código 1 se houver erro. Sem dependências.
import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'public');
const rd = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const errs = [], warns = []; const E = m => errs.push(m), W = m => warns.push(m);
const STATUS = ['publicado', 'revisar', 'rascunho'], IMG = ['ilustracao', 'externa', 'microfotografia'], CONF = ['confirmada', 'alta', 'media', 'documento'];
const reg = rd('data/modulos.json'); const ids = new Set(); let total = 0, lowres = 0;
function pngJpegSize(f) { // lê dimensões de JPEG/PNG sem dependências
  const b = fs.readFileSync(f);
  if (b[0] === 0x89 && b[1] === 0x50) return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
  if (b[0] === 0xff && b[1] === 0xd8) { let i = 2; while (i < b.length) { if (b[i] !== 0xff) { i++; continue; } const m = b[i + 1]; if (m >= 0xc0 && m <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(m)) return { h: b.readUInt16BE(i + 5), w: b.readUInt16BE(i + 7) }; i += 2 + b.readUInt16BE(i + 2); } }
  return null;
}
for (const m of reg.modules) {
  if (!fs.existsSync(path.join(root, m.dataFile))) { E(`módulo ${m.id}: dataFile ausente (${m.dataFile})`); continue; }
  const { specimens } = rd(m.dataFile);
  for (const s of specimens) {
    total++; const t = `${m.id}/${s.id}`;
    if (!/^[a-z0-9_\-]+$/.test(s.id)) E(`${t}: id inválido (use a-z, 0-9, _ e -)`);
    if (ids.has(m.id + s.id)) E(`${t}: id duplicado`); ids.add(m.id + s.id);
    for (const k of ['commonName', 'scientificName', 'category', 'morphologyDescription']) if (!s[k]) E(`${t}: campo obrigatório ausente: ${k}`);
    if (!STATUS.includes(s.status)) E(`${t}: status inválido "${s.status}"`);
    if (s.status === 'revisar' && !s.reviewNote) E(`${t}: status "revisar" exige reviewNote`);
    if (!Array.isArray(s.images) || !s.images.length) { E(`${t}: images[] ausente ou vazio`); continue; }
    const iids = new Set();
    for (const im of s.images) {
      const it = `${t}#${im.id}`;
      if (!im.id || iids.has(im.id)) E(`${it}: id de imagem ausente/duplicado`); iids.add(im.id);
      if (!IMG.includes(im.type)) E(`${it}: type inválido "${im.type}"`);
      if (!im.alt) E(`${it}: alt ausente (acessibilidade)`);
      if (im.confidence && !CONF.includes(im.confidence)) E(`${it}: confidence inválida "${im.confidence}"`);
      const f = path.join(root, 'assets/img', im.file);
      if (!fs.existsSync(f)) E(`${it}: arquivo não existe (${im.file})`);
      else { const d = pngJpegSize(f); if (d && (d.w !== im.width || d.h !== im.height)) E(`${it}: dimensões declaradas ${im.width}x${im.height} ≠ reais ${d.w}x${d.h}`); }
      if (im.type === 'microfotografia' && !im.credit) W(`${it}: microfotografia sem crédito`);
      if (im.creditStatus && !['informado', 'a-confirmar'].includes(im.creditStatus)) E(`${it}: creditStatus inválido`);
      if (im.date && !/^\d{4}-\d{2}-\d{2}$/.test(im.date)) E(`${it}: date deve ser AAAA-MM-DD`);
      if (im.creditStatus === 'a-confirmar') W(`${it}: autoria a confirmar`);
      if (im.type === 'externa' && s.status === 'publicado') W(`${it}: imagem externa em registro publicado — confirme origem/licença`);
      if (im.type === 'microfotografia' && im.width < 800 && im.height < 800) lowres++;
      for (const h of im.hotspots || []) { if (!(h.x >= 0 && h.x <= 100 && h.y >= 0 && h.y <= 100)) E(`${it}: hotspot ${h.id} fora de 0–100`); if (!h.title || !h.description) E(`${it}: hotspot ${h.id} sem título/descrição`); }
      if (new Set((im.hotspots || []).map(h => h.id)).size !== (im.hotspots || []).length) E(`${it}: ids de hotspot duplicados`);
    }
  }
}
const quiz = rd('data/quiz.json'); const qids = new Set();
for (const q of quiz) { if (qids.has(q.id)) E(`quiz ${q.id}: duplicado`); qids.add(q.id); if (!(q.correctIndex >= 0 && q.correctIndex < q.options.length)) E(`quiz ${q.id}: correctIndex fora do intervalo`); if (new Set(q.options).size !== q.options.length) W(`quiz ${q.id}: alternativas repetidas`); }
const prot = rd('data/protocolos.json'); const art = rd('data/artefatos.json');
// referências e protocolos: todo parâmetro conferido precisa apontar para fonte existente e legível
const refsDoc = rd('data/referencias.json'); const REFID = new Set(); const VST = ['confirmado', 'corrigido', 'removido', 'ressalva'];
for (const r of refsDoc.items) {
  if (!r.id || REFID.has(r.id)) E(`referência ${r.id}: id ausente/duplicado`); REFID.add(r.id);
  if (!r.citation || !r.short || !r.access) E(`referência ${r.id}: falta citation/short/access`);
  if (r.doi && !/^10\.\d{4,9}\/\S+$/.test(r.doi)) E(`referência ${r.id}: DOI malformado`);
  if (r.pmid && !/^\d+$/.test(r.pmid)) E(`referência ${r.id}: PMID malformado`);
  if (r.url && !/^https:\/\//.test(r.url)) E(`referência ${r.id}: url precisa ser https`);
  if (!r.doi && !r.pmid && !r.url && !['classicos', 'docx_protoz'].includes(r.id)) W(`referência ${r.id}: sem DOI/PMID/URL (não rastreável)`);
}
if (!refsDoc.review || !refsDoc.review.reviewedOn || !refsDoc.review.notValidation) E('referencias.json: faltam review.reviewedOn / review.notValidation');
// verificação científica por afirmação (espécies, quiz, artefatos)
const VSP = ['confirmado', 'corrigido', 'ressalva', 'observacao']; let nClaims = 0, nRemoved = 0;
for (const m of reg.modules) {
  for (const s of rd(m.dataFile).specimens) {
    const t = `${m.id}/${s.id}`; const ver = s.verification || [];
    if (!ver.length) E(`${t}: sem "verification" (todas as afirmações precisam de status e fonte)`);
    const shown = [s.approxSizeMicrons, s.morphologyDescription, s.disease, s.pathogenesis, s.benchTip, s.differentialDiagnosis, ...(s.keyDiagnosticFeatures || []), ...(s.clinicalManifestations || []), ...(s.treatment || []), ...(s.prophylaxis || [])].filter(Boolean);
    const texts = ver.map(v => v.text);
    for (const v of ver) {
      nClaims++;
      if (!VSP.includes(v.status)) E(`${t} ${v.id}: status inválido "${v.status}"`);
      if (v.status !== 'observacao' && !(v.refs || []).length) E(`${t} ${v.id}: ${v.status} sem referência`);
      if (v.status === 'corrigido' && !v.before) E(`${t} ${v.id}: corrigido sem texto anterior ("before")`);
      for (const r of v.refs || []) if (!REFID.has(r)) E(`${t} ${v.id}: referência inexistente "${r}"`);
      if (v.status !== 'observacao' && !v.evidence) E(`${t} ${v.id}: sem trecho-evidência`);
    }
    for (const sh of shown) { const parts = sh.split(' · ').length > 1 && sh === s.approxSizeMicrons ? sh.split(' · ') : [sh]; for (const part of parts) if (!texts.some(x => part.includes(x) || x === part)) { if (!texts.some(x => sh.includes(x))) E(`${t}: texto exibido sem registro de verificação: "${part.slice(0, 60)}…"`); } }
    nRemoved += (s.removed || []).length;
    const d = s.diagnosticMethods || {}; const dm = [d.goldStandard, ...(d.alternatives || []), d.sampleType, d.technicalObservation].filter(Boolean);
    const c = s.transmissionAndCycle || {}; const cy = [c.transmissionRoute, c.infectiveForm, c.diagnosticForm, c.habitat, c.cycleType].filter(Boolean);
    for (const sh of [...dm, ...cy]) if (!texts.some(x => sh.includes(x))) E(`${t}: texto de diagnóstico/ciclo sem registro de verificação: "${sh.slice(0, 60)}…"`);
  }
}
for (const q of quiz) { for (const r of q.refs || []) if (!REFID.has(r)) E(`quiz ${q.id}: referência inexistente "${r}"`); if (!(q.refs || []).length) E(`quiz ${q.id}: sem referência`); }
for (const a of art.itens || []) { for (const r of a.refs || []) if (!REFID.has(r)) E(`artefato ${a.nome}: referência inexistente "${r}"`); if (!(a.refs || []).length) E(`artefato ${a.nome}: sem referência`); }
console.log(`Afirmações verificadas: ${nClaims} | itens removidos (auditoria): ${nRemoved}`);
for (const p of prot) {
  const where = `protocolo ${p.id}`; const own = new Set(p.refs || []);
  for (const k of ['title', 'indication', 'principle']) if (!p[k]) E(`${where}: falta ${k}`);
  for (const k of ['stepByStep', 'evidence', 'verification', 'refs']) if (!Array.isArray(p[k]) || !p[k].length) E(`${where}: ${k} vazio/ausente`);
  for (const id of own) if (!REFID.has(id)) E(`${where}: referência inexistente "${id}"`);
  const cited = [...(p.evidence || []).flatMap(e => e.refs || []), ...(p.verification || []).flatMap(v => v.refs || []), ...((p.intensity && p.intensity.refs) || [])];
  for (const id of cited) { if (!REFID.has(id)) E(`${where}: citação a referência inexistente "${id}"`); else if (!own.has(id)) E(`${where}: cita "${id}" mas não a lista em refs`); }
  for (const e of p.evidence || []) if (!(e.refs || []).length) E(`${where}: evidência sem fonte: "${(e.text || '').slice(0, 50)}…"`);
  for (const v of p.verification || []) {
    if (!VST.includes(v.status)) E(`${where}: status de conferência inválido "${v.status}"`);
    if ((v.status === 'confirmado' || v.status === 'corrigido') && !(v.refs || []).length) E(`${where}: "${v.item}" é ${v.status} mas não cita fonte`);
  }
}

// imagens órfãs (arquivo em assets/img sem registro)
const used = new Set(); for (const m of reg.modules) for (const s of rd(m.dataFile).specimens) for (const im of s.images || []) used.add(im.file);
for (const d of fs.readdirSync(path.join(root, 'assets/img')).filter(x => x !== 'brand')) for (const f of fs.readdirSync(path.join(root, 'assets/img', d))) if (!used.has(`${d}/${f}`)) W(`imagem órfã (sem registro): ${d}/${f}`);
if (lowres) W(`${lowres} imagem(ns) de baixa resolução (<800 px nos dois lados): substitua pelos arquivos originais (tools/preparar-imagem.py)`);
console.log(`Espécies: ${total} | quiz: ${quiz.length} | protocolos: ${prot.length} | artefatos: ${art.itens.length}`);
warns.forEach(w => console.log('AVISO ', w)); errs.forEach(e => console.log('ERRO  ', e));
console.log(errs.length ? `\n${errs.length} erro(s).` : '\nDados íntegros.'); process.exit(errs.length ? 1 : 0);
