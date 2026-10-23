# Tutorial — como gerar o APK do Atlas

Vale para macOS e Linux (no Windows, use WSL2 ou o GitHub Actions da seção 4).
**Aviso:** o código não foi compilado por quem o escreveu (ver `docs/ANDROID.md`). Se o passo 3 apontar erros do `flutter analyze`, eles são do código, não do seu ambiente: envie a saída para correção.

## 1. Pré-requisitos (uma vez)
1. **Flutter** estável (≥ 3.22). Confira: `flutter --version`.
2. **JDK 17** (`java -version`). O Android Studio já traz um JDK.
3. **Android SDK**: instale o Android Studio, abra-o uma vez e, em *Settings → Languages & Frameworks → Android SDK*, instale *Android SDK Platform* (mais recente) e *Command-line Tools*.
4. Aceite as licenças e valide:
   ```bash
   flutter doctor --android-licenses
   flutter doctor          # a linha "Android toolchain" deve estar com ✓
   ```
5. **Python 3 e Pillow** (para gerar os ícones; sem Pillow o ícone padrão do Flutter é mantido):
   ```bash
   pip3 install pillow
   ```

## 2. Preparar o projeto
```bash
unzip atlas-parasitologia-v5.zip
cd atlas-parasitologia/flutter_app
chmod +x tool/build_apk.sh      # só se o zip perdeu a permissão
```

## 3. Gerar o APK
```bash
tool/build_apk.sh
```
O script executa, nesta ordem: `flutter --version` → conferência dos dados → (1ª vez) `flutter create --platforms=android` e restauração de `lib/`, `test/`, `pubspec.yaml` → rótulo do app, **ícone e splash** (`tool/make_brand.py --android`) → `flutter pub get` → `flutter analyze` → `flutter test` → `flutter build apk --release`.

Resultado em `build/app/outputs/flutter-apk/`: `app-release.apk` e `SHA256SUMS.txt`.

Opções: `--split-abi` (um APK por arquitetura; para a maioria dos celulares atuais use `app-arm64-v8a-release.apk`) e `--skip-tests`.

Mensagens esperadas e inofensivas: `tree-sitter-dart ausente; verificação PULADA` (é só a checagem de sintaxe opcional do script Python; `flutter analyze` a substitui).

### Se algo falhar
| Sintoma | Causa provável / ação |
|---|---|
| `sed: ... command a expects \ followed by text` | Versão antiga do script (usava `sed -i`, incompatível com macOS). Use o v4.1 ou superior. |
| `'flutter' não está no PATH` | Adicione `flutter/bin` ao PATH e abra um novo terminal. |
| `flutter doctor` reclama de licenças / cmdline-tools | Passo 1.3 e 1.4. |
| `Pillow ausente` | `pip3 install pillow` e rode de novo (o script é idempotente: refaz rótulo, ícone e splash). |
| Ícone ou splash do Flutter (azul) em vez do Atlas | O passo de marca falhou (veja o aviso no log). Rode `python3 tool/make_brand.py --android` e depois `flutter clean && tool/build_apk.sh`. |
| Erro de recurso do Android (`styles.xml`, `launch_background`, `ic_launcher`) | Envie o trecho do erro; apague `android/res` gerado com `rm -rf android` e rode de novo. |
| Erros em `flutter analyze` (`error •`) | Problema no código; copie a saída completa. Avisos `info •` não interrompem o build. |
| Aviso "há testes falhando" | O APK é gerado mesmo assim (use `STRICT_TESTS=1 tool/build_apk.sh` para bloquear). Copie a saída do teste e envie para correção; para pular os testes: `tool/build_apk.sh --skip-tests`. |
| Erro de Gradle/Kotlin/AGP após atualizar o Flutter | Apague `android/` (é regenerada) e rode de novo: `rm -rf android && tool/build_apk.sh`. |
| `Could not find ... 'ANDROID_HOME'` | Defina `export ANDROID_HOME=$HOME/Library/Android/sdk` (macOS) ou `$HOME/Android/Sdk` (Linux), ou `flutter config --android-sdk <caminho>`. |

## 4. Alternativa sem instalar nada: GitHub Actions
1. Envie a pasta `atlas-parasitologia/` (inclui `.github/workflows/android.yml`) para um repositório seu.
2. Aba **Actions → android-apk → Run workflow**.
3. Ao terminar, baixe o artefato `atlas-parasitologia-apk` (APK + `SHA256SUMS.txt`).
(O workflow também não foi executado pelo autor.)

## 5. Instalar no celular
**Por cabo (USB):** ative *Opções do desenvolvedor → Depuração USB* e rode `adb install -r build/app/outputs/flutter-apk/app-release.apk`.
**Por arquivo:** copie o `.apk` ao aparelho, abra-o e permita *instalar apps de fontes desconhecidas* para o app usado (Arquivos, Drive…).
Para conferir a integridade: `sha256sum app-release.apk` (macOS: `shasum -a 256`) e compare com `SHA256SUMS.txt`.

## 6. Publicar na Play Store (opcional)
O release sai assinado com a **chave de debug**, que a Play Store rejeita. Crie uma keystore e configure a assinatura conforme `docs/ANDROID.md` (seção *Assinatura*), depois gere um App Bundle: `flutter build appbundle --release`. **Faça backup da keystore e das senhas**: sem elas não há como atualizar o app.

## 7. Atualizar o conteúdo e gerar uma nova versão
```bash
python3 tool/sync_assets.py       # copia ../public/data e ../public/assets/img e regrava o manifesto sha256
python3 tool/verify_contract.py   # confere dados × app
# aumente a versão em pubspec.yaml (version: 1.0.1+2) e em lib/constants.dart (appVersion)
tool/build_apk.sh
```
Reprodutibilidade: o manifesto não contém data/hora; a mesma entrada gera o mesmo `combinedSha256`, exibido em *Sobre → Integridade dos dados*. O hash do APK em si pode variar entre builds (assinatura/metadados do Gradle); o que é reprodutível é o conteúdo de dados.
