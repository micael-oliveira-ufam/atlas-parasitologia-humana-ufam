// Visualizador: zoom (roda/pinça/botões), arrastar, brilho/contraste, marcadores, tela cheia.
// Clique (sem arrastar) ou Enter abre a imagem ampliada (onOpen).
// Não simula troca de objetiva nem corantes: a imagem é a que foi fotografada/ilustrada.
import { h } from './dom.js';
import { imgSrc } from './store.js';

export function createViewer(image, { onHotspot, onOpen } = {}) {
  const MIN = 1, MAX = 5;
  let scale = 1, tx = 0, ty = 0, bright = 100, contr = 100, showHs = true, active = null;
  const ar = image.width / image.height;
  const hs = image.hotspots || [];

  const img = h('img', { src: imgSrc(image), alt: image.alt, width: image.width, height: image.height, draggable: 'false', class: 'vw-img' });
  const markers = hs.map((p, i) => {
    const b = h('button', { class: 'vw-mark', type: 'button', 'aria-label': `Marcador ${i + 1}: ${p.title}`, 'aria-pressed': 'false',
      style: { left: p.x + '%', top: p.y + '%' }, onClick: e => { e.stopPropagation(); select(p.id, true); },
      onPointerdown: e => e.stopPropagation() }, h('span', null, String(i + 1)));
    return b;
  });
  const frame = h('div', { class: 'vw-frame' }, img, ...markers);
  const stage = h('div', { class: 'vw-stage', tabindex: '0', role: 'group', 'aria-label': 'Campo microscópico. Clique ou pressione Enter para abrir a imagem ampliada. Use a roda do mouse ou + e − para ampliar; setas para mover.' }, frame);
  const readout = h('span', { class: 'vw-zoom', 'aria-live': 'off' }, '1×');

  function fit() {
    const W = stage.clientWidth, H = stage.clientHeight; if (!W || !H) return;
    let w = Math.min(W, H * ar), hh = w / ar;
    frame.style.setProperty('width', w + 'px'); frame.style.setProperty('height', hh + 'px');
  }
  function clampPan() {
    const W = stage.clientWidth, H = stage.clientHeight, fw = frame.offsetWidth * scale, fh = frame.offsetHeight * scale;
    const mx = Math.max(0, (fw - W) / 2) + 40, my = Math.max(0, (fh - H) / 2) + 40;
    tx = Math.min(mx, Math.max(-mx, tx)); ty = Math.min(my, Math.max(-my, ty));
  }
  function apply() {
    clampPan();
    frame.style.setProperty('transform', `translate(${tx}px, ${ty}px) scale(${scale})`);
    frame.style.setProperty('--inv', String(1 / scale));
    img.style.setProperty('filter', `brightness(${bright}%) contrast(${contr}%)`);
    readout.textContent = scale.toFixed(scale % 1 ? 1 : 0) + '×';
  }
  function zoomAt(f, cx, cy) {
    const ns = Math.min(MAX, Math.max(MIN, scale * f)); if (ns === scale) return;
    const r = stage.getBoundingClientRect(); const px = (cx ?? r.left + r.width / 2) - (r.left + r.width / 2), py = (cy ?? r.top + r.height / 2) - (r.top + r.height / 2);
    tx = px - (px - tx) * (ns / scale); ty = py - (py - ty) * (ns / scale); scale = ns; if (scale === 1) { tx = 0; ty = 0; } apply();
  }
  const reset = () => { scale = 1; tx = 0; ty = 0; bright = 100; contr = 100; bR.value = 100; cR.value = 100; apply(); };

  // arrastar / pinça
  const ptrs = new Map(); let pinch0 = 0, down = null;
  stage.addEventListener('pointerdown', e => { down = ptrs.size ? { moved: true } : { x: e.clientX, y: e.clientY, moved: false }; stage.setPointerCapture(e.pointerId); ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY }); if (ptrs.size === 2) { const [a, b] = [...ptrs.values()]; pinch0 = Math.hypot(a.x - b.x, a.y - b.y); } stage.classList.add('grab'); });
  stage.addEventListener('pointermove', e => {
    const p = ptrs.get(e.pointerId); if (!p) return;
    if (down && !down.moved && Math.hypot(e.clientX - down.x, e.clientY - down.y) > 5) down.moved = true;
    if (ptrs.size === 2) { ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY }); const [a, b] = [...ptrs.values()]; const d = Math.hypot(a.x - b.x, a.y - b.y); if (pinch0) zoomAt(d / pinch0, (a.x + b.x) / 2, (a.y + b.y) / 2); pinch0 = d; return; }
    tx += e.clientX - p.x; ty += e.clientY - p.y; ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY }); apply();
  });
  const up = e => {
    const click = e.type === 'pointerup' && down && !down.moved && ptrs.size === 1;
    ptrs.delete(e.pointerId); pinch0 = 0; if (!ptrs.size) { stage.classList.remove('grab'); down = null; }
    if (click && onOpen) onOpen();
  };
  stage.addEventListener('pointerup', up); stage.addEventListener('pointercancel', up);
  stage.addEventListener('wheel', e => { e.preventDefault(); zoomAt(e.deltaY < 0 ? 1.18 : 1 / 1.18, e.clientX, e.clientY); }, { passive: false });
  stage.addEventListener('keydown', e => {
    const k = e.key, s = 40;
    if (k === 'Enter') { if (onOpen && e.target === stage) onOpen(); else return; } else if (k === '+' || k === '=') zoomAt(1.25); else if (k === '-' || k === '_') zoomAt(1 / 1.25); else if (k === '0') reset();
    else if (k === 'ArrowLeft') tx += s; else if (k === 'ArrowRight') tx -= s; else if (k === 'ArrowUp') ty += s; else if (k === 'ArrowDown') ty -= s; else return;
    e.preventDefault(); apply();
  });

  function select(id, focusMarker) {
    active = active === id ? null : id;
    markers.forEach((m, i) => { const on = hs[i].id === active; m.classList.toggle('on', on); m.setAttribute('aria-pressed', String(on)); });
    onHotspot && onHotspot(hs.find(p => p.id === active) || null, hs.findIndex(p => p.id === active));
  }

  const btn = (label, text, fn, cls = '') => h('button', { type: 'button', class: 'btn sm ' + cls, 'aria-label': label, title: label, onClick: fn }, text);
  const bR = h('input', { type: 'range', min: '50', max: '150', value: '100', 'aria-label': 'Brilho', onInput: e => { bright = +e.target.value; apply(); } });
  const cR = h('input', { type: 'range', min: '50', max: '200', value: '100', 'aria-label': 'Contraste', onInput: e => { contr = +e.target.value; apply(); } });
  const hsBtn = hs.length ? btn('Mostrar/ocultar marcadores', 'Marcadores', () => { showHs = !showHs; frame.classList.toggle('nohs', !showHs); hsBtn.setAttribute('aria-pressed', String(showHs)); hsBtn.classList.toggle('on', showHs); }, 'on') : null;
  if (hsBtn) hsBtn.setAttribute('aria-pressed', 'true');
  const root = h('div', { class: 'viewer' }, stage,
    h('div', { class: 'vw-bar' },
      btn('Reduzir', '−', () => zoomAt(1 / 1.25)), readout, btn('Ampliar', '+', () => zoomAt(1.25)),
      btn('Restaurar visualização', 'Restaurar', reset), onOpen ? btn('Abrir imagem ampliada', 'Ampliar imagem', () => onOpen(), 'on') : null, hsBtn,
      h('label', { class: 'rng' }, 'Brilho', bR), h('label', { class: 'rng' }, 'Contraste', cR),
      btn('Tela cheia', 'Tela cheia', () => { if (document.fullscreenElement) document.exitFullscreen(); else root.requestFullscreen && root.requestFullscreen(); })));
  new ResizeObserver(() => { fit(); apply(); }).observe(stage);
  img.addEventListener('load', () => { fit(); apply(); });
  return { el: root, select, hotspots: hs };
}
