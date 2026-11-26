// Galeria estática da ficha da espécie: imagem principal + miniaturas. Sem gestos na página
// (a rolagem do celular nunca é capturada): tocar na imagem abre o visualizador com zoom.
import { h, clear } from './dom.js';
import { imgSrc } from './store.js';
import { icon } from './icons.js';
import { openLightbox } from './lightbox.js';
import { IMGTYPE, CONF, creditText, creditPending } from './meta.js';

export function createGallery(s) {
  const imgs = s.images; let i = 0;
  const main = h('img', { class: 'g-img', alt: '', decoding: 'async' });
  const stage = h('button', { type: 'button', class: 'g-stage', 'aria-label': 'Ampliar imagem (zoom)', onClick: () => openLightbox(imgs, i, { title: s.commonName }) },
    main, h('span', { class: 'g-cta' }, icon('expand', 16), h('span', null, 'Ampliar')));
  const info = h('div', { class: 'img-info', 'aria-live': 'polite' });
  const thumbs = h('div', { class: 'thumbs', role: 'list', 'aria-label': 'Imagens desta espécie' });
  const btns = imgs.map((im, k) => {
    const b = h('button', { type: 'button', class: 'thumb-btn', role: 'listitem', title: im.alt, 'aria-label': `Imagem ${k + 1} de ${imgs.length}: ${im.alt}`, onClick: () => show(k) },
      h('img', { src: imgSrc(im), alt: '', loading: 'lazy', width: im.width, height: im.height }),
      h('span', null, im.figure ? `Fig. ${im.figure}` : im.lamina ? `#${String(im.lamina).padStart(2, '0')}` : 'foto'));
    thumbs.append(b); return b;
  });
  function show(k) {
    i = k; const im = imgs[k];
    main.src = imgSrc(im); main.alt = im.alt || ''; main.width = im.width; main.height = im.height;
    stage.style.setProperty('--ar', `${im.width} / ${im.height}`);
    btns.forEach((b, j) => { const on = j === k; b.classList.toggle('on', on); b.setAttribute('aria-current', String(on)); });
    const conf = CONF[im.confidence];
    clear(info).append(
      h('div', { class: 'badges' }, h('span', { class: 'badge ' + (im.type === 'microfotografia' ? 'ok' : 'warn') }, IMGTYPE[im.type] || im.type),
        im.figure ? h('span', { class: 'badge' }, `Figura ${im.figure} (doc. v4)`) : null,
        im.lamina ? h('span', { class: 'badge' }, `Lâmina ${String(im.lamina).padStart(2, '0')} · ${im.kind === 'detalhe' ? 'detalhe ampliado' : 'campo geral'}`) : null,
        im.detail ? h('span', { class: 'badge' }, '+ ampliação digital') : null,
        conf ? h('span', { class: 'badge ' + conf[1] }, conf[0]) : null,
        im.credit && creditPending(im) ? h('span', { class: 'badge warn' }, 'Autoria a confirmar') : null),
      im.caption ? h('p', { class: 'caption' }, im.caption) : null,
      h('p', { class: 'credit', title: im.dateBasis || null }, creditText(im)));
    const b = btns[k]; thumbs.scrollLeft = Math.max(0, b.offsetLeft - (thumbs.clientWidth - b.offsetWidth) / 2);
  }
  show(0);
  return h('div', { class: 'gallery' }, stage, imgs.length > 1 ? thumbs : null, info);
}
