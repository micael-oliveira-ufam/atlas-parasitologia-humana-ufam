import { h } from '../dom.js';
import { store, imgSrc, cover } from '../store.js';
import { page, nFotos, brief } from './common.js';
import { downloadCard } from './download.js';
import { icon } from '../icons.js';
import { lens, countUp } from '../fx.js';

const STATUS_LABEL = { ativo: 'Ativo', 'em-construcao': 'Em construção' };
const label = s => s.commonName.split(' (')[0];
const photoOf = s => s.images.find(i => i.type === 'microfotografia') || cover(s);
/** Espécies elegíveis para destaque: publicadas e com foto de lâmina. */
const featured = () => store.specimens.filter(s => s.status === 'publicado' && s.images.some(i => i.type === 'microfotografia'));
const dayIndex = () => Math.floor((Date.now() - new Date().getTimezoneOffset() * 60000) / 86400000);

function lensHero() {
  const pool = featured(); let cur = null;
  const pick = () => { const sp = pool[Math.floor(Math.random() * pool.length)]; const ph = sp.images.filter(i => i.type === 'microfotografia'); return { sp, im: ph[Math.floor(Math.random() * ph.length)] }; };
  const blur = h('img', { class: 'lens-bg', alt: '', decoding: 'async' }), sharp = h('img', { class: 'lens-fg', alt: '', decoding: 'async' });
  const ring = h('span', { class: 'lens-ring', 'aria-hidden': 'true' });
  const cap = h('a', { class: 'lens-cap' }), stage = h('div', { class: 'lens-stage', role: 'img', 'aria-label': 'Fotografia de lâmina com lupa interativa' }, blur, sharp, ring);
  const paint = () => { cur = pick(); [blur, sharp].forEach(i => { i.src = imgSrc(cur.im); }); cap.href = `#/m/${cur.sp.moduleId}/${cur.sp.id}`; cap.replaceChildren(icon('scope', 16), h('span', null, label(cur.sp))); stage.style.setProperty('--ar', `${cur.im.width} / ${cur.im.height}`); };
  if (pool.length) paint();
  lens(stage);
  const again = h('button', { type: 'button', class: 'lens-next', 'aria-label': 'Mostrar outra lâmina', title: 'Outra lâmina', onClick: paint }, icon('shuffle', 18));
  return h('div', { class: 'lens-wrap' }, stage, h('div', { class: 'lens-bar' }, h('span', { class: 'small' }, 'Mova a lupa sobre a lâmina'), cap, again));
}

function dayCard() {
  const pool = featured(); if (!pool.length) return null;
  const sp = pool[dayIndex() % pool.length], im = photoOf(sp), href = `#/m/${sp.moduleId}/${sp.id}`;
  return h('section', { class: 'day rv-item', 'aria-labelledby': 'day-t' },
    h('a', { class: 'day-img', href, 'aria-hidden': 'true', tabindex: '-1' }, h('img', { src: imgSrc(im), alt: '', loading: 'lazy', width: im.width, height: im.height })),
    h('div', { class: 'day-txt' }, h('span', { class: 'chip' }, icon('spark', 14), ' Parasita do dia'), h('h2', { id: 'day-t' }, label(sp)), h('p', { class: 'sci' }, sp.scientificName.split(' (')[0]),
      h('p', null, brief(sp.disease) || sp.evolutionaryStage), h('p', { class: 'row' }, h('a', { class: 'btn primary', href }, 'Abrir a ficha'), h('a', { class: 'btn', href: '#/quiz' }, 'Testar no quiz'))));
}

function rail() {
  const items = store.specimens;
  return h('div', { class: 'rail', role: 'list', tabindex: '0', 'aria-label': 'Espécies do atlas (role para os lados)' }, items.map(s => { const m = store.modules.find(x => x.id === s.moduleId), c = photoOf(s);
    return h('a', { class: `rail-card ${m ? m.accent : ''}`, role: 'listitem', href: `#/m/${s.moduleId}/${s.id}` }, h('img', { src: imgSrc(c), alt: '', loading: 'lazy', width: c.width, height: c.height }), h('span', { class: 'rail-t' }, label(s)), h('span', { class: 'rail-s' }, m ? m.title : '')); }));
}

export function home() {
  const s = store.site, sp = store.specimens;
  const fotos = sp.reduce((a, x) => a + nFotos(x), 0);
  const stats = [[store.modules.length, 'módulos'], [sp.length, 'espécies'], [fotos, 'fotos de lâminas'], [(store.refs.items || []).length, 'fontes citadas']];
  const nums = stats.map(([n]) => { const d = h('dt', null, String(n)); countUp(d, n); return d; });
  const cards = store.modules.map(m => {
    const pub = m.specimens.filter(x => x.status === 'publicado').length, rev = m.specimens.filter(x => x.status === 'revisar').length;
    const mosaic = m.specimens.slice(0, 4).map(photoOf);
    return h('a', { class: `card mod ${m.accent}`, href: `#/m/${m.id}` },
      mosaic.length ? h('div', { class: 'mosaic', 'aria-hidden': 'true' }, mosaic.map(im => h('img', { src: imgSrc(im), alt: '', loading: 'lazy', width: im.width, height: im.height }))) : h('div', { class: 'mosaic empty-m', 'aria-hidden': 'true' }),
      h('div', { class: 'mod-body' },
        h('span', { class: 'chip' }, STATUS_LABEL[m.status] || m.status),
        h('h3', null, m.title), h('p', { class: 'sub' }, m.subtitle), h('p', null, m.description),
        h('p', { class: 'count' }, `${pub} espécie${pub === 1 ? '' : 's'} publicada${pub === 1 ? '' : 's'}`, rev ? ` · ${rev} em revisão` : '', ' ', icon('right', 16))));
  });
  const tools = [['#/quiz', 'Quiz com imagens', 'Olhe a lâmina e acerte o parasita — ou responda perguntas de texto com fontes.', 'scope', 'violet'], ['#/protocolos', 'Protocolos laboratoriais', 'Hoffmann, Graham, Rugai/Baermann, Faust e Kato-Katz.', 'sliders', 'amber'], ['#/artefatos', 'Guia de artefatos', 'Como não confundir bolhas, pólen, fibras e amido com parasitas.', 'search', 'teal'], ['#/downloads', 'Downloads', 'Atlas do site em PDF, atlas da OPAS e o app Android.', 'download', 'teal']];
  return page('Início',
    h('div', { class: 'hero' },
      h('div', { class: 'hero-txt' },
        h('img', { class: 'hero-logo', src: 'assets/brand/atlas-logo-white.svg', alt: 'Atlas de Parasitologia Humana', width: 300, height: 80 }),
        h('p', { class: 'eyebrow' }, h('img', { class: 'ufam-mini', src: 'assets/img/brand/ufam_brasao.png', alt: '', width: 26, height: 26 }), s.institution || 'Laminário digital'),
        h('h1', null, s.title),
        h('p', { class: 'lead' }, 'Fotografias de lâminas reais com zoom por gestos, critérios morfológicos, diagnóstico diferencial e quiz com imagens.'),
        h('div', { class: 'hero-cta' }, h('a', { class: 'btn primary', href: '#/m/' + (store.modules[0] || {}).id }, 'Explorar o atlas'), h('a', { class: 'btn ghost', href: '#/quiz' }, icon('play', 16), 'Jogar o quiz'), h('a', { class: 'btn ghost', href: '#/downloads' }, icon('download', 16), 'Baixar')),
        h('dl', { class: 'stats' }, stats.map(([, l], i) => h('div', null, nums[i], h('dd', null, l))))),
      lensHero()),
    dayCard(),
    h('h2', { class: 'sec-t' }, 'Módulos'), h('div', { class: 'grid mods' }, cards),
    h('h2', { class: 'sec-t' }, 'Explorar espécies'), rail(),
    h('h2', { class: 'sec-t' }, 'Ferramentas de estudo'), h('div', { class: 'grid tools' }, tools.map(([href, t, d, ic, ac]) => h('a', { class: `card tool ${ac}`, href }, h('span', { class: 'tool-ico' }, icon(ic, 22)), h('h3', null, t), h('p', null, d)))),
    h('h2', { class: 'sec-t' }, 'Aplicativo'), downloadCard());
}
