import { h } from '../dom.js';
import { store } from '../store.js';
import { page, refName } from './common.js';
import { imgSrc } from '../store.js';
import { openLightbox } from '../lightbox.js';
import { icon } from '../icons.js';

export function artifactsPage() {
  const a = store.artifacts;
  return page('Artefatos',
    h('h1', null, 'Guia de artefatos'), h('p', { class: 'lead' }, 'Como não confundir estruturas inertes e resíduos com parasitas na microscopia óptica.'),
    h('div', { class: 'grid art' }, a.itens.map((it, i) => h('article', { class: 'card art-item' }, h('h3', null, `${i + 1}. ${it.nome}`), h('p', { class: 'badge bad' }, 'Confundida com: ' + it.confundidaCom), h('p', null, h('strong', null, 'Como diferenciar: '), it.comoDiferenciar), it.status ? h('p', { class: 'badge ' + (it.status === 'ressalva' ? 'bad' : 'ok') }, it.status === 'ressalva' ? 'Com ressalva' : it.status) : null, (it.refs || []).length ? h('p', { class: 'muted small' }, 'Fontes: ' + it.refs.map(refName).join('; ')) : null, it.evidencia ? h('p', { class: 'muted small' }, 'Evidência: ' + it.evidencia) : null))),
    h('aside', { class: 'tip' }, h('strong', null, 'Dica de bancada'), h('p', null, a.dica)),
    unidentified(a.naoIdentificadas));
}

function unidentified(n) {
  if (!n || !(n.fotos || []).length) return h('p', { class: 'muted' }, 'Este guia ainda não tem fotos de artefatos reais; ele será ilustrado quando houver microfotografias de bolhas, pólen, fibras e amido.');
  return h('section', { class: 'sec wide' }, h('h2', null, n.titulo), h('div', { class: 'notice', role: 'note' }, n.aviso),
    h('div', { class: 'grid specs' }, n.fotos.map((im, i) => h('figure', { class: 'card fig' },
      h('button', { type: 'button', class: 'g-stage', 'aria-label': `Ampliar: ${im.alt}`, style: { '--ar': `${im.width} / ${im.height}` }, onClick: () => openLightbox(n.fotos, i, { title: n.titulo }) },
        h('img', { class: 'g-img', src: imgSrc(im), alt: im.alt, loading: 'lazy', width: im.width, height: im.height }), h('span', { class: 'g-cta' }, icon('expand', 16), h('span', null, 'Ampliar'))),
      h('figcaption', { class: 'card-body small' }, im.caption)))));
}
