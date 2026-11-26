// Efeitos de interface (todos desligados com prefers-reduced-motion): aparecer ao rolar, contagem animada,
// destaque da seção atual no índice da ficha e a "lupa" interativa da página inicial.
export const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

let io = null;
export function reveal(root) {
  const els = [...root.querySelectorAll('.grid > .card, .sec, .rv-item, .dl-card2, .mode')];
  if (reduced() || !('IntersectionObserver' in window)) return;
  io && io.disconnect();
  io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
  els.forEach((el, i) => { el.classList.add('rv'); el.style.setProperty('--d', (i % 6) * 55 + 'ms'); io.observe(el); });
}

export function countUp(el, n, ms = 900) {
  el.textContent = String(n);
  if (reduced() || !('IntersectionObserver' in window)) return;
  const o = new IntersectionObserver(es => { if (!es[0].isIntersecting) return; o.disconnect(); const t0 = performance.now();
    const step = t => { const k = Math.min(1, (t - t0) / ms); el.textContent = String(Math.round(n * (1 - Math.pow(1 - k, 3)))); if (k < 1) requestAnimationFrame(step); }; requestAnimationFrame(step); });
  o.observe(el);
}

/** Realça no índice (.toc) a seção visível. */
export function spy(root) {
  const links = [...root.querySelectorAll('.toc a[data-sec]')]; if (!links.length || !('IntersectionObserver' in window)) return;
  const map = new Map(links.map(a => [a.dataset.sec, a]));
  const o = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { links.forEach(l => l.classList.remove('on')); const a = map.get(e.target.id); a && a.classList.add('on'); a && a.scrollIntoView({ block: 'nearest', inline: 'center' }); } }), { rootMargin: '-20% 0px -70% 0px' });
  map.forEach((_, id) => { const s = document.getElementById(id); s && o.observe(s); });
}

/** Lupa: segue o dedo/mouse sobre uma foto desfocada e mostra a versão nítida só dentro do círculo. */
export function lens(stage) {
  let raf = 0, user = false, t0 = performance.now();
  const set = (x, y) => { stage.style.setProperty('--lx', x + '%'); stage.style.setProperty('--ly', y + '%'); };
  set(55, 48);
  const move = e => { const r = stage.getBoundingClientRect(); user = true; cancelAnimationFrame(raf); set(Math.min(100, Math.max(0, (e.clientX - r.left) / r.width * 100)), Math.min(100, Math.max(0, (e.clientY - r.top) / r.height * 100))); };
  stage.addEventListener('pointermove', move); stage.addEventListener('pointerdown', move);
  if (!reduced()) {
    const tick = t => { if (user || !stage.isConnected) return; const k = (t - t0) / 1000; set(50 + 26 * Math.sin(k * .7), 50 + 22 * Math.sin(k * 1.1 + 1)); raf = requestAnimationFrame(tick); };
    raf = requestAnimationFrame(tick);
  }
}
