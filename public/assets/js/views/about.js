import { h } from '../dom.js';
import { store } from '../store.js';
import { page, STLABEL } from './common.js';
import { fmtDate } from '../meta.js';

function creditRows() {
  const seen = new Set(), rows = [];
  for (const sp of store.specimens) for (const im of sp.images) {
    const key = im.sourceFile || `${sp.id}:${im.id}`;
    if (seen.has(key)) continue; seen.add(key);
    rows.push({ lam: im.lamina, sp, im });
  }
  return rows.sort((a, b) => (a.lam ?? 1e9) - (b.lam ?? 1e9) || a.sp.commonName.localeCompare(b.sp.commonName));
}
function creditsTable() {
  const rows = creditRows();
  return h('div', { class: 'tbl-wrap' }, h('table', { class: 'tbl' },
    h('caption', { class: 'sr' }, 'Créditos das imagens por lâmina'),
    h('thead', null, h('tr', null, ['Lâmina', 'Espécie', 'Crédito', 'Data da foto', 'Situação'].map(c => h('th', { scope: 'col' }, c)))),
    h('tbody', null, rows.map(({ lam, sp, im }) => h('tr', null,
      h('th', { scope: 'row' }, lam ? String(lam).padStart(2, '0') : 'Externa'),
      h('td', null, h('a', { href: `#/m/${sp.moduleId}/${sp.id}` }, sp.commonName)),
      h('td', null, im.credit || 'Não informado'),
      h('td', null, fmtDate(im.date) || '—'),
      h('td', null, !im.credit ? h('span', { class: 'badge bad' }, 'Origem a confirmar') : im.creditStatus === 'a-confirmar' ? h('span', { class: 'badge warn' }, 'Autoria a confirmar') : h('span', { class: 'badge ok' }, 'Informado pelo autor')))))));
}
export function aboutPage() {
  const s = store.site;
  return page('Sobre',
    h('h1', null, 'Sobre o atlas'),
    h('p', null, 'Atlas de apoio ao ensino de parasitologia humana, organizado em módulos taxonômicos independentes. ', s.course, '.'),
    h('h2', null, 'Como interpretar as imagens'),
    h('ul', { class: 'list' },
      h('li', null, h('strong', null, 'Microfotografia: '), 'foto de lâmina real, com o número da lâmina e o grau de confiança da identificação indicados.'),
      h('li', null, h('strong', null, 'Identificação “confirmada” / “alta” / “média”: '), 'confirmada = conferida pelo autor; alta = morfologia típica; média = deve ser conferida com o docente ou atlas.'),
      h('li', null, h('strong', null, 'Imagem externa: '), 'figura de origem não documentada; só deve ser divulgada após confirmação de autoria e licença.'),
      h('li', null, h('strong', null, 'Em revisão: '), 'registro com divergência conhecida entre imagem e texto, descrita na própria página.')),
    h('h2', null, 'Limitações'),
    h('p', null, 'As imagens foram reduzidas para a web (miniaturas), então a ampliação máxima mostra pixels. O visualizador não simula troca de objetivas nem corantes; o aumento da objetiva não foi registrado nas fotos. As dimensões são valores de referência de livros-texto, não medidas feitas sobre as imagens.'),
    h('div', { class: 'ufam-box' }, h('img', { src: 'assets/img/brand/ufam_brasao.png', alt: 'Brasão da Universidade Federal do Amazonas', width: 96, height: 96 }), h('div', null, h('strong', null, s.institution), h('div', null, s.course))),
    h('h2', null, 'Equipe'),
    h('ul', { class: 'list' }, (s.developers || []).map(p => h('li', null, h('strong', null, p.name), ' — ', p.role)), s.advisor ? h('li', null, h('strong', null, s.advisor.name), ' — ', s.advisor.role) : null),
    verificationSummary(),
    h('h3', null, 'Créditos das imagens'),
    h('p', null, 'Cada lâmina é creditada a quem a fotografou. A data é a que consta no nome do arquivo da câmera. Quando a autoria não está documentada, a imagem aparece como “origem a confirmar”. Nenhuma licença de reuso foi definida pelo autor: por padrão, os direitos permanecem com ele.'),
    creditsTable(),
    h('h2', null, 'Bibliografia de base'), h('ul', { class: 'list' }, s.references.map(r => h('li', null, r))),
    s.referencesNote ? h('p', { class: 'muted small' }, s.referencesNote) : null,
    h('h2', null, `Referências citadas (${store.refs.items.length})`),
    h('ul', { class: 'list' }, store.refs.items.map(r => h('li', null, h('strong', null, (r.short || r.id) + ': '), r.citation, r.url ? [' ', h('a', { href: r.url, rel: 'noopener' }, r.url)] : null, r.access ? h('div', { class: 'muted small' }, 'Acesso nesta revisão: ' + r.access) : null))));
}

function verificationSummary() {
  const rv = store.refs.review || {}, cl = store.specimens.flatMap(sp => sp.verification || []);
  const n = st => cl.filter(c => c.status === st).length, removed = store.specimens.reduce((a, sp) => a + (sp.removed || []).length, 0);
  return h('div', null, h('h2', null, 'Verificação científica'),
    h('p', null, `${cl.length} afirmações conferidas: ${n('confirmado')} confirmadas, ${n('corrigido')} corrigidas, ${n('ressalva')} com ressalva, ${n('observacao')} observações das lâminas; ${removed} itens do texto anterior retirados.`),
    rv.reviewedOn ? h('p', null, 'Data da revisão: ', fmtDate(rv.reviewedOn)) : null, rv.scope ? h('p', null, rv.scope) : null,
    rv.notValidation ? h('div', { class: 'notice bad', role: 'note' }, h('strong', null, 'Limite da validação: '), rv.notValidation) : null,
    (rv.notReviewed || []).length ? [h('h3', null, 'Não revisado'), h('ul', { class: 'list' }, rv.notReviewed.map(x => h('li', null, x)))] : null);
}
