#!/usr/bin/env bash
# Gera o APK do Atlas. Requer Flutter (>= 3.22) e Android SDK já instalados e no PATH.
# Uso:  tool/build_apk.sh [--skip-tests] [--split-abi]
# O scaffolding Android é gerado por `flutter create` (não versionado aqui): assim o projeto
# não carrega arquivos Gradle de uma versão específica do Flutter.
set -euo pipefail

cd "$(dirname "$0")/.."
ORG="br.ufam.parasitologia"
NAME="atlas_parasitologia"
LABEL="Atlas Parasitologia"
SKIP_TESTS=0; SPLIT=0
for a in "$@"; do
  case "$a" in
    --skip-tests) SKIP_TESTS=1 ;;
    --split-abi) SPLIT=1 ;;
    -h|--help) sed -n '2,6p' "$0"; exit 0 ;;
    *) echo "opção desconhecida: $a" >&2; exit 2 ;;
  esac
done

command -v flutter >/dev/null || { echo "ERRO: 'flutter' não está no PATH. Veja docs/ANDROID.md." >&2; exit 1; }
echo "== Flutter =="; flutter --version

echo "== Conferindo dados (não exige Flutter) =="
python3 tool/verify_contract.py

if [ ! -d android ]; then
  echo "== Gerando scaffolding Android =="
  tmp="$(mktemp -d)"
  cp -r lib "$tmp/lib"; cp -r test "$tmp/test"; cp pubspec.yaml analysis_options.yaml "$tmp/"
  flutter create --platforms=android --org "$ORG" --project-name "$NAME" . >/dev/null
  # flutter create sobrescreve lib/main.dart, test/ e pubspec.yaml: restaura os nossos.
  rm -rf lib test; cp -r "$tmp/lib" lib; cp -r "$tmp/test" test
  cp "$tmp/pubspec.yaml" pubspec.yaml; cp "$tmp/analysis_options.yaml" analysis_options.yaml
  rm -rf "$tmp"
fi

# Ajustes que valem mesmo se android/ já existir (idempotentes; sem `sed -i`, que difere entre macOS e Linux)
echo "== Rótulo, ícone e splash =="
python3 - "$LABEL" <<'PY'
import re, sys
p = 'android/app/src/main/AndroidManifest.xml'
s = open(p, encoding='utf-8').read()
s2 = re.sub(r'android:label="[^"]*"', 'android:label="%s"' % sys.argv[1], s, count=1)
open(p, 'w', encoding='utf-8').write(s2)
print('rótulo ->', sys.argv[1])
PY
python3 tool/make_brand.py --android || echo "AVISO: ícone e splash padrão do Flutter mantidos (instale Pillow: pip3 install pillow)."

echo "== Dependências =="
flutter pub get
echo "== Análise estática =="
flutter analyze --no-fatal-infos
if [ "$SKIP_TESTS" -eq 0 ]; then
  echo "== Testes =="
  if ! flutter test; then
    if [ "${STRICT_TESTS:-0}" = "1" ]; then echo "ERRO: testes falharam (STRICT_TESTS=1)."; exit 1; fi
    echo "AVISO: há testes falhando; o APK será gerado mesmo assim. Corrija os testes antes de distribuir (STRICT_TESTS=1 bloqueia o build)."
  fi
fi

echo "== Build =="
args=(build apk --release)
[ "$SPLIT" -eq 1 ] && args+=(--split-per-abi)
flutter "${args[@]}"

out="build/app/outputs/flutter-apk"
echo "== Resultado =="; ls -l "$out"/*.apk
if command -v sha256sum >/dev/null; then H="sha256sum"; else H="shasum -a 256"; fi
( cd "$out" && $H ./*.apk ) | tee "$out/SHA256SUMS.txt"
echo
echo "AVISO: o APK de release usa a chave de DEBUG por padrão (serve para instalar/testar)."
echo "Para a Play Store, configure uma keystore própria (docs/ANDROID.md)."
