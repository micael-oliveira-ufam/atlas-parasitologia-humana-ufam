import { h, clear } from '../dom.js';
import { getModule, getSpecimen, imgSrc } from '../store.js';
import { createViewer } from '../viewer.js';
import { openLightbox } from '../lightbox.js';
import { page, badges, list, CONF, STLABEL, refName, IMGTYPE, creditText, creditPending } from './common.js';

const row = (k, v) => v ? h('div', { class: 'kv' }, h('dt', null, k), h('dd', null, v)) : null;
const section = (id, title, ...kids) => { const c = kids.flat().filter(Boolean); return c.length ? h('section', { class: 'sec', id }, h('h2', null, title), ...c) : null; };

export function specimenPage(modId, id) {
  const m = getModule(modId), s = m && getSpecimen(modId, id); if (!s) return null;
  const idx = m.specimens.findIndex(x => x.id === id), prev = m.specimens[idx - 1], next = m.specimens[idx + 1];
  const viewerHost = h('div'), infoHost = h('div', { class: 'img-info', 'aria-live': 'polite' }), hsBox = h('div', { class: 'hs-box', 'aria-live': 'polite' });
  const thumbs = h('div', { class: 'thumbs', role: 'list', 'aria-label': 'Imagens desta espécie' });
  let current = null; const btns = new Map();

  function show(im) {
    current = im; btns.forEach((b, k) => { const on = k === im.id; b.classList.toggle('on', on); b.setAttribute('aria-current', String(on)); });
    const v = createViewer(im, { onOpen: () => openLightbox(s.images, s.images.indexOf(im), { title: s.commonName }), onHotspot: (p, i) => hsBox.replaceChildren(p ? h('div', null, h('h3', null, `${i + 1}. ${p.title}`), h('p', null, p.description)) : h('p', { class: 'muted' }, 'Clique em um marcador numerado para ver a estrutura.')) });
    clear(viewerHost).append(v.el);
    hsBox.replaceChildren(h('p', { class: 'muted' }, (im.hotspots || []).length ? 'Clique em um marcador numerado para ver a estrutura.' : 'Esta imagem ainda não possui marcadores estruturais.'));
    const conf = CONF[im.confidence];
    clear(infoHost).append(
      h('div', { class: 'badges' }, h('span', { class: 'badge ' + (im.type === 'microfotografia' ? 'ok' : 'warn') }, IMGTYPE[im.type] || im.type),
        im.lamina ? h('span', { class: 'badge' }, `Lâmina ${String(im.lamina).padStart(2, '0')} · ${im.kind === 'detalhe' ? 'detalhe ampliado' : 'campo geral'}`) : null,
        conf ? h('span', { class: 'badge ' + conf[1] }, conf[0]) : null,
        im.credit && creditPending(im) ? h('span', { class: 'badge warn' }, 'Autoria a confirmar') : null),
      im.caption ? h('p', { class: 'caption' }, im.caption) : null,
      h('p', { class: 'credit', title: im.dateBasis || null }, creditText(im)));
  }
  s.images.forEach(im => {
    const b = h('button', { type: 'button', class: 'thumb-btn', role: 'listitem', title: im.alt, 'aria-label': im.alt, onClick: () => show(im) },
      h('img', { src: imgSrc(im), alt: '', loading: 'lazy', width: im.width, height: im.height }),
      h('span', null, im.lamina ? `#${String(im.lamina).padStart(2, '0')} ${im.kind === 'detalhe' ? 'detalhe' : 'campo'}` : 'externa'));
    btns.set(im.id, b); thumbs.append(b);
  });
  show(s.images[0]);

  const t = s.taxonomy || {}, d = s.diagnosticMethods || {}, c = s.transmissionAndCycle || {};
  const tax = ['phylum', 'class', 'order', 'family', 'genus', 'species'].filter(k => t[k]);
  const TL = { phylum: 'Filo', class: 'Classe', order: 'Ordem', family: 'Família', genus: 'Gênero', species: 'Espécie' };
  const toc = [['morfologia', 'Morfologia'], ['tratamento', 'Tratamento'], ['verificacao', 'Verificação científica'], ['diagnostico', 'Diagnóstico'], ['ciclo', 'Ciclo e transmissão'], ['clinica', 'Clínica'], ['profilaxia', 'Profilaxia'], ['diferencial', 'Diferencial']];
  return page(s.commonName,
    h('nav', { class: 'crumbs', 'aria-label': 'Trilha' }, h('a', { href: '#/' }, 'Início'), ' / ', h('a', { href: `#/m/${m.id}` }, m.title), ' / ', s.commonName),
    h('header', { class: 'spec-head' }, h('h1', null, s.commonName), h('p', { class: 'sci big' }, s.scientificName), badges(s)),
    s.reviewNote ? h('div', { class: 'notice bad', role: 'note' }, h('strong', null, 'Em revisão: '), s.reviewNote) : null,
    h('div', { class: 'spec-grid' },
      h('div', null, viewerHost, infoHost, s.images.length > 1 ? thumbs : null),
      h('aside', { class: 'side' },
        h('h2', null, 'Marcadores'), hsBox,
        s.keyDiagnosticFeatures ? [h('h2', null, 'Critérios-chave'), list(s.keyDiagnosticFeatures)] : null,
        h('dl', { class: 'facts' }, row('Estágio', s.evolutionaryStage), row('Dimensões de referência', s.approxSizeMicrons),
          h('p', { class: 'muted small' }, 'Dimensões são valores de livro-texto, não medidas feitas nas fotos.')))),
    h('nav', { class: 'toc', 'aria-label': 'Seções' }, toc.map(([a, l]) => h('a', { href: `#/m/${m.id}/${s.id}`, onClick: e => { e.preventDefault(); const el = document.getElementById(a); el && el.scrollIntoView({ behavior: 'smooth' }); } }, l))),
    section('morfologia', 'Morfologia', h('p', null, s.morphologyDescription), tax.length ? h('dl', { class: 'tax' }, tax.map(k => row(TL[k], t[k])), row('NCBI Taxonomy', t.ncbi)) : null, t.note ? h('p', { class: 'muted small' }, t.note) : null),
    section('diagnostico', 'Diagnóstico laboratorial', h('dl', { class: 'facts' }, row('Método de escolha', d.goldStandard), row('Amostra', d.sampleType), row('Observação técnica', d.technicalObservation)),
      d.alternatives && d.alternatives.length ? [h('h3', null, 'Alternativas'), list(d.alternatives)] : null),
    section('ciclo', 'Ciclo e transmissão', h('dl', { class: 'facts' }, row('Via de transmissão', c.transmissionRoute), row('Forma infectante', c.infectiveForm), row('Forma diagnóstica', c.diagnosticForm), row('Habitat', c.habitat), row('Tipo de ciclo', c.cycleType))),
    section('clinica', 'Doença e clínica', s.disease ? h('p', null, h('strong', null, s.disease)) : null, s.pathogenesis ? h('p', null, s.pathogenesis) : null, s.clinicalManifestations ? [h('h3', null, 'Manifestações'), list(s.clinicalManifestations)] : null),
    section('tratamento', 'Tratamento (fármacos citados)', list(s.treatment), (s.treatment || []).length ? h('p', { class: 'muted small' }, 'Informação didática: doses e esquemas não são reproduzidos; siga diretrizes vigentes e prescrição.') : null),
    section('profilaxia', 'Profilaxia', list(s.prophylaxis)),
    section('diferencial', 'Diagnóstico diferencial', s.differentialDiagnosis ? h('p', null, s.differentialDiagnosis) : null, s.benchTip ? h('aside', { class: 'tip' }, h('strong', null, 'Dica de bancada'), h('p', null, s.benchTip)) : null),
    verification(s),
    h('nav', { class: 'pager', 'aria-label': 'Espécies do módulo' },
      prev ? h('a', { href: `#/m/${m.id}/${prev.id}`, rel: 'prev' }, '← ', prev.commonName) : h('span'),
      next ? h('a', { href: `#/m/${m.id}/${next.id}`, rel: 'next' }, next.commonName, ' →') : h('span')));
}

function verification(s) {
  const v = s.verification || [], rm = s.removed || [];
  if (!v.length && !rm.length) return null;
  return h('section', { class: 'sec', id: 'verificacao' }, h('h2', null, 'Verificação científica'),
    h('p', { class: 'muted' }, `${v.length} afirmações registradas, cada uma com status, referências e trecho-evidência (trechos extraídos por leitor automático de páginas; confira na fonte).`),
    h('details', null, h('summary', null, 'Ver afirmações e fontes'),
      h('div', { class: 'tbl-wrap' }, h('table', { class: 'tbl' },
        h('thead', null, h('tr', null, ['Seção', 'Afirmação', 'Status', 'Fontes e evidência'].map(c => h('th', { scope: 'col' }, c)))),
        h('tbody', null, v.map(c => { const st = STLABEL[c.status] || [c.status, '']; return h('tr', null,
          h('td', null, c.section), h('td', null, c.text, c.before ? h('div', { class: 'muted small' }, 'Antes: ' + c.before) : null),
          h('td', null, h('span', { class: 'badge ' + st[1] }, st[0])),
          h('td', null, (c.refs || []).map(refName).join('; ') || '—', c.evidence ? h('div', { class: 'muted small' }, c.evidence) : null, c.note ? h('div', { class: 'muted small' }, c.note) : null)); }))))),
    rm.length ? h('details', null, h('summary', null, `Itens do texto anterior retirados (${rm.length})`),
      h('ul', { class: 'list' }, rm.map(r => h('li', null, h('strong', null, r.field ? r.field + ': ' : ''), r.before, h('div', { class: 'muted small' }, 'Motivo: ' + r.reason))))) : null);
}
