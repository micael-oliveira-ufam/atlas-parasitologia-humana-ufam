import { h, clear, slug } from '../dom.js';
import { getModule } from '../store.js';
import { page, specCard } from './common.js';

export function modulePage(id) {
  const m = getModule(id); if (!m) return null;
  const q = { text: '', cat: '' };
  const grid = h('div', { class: 'grid specs' });
  const info = h('p', { class: 'muted', 'aria-live': 'polite' });
  const cats = [...new Set(m.specimens.map(s => s.category))];
  function paint() {
    const t = slug(q.text);
    const items = m.specimens.filter(s => (!q.cat || s.category === q.cat) && (!t || slug([s.commonName, s.scientificName, s.disease, s.evolutionaryStage].join(' ')).includes(t)));
    clear(grid).append(...items.map(specCard));
    info.textContent = `${items.length} de ${m.specimens.length} lâmina(s)`;
  }
  const sel = (label, key, opts) => h('label', null, label, h('select', { onChange: e => { q[key] = e.target.value; paint(); } }, h('option', { value: '' }, 'Todos'), opts.map(o => h('option', { value: o }, o))));
  const filters = m.specimens.length ? h('div', { class: 'filters' },
    h('label', null, 'Buscar', h('input', { type: 'search', placeholder: 'nome, doença…', onInput: e => { q.text = e.target.value; paint(); } })),
    cats.length > 1 ? sel('Categoria', 'cat', cats) : null, info) : null;
  const empty = h('div', { class: 'empty' }, h('h3', null, 'Nenhuma lâmina publicada ainda'), h('p', null, 'Este módulo está pronto para receber conteúdo. Para adicionar lâminas, edite ', h('code', null, m.dataFile), ' e coloque as imagens em ', h('code', null, 'assets/img/' + m.id + '/'), ' (passo a passo em docs/ADICIONAR_LAMINAS.md).'));
  paint();
  return page(m.title,
    h('nav', { class: 'crumbs', 'aria-label': 'Trilha' }, h('a', { href: '#/' }, 'Início'), ' / ', m.title),
    h('div', { class: `mod-head ${m.accent}` }, h('h1', null, m.title), h('p', { class: 'lead' }, m.subtitle), h('p', null, m.description)),
    m.status === 'em-construcao' ? h('div', { class: 'notice' }, h('strong', null, 'Módulo em construção. '), 'O conteúdo abaixo é provisório e está sinalizado “em revisão”.') : null,
    filters, m.specimens.length ? grid : empty);
}
