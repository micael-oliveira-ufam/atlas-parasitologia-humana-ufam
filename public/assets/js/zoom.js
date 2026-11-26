// Motor de zoom e arrasto por Pointer Events (mouse, toque e caneta).
//
// Gestos
//   • pinça (2 dedos) amplia/reduz ancorada no ponto entre os dedos; arrastar com 1 dedo/mouse move a imagem;
//   • toque duplo / duplo clique alterna entre "ajustada" e ampliada no ponto tocado;
//   • roda do mouse e pinça de trackpad (ctrl + roda); teclado: + − 0 e setas;
//   • na escala 1 (imagem inteira à vista) o arrasto não move a imagem: deslizar na horizontal chama onSwipe(±1)
//     e deslizar para baixo chama onDismiss() — a imagem acompanha o dedo e volta se o gesto for curto.
//
// O elemento usa touch-action:none: tudo é tratado aqui, então a página atrás nunca rola nem dá zoom junto.
// A imagem nunca sai da área (limites): fica centralizada quando menor que a área.
import { h } from './dom.js';

export function createZoomPane({ max = 8, dbl = 2.5, onChange, onSwipe, onDismiss } = {}) {
  const img = h('img', { class: 'zp-img', alt: '', draggable: 'false', decoding: 'async' });
  const frame = h('div', { class: 'zp-frame' }, img);
  const el = h('div', { class: 'zp', tabindex: '0', role: 'group' }, frame);
  let s = 1, x = 0, y = 0, fw = 0, fh = 0, ar = 4 / 3, off = null, bright = 100, contr = 100;
  const ptrs = new Map(); let g = null, lastTap = null, animT = 0;
  const W = () => el.clientWidth, H = () => el.clientHeight;

  function clampPos() {
    const cw = fw * s, ch = fh * s, w = W(), hh = H();
    x = cw <= w ? (w - cw) / 2 : Math.min(0, Math.max(w - cw, x));
    y = ch <= hh ? (hh - ch) / 2 : Math.min(0, Math.max(hh - ch, y));
  }
  function apply(animate = false) {
    if (animate) { frame.classList.add('anim'); clearTimeout(animT); animT = setTimeout(() => frame.classList.remove('anim'), 260); }
    const ox = off ? off.x : 0, oy = off ? off.y : 0;
    frame.style.transform = `translate3d(${x + ox}px, ${y + oy}px, 0) scale(${s})`;
    frame.style.setProperty('--inv', String(1 / s));
    el.classList.toggle('zoomed', s > 1.001);
    onChange && onChange({ scale: s });
  }
  function fit() {
    const w = W(), hh = H(); if (!w || !hh) return;
    fw = Math.min(w, hh * ar); fh = fw / ar;
    frame.style.width = fw + 'px'; frame.style.height = fh + 'px';
    clampPos(); apply();
  }
  const local = e => { const r = el.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top }; };
  function zoomTo(ns, cx, cy, animate = false) {
    ns = Math.min(max, Math.max(1, ns));
    if (cx === undefined) { cx = W() / 2; cy = H() / 2; }
    const k = ns / s; x = cx - (cx - x) * k; y = cy - (cy - y) * k; s = ns;
    if (s <= 1.001) s = 1;
    clampPos(); apply(animate);
  }
  const reset = (animate = true) => { s = 1; off = null; clampPos(); apply(animate); };

  el.addEventListener('pointerdown', e => {
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    try { el.setPointerCapture(e.pointerId); } catch { /* ok */ }
    ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (ptrs.size === 1) g = { mode: 'pan', sx: e.clientX, sy: e.clientY, t: performance.now(), moved: 0 };
    else if (ptrs.size === 2) {
      const [a, b] = [...ptrs.values()], r = el.getBoundingClientRect();
      g = { mode: 'pinch', d0: Math.max(1, Math.hypot(a.x - b.x, a.y - b.y)), s0: s, x0: x, y0: y,
        m0: { x: (a.x + b.x) / 2 - r.left, y: (a.y + b.y) / 2 - r.top }, moved: 99 };
      off = null;
    }
    el.classList.add('grabbing');
  });

  el.addEventListener('pointermove', e => {
    const p = ptrs.get(e.pointerId); if (!p || !g) return;
    const px = p.x, py = p.y; p.x = e.clientX; p.y = e.clientY;
    if (g.mode === 'pinch' && ptrs.size >= 2) {
      const [a, b] = [...ptrs.values()], r = el.getBoundingClientRect();
      const ns = Math.min(max, Math.max(1, g.s0 * Math.hypot(a.x - b.x, a.y - b.y) / g.d0));
      const m = { x: (a.x + b.x) / 2 - r.left, y: (a.y + b.y) / 2 - r.top };
      const lx = (g.m0.x - g.x0) / g.s0, ly = (g.m0.y - g.y0) / g.s0;
      s = ns; x = m.x - lx * ns; y = m.y - ly * ns; clampPos(); apply(); return;
    }
    g.moved = Math.max(g.moved, Math.hypot(e.clientX - g.sx, e.clientY - g.sy));
    if (s > 1.001) { x += e.clientX - px; y += e.clientY - py; clampPos(); apply(); }
    else if (g.moved > 6) { off = { x: (e.clientX - g.sx) * 0.85, y: Math.max(0, (e.clientY - g.sy)) * 0.85 }; apply(); }
  });

  function end(e) {
    if (!ptrs.delete(e.pointerId)) return;
    try { el.releasePointerCapture(e.pointerId); } catch { /* ok */ }
    if (!ptrs.size) el.classList.remove('grabbing');
    if (!g) return;
    if (g.mode === 'pinch') {
      if (s < 1.02) reset(true);
      if (ptrs.size === 1) { const [r] = [...ptrs.values()]; g = { mode: 'pan', sx: r.x, sy: r.y, t: performance.now(), moved: 99 }; } else g = null;
      return;
    }
    const up = e.type === 'pointerup', dx = e.clientX - g.sx, dy = e.clientY - g.sy, dt = performance.now() - g.t, moved = g.moved;
    g = null;
    if (s <= 1.001) {
      const hadOff = !!off; off = null;
      if (up && Math.abs(dx) > 56 && Math.abs(dx) > Math.abs(dy) * 1.3 && dt < 900 && onSwipe) { apply(true); onSwipe(dx < 0 ? 1 : -1); return; }
      if (up && dy > 96 && dy > Math.abs(dx) * 1.3 && onDismiss) { onDismiss(); return; }
      if (hadOff) apply(true);
    }
    if (up && moved < 8 && dt < 500) {   // toque curto: duplo toque alterna o zoom
      const now = performance.now(), pt = local(e);
      if (lastTap && now - lastTap.t < 320 && Math.hypot(pt.x - lastTap.x, pt.y - lastTap.y) < 36) {
        lastTap = null; if (s > 1.05) reset(true); else zoomTo(dbl, pt.x, pt.y, true);
      } else lastTap = { t: now, x: pt.x, y: pt.y };
    }
  }
  el.addEventListener('pointerup', end); el.addEventListener('pointercancel', end);
  el.addEventListener('lostpointercapture', e => { if (ptrs.has(e.pointerId)) end({ pointerId: e.pointerId, type: 'pointercancel', clientX: 0, clientY: 0 }); });

  el.addEventListener('wheel', e => {
    e.preventDefault();
    const unit = e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? 400 : 1, p = local(e);
    zoomTo(s * Math.exp(-e.deltaY * unit * (e.ctrlKey ? 0.012 : 0.0016)), p.x, p.y);
  }, { passive: false });

  el.addEventListener('keydown', e => {
    const k = e.key, st = 70;
    if (k === '+' || k === '=') zoomTo(s * 1.4, undefined, undefined, true);
    else if (k === '-' || k === '_') zoomTo(s / 1.4, undefined, undefined, true);
    else if (k === '0') reset(true);
    else if (s > 1.001 && k.startsWith('Arrow')) {
      if (k === 'ArrowLeft') x += st; else if (k === 'ArrowRight') x -= st; else if (k === 'ArrowUp') y += st; else y -= st;
      clampPos(); apply();
    } else return;
    e.preventDefault();
  });

  new ResizeObserver(fit).observe(el);
  img.addEventListener('load', fit);

  let markers = [];
  const api = {
    el,
    /** @param {{src:string,width:number,height:number,alt?:string}} im */
    setImage(im) {
      ar = (im.width && im.height) ? im.width / im.height : 4 / 3;
      s = 1; off = null; lastTap = null;
      img.src = im.src; img.alt = im.alt || '';
      fit(); apply();
    },
    setMarkers(list, onSelect) {
      markers.forEach(m => m.remove()); markers = [];
      (list || []).forEach((p, i) => {
        const b = h('button', { class: 'zp-mark', type: 'button', 'aria-label': `Marcador ${i + 1}: ${p.title}`, style: { left: p.x + '%', top: p.y + '%' },
          onPointerdown: ev => ev.stopPropagation(), onClick: ev => { ev.stopPropagation(); markers.forEach(m => m.classList.remove('on')); b.classList.add('on'); onSelect && onSelect(p, i); } }, h('span', null, String(i + 1)));
        markers.push(b); frame.append(b);
      });
    },
    setFilter(b, c) { bright = b; contr = c; img.style.filter = (b === 100 && c === 100) ? '' : `brightness(${b}%) contrast(${c}%)`; },
    zoomBy(f) { zoomTo(s * f, undefined, undefined, true); },
    reset,
    get scale() { return s; },
    get filter() { return { bright, contr }; },
  };
  return api;
}
