import { h } from '../dom.js';
import { store } from '../store.js';
import { page } from './common.js';
import { downloadCard } from './download.js';

const STATUS_LABEL = { ativo: 'Ativo', 'em-construcao': 'Em construção' };
export function home() {
  const s = store.site;
  const cards = store.modules.map(m => {
    const pub = m.specimens.filter(x => x.status === 'publicado').length, rev = m.specimens.filter(x => x.status === 'revisar').length;
    return h('a', { class: `card mod ${m.accent}`, href: `#/m/${m.id}` },
      h('span', { class: 'chip' }, STATUS_LABEL[m.status] || m.status),
      h('h3', null, m.title), h('p', { class: 'sub' }, m.subtitle), h('p', null, m.description),
      h('p', { class: 'count' }, `${pub} lâmina${pub === 1 ? '' : 's'} publicada${pub === 1 ? '' : 's'}`, rev ? ` · ${rev} em revisão` : ''));
  });
  const tools = [['#/artefatos', 'Guia de artefatos', 'Como não confundir bolhas, pólen, fibras e amido com parasitas.'], ['#/protocolos', 'Protocolos laboratoriais', 'Hoffmann, Graham, Rugai/Baermann, Faust e Kato-Katz.'], ['#/quiz', 'Quiz', 'Questões de parasitologia, saneamento e saúde indígena.']];
  return page('Início',
    h('div', { class: 'hero' }, h('img', { class: 'ufam-seal', src: 'assets/img/brand/ufam_brasao.png', alt: 'Brasão da Universidade Federal do Amazonas', width: 84, height: 84 }), h('p', { class: 'eyebrow' }, s.institution || 'Laminário digital'), h('h1', null, s.title), h('p', { class: 'lead' }, 'Explore lâminas com zoom e marcadores estruturais, compare diagnósticos diferenciais e treine com o quiz. O conteúdo é organizado em módulos taxonômicos.')),
    h('h2', null, 'Módulos'), h('div', { class: 'grid mods' }, cards),
    h('h2', null, 'Aplicativo'), downloadCard(),
    h('h2', null, 'Ferramentas de estudo'), h('div', { class: 'grid tools' }, tools.map(([href, t, d]) => h('a', { class: 'card tool', href }, h('h3', null, t), h('p', null, d)))));
}
