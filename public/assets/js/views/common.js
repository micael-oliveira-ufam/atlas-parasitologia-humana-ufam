import { h } from '../dom.js';
import { imgSrc, cover, store } from '../store.js';
import { IMGTYPE, creditText, creditPending } from '../meta.js';
import { openLightbox } from '../lightbox.js';
export { IMGTYPE, creditText, creditPending };

export const STATUS = { publicado: null, revisar: 'Em revisão', rascunho: 'Rascunho' };
export const CONF = { confirmada: ['Identificação confirmada', 'ok'], alta: ['Identificação: alta confiança', 'ok'], media: ['Identificação: média — a confirmar', 'warn'], documento: ['Identificação conforme legenda do documento de lâminas', 'warn'] };
export const STLABEL = { confirmado: ['Confirmado', 'ok'], corrigido: ['Corrigido', 'warn'], ressalva: ['Ressalva', 'bad'], observacao: ['Observação da lâmina', ''] };
export const refName = id => { const r = (store.refs.items || []).find(x => x.id === id); return r ? r.short || r.id : id; };

export function badges(s) {
  const types = [...new Set(s.images.map(i => i.type))];
  const n = s.images.filter(i => i.kind === 'detalhe').length || s.images.length;
  return h('div', { class: 'badges' },
    h('span', { class: 'badge cat' }, s.category),
    ...types.map(t => h('span', { class: 'badge ' + (t === 'microfotografia' ? 'ok' : 'warn') }, (IMGTYPE[t] || t) + (t === 'microfotografia' ? ` · ${n} lâmina${n === 1 ? '' : 's'}` : ''))),
    STATUS[s.status] ? h('span', { class: 'badge bad' }, STATUS[s.status]) : null);
}
export function specCard(s) {
  const c = cover(s), href = `#/m/${s.moduleId}/${s.id}`;
  return h('article', { class: 'card spec' },
    h('button', { type: 'button', class: 'thumb zoomable', title: 'Clique para ampliar', 'aria-label': `Ampliar imagem: ${c.alt}`, onClick: () => openLightbox(s.images, 0, { title: s.commonName }) },
      h('img', { src: imgSrc(c), alt: '', loading: 'lazy', width: c.width, height: c.height })),
    h('div', { class: 'card-body' },
      h('h3', null, h('a', { class: 'card-link', href }, s.commonName)), h('p', { class: 'sci' }, s.scientificName), h('p', { class: 'muted' }, s.disease || s.evolutionaryStage), badges(s),
      h('p', { class: 'more' }, h('a', { href }, 'Abrir ficha completa →'))));
}
export const list = (arr, ordered) => arr && arr.length ? h(ordered ? 'ol' : 'ul', { class: 'list' }, arr.map(x => h('li', null, x))) : null;
export function page(title, ...kids) { return h('section', { class: 'wrap page', dataset: { title } }, ...kids); }
