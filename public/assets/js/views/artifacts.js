import { h } from '../dom.js';
import { store } from '../store.js';
import { page, refName } from './common.js';

export function artifactsPage() {
  const a = store.artifacts;
  return page('Artefatos',
    h('h1', null, 'Guia de artefatos'), h('p', { class: 'lead' }, 'Como não confundir estruturas inertes e resíduos com parasitas na microscopia óptica.'),
    h('div', { class: 'grid art' }, a.itens.map((it, i) => h('article', { class: 'card art-item' }, h('h3', null, `${i + 1}. ${it.nome}`), h('p', { class: 'badge bad' }, 'Confundida com: ' + it.confundidaCom), h('p', null, h('strong', null, 'Como diferenciar: '), it.comoDiferenciar), it.status ? h('p', { class: 'badge ' + (it.status === 'ressalva' ? 'bad' : 'ok') }, it.status === 'ressalva' ? 'Com ressalva' : it.status) : null, (it.refs || []).length ? h('p', { class: 'muted small' }, 'Fontes: ' + it.refs.map(refName).join('; ')) : null, it.evidencia ? h('p', { class: 'muted small' }, 'Evidência: ' + it.evidencia) : null))),
    h('aside', { class: 'tip' }, h('strong', null, 'Dica de bancada'), h('p', null, a.dica)),
    h('p', { class: 'muted' }, 'Este guia ainda não tem fotos de artefatos reais; ele será ilustrado quando houver microfotografias de bolhas, pólen, fibras e amido.'));
}
