// Visualizador em tela cheia, com zoom por gestos (veja zoom.js), navegação pela galeria da espécie,
// ajuste de brilho/contraste e painel de informações (legenda, crédito, fontes).
// <dialog> modal: foco preso, Esc fecha, e o botão "voltar" do celular fecha o visualizador (History API)
// em vez de sair da página.
import { h, clear } from './dom.js';
import { imgSrc } from './store.js';
import { icon } from './icons.js';
import { createZoomPane } from './zoom.js';
import { IMGTYPE, creditText, creditPending, refLabel } from './meta.js';

let dlg = null, zp, titleEl, countEl, hint, info, infoBtn, prevBtn, nextBtn, zoomLbl, viewSeg, filt, st = null, opener = null, hintT = 0, pushed = false;
const hasDetail = im => !!(im && im.detail && im.detail.file);

function btn(name, label, on, extra = {}) {
  return h('button', { type: 'button', class: 'lb-btn', 'aria-label': label, title: label, onClick: on, ...extra }, icon(name, 22));
}

function build() {
  zp = createZoomPane({
    onChange: ({ scale }) => { if (zoomLbl) zoomLbl.textContent = Math.round(scale * 100) + '%'; },
    onSwipe: d => go(d),
    onDismiss: () => requestClose(),
  });
  titleEl = h('h2', { class: 'lb-title', id: 'lb-title' });
  countEl = h('span', { class: 'lb-count', 'aria-live': 'polite' });
  zoomLbl = h('span', { class: 'lb-zoom', 'aria-hidden': 'true' }, '100%');
  hint = h('p', { class: 'lb-hint', role: 'status' });
  info = h('div', { class: 'lb-info', id: 'lb-info', hidden: true });
  prevBtn = btn('left', 'Imagem anterior', () => go(-1), { class: 'lb-btn lb-side prev' });
  nextBtn = btn('right', 'Próxima imagem', () => go(1), { class: 'lb-btn lb-side next' });
  infoBtn = btn('info', 'Informações da imagem', () => toggleInfo(), { 'aria-expanded': 'false', 'aria-controls': 'lb-info' });
  viewSeg = h('div', { class: 'lb-seg', role: 'group', 'aria-label': 'Versão da imagem' },
    h('button', { type: 'button', 'data-v': 'foto', onClick: () => setView('foto') }, 'Foto'),
    h('button', { type: 'button', 'data-v': 'ampliacao', onClick: () => setView('ampliacao') }, 'Ampliação digital'));
  const rng = (label, key) => h('label', { class: 'lb-rng' }, label, h('input', { type: 'range', min: 50, max: 180, value: 100, 'aria-label': label,
    onInput: e => { const f = zp.filter; zp.setFilter(key === 'b' ? +e.target.value : f.bright, key === 'c' ? +e.target.value : f.contr); } }));
  filt = h('div', { class: 'lb-filt', hidden: true }, rng('Brilho', 'b'), rng('Contraste', 'c'),
    h('button', { type: 'button', class: 'btn sm', onClick: () => { zp.setFilter(100, 100); filt.querySelectorAll('input').forEach(i => { i.value = 100; }); } }, 'Restaurar'));
  const filtBtn = btn('sliders', 'Brilho e contraste', () => { filt.hidden = !filt.hidden; filtBtn.setAttribute('aria-expanded', String(!filt.hidden)); }, { 'aria-expanded': 'false' });

  const bar = h('div', { class: 'lb-bar' },
    btn('minus', 'Reduzir', () => zp.zoomBy(1 / 1.5)), zoomLbl, btn('plus', 'Ampliar', () => zp.zoomBy(1.5)),
    btn('fit', 'Ajustar à tela', () => zp.reset(true)), filtBtn, infoBtn);
  dlg = h('dialog', { class: 'lb', 'aria-labelledby': 'lb-title' },
    h('div', { class: 'lb-top' }, h('div', { class: 'lb-ttl' }, titleEl, countEl), btn('close', 'Fechar', () => requestClose(), { class: 'lb-btn lb-close' })),
    h('div', { class: 'lb-stage' }, zp.el, prevBtn, nextBtn, hint),
    viewSeg, filt, info, bar);
  dlg.addEventListener('cancel', e => { e.preventDefault(); requestClose(); });
  dlg.addEventListener('keydown', e => {
    if (e.target.closest && e.target.closest('input')) return;
    if (e.key === 'ArrowLeft' && zp.scale <= 1.001) { go(-1); e.preventDefault(); }
    else if (e.key === 'ArrowRight' && zp.scale <= 1.001) { go(1); e.preventDefault(); }
  });
  dlg.addEventListener('close', onClosed);
  document.body.append(dlg);
  window.addEventListener('popstate', () => { if (dlg.open) { pushed = false; closeNow(); } });
}

function toggleInfo(force) {
  const open = force === undefined ? info.hidden : force;
  info.hidden = !open; infoBtn.setAttribute('aria-expanded', String(open)); dlg.classList.toggle('with-info', open);
  requestAnimationFrame(() => window.dispatchEvent(new Event('resize')));
}

function setView(v) {
  st.view = v; paint();
}

function go(d) {
  if (!st || st.list.length < 2) return;
  st.i = (st.i + d + st.list.length) % st.list.length; st.view = 'foto'; paint();
  flash(`${st.i + 1} de ${st.list.length}`);
}

function flash(msg) { hint.textContent = msg; hint.classList.add('on'); clearTimeout(hintT); hintT = setTimeout(() => hint.classList.remove('on'), 1400); }

function paint() {
  const im = st.list[st.i], n = st.list.length, det = hasDetail(im) && st.view === 'ampliacao';
  const file = det ? im.detail : im;
  zp.setImage({ src: imgSrc(file), width: file.width, height: file.height, alt: im.alt || '' });
  zp.setFilter(100, 100); filt.querySelectorAll('input').forEach(i => { i.value = 100; });
  titleEl.textContent = st.title || im.alt || 'Imagem';
  countEl.textContent = n > 1 ? `${st.i + 1} de ${n}` : '';
  prevBtn.hidden = nextBtn.hidden = n < 2;
  viewSeg.hidden = !hasDetail(im);
  viewSeg.querySelectorAll('button').forEach(b => { const on = b.dataset.v === (det ? 'ampliacao' : 'foto'); b.classList.toggle('on', on); b.setAttribute('aria-pressed', String(on)); });
  const tags = [
    h('span', { class: 'badge ' + (im.type === 'microfotografia' ? 'ok' : 'warn') }, IMGTYPE[im.type] || im.type),
    im.figure ? h('span', { class: 'badge' }, `Figura ${im.figure} (doc. v4)`) : null,
    im.lamina ? h('span', { class: 'badge' }, `Lâmina ${String(im.lamina).padStart(2, '0')} · ${im.kind === 'detalhe' ? 'detalhe ampliado' : 'campo geral'}`) : null,
    creditPending(im) ? h('span', { class: 'badge warn' }, im.credit ? 'Autoria a confirmar' : 'Sem crédito') : null,
  ];
  clear(info).append(
    h('div', { class: 'badges' }, tags),
    det ? h('p', { class: 'caption' }, im.detail.label || 'Ampliação digital') : null,
    im.caption ? h('p', { class: 'caption' }, im.caption) : null,
    h('p', { class: 'credit' }, creditText(im)),
    (im.refs || []).length ? h('p', { class: 'credit' }, 'Fontes: ', im.refs.map(refLabel).join('; ')) : null,
    h('p', { class: 'credit' }, `Arquivo: ${file.width || '?'} × ${file.height || '?'} px. `,
      h('a', { href: imgSrc(file), target: '_blank', rel: 'noopener' }, 'Abrir o arquivo em outra aba')));
  const nb = st.list[(st.i + 1) % n], pb = st.list[(st.i - 1 + n) % n];   // pré-carrega vizinhas
  [nb, pb].forEach(x => { if (x && x !== im) new Image().src = imgSrc(x); });
}

function requestClose() {
  if (!dlg || !dlg.open) return;
  if (pushed && history.state && history.state.lb) { history.back(); } else closeNow();   // popstate faz o resto
}
function closeNow() { if (dlg.open) dlg.close(); }
function onClosed() {
  if (pushed && history.state && history.state.lb) { pushed = false; try { history.back(); } catch { /* ok */ } }
  document.documentElement.classList.remove('lb-open');
  st = null; if (opener && opener.isConnected) { try { opener.focus({ preventScroll: true }); } catch { /* ok */ } } opener = null;
}

/** @param {object[]} images lista de imagens (objetos do JSON) @param {number} index posição inicial */
export function openLightbox(images, index = 0, { title } = {}) {
  if (!images || !images.length) return;
  if (!dlg) build();
  opener = document.activeElement;
  st = { list: images, i: Math.min(Math.max(0, index), images.length - 1), title, view: 'foto' };
  toggleInfo(false); filt.hidden = true;
  if (!dlg.open) {
    dlg.showModal(); document.documentElement.classList.add('lb-open');
    try { history.pushState({ lb: 1 }, ''); pushed = true; } catch { pushed = false; }
  }
  paint();
  const coarse = matchMedia('(pointer:coarse)').matches;
  flash(coarse ? 'Pinça para ampliar · toque duplo · deslize para trocar' : 'Roda do mouse ou + / − para ampliar · arraste para mover');
  zp.el.focus({ preventScroll: true });
}
