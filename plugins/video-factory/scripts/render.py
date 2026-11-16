#!/usr/bin/env python3
"""Render a 1080x1920 Short from work/<slug>/{script.json,timing.json,voice.mp3,[music.mp3]}.
usage: render.py <slug>
Moving stills (Ken Burns), word-by-word captions, hook title, ducked music bed."""
import datetime as dt, os, subprocess, sys, textwrap
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from common import load, save, path, die

slug = sys.argv[1]
wd = lambda *a: path("work", slug, *a)
script = load(wd("script.json")) or die("no script.json")
LONG = script.get("format") == "long"  # long = horizontal YouTube video; anything else = vertical Short
W, H, FPS, Z = (1920, 1080, 30, 1.2) if LONG else (1080, 1920, 30, 1.2)
Q = 0.6 if LONG else 1.0  # display type is limited by height on a horizontal frame
timing = load(wd("timing.json")) or die("no timing.json; run tts.py")
draft = timing.get("draft", False)
FONT = next(f for f in ("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf") if os.path.exists(f))
VIVID = [((255, 45, 120), (140, 20, 200)), ((255, 140, 0), (235, 55, 45)), ((110, 60, 255), (30, 160, 255)),
         ((0, 185, 225), (0, 105, 200)), ((20, 170, 110), (10, 110, 150))]
S = (int(W * Z), int(H * Z))


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        die("ffmpeg failed:\n" + r.stderr[-1500:])


def backdrop(i):
    """Vivid two-colour gradient with soft translucent shapes, so no frame is a flat dark screen."""
    a, b = VIVID[i % len(VIVID)]
    g = Image.linear_gradient("L").rotate(25 * (1 if i % 2 else -1), expand=True).resize(S)
    bg = Image.composite(Image.new("RGB", S, b), Image.new("RGB", S, a), g)
    ov = Image.new("RGBA", S, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for k, (cx, cy, r) in enumerate([(0.12, 0.10, 0.30), (0.92, 0.30, 0.22), (0.20, 0.80, 0.26), (0.85, 0.92, 0.34)]):
        x, y, rr = cx * S[0], cy * S[1], r * S[0]
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 255, 255, 26 if (k + i) % 2 else 14))
    return Image.alpha_composite(bg.convert("RGBA"), ov)


def sticker(im, angle):
    """The picture as a tilted card with rounded corners, white border and a drop shadow."""
    fg = ImageOps.contain(im, (int(S[0] * 0.80), int(S[1] * 0.56)))
    if fg.width < S[0] * 0.6:
        fg = ImageOps.fit(im, (int(S[0] * 0.72), int(S[1] * 0.50)), centering=(0.5, 0.3))
    bw, r = 18, 54
    card = Image.new("RGBA", (fg.width + 2 * bw, fg.height + 2 * bw), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), r, fill="white")
    m = Image.new("L", fg.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, fg.width - 1, fg.height - 1), r - bw, fill=255)
    card.paste(fg, (bw, bw), m)
    card = card.rotate(angle, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", (card.width + 120, card.height + 120), (0, 0, 0, 0))
    sh.paste((0, 0, 0, 150), (60, 78), card.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(26)); sh.alpha_composite(card, (60, 60))
    return sh


cfg = load(path("config", "channel.json"), {})
DOC = cfg.get("style", "documental") == "documental"
FDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts")
DISP = os.path.join(FDIR, "BebasNeue-Regular.ttf") if os.path.exists(os.path.join(FDIR, "BebasNeue-Regular.ttf")) else FONT
TYPE = os.path.join(FDIR, "SpecialElite-Regular.ttf") if os.path.exists(os.path.join(FDIR, "SpecialElite-Regular.ttf")) else FONT
RED, PAPER, INK = (222, 44, 44), (236, 230, 214), (28, 26, 24)
KINDS = ("doc", "stat", "timeline", "card")


def fit(d, text_lines, font_path, size, maxw, minsize=70):
    f = ImageFont.truetype(font_path, size)
    while size > minsize and max(d.textlength(ln, font=f) for ln in text_lines) > maxw:
        size -= 8; f = ImageFont.truetype(font_path, size)
    return f, size


def wrap_px(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        if cur and d.textlength(cur + " " + w, font=f) > maxw:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + ([cur] if cur else [])


def dark(i):
    """Documentary backdrop: near-black with a soft spotlight and a few thin light rays."""
    g = Image.radial_gradient("L").resize(S)
    bg = Image.composite(Image.new("RGB", S, (10, 10, 12)), Image.new("RGB", S, (44, 44, 50)), g).convert("RGBA")
    ov = Image.new("RGBA", S, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for k in range(5):
        x = (0.13 + 0.19 * k + 0.07 * (i % 3)) * S[0]
        d.line((x, 0, x - S[0] * 0.35 * (1 if (i + k) % 2 else -1), S[1]), fill=(255, 255, 255, 10), width=3)
    return Image.alpha_composite(bg, ov)


def paste_rot(bg, layer, angle, cx, cy, shadow=True):
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    if shadow:
        sh = Image.new("RGBA", (layer.width + 160, layer.height + 160), (0, 0, 0, 0))
        sh.paste((0, 0, 0, 190), (80, 100), layer.split()[3]); sh = sh.filter(ImageFilter.GaussianBlur(34))
        bg.alpha_composite(sh, (int(cx - sh.width / 2), int(cy - sh.height / 2)))
    bg.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))


def g_photo(bg, sc, img, i, k):
    """A picture as an evidence photo: white frame, slight tilt, optional typewriter label."""
    im = ImageOps.exif_transpose(Image.open(wd(img))).convert("RGB")
    fg = ImageOps.contain(im, (int(S[0] * 0.70), int(S[1] * 0.46)))
    if fg.width < S[0] * 0.55:
        fg = ImageOps.fit(im, (int(S[0] * 0.70), int(S[1] * 0.46)), centering=(0.5, 0.3))
    fg = Image.blend(fg, ImageOps.grayscale(fg).convert("RGB"), 0.35)
    m, foot = 26, 120 if sc.get("label") else 26
    card = Image.new("RGBA", (fg.width + 2 * m, fg.height + m + foot), PAPER + (255,))
    card.paste(fg, (m, m))
    if sc.get("label"):
        d = ImageDraw.Draw(card); f, _ = fit(d, [sc["label"]], TYPE, 58, card.width - 80, 30)
        d.text((card.width / 2, fg.height + m + foot / 2), sc["label"], font=f, fill=INK, anchor="mm")
    paste_rot(bg, card, (2.5, -2.5, 1.5, -1.5)[(i + k) % 4], S[0] / 2, S[1] * 0.44)
    d = ImageDraw.Draw(bg); d.rectangle((S[0] * 0.5 - 70, S[1] * 0.44 - card.height / 2 - 34, S[0] * 0.5 + 70, S[1] * 0.44 - card.height / 2 + 30), fill=RED + (235,))


def g_card(bg, sc, prog):
    """Kinetic title: words appear build by build; the last build adds the red rule."""
    d = ImageDraw.Draw(bg); words = sc["card"].upper().split()
    full = textwrap.wrap(" ".join(words), 11) or [""]
    f, fs = fit(d, full, DISP, int((560 if len(sc["card"]) <= 3 else 400) * Q), S[0] * 0.74, 110)
    shown = max(1, min(len(words), int(len(words) * min(1.0, prog * 1.5) + 0.999)))  # reveal faster than the shots advance
    y = S[1] * 0.44 - len(full) * fs * 0.5; n = 0
    for ln in full:
        x = S[0] / 2 - d.textlength(ln, font=f) / 2
        for w in ln.split():
            n += 1
            if n <= shown:
                d.text((x, y), w, font=f, fill=RED if (n == len(words) and prog >= 1 and len(words) > 1) else "white")
            x += d.textlength(w + " ", font=f)
        y += fs * 1.0
    if prog >= 0.7:  # the rule shows one shot before the last word turns red, so the end card keeps changing
        d.rectangle((S[0] * 0.36, y + 24, S[0] * 0.64, y + 40), fill=RED)


def g_doc(bg, sc, prog):
    """A typed document: label, typewriter text appearing in steps, then a red marker on the key phrase."""
    doc = sc["doc"]; w, h = int(S[0] * 0.72), int(S[1] * 0.42)
    card = Image.new("RGBA", (w, h), PAPER + (255,)); d = ImageDraw.Draw(card)
    fl, _ = fit(d, [doc.get("label", "").upper() or " "], TYPE, 46, w - 150, 24); d.text((70, 64), doc.get("label", "").upper(), font=fl, fill=(110, 104, 96))
    d.line((70, 132, w - 70, 132), fill=(150, 144, 134), width=3)
    size = 96; f = ImageFont.truetype(TYPE, size); lines = wrap_px(d, doc["text"], f, w - 140)
    while size > 54 and len(lines) * size * 1.35 > h - 240:
        size -= 6; f = ImageFont.truetype(TYPE, size); lines = wrap_px(d, doc["text"], f, w - 140)
    total = sum(len(x) for x in lines); left = max(3, round(total * min(1, prog * 1.25))); y = 180
    hl = (doc.get("highlight") or "").lower().strip(" .,;:!?¡¿")
    hs = " ".join(lines).lower().find(hl) if hl else -1  # the marker may span several lines: one bar per line
    he = hs + len(hl); off = 0
    for ln in lines:
        part = ln[:left]; left -= len(part)
        a, b = max(hs - off, 0), min(he - off, len(ln))
        if hs >= 0 and prog >= 1 and a < b:
            x0 = 70 + d.textlength(ln[:a], font=f); x1 = 70 + d.textlength(ln[:b], font=f)
            d.rectangle((x0 - 8, y - 6, x1 + 8, y + size * 1.05), fill=(230, 60, 60, 255))
        off += len(ln) + 1
        d.text((70, y), part, font=f, fill=INK); y += size * 1.35
        if left <= 0:
            break
    paste_rot(bg, card, -2.0, S[0] / 2, S[1] * 0.44)


def g_stat(bg, sc, prog):
    """A huge figure with a small heading; the last build turns it red and stamps the label."""
    st = sc["stat"]; d = ImageDraw.Draw(bg); cy = S[1] * 0.43
    if st.get("over"):
        fo, _ = fit(d, [st["over"].upper()], TYPE, 60, S[0] * 0.74, 34)
        d.text((S[0] / 2, cy - 330 * Q), st["over"].upper(), font=fo, fill=(200, 200, 205), anchor="mm")
    f, fs = fit(d, [st["value"].upper()], DISP, int(620 * Q), S[0] * 0.76, 160)
    d.text((S[0] / 2, cy), st["value"].upper(), font=f, fill=RED if prog >= 1 else "white", anchor="mm")
    if st.get("label") and prog >= 0.6:
        fl, ls = fit(d, [st["label"].upper()], DISP, int(120 * Q) + 20, S[0] * 0.66, 60)
        tw = d.textlength(st["label"].upper(), font=fl); y = cy + fs * 0.5 + 70 * Q
        lab = Image.new("RGBA", (int(tw) + 90, ls + 50), (0, 0, 0, 0)); dl = ImageDraw.Draw(lab)
        dl.rectangle((0, 0, lab.width - 1, lab.height - 1), fill=RED + (255,)); dl.text((lab.width / 2, lab.height / 2 + 4), st["label"].upper(), font=fl, fill="white", anchor="mm")
        paste_rot(bg, lab, -3, S[0] / 2, y + lab.height / 2, shadow=False)


def g_timeline(bg, sc, prog):
    """Two moments joined by a line that grows; the last build shows the distance between them."""
    tl = sc["timeline"]; d = ImageDraw.Draw(bg); cy = S[1] * 0.47; x0, x1 = S[0] * 0.24, S[0] * 0.76
    ft, _ = fit(d, [tl["from"].upper(), tl["to"].upper()], DISP, int(190 * Q) + 20, S[0] * 0.26, 80)
    d.line((x0, cy, x1, cy), fill=(90, 90, 96), width=6)
    xe = x0 + (x1 - x0) * min(1, prog * 1.2)
    d.line((x0, cy, xe, cy), fill=RED, width=14)
    d.line((x0, cy - 46, x0, cy + 46), fill="white", width=8); d.text((x0, cy + 70), tl["from"].upper(), font=ft, fill="white", anchor="ma")
    if xe >= x1:
        d.line((x1, cy - 46, x1, cy + 46), fill="white", width=8); d.text((x1, cy + 70), tl["to"].upper(), font=ft, fill="white", anchor="ma")
    if tl.get("label") and prog >= 1:
        fl, _ = fit(d, [tl["label"].upper()], DISP, int(300 * Q), S[0] * 0.74, 110)
        d.text((S[0] / 2, cy - 250 * Q), tl["label"].upper(), font=fl, fill=RED, anchor="mm")


def still(i, sc, img=None, k=0, ns=1):
    prog = (k + 1) / ns
    if DOC:
        bg = dark(i + k)
        if img:
            g_photo(bg, sc, img, i, k)
        elif sc.get("doc"):
            g_doc(bg, sc, prog)
        elif sc.get("stat"):
            g_stat(bg, sc, prog)
        elif sc.get("timeline"):
            g_timeline(bg, sc, prog)
        else:
            g_card(bg, sc, prog)
    else:
        bg = backdrop(i + k)
        if img:
            im = ImageOps.exif_transpose(Image.open(wd(img))).convert("RGB")
            st = sticker(im, (2.5, -2.5, 1.5, -1.5)[(i + k) % 4])
            bg.alpha_composite(st, ((S[0] - st.width) // 2, int(S[1] * 0.44) - st.height // 2))
        else:
            d = ImageDraw.Draw(bg)
            txt = sc.get("card") or (sc.get("stat") or {}).get("value") or (sc.get("timeline") or {}).get("label") or (sc.get("doc") or {}).get("highlight") or ""
            lines = textwrap.wrap(txt.upper(), 12) or [""]
            f, fs = fit(d, lines, FONT, 520 if len(txt) <= 3 else 320, S[0] * 0.74, 90)
            y = int(S[1] * 0.44) - len(lines) * fs * 0.6
            for ln in lines:
                d.text((S[0] / 2, y), ln, font=f, fill="white", anchor="ma", stroke_width=8, stroke_fill=(20, 20, 30)); y += fs * 1.15
            d.rounded_rectangle((S[0] * 0.35, y + 20, S[0] * 0.65, y + 46), 13, fill=(255, 212, 0))
    p = wd("render", f"s{i:02d}_{k}.png"); bg.convert("RGB").save(p); return p


def ts(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


CAPFONT, CAPSIZE, HOOKSIZE = ("Bebas Neue", 118, 86) if DOC else ("Inter ExtraBold", 96, 70)
CAPSIZE, HOOKSIZE, CAPMV, HOOKMV = (int(CAPSIZE * 0.72), int(HOOKSIZE * 0.72), 64, 44) if LONG else (CAPSIZE, HOOKSIZE, 470, 210)
HOOKFG, HOOKBG = ("&H00FFFFFF", "&H002C2CDE") if DOC else ("&H00000000", "&H0000D4FF")


def captions():
    ws, chunks, cur = timing["words"], [], []
    for i, w in enumerate(ws):
        cur.append(w)
        last = i == len(ws) - 1
        if (last or len(cur) == 3 or sum(len(x["w"]) for x in cur) >= 14 or w["w"][-1] in ".,;:?!…"
                or ws[i + 1]["scene"] != w["scene"] or ws[i + 1]["s"] - w["e"] > 0.35):
            chunks.append(cur); cur = []
    ev = []
    for ci, ch in enumerate(chunks):
        end = min(ch[-1]["e"] + 0.25, chunks[ci + 1][0]["s"]) if ci + 1 < len(chunks) else ch[-1]["e"] + 0.3
        for k, w in enumerate(ch):
            a, b = w["s"], (ch[k + 1]["s"] if k + 1 < len(ch) else end)
            hl = "&H2C2CDE&" if DOC else ("&H00D4FF&", "&H7CFF4D&")[ci % 2]  # red, or yellow / green (BGR)
            txt = " ".join(("{\\c" + hl + "}" + x["w"].upper() + "{\\c&HFFFFFF&}") if j == k else x["w"].upper()
                           for j, x in enumerate(ch))
            sc0 = 80 if k == 0 else 108
            pop = "{\\frz%d\\fscx%d\\fscy%d\\t(0,90,\\fscx100\\fscy100)}" % ((2, -2)[ci % 2], sc0, sc0)
            ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Cap,,0,0,0,,{pop}{txt}")
    hook_end = min(timing["scenes"][0]["end"], 3.5)
    ev.append(f"Dialogue: 2,{ts(0)},{ts(hook_end)},Hook,,0,0,0,,{{\\fad(0,200)}}{script['hook_text'].upper()}")
    if draft:
        ev.append(f"Dialogue: 3,{ts(0)},{ts(timing['duration'])},Draft,,0,0,0,,BORRADOR · SIN VOZ · NO PUBLICAR")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{CAPFONT},{CAPSIZE},&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,7,3,2,70,70,{CAPMV},1
Style: Hook,{CAPFONT},{HOOKSIZE},{HOOKFG},{HOOKFG},{HOOKBG},{HOOKBG},-1,0,0,0,100,100,0,0,3,18,0,8,90,90,{HOOKMV},1
Style: Draft,Inter,34,&H00FFFFFF,&H00FFFFFF,&H000000C8,&H000000C8,-1,0,0,0,100,100,0,0,3,8,0,8,40,40,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    p = wd("render", "captions.ass"); open(p, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n"); return p


# every scene is cut into ~2 s shots, each with its own framing and a small zoom "kick" on the cut
segs, cuts, first_still = [], [], None
for i, (sc, tm) in enumerate(zip(script["scenes"], timing["scenes"])):
    n = max(int(round((tm["end"] - tm["start"]) * FPS)), 1)
    imgs = sc.get("images") or ([sc["image"]] if sc.get("image") else [])
    ns = max(1, min(4, round(n / FPS / 2.1)))
    for k in range(ns):
        nk = n // ns + (n % ns if k == ns - 1 else 0)
        img = imgs[k % len(imgs)] if imgs else None
        kick = "0.07*exp(-on/3)"
        if img and DOC:  # gentle moves: the framed photo must never leave the frame
            z, fx, fy = [(f"1.0+0.10*on/{nk}+0.04*exp(-on/3)", "0.5", "0.42"), (f"1.08+0.04*exp(-on/3)", f"0.38+0.24*on/{nk}", "0.42"),
                         (f"1.12-0.10*on/{nk}+0.04*exp(-on/3)", "0.5", "0.44"), (f"1.04+0.06*on/{nk}+0.04*exp(-on/3)", f"0.62-0.24*on/{nk}", "0.42")][(i + k) % 4]
        elif img:
            z, fx, fy = [(f"1.02+0.16*on/{nk}+{kick}", "0.5", "0.42"), (f"1.20+{kick}", f"0.12+0.76*on/{nk}", "0.40"),
                         (f"1.26-0.18*on/{nk}+{kick}", "0.5", "0.44"), (f"1.14+0.10*on/{nk}+{kick}", f"0.88-0.76*on/{nk}", "0.38")][(i + k) % 4]
        else:
            z, fx, fy = [(f"1.0+0.10*on/{nk}+{kick}", "0.5", "0.42"), (f"1.12-0.10*on/{nk}+{kick}", "0.5", "0.42")][k % 2]
        src = still(i, sc, img, k if (len(imgs) > 1 or not img) else 0, ns)
        first_still = first_still or src
        out = wd("render", f"s{i:02d}_{k}.mp4")
        run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-loop", "1", "-i", src, "-frames:v", str(nk),
             "-vf", f"scale={S[0]*2}:-2,zoompan=z='{z}':x='(iw-iw/zoom)*({fx})':y='(ih-ih/zoom)*({fy})':d=1:s={W}x{H}:fps={FPS},format=yuv420p",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", out])
        segs.append(out)
        cuts.append((tm["start"] + (n // ns) * k / FPS, k == 0, not img))


def sfx_track(dur):
    """Synthesised whoosh on every scene change, soft tick on inner cuts, pop on text cards. No samples used."""
    import numpy as np, wave
    sr = 44100; buf = np.zeros(int(dur * sr) + sr, dtype=np.float32); rng = np.random.default_rng(7)
    def add(t0, x):
        a = int(max(t0, 0) * sr); x = x[:len(buf) - a]; buf[a:a + len(x)] += x
    nw = int(0.32 * sr); env = np.sin(np.linspace(0, np.pi, nw)) ** 2
    noise = np.cumsum(rng.standard_normal(nw)); noise -= np.linspace(noise[0], noise[-1], nw); noise /= np.abs(noise).max()
    hiss = rng.standard_normal(nw) * np.linspace(0.1, 1, nw)
    whoosh = ((0.5 * noise + 0.5 * hiss / np.abs(hiss).max()) * env * 0.30).astype(np.float32)
    nt = int(0.05 * sr); tick = (np.sin(2 * np.pi * 1400 * np.arange(nt) / sr) * np.exp(-np.arange(nt) / (0.008 * sr)) * 0.10).astype(np.float32)
    npop = int(0.16 * sr); tt = np.arange(npop) / sr
    pop = (np.sin(2 * np.pi * (520 + 900 * tt / 0.16) * tt) * np.exp(-tt / 0.05) * 0.28).astype(np.float32)
    for t0, scene_start, is_card in cuts:
        if t0 < 0.05:
            continue
        if scene_start:
            add(t0 - 0.16, whoosh)
            if is_card:
                add(t0 + 0.02, pop)
        else:
            add(t0, tick)
    p = wd("render", "sfx.wav")
    with wave.open(p, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(buf[:int(dur * sr)], -1, 1) * 32767).astype("<i2").tobytes())
    return p


lst = wd("render", "concat.txt")
open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))

day = dt.date.today().isoformat()
odir = ("output", "drafts", f"{day}-{slug}") if draft else ("output", f"{day}-{slug}")
video = path(*odir, "video.mp4")
ass = captions().replace("\\", "/").replace(":", "\\:")
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wd("voice.mp3")]
music = wd("music.mp3"); dur = timing["duration"]
if draft:
    af = "[1:a]anull[a]"
elif os.path.exists(music):
    cmd += ["-stream_loop", "-1", "-i", music, "-i", sfx_track(dur)]
    af = ("[1:a]asplit=2[v1][v2];[2:a]volume=0.5[m];[m][v1]sidechaincompress=threshold=0.03:ratio=10:attack=20:release=400[md];"
          "[v2][md][3:a]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
else:
    cmd += ["-i", sfx_track(dur)]
    af = "[1:a][2:a]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]"
vf = f"color=c={'0xDE2C2C' if DOC else '0xFFD400'}:s={W}x14:r={FPS}[bar];[0:v][bar]overlay=x='-{W}+{W}*t/{dur:.2f}':y={H - 14}:shortest=1[vb];[vb]ass='{ass}':fontsdir='{FDIR}'[v]"
cmd += ["-filter_complex", f"{vf};{af}", "-map", "[v]", "-map", "[a]", "-t", f"{dur:.2f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", video]
run(cmd)

# thumbnail: first still + hook
th = Image.open(first_still).resize((W, H)); d = ImageDraw.Draw(th)
f = ImageFont.truetype(FONT, 110); y = int(H * 0.615)
for ln in textwrap.wrap(script["hook_text"].upper(), 14):
    d.text((W / 2, y), ln, font=f, fill="white" if DOC else (255, 212, 0), anchor="ma", stroke_width=10, stroke_fill="black"); y += 128
th.convert("RGB").save(path(*odir, "thumbnail.jpg"), quality=90)

research = load(wd("research.json"), {"images": []})
used = {x for sc in script["scenes"] for x in (sc.get("images") or [sc.get("image")])}
credits = [f"{im['title']} — {im['author']} ({im['license']}) {im['source']}" for im in research["images"] if im["file"] in used]
# chapters: the script gives estimated times; the real ones come from the narration timing of the scene each chapter opens
chap = []
if script.get("chapters"):
    wps, cum, est = cfg.get("words_per_second", 2.6), 0, []
    for sc in script["scenes"]:
        est.append(cum / wps); cum += len(sc["text"].split())
    for c in script["chapters"]:
        parts = c["t"].split(":"); t0 = int(parts[-2]) * 60 + int(parts[-1])
        i = min(range(len(est)), key=lambda k: abs(est[k] - t0)); s = timing["scenes"][i]["start"]
        chap.append({"t": f"{int(s // 60):02d}:{int(s % 60):02d}", "title": c["title"]})
    chap[0]["t"] = "00:00"
desc = script["description"].strip()
if chap:
    desc += "\n\nCapítulos:\n" + "\n".join(f"{c['t']} {c['title']}" for c in chap)
desc += "\n\nFuentes:\n" + "\n".join(script["sources"])
if credits:
    desc += "\n\nImágenes (Wikimedia Commons):\n" + "\n".join(credits)
desc += "\n\nNarración generada con voz sintética (ElevenLabs).\n\n" + " ".join(script["hashtags"])
save(path(*odir, "metadata.json"), {"format": "long" if LONG else "short", "chapters": chap, "title": script["title"], "description": desc, "hashtags": script["hashtags"],
                                    "duration": timing["duration"], "draft": draft, "trend": script["trend"],
                                    "synthetic_voice_disclosure": True, "image_credits": credits})
if not LONG and not draft:  # TikTok takes the same vertical file; only the caption differs
    import shutil
    shutil.copy(video, path(*odir, "tiktok.mp4"))
    tags = " ".join(h for h in script["hashtags"] if h.lower() != "#shorts")
    open(path(*odir, "tiktok.txt"), "w", encoding="utf-8").write(f"{script['title']}\n\n{script['description'].strip()}\n\n{tags} #fyp #parati\n")
print(f"{'DRAFT ' if draft else ''}rendered {video} ({timing['duration']:.1f}s)")
