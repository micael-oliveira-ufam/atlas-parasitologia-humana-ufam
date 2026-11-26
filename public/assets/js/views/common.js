import { h } from '../dom.js';
import { imgSrc, cover, store } from '../store.js';
import { IMGTYPE, CONF, creditText, creditPending, refLabel } from '../meta.js';
import { openLightbox } from '../lightbox.js';
import { icon } from '../icons.js';
export { IMGTYPE, CONF, creditText, creditPending };

export const STATUS = { publicado: null, revisar: 'Em revisão', rascunho: 'Rascunho' };
export const STLABEL = { confirmado: ['Confirmado', 'ok'], corrigido: ['Corrigido', 'warn'], ressalva: ['Ressalva', 'bad'], observacao: ['Observação da lâmina', ''] };
export const refName = refLabel;

/** Primeira frase de um texto longo (cartões e destaques; a ficha mostra o texto completo). */
export const brief = t => { if (!t) return ''; const m = t.match(/^.*?\.(?=\s|$)/); return m ? m[0] : t; };

/** Número de fotos de lâmina da espécie (contagem real das imagens do tipo microfotografia). */
export const nFotos = s => s.images.filter(i => i.type === 'microfotografia').length;

export function badges(s) {
  const types = [...new Set(s.images.map(i => i.type))], n = nFotos(s);
  return h('div', { class: 'badges' },
    h('span', { class: 'badge cat' }, s.category),
    ...types.map(t => h('span', { class: 'badge ' + (t === 'microfotografia' ? 'ok' : 'warn') }, (IMGTYPE[t] || t) + (t === 'microfotografia' ? ` · ${n} foto${n === 1 ? '' : 's'}` : ''))),
    STATUS[s.status] ? h('span', { class: 'badge bad' }, STATUS[s.status]) : null);
}

/** Cartão da espécie: a imagem e o título abrem a ficha; o botão ⤢ abre a galeria ampliada. */
export function specCard(s) {
  const c = cover(s), href = `#/m/${s.moduleId}/${s.id}`;
  return h('article', { class: 'card spec' },
    h('div', { class: 'thumb' },
      h('a', { href, class: 'thumb-link', tabindex: '-1', 'aria-hidden': 'true' }, h('img', { src: imgSrc(c), alt: '', loading: 'lazy', width: c.width, height: c.height })),
      h('button', { type: 'button', class: 'zoom-fab', title: 'Ampliar imagens', 'aria-label': `Ampliar imagens de ${s.commonName}`, onClick: () => openLightbox(s.images, 0, { title: s.commonName }) }, icon('expand', 18)),
      s.images.length > 1 ? h('span', { class: 'pill-n', 'aria-hidden': 'true' }, `${s.images.length} imagens`) : null),
    h('div', { class: 'card-body' },
      h('h3', null, h('a', { class: 'card-link', href }, s.commonName)), h('p', { class: 'sci' }, s.scientificName), h('p', { class: 'muted' }, brief(s.disease) || s.evolutionaryStage), badges(s)));
}
export const list = (arr, ordered) => arr && arr.length ? h(ordered ? 'ol' : 'ul', { class: 'list' }, arr.map(x => h('li', null, x))) : null;
export function page(title, ...kids) { return h('section', { class: 'wrap page', dataset: { title } }, ...kids); }
