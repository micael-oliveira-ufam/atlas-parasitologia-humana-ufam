// Carrega e indexa os dados (todos estáticos, em /data).
const j = async url => { const r = await fetch(url, { cache: 'no-cache' }); if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`); return r.json(); };

export const store = { site: null, modules: [], specimens: [], quiz: [], protocols: [], artifacts: null, refs: { review: null, items: [] } };

export async function loadAll() {
  const reg = await j('data/modulos.json');
  store.site = reg.site;
  const mods = [...reg.modules].sort((a, b) => a.order - b.order);
  const datas = await Promise.all(mods.map(m => j(m.dataFile)));
  store.modules = mods.map((m, i) => ({ ...m, specimens: datas[i].specimens.filter(s => s.status !== 'rascunho').map(s => ({ ...s, moduleId: m.id })), drafts: datas[i].specimens.filter(s => s.status === 'rascunho').length }));
  store.specimens = store.modules.flatMap(m => m.specimens.map(s => ({ ...s, moduleId: m.id })));
  [store.quiz, store.protocols, store.artifacts, store.refs] = await Promise.all([j('data/quiz.json'), j('data/protocolos.json'), j('data/artefatos.json'), j('data/referencias.json')]);
  return store;
}
export const getModule = id => store.modules.find(m => m.id === id);
export const getSpecimen = (modId, id) => store.specimens.find(s => s.moduleId === modId && s.id === id);
export const imgSrc = im => 'assets/img/' + im.file;
export const cover = s => s.images[0];
