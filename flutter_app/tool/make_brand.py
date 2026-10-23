#!/usr/bin/env python3
"""Gera a identidade visual do app (logo, ícones Android e splash) a partir de UMA descrição geométrica.

Saídas (determinísticas; sem datas):
  brand/logo.svg, brand/logo_tile.png (512), brand/logo_mark.png (512, fundo transparente)
Com --android (e android/app/src/main/res existente):
  ícone legado (mipmap-*), ícone adaptativo (primeiro plano + monocromático p/ Android 13),
  splash nativo (Android <12: launch_background; Android 12+: values-v31).
Requer Pillow.   Uso: python3 tool/make_brand.py [--android]
"""
import math, os, sys
try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Pillow ausente (pip3 install pillow)."); sys.exit(1)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEAL, CREAM, AMBER = (15, 95, 88), (246, 243, 236), (232, 163, 61)
HEX = lambda c: '#%02X%02X%02X' % c

# --- geometria (coordenadas 0..1024; traços centrados na linha) -------------------------
RING = dict(cx=512, cy=512, r=330, w=44)                       # campo do microscópio
EGG = dict(cx=455, cy=540, rx=125, ry=155, w=26)               # casca do ovo
EMB = dict(cx=455, cy=540, rx=58, ry=82)                       # embrião
WORM_A, WORM_B, WORM_AMP, WORM_PERIODS, WORM_W, WORM_N = (600, 300), (690, 640), 38, 2, 24, 90


def worm_points():
    ax, ay = WORM_A; bx, by = WORM_B
    L = math.hypot(bx - ax, by - ay); dx, dy = (bx - ax) / L, (by - ay) / L; nx, ny = -dy, dx
    pts = []
    for i in range(WORM_N + 1):
        t = i / WORM_N; off = WORM_AMP * math.sin(2 * math.pi * WORM_PERIODS * t)
        pts.append((ax + dx * L * t + nx * off, ay + dy * L * t + ny * off))
    return pts


def colors(mono):
    w = (255, 255, 255)
    return (w, w, w) if mono else (CREAM, AMBER, CREAM)   # anel, ovo, verme


def draw_glyph(d, px, scale, mono):
    k = px / 1024.0
    m = lambda v: (512 + (v - 512) * scale) * k
    s = lambda v: v * scale * k
    c_ring, c_egg, c_worm = colors(mono)
    R = RING; ro = R['r'] + R['w'] / 2
    d.ellipse((m(R['cx'] - ro), m(R['cy'] - ro), m(R['cx'] + ro), m(R['cy'] + ro)), outline=c_ring, width=max(1, round(s(R['w']))))
    E = EGG; ex, ey = E['rx'] + E['w'] / 2, E['ry'] + E['w'] / 2
    d.ellipse((m(E['cx'] - ex), m(E['cy'] - ey), m(E['cx'] + ex), m(E['cy'] + ey)), outline=c_egg, width=max(1, round(s(E['w']))))
    B = EMB
    d.ellipse((m(B['cx'] - B['rx']), m(B['cy'] - B['ry']), m(B['cx'] + B['rx']), m(B['cy'] + B['ry'])), fill=c_egg)
    pts = [(m(x), m(y)) for x, y in worm_points()]
    w = max(1, round(s(WORM_W))); d.line(pts, fill=c_worm, width=w, joint='curve')
    for x, y in (pts[0], pts[-1]):
        d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=c_worm)


def render(px, scale=1.0, mono=False, tile=False, ss=3):
    n = px * ss
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if tile:
        d.rounded_rectangle((0, 0, n - 1, n - 1), radius=int(n * 0.22), fill=TEAL + (255,))
    draw_glyph(d, n, scale, mono)
    return im.resize((px, px), Image.LANCZOS)


def write_svg(path):
    R, E, B = RING, EGG, EMB
    pts = ' '.join('%.1f,%.1f' % p for p in worm_points())
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" role="img" aria-label="Atlas de Parasitologia">
  <rect width="1024" height="1024" rx="225" fill="{HEX(TEAL)}"/>
  <circle cx="{R['cx']}" cy="{R['cy']}" r="{R['r']}" fill="none" stroke="{HEX(CREAM)}" stroke-width="{R['w']}"/>
  <ellipse cx="{E['cx']}" cy="{E['cy']}" rx="{E['rx']}" ry="{E['ry']}" fill="none" stroke="{HEX(AMBER)}" stroke-width="{E['w']}"/>
  <ellipse cx="{B['cx']}" cy="{B['cy']}" rx="{B['rx']}" ry="{B['ry']}" fill="{HEX(AMBER)}"/>
  <polyline points="{pts}" fill="none" stroke="{HEX(CREAM)}" stroke-width="{WORM_W}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
'''
    open(path, 'w', encoding='utf-8').write(svg)


def save(im, path):
    os.makedirs(os.path.dirname(path), exist_ok=True); im.save(path, optimize=True)


def make_brand():
    b = os.path.join(ROOT, 'brand')
    os.makedirs(b, exist_ok=True)
    write_svg(os.path.join(b, 'logo.svg'))
    save(render(512, tile=True), os.path.join(b, 'logo_tile.png'))
    save(render(512), os.path.join(b, 'logo_mark.png'))
    print('brand/: logo.svg, logo_tile.png, logo_mark.png')


DENS = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}


def make_android():
    res = os.path.join(ROOT, 'android', 'app', 'src', 'main', 'res')
    if not os.path.isdir(res):
        print('android/app/src/main/res não existe (rode flutter create antes).'); return 1
    for name, f in DENS.items():                                   # ícone legado
        save(render(round(48 * f), tile=True), os.path.join(res, f'mipmap-{name}', 'ic_launcher.png'))
    SAFE = 0.86   # anel (diâmetro 704/1024) fica em ~60% do quadro 108dp, dentro da zona segura (66dp)
    for name, f in DENS.items():                                   # adaptativo: 108dp
        px = round(108 * f)
        save(render(px, scale=SAFE), os.path.join(res, f'drawable-{name}', 'ic_launcher_foreground.png'))
        save(render(px, scale=SAFE, mono=True), os.path.join(res, f'drawable-{name}', 'ic_launcher_monochrome.png'))
    save(render(960, scale=0.88), os.path.join(res, 'drawable-nodpi', 'splash_icon.png'))   # Android 12+
    save(render(480, scale=0.95), os.path.join(res, 'drawable-nodpi', 'splash_logo.png'))   # Android <12

    def w(rel, text):
        p = os.path.join(res, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(text)

    w('values/ic_launcher_background.xml', f'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">{HEX(TEAL)}</color>\n</resources>\n')
    w('mipmap-anydpi-v26/ic_launcher.xml', '''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
    <monochrome android:drawable="@drawable/ic_launcher_monochrome"/>
</adaptive-icon>
''')
    launch = '''<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@color/ic_launcher_background"/>
    <item>
        <bitmap android:gravity="center" android:src="@drawable/splash_logo"/>
    </item>
</layer-list>
'''
    for d in ('drawable', 'drawable-v21'):
        w(f'{d}/launch_background.xml', launch)
    v31 = f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="LaunchTheme" parent="@android:style/Theme.Light.NoTitleBar">
        <item name="android:windowBackground">@drawable/launch_background</item>
        <item name="android:windowSplashScreenBackground">{HEX(TEAL)}</item>
        <item name="android:windowSplashScreenAnimatedIcon">@drawable/splash_icon</item>
        <item name="android:windowFullscreen">false</item>
    </style>
</resources>
'''
    w('values-v31/styles.xml', v31)
    w('values-night-v31/styles.xml', v31)    # no modo escuro, "night" tem precedência sobre a versão da API
    print('android/res: ícone legado + adaptativo + monocromático, splash (<12 e 12+)')
    return 0


if __name__ == '__main__':
    make_brand()
    sys.exit(make_android() if '--android' in sys.argv else 0)
