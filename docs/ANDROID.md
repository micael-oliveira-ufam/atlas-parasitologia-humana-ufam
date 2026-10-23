# Atlas — aplicativo Android (Flutter)

App **offline** (nenhum dado sai do aparelho; não pede permissões) que reaproveita os mesmos JSON e imagens do site.
Código em `flutter_app/`.

## Estado de verificação (leia antes de usar)

O app foi escrito em um ambiente **sem Flutter, Dart nem Android SDK** (downloads bloqueados). Portanto:

| Verificação | Situação |
|---|---|
| Sintaxe de todos os `.dart` (tree-sitter-dart) | **Feita** — 0 erros |
| Imports resolvem para arquivos existentes | **Feita** |
| Contrato de dados (chaves/tipos lidos pelo app × JSON), referências cruzadas, imagens presentes, manifesto sha256 | **Feita** (`python3 tool/verify_contract.py`) |
| Expectativas dos testes (contagens, buscas) conferidas com um espelho em Python | **Feita** |
| Geração dos ícones (PIL) | **Feita** (tamanhos conferidos) |
| `flutter analyze` (tipos, nulabilidade, lints) | **NÃO feita** |
| `flutter test` | **NÃO feita** |
| Compilação / APK / execução em aparelho ou emulador | **NÃO feitas** |
| Workflow do GitHub Actions | **NÃO executado** |
| Gesto de pinça/arraste no visualizador (conflito PageView × InteractiveViewer) | **NÃO testado** |

Espere possíveis erros de compilação ou avisos na primeira execução; `tool/build_apk.sh` roda `flutter analyze` e `flutter test` antes do build, justamente para expô-los.

## Requisitos
Flutter ≥ 3.22 (Dart ≥ 3.4; o código usa `ColorScheme.surfaceContainerHighest`), JDK 17, Android SDK (aceitar licenças: `flutter doctor --android-licenses`).

## Gerar o APK
Passo a passo completo, com solução de problemas: **`docs/TUTORIAL_APK.md`**.

```bash
cd flutter_app
tool/build_apk.sh            # analyze + test + build release
tool/build_apk.sh --split-abi  # um APK por arquitetura (menor)
```
Saída: `build/app/outputs/flutter-apk/app-release.apk` e `SHA256SUMS.txt`.
Sem Flutter local: GitHub Actions → *android-apk* → *Run workflow*.

O script gera o scaffolding Android com `flutter create --platforms=android` (pasta `android/` não é versionada), restaura `lib/`, `test/` e `pubspec.yaml`, ajusta o rótulo e cria os ícones.

## Instalar no aparelho
Copie o `.apk`, permita "instalar apps desconhecidos" para o gerenciador de arquivos usado e abra o arquivo. Confira o SHA-256 com `sha256sum` se o arquivo trafegou por terceiros.

## Assinatura
O release sai assinado com a **chave de debug** (basta para instalar). Para a Play Store: crie uma keystore (`keytool -genkey -v -keystore ~/atlas.jks -keyalg RSA -keysize 2048 -validity 10000 -alias atlas`), crie `android/key.properties` (já no `.gitignore`) e configure `signingConfigs` em `android/app/build.gradle(.kts)` conforme a documentação do Flutter. **Guarde a keystore: sem ela não há atualizações.**

## Atualizar o conteúdo
O conteúdo vive em `../public/data` e `../public/assets/img` (mesma fonte do site). Depois de editar:
```bash
python3 tool/sync_assets.py     # copia para assets/ e reescreve assets/data/manifest.json
python3 tool/verify_contract.py # confere dados e manifesto
```
Aumente a versão em `pubspec.yaml` **e** em `lib/constants.dart` (`appVersion`).
O manifesto não tem data/hora: a mesma entrada gera o mesmo `combinedSha256` (reprodutível). A tela *Sobre* mostra o início desse hash.

## Logo e splash
Identidade visual original (campo de microscópio, ovo de nematódeo em âmbar e um verme), gerada por `flutter_app/tool/make_brand.py` a partir de uma única descrição geométrica:
- `brand/logo.svg` (editável), `brand/logo_tile.png` (512 px; serve de ícone de loja) e `brand/logo_mark.png` (fundo transparente, usado no splash).
- Android (gerado por `tool/build_apk.sh` após o `flutter create`): ícone legado, **ícone adaptativo** (com versão monocromática para o ícone temático do Android 13+) e **splash nativo** (Android < 12 via `launch_background`; Android 12+ via `values-v31`/`values-night-v31`).
- Em Dart, `lib/ui/splash.dart` continua a mesma tela (mesmo fundo `#0F5F58`) enquanto os dados carregam, por no mínimo 1,4 s, e respeita "remover animações" do sistema.
- Para trocar o desenho: edite as constantes de geometria/cores no topo de `tool/make_brand.py`, rode `python3 tool/make_brand.py --android` (ou o build) e confira `brand/`.

Verificado aqui: PNGs/SVG gerados e inspecionados visualmente; XMLs Android bem-formados; o primeiro plano do ícone adaptativo e o ícone do splash do Android 12 ficam dentro das zonas seguras (checado por pixel). **Não verificado:** a aparência em aparelho/emulador (máscaras de cada fabricante, splash de cada versão do Android) e a compilação dos recursos pelo Gradle.

## O que o app tem
Atlas por módulo → espécie (galeria, morfologia, diagnóstico, ciclo, profilaxia); **toque na imagem** abre visualizador em tela cheia (deslizar, pinça, duplo toque, brilho/contraste, crédito sempre visível, pontos anotados quando existirem); protocolos com evidências, verificação item a item e referências (DOI/PubMed copiáveis); quiz com ordem embaralhada; guia de artefatos; busca sem acentos; créditos das imagens e hash dos dados em *Sobre*; tema claro/escuro.

## Limitações conhecidas (herdadas dos dados)
- Quiz sem auditoria científica independente (conteúdo originalmente da prova DSEI/SASISUS, fora do tema do atlas).
- Imagens são recortes de baixa resolução das lâminas; créditos de algumas imagens constam como "a confirmar" (a tela *Sobre* contabiliza).
- Nenhuma imagem tem pontos anotados (*hotspots*) ainda; o recurso existe no código e no visualizador.
- Textos das fichas de espécie não passaram pela mesma revisão de literatura dos protocolos.
- O app não abre links externos (sem dependências); apenas copia DOI/PubMed.
