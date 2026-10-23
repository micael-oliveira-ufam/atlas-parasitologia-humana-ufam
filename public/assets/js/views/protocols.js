import { h } from '../dom.js';
import { store } from '../store.js';
import { page, list } from './common.js';

const ST = { confirmado: ['Confirmado', 'ok'], corrigido: ['Corrigido', 'warn'], removido: ['Removido', 'bad'], ressalva: ['Ressalva', 'warn'] };
const fmt = iso => iso.split('-').reverse().join('/');

function refLabels(ids) {
  const map = new Map(store.refs.items.map(r => [r.id, r]));
  return (ids || []).map(id => map.get(id)).filter(Boolean).map(r =>
    h('a', { class: 'refchip', href: '#/protocolos', title: r.citation, onClick: e => { e.preventDefault(); const box = e.currentTarget.closest('.proto-body'); const el = box && box.querySelector('#ref-' + r.id + '-' + box.parentElement.id); if (el) { el.scrollIntoView({ block: 'center' }); el.classList.add('flash'); setTimeout(() => el.classList.remove('flash'), 1500); } } }, r.short));
}
function refItem(r, pid) {
  const links = [
    r.doi ? h('a', { href: 'https://doi.org/' + r.doi, target: '_blank', rel: 'noopener' }, 'DOI') : null,
    r.pmid ? h('a', { href: 'https://pubmed.ncbi.nlm.nih.gov/' + r.pmid + '/', target: '_blank', rel: 'noopener' }, 'PubMed ' + r.pmid) : null,
    r.url ? h('a', { href: r.url, target: '_blank', rel: 'noopener' }, 'Fonte online') : null,
  ].filter(Boolean);
  return h('li', { id: 'ref-' + r.id + (pid ? '-' + pid : '') }, r.citation, ' ',
    h('span', { class: 'muted small' }, '[acesso nesta revisão: ', r.access, '] '),
    ...links.flatMap((l, i) => i ? [' · ', l] : [l]));
}

export function protocolsPage() {
  const rv = store.refs.review, map = new Map(store.refs.items.map(r => [r.id, r]));
  const note = rv ? h('div', { class: 'notice', role: 'note' },
    h('strong', null, `Conferido com a literatura em ${fmt(rv.reviewedOn)}. `), rv.scope, ' ',
    h('strong', null, 'Atenção: '), rv.notValidation,
    h('p', { class: 'small' }, h('strong', null, 'Fora do escopo desta conferência: '), rv.notReviewed.join('; '), '.'),
    h('p', { class: 'small' }, rv.sourceAccessNote)) : null;
  return page('Protocolos',
    h('h1', null, 'Protocolos laboratoriais'),
    h('p', { class: 'lead' }, 'Métodos coproparasitológicos revisados com a literatura. Em cada protocolo, a seção “Conferência” mostra o que foi confirmado, corrigido ou retirado em relação ao texto anterior.'),
    note,
    store.protocols.map(p => h('details', { class: 'proto', id: p.id },
      h('summary', null, h('span', { class: 'ttl' }, p.title), h('span', { class: 'muted' }, p.popularName)),
      h('div', { class: 'proto-body' },
        h('p', null, h('strong', null, 'Indicação: '), p.indication), h('p', null, h('strong', null, 'Princípio: '), p.principle),
        h('h3', null, 'Materiais e reagentes'), list(p.reagentsAndMaterials), h('h3', null, 'Passo a passo'), list(p.stepByStep, true),
        h('div', { class: 'two' }, h('div', null, h('h3', null, 'Vantagens'), list(p.advantages)), h('div', null, h('h3', null, 'Limitações'), list(p.limitations))),
        h('h3', null, 'Parasitos detectados'), h('p', null, p.keyParasitesDetected.join(' · ')),
        p.intensity ? [h('h3', null, 'Classes de intensidade (OPG)'),
          h('div', { class: 'tbl-wrap' }, h('table', { class: 'tbl' }, h('thead', null, h('tr', null, p.intensity.header.map(c => h('th', { scope: 'col' }, c)))),
            h('tbody', null, p.intensity.rows.map(r => h('tr', null, r.map((c, i) => h(i ? 'td' : 'th', i ? null : { scope: 'row' }, c))))))),
          h('p', { class: 'muted small' }, p.intensity.source, '. ', p.intensity.note, ' ', ...refLabels(p.intensity.refs))] : null,
        h('h3', null, 'Evidência publicada'),
        h('ul', { class: 'list' }, p.evidence.map(e => h('li', null, e.text, ' ', ...refLabels(e.refs)))),
        h('h3', null, 'Conferência do texto com a literatura'),
        h('div', { class: 'tbl-wrap' }, h('table', { class: 'tbl' },
          h('thead', null, h('tr', null, ['Item', 'Situação', 'Observação', 'Fontes'].map(c => h('th', { scope: 'col' }, c)))),
          h('tbody', null, p.verification.map(v => h('tr', null,
            h('th', { scope: 'row' }, v.item),
            h('td', null, h('span', { class: 'badge ' + ST[v.status][1] }, ST[v.status][0])),
            h('td', null, v.note),
            h('td', null, ...refLabels(v.refs))))))),
        h('h3', null, 'Referências deste protocolo'),
        h('ol', { class: 'list refs' }, p.refs.map(id => map.get(id)).filter(Boolean).map(r => refItem(r, p.id)))))));
}
