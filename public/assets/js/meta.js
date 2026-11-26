// Rótulos e formatação compartilhados (só depende de store.js, para evitar importações circulares).
import { store } from './store.js';
export const refLabel = id => { const r = (store.refs.items || []).find(x => x.id === id); return r ? r.short || r.id : id; };
export const CONF = { confirmada: ['Identificação confirmada', 'ok'], alta: ['Identificação: alta confiança', 'ok'], media: ['Identificação: média — a confirmar', 'warn'], documento: ['Identificação conforme legenda do documento de lâminas', 'warn'] };
export const IMGTYPE = { ilustracao: 'Ilustração esquemática', externa: 'Imagem externa (origem a confirmar)', microfotografia: 'Microfotografia' };
export const fmtDate = iso => (iso && /^\d{4}-\d{2}-\d{2}$/.test(iso)) ? iso.split('-').reverse().join('/') : null;
export function creditText(im) {
  if (!im.credit) return 'Crédito da imagem: não informado (origem a confirmar).';
  const d = fmtDate(im.date);
  return `Crédito: ${im.credit}${d ? ` · foto de ${d}` : ''}${im.license ? ' · ' + im.license : ''}`;
}
export const creditPending = im => !im.credit || im.creditStatus === 'a-confirmar';
