"""Arte de capa, de abertura de capítulo e de contracapa do atlas em PDF/DOCX (ilustrações ORIGINAIS e estilizadas).

Gera só o fundo (sem texto): o texto entra como texto de verdade no documento (selecionável e pesquisável).
Os desenhos são decorativos: não têm escala nem valor diagnóstico. Determinístico (semente fixa).
Uso: importado por tools/gerar-atlas-pdf.py; também roda sozinho para pré-visualizar: python3 -I tools/arte_livro.py <pasta>.
"""
import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

W, H = 1654, 2339          # A4 a 200 dpi
S = 2                      # super-amostragem dos desenhos
CM = W / 21.0              # pixels por cm

PAL = {  # (topo, meio, base), claro, médio
    "teal":   dict(g=((5, 52, 48), (11, 107, 98), (31, 163, 151)), light=(191, 237, 230), mid=(70, 190, 178), dark=(6, 60, 55)),
    "amber":  dict(g=((98, 48, 4), (178, 104, 14), (242, 181, 68)), light=(255, 232, 186), mid=(235, 160, 50), dark=(110, 56, 6)),
    "violet": dict(g=((38, 22, 80), (91, 63, 148), (155, 123, 214)), light=(226, 214, 250), mid=(150, 118, 215), dark=(48, 28, 98)),
}
BARS = [(11, 107, 98), (162, 96, 13), (91, 63, 148)]   # as três cores dos módulos


def gradient(stops, glow=(0.85, 0.12), glow_rgb=(255, 255, 255), glow_a=0.22):
    top, mid, bot = [np.array(c, float) for c in stops]
    y = np.linspace(0, 1, H)[:, None, None]
    img = np.where(y < 0.5, top + (mid - top) * (y / 0.5), mid + (bot - mid) * ((y - 0.5) / 0.5)) * np.ones((1, W, 1))
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx / W - glow[0]) * 1.0) ** 2 + ((yy / H - glow[1]) * 0.7) ** 2)
    a = np.clip(1 - d / 0.75, 0, 1)[..., None] ** 2 * glow_a
    img = img * (1 - a) + np.array(glow_rgb, float) * a
    return Image.fromarray(np.clip(img, 0, 255).astype("uint8"), "RGB").convert("RGBA")


def _layer():
    return Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))


def _comp(base, layer, alpha):
    """Reduz a camada super-amostrada e a compõe com opacidade `alpha`."""
    lay = layer.resize((W, H), Image.LANCZOS)
    if alpha < 1:
        a = lay.getchannel("A").point(lambda v: int(v * alpha)); lay.putalpha(a)
    base.alpha_composite(lay)


def _rgba(c, a=255):
    return (*c, a)


# ---------- motivos (desenhados num tile, girados e colados) ----------
def _tile(size, fn, rot, layer, cx, cy):
    t = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0)); fn(ImageDraw.Draw(t), size, size, size)
    t = t.rotate(rot, resample=Image.BICUBIC)
    layer.alpha_composite(t, (int(cx * S - size), int(cy * S - size)))


def egg_ascaris(d, cx, cy, s, c=None):
    c = c or PAL["amber"]
    a, b = s * 0.9, s * 0.68
    d.ellipse([cx - a, cy - b, cx + a, cy + b], fill=_rgba(c["dark"]))
    for k in range(48):  # casca mamilonada
        t = 2 * math.pi * k / 48
        d.ellipse([cx + a * math.cos(t) - s * .07, cy + b * math.sin(t) - s * .07, cx + a * math.cos(t) + s * .07, cy + b * math.sin(t) + s * .07], fill=_rgba(c["mid"]))
    d.ellipse([cx - a * .84, cy - b * .84, cx + a * .84, cy + b * .84], fill=_rgba(c["light"]))
    d.ellipse([cx - a * .66, cy - b * .66, cx + a * .66, cy + b * .66], fill=_rgba(c["mid"]))
    d.ellipse([cx - a * .3, cy - b * .3, cx + a * .3, cy + b * .3], fill=_rgba(c["dark"]))


def egg_taenia(d, cx, cy, s, c=None):
    c = c or PAL["amber"]
    r = s * 0.8
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=_rgba(c["dark"]))
    for k in range(40):  # estriações radiais do embrióforo
        t = 2 * math.pi * k / 40
        d.line([cx + r * .72 * math.cos(t), cy + r * .72 * math.sin(t), cx + r * .97 * math.cos(t), cy + r * .97 * math.sin(t)], fill=_rgba(c["light"]), width=max(2, int(s * .05)))
    d.ellipse([cx - r * .68, cy - r * .68, cx + r * .68, cy + r * .68], fill=_rgba(c["mid"]))
    for k in range(6):  # ganchos da oncosfera
        t = 2 * math.pi * k / 6
        x, y = cx + r * .3 * math.cos(t), cy + r * .3 * math.sin(t)
        d.ellipse([x - s * .06, y - s * .06, x + s * .06, y + s * .06], fill=_rgba(c["light"]))


def egg_hymeno(d, cx, cy, s, c=None):
    c = c or PAL["amber"]
    a, b = s * 0.82, s * 0.62
    d.ellipse([cx - a, cy - b, cx + a, cy + b], fill=_rgba(c["light"]))
    d.ellipse([cx - a * .55, cy - b * .55, cx + a * .55, cy + b * .55], fill=_rgba(c["mid"]))
    for k in (-2, -1, 1, 2):  # filamentos polares
        d.line([cx - a * .5, cy + k * s * .06, cx - a * .98, cy + k * s * .22], fill=_rgba(c["dark"]), width=max(2, int(s * .04)))


def cyst(d, cx, cy, s, c=None):
    c = c or PAL["violet"]
    r = s * 0.8
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=_rgba(c["light"]))
    d.ellipse([cx - r * .9, cy - r * .9, cx + r * .9, cy + r * .9], fill=_rgba(c["mid"]))
    for dx, dy in ((-.28, -.2), (.3, -.18), (0, .32)):  # núcleos
        d.ellipse([cx + r * dx - r * .17, cy + r * dy - r * .17, cx + r * dx + r * .17, cy + r * dy + r * .17], fill=_rgba(c["dark"]))
    d.rounded_rectangle([cx - r * .5, cy + r * .02, cx - r * .12, cy + r * .12], radius=int(r * .05), fill=_rgba(c["dark"]))


def giardia(d, cx, cy, s, c=None):
    c = c or PAL["violet"]
    a, b = s * 0.55, s * 0.82
    d.polygon([(cx - a * .5, cy + b * .55), (cx + a * .5, cy + b * .55), (cx, cy + b * 1.1)], fill=_rgba(c["mid"]))
    d.ellipse([cx - a, cy - b, cx + a, cy + b * .8], fill=_rgba(c["light"]))
    for dx in (-.4, .4):  # dois núcleos ("face")
        d.ellipse([cx + a * dx - a * .26, cy - b * .35 - a * .26, cx + a * dx + a * .26, cy - b * .35 + a * .26], fill=_rgba(c["dark"]))
    d.line([cx, cy - b * .1, cx, cy + b * .9], fill=_rgba(c["dark"]), width=max(2, int(s * .05)))
    for sx in (-1, 1):  # flagelos
        pts = [(cx + sx * (a * .6 + k * s * .05 + math.sin(k * 1.2) * s * .08), cy + b * .6 + k * s * .1) for k in range(10)]
        d.line(pts, fill=_rgba(c["mid"]), width=max(2, int(s * .045)))


def worm(layer, x0, y0, x1, y1, amp, freq, rmax, color, hi):
    """Verme/larva sinuoso, afilado nas pontas, desenhado direto na camada."""
    d = ImageDraw.Draw(layer)
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; px, py = -uy, ux
    n = 220
    for k in range(n + 1):
        t = k / n
        off = amp * math.sin(2 * math.pi * freq * t) * (0.4 + 0.6 * math.sin(math.pi * t))
        x, y = (x0 + ux * L * t + px * off) * S, (y0 + uy * L * t + py * off) * S
        r = rmax * S * (0.25 + 0.75 * math.sin(math.pi * min(1, t * 1.05)) ** .55)
        d.ellipse([x - r, y - r, x + r, y + r], fill=_rgba(color))
    for k in range(0, n + 1, 3):  # linha clara do tubo digestivo
        t = k / n
        off = amp * math.sin(2 * math.pi * freq * t) * (0.4 + 0.6 * math.sin(math.pi * t))
        x, y = (x0 + ux * L * t + px * off) * S, (y0 + uy * L * t + py * off) * S
        r = rmax * S * .22 * math.sin(math.pi * t) ** .5
        d.ellipse([x - r, y - r, x + r, y + r], fill=_rgba(hi))


def tape(layer, pts, w0, w1, color, edge):
    """Cadeia de proglotes (retângulos arredondados) ao longo de uma curva; mais largos para o fim."""
    d = ImageDraw.Draw(layer)
    n = len(pts)
    for i in range(n - 1):
        (xa, ya), (xb, yb) = pts[i], pts[i + 1]
        ang = math.atan2(yb - ya, xb - xa); t = i / max(1, n - 2)
        w = (w0 + (w1 - w0) * t) * S; L = math.hypot(xb - xa, yb - ya) * S * 0.92
        cx, cy = (xa + xb) / 2 * S, (ya + yb) / 2 * S
        ux, uy, px, py = math.cos(ang), math.sin(ang), -math.sin(ang), math.cos(ang)
        quad = lambda k: [(cx + ux * L / 2 * sx * k + px * w / 2 * sy * k, cy + uy * L / 2 * sx * k + py * w / 2 * sy * k) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        d.polygon(quad(1.0), fill=_rgba(edge)); d.polygon(quad(0.8), fill=_rgba(color))


MOTIF = {"nem": (egg_ascaris,), "pla": (egg_taenia, egg_hymeno), "pro": (cyst, giardia)}


def scatter(base, kind, c, seed, rects, n=10, alpha=0.30, smin=40, smax=110):
    """Motivos espalhados dentro de `rects` (em cm: x0,y0,x1,y1), sem desenhar sobre o cartão de texto."""
    rnd = random.Random(seed); lay = _layer()
    for _ in range(n):
        x0, y0, x1, y1 = rnd.choice(rects)
        cx, cy = rnd.uniform(x0, x1) * CM, rnd.uniform(y0, y1) * CM
        s = rnd.uniform(smin, smax) * S
        fn = rnd.choice(MOTIF[kind]); _tile(int(s * 1.2), lambda d, a, b, ss, fn=fn: fn(d, a, b, ss * .85, c), rnd.uniform(0, 360), lay, cx, cy)
    _comp(base, lay, alpha)


def field(base, cx, cy, r, ticks=True, fill_a=34, ring_a=120):
    """Campo circular de microscópio com escala de ocular na borda."""
    lay = _layer(); d = ImageDraw.Draw(lay); cx, cy, r = cx * S, cy * S, r * S
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, fill_a))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255, ring_a), width=int(5 * S))
    if ticks:
        for k in range(120):
            t = 2 * math.pi * k / 120; long = k % 10 == 0
            r1, r2 = r * (0.9 if long else 0.94), r * 0.985
            d.line([cx + r1 * math.cos(t), cy + r1 * math.sin(t), cx + r2 * math.cos(t), cy + r2 * math.sin(t)], fill=(255, 255, 255, ring_a), width=int((5 if long else 3) * S))
    _comp(base, lay, 1)


def bars(base, y, h=26, x0=0, x1=W):
    d = ImageDraw.Draw(base); seg = (x1 - x0) / 3
    for i, c in enumerate(BARS):
        d.rectangle([x0 + i * seg, y, x0 + (i + 1) * seg, y + h], fill=_rgba(c))


def card(base, x0, y0, x1, y1, alpha=238, radius=34, edge=None):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([x0 * CM, y0 * CM, x1 * CM, y1 * CM], radius=radius, fill=(255, 255, 255, alpha), outline=edge, width=4 if edge else 0)
    base.alpha_composite(lay)


def footer_strip(base, h_cm=1.9):
    d = ImageDraw.Draw(base); y = H - h_cm * CM
    d.rectangle([0, y, W, H], fill=(255, 255, 255, 255)); bars(base, int(y), 10)


def _save(img, path, q=86):
    Image.alpha_composite(Image.new("RGBA", img.size, (255, 255, 255, 255)), img).convert("RGB").save(path, "JPEG", quality=q, optimize=True)
    return path


# ---------- páginas ----------
CARD = (1.9, 14.6, 19.1, 26.9)    # cartão do texto do capítulo (cm) — o documento posiciona o texto sobre ele


def capa(path, mark_png):
    img = gradient(((7, 56, 70), (24, 80, 120), (84, 56, 140)), glow=(0.5, 0.18), glow_a=0.30)
    field(img, W / 2, 6.6 * CM, 7.4 * CM)
    # motivos nas bordas, longe do bloco de título
    scatter(img, "nem", PAL["amber"], 3, [(0.4, 0.8, 4.2, 12), (16.8, 0.8, 20.6, 12)], n=5, alpha=.38, smin=50, smax=100)
    scatter(img, "pro", PAL["violet"], 5, [(0.3, 14.5, 1.6, 22), (19.4, 14.5, 20.7, 22), (3, 19.2, 18, 22.2)], n=7, alpha=.42, smin=45, smax=90)
    lay = _layer()
    worm(lay, 1.2 * CM, 2.2 * CM, 4.6 * CM, 11.4 * CM, 1.3 * CM, 1.4, 0.34 * CM, PAL["amber"]["mid"], PAL["amber"]["light"])
    worm(lay, 19.8 * CM, 3.0 * CM, 16.6 * CM, 11.0 * CM, 1.2 * CM, 1.3, 0.30 * CM, PAL["teal"]["mid"], PAL["teal"]["light"])
    _comp(img, lay, .55)
    m = Image.open(mark_png).convert("RGBA"); sz = int(11.4 * CM); m = m.resize((sz, sz), Image.LANCZOS)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow); cx, cy = W / 2, 6.6 * CM
    gd.ellipse([cx - sz * .56, cy - sz * .56, cx + sz * .56, cy + sz * .56], fill=(255, 255, 255, 60))
    img.alpha_composite(glow); img.alpha_composite(m, (int(cx - sz / 2), int(cy - sz / 2)))
    bars(img, int(H - 1.0 * CM), int(1.0 * CM))
    return _save(img, path)


def capitulo(path, accent, kind, seed, n_esp=7):
    c = PAL[accent]
    img = gradient(c["g"], glow=(0.9, 0.1), glow_a=0.28)
    field(img, 15.6 * CM, 5.4 * CM, 6.6 * CM)
    lay = _layer()
    if kind == "nem":
        worm(lay, 11.6 * CM, 10.8 * CM, 20.6 * CM, 2.4 * CM, 1.4 * CM, 1.6, 0.42 * CM, c["light"], c["mid"])
        worm(lay, 13.4 * CM, 12.4 * CM, 20.6 * CM, 7.2 * CM, 1.0 * CM, 1.8, 0.30 * CM, c["mid"], c["light"])
    elif kind == "pla":
        pts = [(11.4 * CM + i * 0.52 * CM, 12.0 * CM - 0.28 * CM * i + math.sin(i * .55) * 0.8 * CM) for i in range(18)]
        tape(lay, pts, 0.55 * CM, 1.5 * CM, c["light"], c["mid"])
    _comp(img, lay, .50)
    x0, y0, x1, _ = CARD; y1 = min(CARD[3], y0 + 5.2 + 0.66 * n_esp)   # o cartão acompanha o tamanho da lista
    scatter(img, kind, c, seed, [(10.0, 0.8, 20.6, 13.4), (0.4, 12.9, 20.7, 14.2)], n=5, alpha=.50, smin=60, smax=120)
    scatter(img, kind, c, seed + 7, [(0.6, y1 + 0.5, 20.4, 27.4)], n=9, alpha=.55, smin=70, smax=150)
    card(img, x0, y0, x1, y1)
    footer_strip(img)
    return _save(img, path)


def contracapa(path, mark_png):
    img = gradient(((84, 56, 140), (24, 80, 120), (7, 56, 70)), glow=(0.15, 0.9), glow_a=0.30)
    field(img, W / 2, 5.0 * CM, 5.4 * CM, fill_a=26)
    for i, (k, a) in enumerate((("nem", "amber"), ("pla", "amber"), ("pro", "violet"))):
        scatter(img, k, PAL[a], 11 + i, [(0.5, 0.8, 20.5, 9.6)], n=3, alpha=.34, smin=50, smax=90)
    m = Image.open(mark_png).convert("RGBA"); sz = int(5.4 * CM); m = m.resize((sz, sz), Image.LANCZOS)
    img.alpha_composite(m, (int(W / 2 - sz / 2), int(5.0 * CM - sz / 2)))
    card(img, 1.9, 11.6, 19.1, 25.6)
    bars(img, int(H - 1.0 * CM), int(1.0 * CM))
    return _save(img, path)


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "."); out.mkdir(parents=True, exist_ok=True)
    mark = Path(__file__).resolve().parent.parent / "public/assets/brand/atlas-mark-512.png"
    capa(out / "capa.jpg", mark); contracapa(out / "contracapa.jpg", mark)
    for n, (a, k) in enumerate((("teal", "nem"), ("amber", "pla"), ("violet", "pro")), 1):
        capitulo(out / f"cap{n}.jpg", a, k, n)
    print("ok", out)
