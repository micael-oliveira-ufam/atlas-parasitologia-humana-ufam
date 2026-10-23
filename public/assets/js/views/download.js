import { h } from '../dom.js';

export const APK = { url: 'https://github.com/micael-oliveira-ufam/atlas-parasitologia-humana-ufam/releases/download/Atlas-Parasitologia-v2.0.0/Atlas-Parasitologia-v2.0.0.apk', releases: 'https://github.com/micael-oliveira-ufam/atlas-parasitologia-humana-ufam/releases', file: 'Atlas-Parasitologia-v2.0.0.apk', version: '2.0.0', sha256: '92cdd08fcfe07c0d67c6356724617c9fdf0607f9ccd13fd13d6a75b4cb74cd44' };

// Cartão de download do aplicativo (somente Android).
export function downloadCard() {
  return h('div', { class: 'dl-card' },
    h('div', null, h('strong', null, 'Aplicativo para Android'), h('p', { class: 'muted small' }, `Versão ${APK.version} · APK de ~54 MB · funciona offline. `, h('strong', null, 'Somente Android'), ': não há versão para iPhone/iOS (use este site).`)),
    h('p', null, h('a', { class: 'btn primary', href: APK.url, rel: 'noopener', download: APK.file }, '⬇ Baixar APK (Android)'), ' ', h('a', { href: APK.releases, rel: 'noopener' }, 'todas as versões')),
    h('details', null, h('summary', null, 'Como instalar e conferir'),
      h('ol', { class: 'list' }, h('li', null, 'No celular Android, baixe o arquivo e abra-o.'), h('li', null, 'Quando o Android pedir, permita a instalação de fontes desconhecidas para o navegador/gerenciador de arquivos usado.'), h('li', null, 'Integridade (SHA-256): ', h('code', null, APK.sha256)))));
}
