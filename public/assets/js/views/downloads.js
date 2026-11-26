import { h } from '../dom.js';
import { page } from './common.js';
import { downloadCard } from './download.js';
import { icon } from '../icons.js';

const DIR = 'assets/downloads/';
const ATLAS = 'Atlas_Parasitologia_Humana_UFAM';
const OPAS = 'OPAS_Pranchas_diagnostico_parasitos_intestinais_2ed_2020.pdf';
const mb = b => (b / 1048576).toFixed(1).replace('.', ',') + ' MB';
let man = null;
const loadMan = () => man ? Promise.resolve(man) : fetch(DIR + 'manifest.json', { cache: 'no-cache' }).then(r => r.ok ? r.json() : null).catch(() => null).then(m => (man = m));

function dl(file, label, kind, meta) {
  const m = meta && meta[file];
  return h('a', { class: 'btn primary dl-btn', href: DIR + file, download: file, rel: 'noopener' }, icon('download', 18), h('span', null, label, m ? h('small', null, ` ${kind} · ${mb(m.bytes)}`) : h('small', null, ` ${kind}`)));
}

export function downloadsPage() {
  const slotAtlas = h('div', { class: 'dl-actions' }), slotOpas = h('div', { class: 'dl-actions' }), sha = h('div', { class: 'muted small' });
  const paint = meta => {
    slotAtlas.replaceChildren(dl(ATLAS + '.pdf', 'Baixar o atlas em PDF', 'PDF', meta), dl(ATLAS + '.docx', 'Baixar em DOCX (editável)', 'DOCX', meta));
    slotOpas.replaceChildren(dl(OPAS, 'Baixar o atlas da OPAS (PDF)', 'PDF', meta));
    const a = meta && meta[ATLAS + '.pdf'], o = meta && meta[OPAS];
    sha.replaceChildren(...(a || o ? [h('details', null, h('summary', { class: 'small' }, 'Conferir integridade (SHA-256)'), a ? h('p', { class: 'small' }, 'Atlas PDF: ', h('code', null, a.sha256)) : null, o ? h('p', { class: 'small' }, 'OPAS PDF: ', h('code', null, o.sha256)) : null)] : []));
  };
  paint(null);
  loadMan().then(m => { if (m) paint(m.arquivos); });
  return page('Downloads',
    h('header', { class: 'dl-head' }, h('h1', null, 'Downloads'), h('p', { class: 'lead' }, 'Leve o atlas para o laboratório: o atlas deste site em PDF, o atlas oficial da OPAS e o aplicativo Android.')),
    h('div', { class: 'grid dl-grid' },
      h('article', { class: 'card dl-card2 teal' },
        h('span', { class: 'chip' }, 'Deste site'), h('h2', null, 'Atlas de Parasitologia Humana (PDF)'),
        h('p', null, 'Todas as espécies com fotos das lâminas, legendas e créditos, morfologia, critérios de identificação, doença, diagnóstico, tratamento (fármacos citados, sem doses) e profilaxia — gerado a partir dos mesmos dados do site.'),
        h('ul', { class: 'list small' },
          h('li', null, 'Imagens reduzidas para limitar o tamanho do arquivo; o site mostra versões maiores.'),
          h('li', null, 'Espécies “em revisão” aparecem sinalizadas; autoria só quando informada pelos autores das fotos.')),
        slotAtlas, sha),
      h('article', { class: 'card dl-card2 amber' },
        h('span', { class: 'chip' }, 'Obra de referência'), h('h2', null, 'Pranchas para o diagnóstico de parasitos intestinais'),
        h('p', null, 'Atlas oficial da OPAS (Organização Pan-Americana da Saúde), segunda edição, 2020 — versão em português do “Bench aids for the diagnosis of intestinal parasites” (OMS, 2019): microfotografias, técnicas de concentração e esfregaços, e colorações.'),
        slotOpas,
        h('p', { class: 'small' }, 'Fonte oficial: ', h('a', { href: 'https://iris.paho.org/handle/10665.2/52299', rel: 'noopener' }, 'repositório IRIS da OPAS'), ' · original em inglês: ', h('a', { href: 'https://www.who.int/publications/i/item/9789241515344', rel: 'noopener' }, 'OMS'), '.'),
        h('details', null, h('summary', null, 'Licença e créditos (leia antes de redistribuir)'),
          h('ul', { class: 'list small' },
            h('li', null, '© Organização Pan-Americana da Saúde, 2020. Licença ', h('a', { href: 'https://creativecommons.org/licenses/by-nc-sa/3.0/igo/deed.pt', rel: 'noopener' }, 'CC BY-NC-SA 3.0 IGO'), ': cópia e redistribuição permitidas para fins não comerciais, com a referência bibliográfica e sob a mesma licença.'),
            h('li', null, 'Referência: Pranchas para o diagnóstico de parasitos intestinais. Segunda edição. Washington, D.C.: Organização Pan-Americana da Saúde; 2020. Licença: CC BY-NC-SA 3.0 IGO.'),
            h('li', null, 'Cópia integral e sem alterações do PDF. Este atlas e a UFAM não são endossados pela OPAS; o logotipo da OPAS aparece apenas dentro do PDF original e não é usado como marca deste site.'),
            h('li', null, 'Materiais de terceiros (figuras de autores citados na obra): a responsabilidade pelo uso é de quem os reutiliza, conforme aviso do próprio documento.'),
            h('li', null, 'As fotos deste site são independentes e não foram copiadas da obra da OPAS.')))),
      h('article', { class: 'card dl-card2 violet' },
        h('span', { class: 'chip' }, 'Somente Android'), h('h2', null, 'Aplicativo offline'), downloadCard())));
}
