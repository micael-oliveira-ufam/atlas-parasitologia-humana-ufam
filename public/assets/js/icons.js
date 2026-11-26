// Ícones SVG de traço (24×24), sem dependências. Decorativos: o botão que os usa leva aria-label.
import { svg } from './dom.js';

const P = {
  close: ['M6 6l12 12M18 6L6 18'],
  plus: ['M12 5v14M5 12h14'],
  minus: ['M5 12h14'],
  fit: ['M8 3H5a2 2 0 0 0-2 2v3M21 8V5a2 2 0 0 0-2-2h-3M16 21h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3'],
  expand: ['M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7'],
  sliders: ['M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6'],
  info: ['M12 16v-4M12 8h.01'],
  left: ['M15 18l-6-6 6-6'],
  right: ['M9 6l6 6-6 6'],
  sun: ['M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4'],
  moon: ['M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z'],
  menu: ['M4 7h16M4 12h16M4 17h16'],
  search: ['M21 21l-4.3-4.3'],
  scope: ['M12 3v3M6 21h12M9 21c0-3 1.5-5 3-5M7 13l3-3 5 5-3 3zM13 7l4-4 4 4-4 4'],
};
const CIRCLES = { info: [12, 12, 9], sun: [12, 12, 4], search: [11, 11, 7] };

export function icon(name, size = 20) {
  const s = svg('svg', { viewBox: '0 0 24 24', width: size, height: size, fill: 'none', stroke: 'currentColor', 'stroke-width': '2',
    'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'aria-hidden': 'true', focusable: 'false', class: 'ico' });
  if (CIRCLES[name]) { const [cx, cy, r] = CIRCLES[name]; s.append(svg('circle', { cx, cy, r })); }
  for (const d of P[name] || []) s.append(svg('path', { d }));
  return s;
}
