import { h, clear, slug } from './dom.js';
import { loadAll, store } from './store.js';
import { icon } from './icons.js';
import { home } from './views/home.js';
import { modulePage } from './views/module.js';
import { specimenPage } from './views/specimen.js';
import { quizPage } from './views/quiz.js';
import { protocolsPage } from './views/protocols.js';
import { artifactsPage } from './views/artifacts.js';
import { searchPage } from './views/search.js';
import { aboutPage } from './views/about.js';

const main = document.getElementById('conteudo');
const topbar = document.getElementById('topbar');
const footer = document.getElementById('footer');

function renderChrome() {
  const links = [
    ['#/', 'Início'],
    ...store.modules.map(m => [`#/m/${m.id}`, m.title]),
    ['#/artefatos', 'Artefatos'], ['#/protocolos', 'Protocolos'], ['#/quiz', 'Quiz'], ['#/sobre', 'Sobre']
  ];
  const form = h('form', { class: 'search', role: 'search', onSubmit: e => { e.preventDefault(); const q = new FormData(e.target).get('q').toString().trim(); if (q) location.hash = '#/busca?q=' + encodeURIComponent(q); } },
    h('input', { type: 'search', name: 'q', placeholder: 'Buscar espécie ou doença…', 'aria-label': 'Buscar no atlas' }));
  const nav = h('nav', { 'aria-label': 'Principal', class: 'nav' }, links.map(([href, label]) => h('a', { href, dataset: { href } }, label)));
  const toggle = h('button', { class: 'icon-btn menu-btn', type: 'button', 'aria-label': 'Abrir menu', 'aria-expanded': 'false', 'aria-controls': 'drawer', onClick: () => setMenu(!topbar.classList.contains('open')) }, icon('menu', 22));
  const theme = h('button', { class: 'icon-btn theme-btn', type: 'button', 'aria-label': 'Alternar tema claro/escuro', onClick: toggleTheme }, icon('moon', 20), icon('sun', 20));
  const drawer = h('div', { class: 'drawer', id: 'drawer' }, nav, form);
  clear(topbar).append(h('div', { class: 'wrap bar' }, h('a', { class: 'brand', href: '#/' }, h('img', { class: 'brand-seal', src: 'assets/img/brand/ufam_brasao.png', alt: '', width: 36, height: 36 }), h('span', null, h('strong', null, 'Atlas de Parasitologia'), h('small', null, 'Humana · laminário digital'))), drawer, theme, toggle));
  topbar.append(h('div', { class: 'scrim', onClick: () => setMenu(false) }));
  const s = store.site;
  clear(footer).append(h('div', { class: 'wrap foot' },
    h('div', null, h('strong', null, s.title), h('p', null, s.course), h('p', null, 'Desenvolvimento: ', s.developer)),
    h('div', null, h('strong', null, 'Referências da disciplina'), h('ul', null, s.references.map(r => h('li', null, r)))),
    h('div', null, h('strong', null, 'Aviso'), h('p', null, 'Material de apoio ao ensino. Não substitui livros-texto, normas laboratoriais nem avaliação clínica.'))));
}

function setMenu(open) {
  topbar.classList.toggle('open', open); document.documentElement.classList.toggle('menu-open', open);
  const b = topbar.querySelector('.menu-btn'); if (b) { b.setAttribute('aria-expanded', String(open)); b.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu'); }
}
function currentTheme() { return document.documentElement.dataset.theme || (matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light'); }
function toggleTheme() {
  const t = currentTheme() === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = t;
  try { localStorage.setItem('atlas-theme', t); } catch { /* armazenamento indisponível: vale só nesta sessão */ }
  const m = document.querySelector('meta[name=theme-color]'); if (m) m.content = t === 'dark' ? '#0e1514' : '#0f5f58';
}
function markNav(path) {
  document.querySelectorAll('.nav a').forEach(a => {
    const href = a.dataset.href.slice(1);
    const on = href === '/' ? path === '/' : path.startsWith(href);
    a.classList.toggle('on', on); if (on) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
  });
}

function notFound() { return h('section', { class: 'wrap page' }, h('h1', null, 'Página não encontrada'), h('p', null, 'O endereço não existe neste atlas. ', h('a', { href: '#/' }, 'Voltar ao início'), '.')); }

function route() {
  const raw = location.hash.replace(/^#/, '') || '/';
  const [path, qs] = raw.split('?'); const params = new URLSearchParams(qs || '');
  const seg = path.split('/').filter(Boolean).map(decodeURIComponent);
  let view;
  try {
    if (!seg.length) view = home();
    else if (seg[0] === 'm' && seg[1] && !seg[2]) view = modulePage(seg[1]);
    else if (seg[0] === 'm' && seg[1] && seg[2]) view = specimenPage(seg[1], seg[2]);
    else if (seg[0] === 'quiz') view = quizPage(params.get('m'));
    else if (seg[0] === 'protocolos') view = protocolsPage();
    else if (seg[0] === 'artefatos') view = artifactsPage();
    else if (seg[0] === 'busca') view = searchPage(params.get('q') || '');
    else if (seg[0] === 'sobre') view = aboutPage();
  } catch (err) { console.error(err); view = null; }
  clear(main).append(view || notFound());
  setMenu(false);
  markNav(path);
  const title = view && view.dataset && view.dataset.title;
  document.title = (title ? title + ' · ' : '') + store.site.title;
  window.scrollTo(0, 0);
  main.focus({ preventScroll: true });
}

window.addEventListener('scroll', () => topbar.classList.toggle('scrolled', window.scrollY > 8), { passive: true });
window.addEventListener('keydown', e => { if (e.key === 'Escape' && topbar.classList.contains('open')) setMenu(false); });
loadAll().then(() => { renderChrome(); route(); window.addEventListener('hashchange', route); })
  .catch(err => { console.error(err); clear(main).append(h('div', { class: 'wrap page' }, h('h1', null, 'Não foi possível carregar o atlas'), h('p', null, 'Os arquivos de dados não puderam ser lidos (', String(err.message), '). Se você abriu o index.html direto do disco, sirva a pasta por HTTP (veja o README).'))); });
