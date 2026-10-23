// Visualização ampliada de uma imagem (e navegação pela galeria da espécie).
// Usa <dialog> modal: Esc fecha, o foco fica preso no diálogo e volta ao elemento que abriu.
import { h, clear } from './dom.js';
import { imgSrc } from './store.js';
import { IMGTYPE, creditText, creditPending } from './meta.js';

let dlg = null, img, head, count, info, prevBtn, nextBtn, state = null, opener = null;

function build() {
  img = h('img', { class: 'lb-img', alt: '' });
  head = h('h2', { class: 'lb-title', id: 'lb-title' });
  count = h('span', { class: 'lb-count', 'aria-live': 'polite' });
  info = h('div', { class: 'lb-info' });
  prevBtn = h('button', { type: 'button', class: 'lb-nav', 'aria-label': 'Imagem anterior', onClick: () => go(-1) }, '‹');
  nextBtn = h('button', { type: 'button', class: 'lb-nav', 'aria-label': 'Próxima imagem', onClick: () => go(1) }, '›');
  const close = h('button', { type: 'button', class: 'btn sm lb-close', 'aria-label': 'Fechar', onClick: () => dlg.close() }, 'Fechar ✕');
  dlg = h('dialog', {
    class: 'lb', 'aria-labelledby': 'lb-title',
    onClick: e => { if (e.target === dlg) dlg.close(); },
    onKeydown: e => { if (e.key === 'ArrowLeft') { go(-1); e.preventDefault(); } else if (e.key === 'ArrowRight') { go(1); e.preventDefault(); } },
    onClose: () => { state = null; if (opener && opener.isConnected) opener.focus(); opener = null; },
  }, h('div', { class: 'lb-head' }, head, count, close), h('div', { class: 'lb-stage' }, prevBtn, img, nextBtn), info);
  document.body.append(dlg);
}

function go(d) {
  if (!state || state.list.length < 2) return;
  state.i = (state.i + d + state.list.length) % state.list.length;
  render();
}

function render() {
  const im = state.list[state.i], n = state.list.length;
  img.src = imgSrc(im);
  img.alt = im.alt || '';
  if (im.width) img.setAttribute('width', String(im.width));
  if (im.height) img.setAttribute('height', String(im.height));
  head.textContent = state.title || im.alt || 'Imagem';
  count.textContent = n > 1 ? `${state.i + 1} de ${n}` : '';
  prevBtn.hidden = nextBtn.hidden = n < 2;
  const tags = [
    h('span', { class: 'badge ' + (im.type === 'microfotografia' ? 'ok' : 'warn') }, IMGTYPE[im.type] || im.type),
    im.lamina ? h('span', { class: 'badge' }, `Lâmina ${String(im.lamina).padStart(2, '0')} · ${im.kind === 'detalhe' ? 'detalhe ampliado' : 'campo geral'}`) : null,
    creditPending(im) ? h('span', { class: 'badge warn' }, im.credit ? 'Autoria a confirmar' : 'Sem crédito') : null,
  ];
  clear(info).append(
    h('div', { class: 'badges' }, tags),
    im.caption ? h('p', { class: 'caption' }, im.caption) : null,
    h('p', { class: 'credit' }, creditText(im)),
    h('p', { class: 'credit' }, `Arquivo: ${im.width || '?'} × ${im.height || '?'} px. `,
      h('a', { href: imgSrc(im), target: '_blank', rel: 'noopener' }, 'Abrir o arquivo em outra aba')));
}

/** @param {object[]} images lista de imagens (objetos do JSON) @param {number} index posição inicial */
export function openLightbox(images, index = 0, { title } = {}) {
  if (!images || !images.length) return;
  if (!dlg) build();
  opener = document.activeElement;
  state = { list: images, i: Math.min(Math.max(0, index), images.length - 1), title };
  render();
  if (!dlg.open) dlg.showModal();
  dlg.querySelector('.lb-close').focus();
}
