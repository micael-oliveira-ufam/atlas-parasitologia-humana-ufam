import { h } from '../dom.js';
import { store, imgSrc } from '../store.js';
import { page, nFotos } from './common.js';
import { downloadCard } from './download.js';
import { icon } from '../icons.js';

const STATUS_LABEL = { ativo: 'Ativo', 'em-construcao': 'Em construção' };

export function home() {
  const s = store.site, sp = store.specimens;
  const fotos = sp.reduce((a, x) => a + nFotos(x), 0);
  const stats = [[store.modules.length, 'módulos'], [sp.length, 'espécies'], [fotos, 'fotos de lâminas'], [(store.refs.items || []).length, 'fontes citadas']];
  const cards = store.modules.map(m => {
    const pub = m.specimens.filter(x => x.status === 'publicado').length, rev = m.specimens.filter(x => x.status === 'revisar').length;
    const mosaic = m.specimens.slice(0, 4).map(x => x.images[0]);
    return h('a', { class: `card mod ${m.accent}`, href: `#/m/${m.id}` },
      mosaic.length ? h('div', { class: 'mosaic', 'aria-hidden': 'true' }, mosaic.map(im => h('img', { src: imgSrc(im), alt: '', loading: 'lazy', width: im.width, height: im.height }))) : h('div', { class: 'mosaic empty-m', 'aria-hidden': 'true' }),
      h('div', { class: 'mod-body' },
        h('span', { class: 'chip' }, STATUS_LABEL[m.status] || m.status),
        h('h3', null, m.title), h('p', { class: 'sub' }, m.subtitle), h('p', null, m.description),
        h('p', { class: 'count' }, `${pub} espécie${pub === 1 ? '' : 's'} publicada${pub === 1 ? '' : 's'}`, rev ? ` · ${rev} em revisão` : '', ' ', icon('right', 16))));
  });
  const tools = [['#/artefatos', 'Guia de artefatos', 'Como não confundir bolhas, pólen, fibras e amido com parasitas.', 'search'], ['#/protocolos', 'Protocolos laboratoriais', 'Hoffmann, Graham, Rugai/Baermann, Faust e Kato-Katz.', 'scope'], ['#/quiz', 'Quiz', 'Questões de parasitologia, saneamento e saúde indígena.', 'info']];
  return page('Início',
    h('div', { class: 'hero' },
      h('div', { class: 'hero-txt' },
        h('p', { class: 'eyebrow' }, s.institution || 'Laminário digital'),
        h('h1', null, s.title),
        h('p', { class: 'lead' }, 'Fotografias de lâminas reais com zoom por gestos, critérios morfológicos, diagnóstico diferencial e quiz — organizados em módulos taxonômicos.'),
        h('div', { class: 'hero-cta' }, h('a', { class: 'btn primary', href: '#/m/' + (store.modules[0] || {}).id }, 'Começar pelos módulos'), h('a', { class: 'btn', href: '#/quiz' }, 'Fazer o quiz'))),
      h('img', { class: 'ufam-seal', src: 'assets/img/brand/ufam_brasao.png', alt: 'Brasão da Universidade Federal do Amazonas', width: 96, height: 96 }),
      h('dl', { class: 'stats' }, stats.map(([n, l]) => h('div', null, h('dt', null, String(n)), h('dd', null, l))))),
    h('h2', null, 'Módulos'), h('div', { class: 'grid mods' }, cards),
    h('h2', null, 'Ferramentas de estudo'), h('div', { class: 'grid tools' }, tools.map(([href, t, d, ic]) => h('a', { class: 'card tool', href }, h('span', { class: 'tool-ico' }, icon(ic, 22)), h('h3', null, t), h('p', null, d)))),
    h('h2', null, 'Aplicativo'), downloadCard());
}
