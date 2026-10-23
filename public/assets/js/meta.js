// Rótulos e formatação compartilhados (sem dependências, para evitar importações circulares).
export const IMGTYPE = { ilustracao: 'Ilustração esquemática', externa: 'Imagem externa (origem a confirmar)', microfotografia: 'Microfotografia' };
export const fmtDate = iso => (iso && /^\d{4}-\d{2}-\d{2}$/.test(iso)) ? iso.split('-').reverse().join('/') : null;
export function creditText(im) {
  if (!im.credit) return 'Crédito da imagem: não informado (origem a confirmar).';
  const d = fmtDate(im.date);
  return `Crédito: ${im.credit}${d ? ` · foto de ${d}` : ''}${im.license ? ' · ' + im.license : ''}`;
}
export const creditPending = im => !im.credit || im.creditStatus === 'a-confirmar';
