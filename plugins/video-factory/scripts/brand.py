#!/usr/bin/env python3
"""Channel branding kit from config/channel.json: canal/logo.png (800x800), canal/banner.png (2560x1440),
canal/descripcion.txt. All art is drawn here (Bebas Neue + Special Elite, both bundled and free to use). usage: brand.py"""
import os, textwrap
from PIL import Image, ImageDraw, ImageFont
from common import load, path, ROOT

cfg = load(path("config", "channel.json"), {})
name = cfg.get("channel_name", "Canal").upper(); handle = cfg.get("channel_handle", "")
F = os.path.join(ROOT, "plugins", "video-factory", "assets", "fonts")
DISP, TYPE = os.path.join(F, "BebasNeue-Regular.ttf"), os.path.join(F, "SpecialElite-Regular.ttf")
RED, INK = (222, 44, 44), (10, 10, 12)
out = lambda n: path("canal", n)


def backdrop(w, h, rays=True):
    g = Image.radial_gradient("L").resize((w, h))
    bg = Image.composite(Image.new("RGB", (w, h), INK), Image.new("RGB", (w, h), (46, 46, 52)), g).convert("RGBA")
    if rays:
        ov = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for k in range(9):
            x = (0.05 + 0.12 * k) * w
            d.line((x, 0, x - w * 0.22 * (1 if k % 2 else -1), h), fill=(255, 255, 255, 9), width=4)
        bg = Image.alpha_composite(bg, ov)
    return bg


def centered(d, xy, text, font, fill):
    """Draw text centred on xy using its real ink box (Bebas Neue sits high in its line box)."""
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=font)
    d.text((xy[0] - (x0 + x1) / 2, xy[1] - (y0 + y1) / 2), text, font=font, fill=fill)


# ---- logo: a red evidence stamp with the initials -------------------------------------------------------
S = 800
logo = backdrop(S, S, rays=False); d = ImageDraw.Draw(logo)
initials = "".join(w[0] for w in name.split() if w)[:2]
d.ellipse((38, 38, S - 38, S - 38), outline=RED, width=10)
d.ellipse((92, 92, S - 92, S - 92), fill=RED)
centered(d, (S / 2, S / 2 + 4), initials, ImageFont.truetype(DISP, 430), "white")
d.rectangle((S / 2 - 120, S - 205, S / 2 + 120, S - 190), fill="white")
logo.convert("RGB").save(out("logo.png"))

# ---- banner: 2560x1440, the title lives inside the 1546x423 safe area that every device shows -----------
W, H = 2560, 1440
ban = backdrop(W, H); d = ImageDraw.Draw(ban, "RGBA")
for cx, cy, ang in ((300, 470, 6), (2260, 980, -7)):  # faint evidence cards at the sides (outside the safe area)
    card = Image.new("RGBA", (330, 420), (236, 230, 214, 46)); dc = ImageDraw.Draw(card)
    dc.rectangle((120, 0, 210, 34), fill=RED + (90,))
    for i in range(7):
        dc.line((34, 90 + i * 46, 296 - (i % 3) * 40, 90 + i * 46), fill=(10, 10, 12, 70), width=6)
    card = card.rotate(ang, expand=True, resample=Image.BICUBIC)
    ban.alpha_composite(card, (cx - card.width // 2, cy - card.height // 2))
words = name.split(); f = ImageFont.truetype(DISP, 310)
first, last = " ".join(words[:-1]) if len(words) > 1 else name, words[-1] if len(words) > 1 else ""
w1 = d.textlength(first + " ", font=f); w2 = d.textlength(last, font=f); x = (W - (w1 + w2)) / 2; ty = 520
d.text((x, ty), first + " ", font=f, fill="white"); d.text((x + w1, ty), last, font=f, fill=RED)
d.rectangle((W / 2 - 150, 845, W / 2 + 150, 859), fill=RED)
tag = "LA CIENCIA Y LA HISTORIA DETRÁS DE LO QUE ES TENDENCIA"
ft = ImageFont.truetype(TYPE, 44)
d.text((W / 2, 892), tag, font=ft, fill=(210, 210, 214), anchor="ma")
ban.convert("RGB").save(out("banner.png"))

# ---- channel description --------------------------------------------------------------------------------
desc = f"""{cfg.get('channel_name', 'Canal')}: la ciencia, la tecnología y la historia que hay detrás de lo que es tendencia, contadas con pruebas.

Cada vídeo parte de algo que no encaja, enseña los documentos, las cifras y las fuentes, y llega a una conclusión que puedes comprobar tú.

🎬 Un Short cada día y un vídeo largo tres veces por semana.
🔎 Todo dato lleva fuente. Las imágenes son de Wikimedia Commons con licencia libre y se acreditan en la descripción de cada vídeo.
🤖 Transparencia: la narración usa voz sintética y los guiones se preparan con ayuda de inteligencia artificial, con una revisión de datos antes de publicar.

¿Qué caso quieres que investiguemos? Cuéntalo en los comentarios.
"""
open(out("descripcion.txt"), "w", encoding="utf-8").write(desc)
print("canal/logo.png, canal/banner.png, canal/descripcion.txt")
