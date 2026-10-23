import { h, slug } from '../dom.js';
import { store } from '../store.js';
import { page, specCard } from './common.js';

export function searchPage(q) {
  const t = slug(q).split(/\s+/).filter(Boolean);
  const hay = s => slug([s.commonName, s.scientificName, s.disease, s.evolutionaryStage, s.category, ...(s.keyDiagnosticFeatures || []), s.differentialDiagnosis || ''].join(' '));
  const res = t.length ? store.specimens.filter(s => { const x = hay(s); return t.every(w => x.includes(w)); }) : [];
  return page('Busca', h('h1', null, `Busca: “${q}”`), h('p', { class: 'muted' }, `${res.length} resultado(s) em ${store.specimens.length} lâminas.`),
    res.length ? h('div', { class: 'grid specs' }, res.map(specCard)) : h('p', null, 'Nada encontrado. Tente o nome científico, a doença ou um critério morfológico.'));
}
