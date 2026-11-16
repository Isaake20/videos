#!/usr/bin/env python3
"""Render a 1080x1920 Short from work/<slug>/{script.json,timing.json,voice.mp3,[music.mp3]}.
usage: render.py <slug>
Moving stills (Ken Burns), word-by-word captions, hook title, ducked music bed."""
import datetime as dt, os, subprocess, sys, textwrap
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from common import load, save, path, die

slug = sys.argv[1]
W, H, FPS, Z = 1080, 1920, 30, 1.2
wd = lambda *a: path("work", slug, *a)
script = load(wd("script.json")) or die("no script.json")
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


def still(i, sc, img=None, k=0):
    bg = backdrop(i + k)
    if img:
        im = ImageOps.exif_transpose(Image.open(wd(img))).convert("RGB")
        st = sticker(im, (2.5, -2.5, 1.5, -1.5)[(i + k) % 4])
        bg.alpha_composite(st, ((S[0] - st.width) // 2, int(S[1] * 0.44) - st.height // 2))
    else:
        d = ImageDraw.Draw(bg)
        lines = textwrap.wrap(sc["card"].upper(), 12)
        fs = 520 if len(sc["card"]) <= 3 else 320
        f = ImageFont.truetype(FONT, fs)
        while fs > 90 and max(d.textlength(ln, font=f) for ln in lines) > S[0] * 0.74:
            fs -= 10; f = ImageFont.truetype(FONT, fs)
        y = int(S[1] * 0.44) - len(lines) * fs * 0.6
        for ln in lines:
            d.text((S[0] / 2 + 8, y + 10), ln, font=f, fill=(0, 0, 0, 140), anchor="ma")
            d.text((S[0] / 2, y), ln, font=f, fill="white", anchor="ma", stroke_width=8, stroke_fill=(20, 20, 30))
            y += fs * 1.15
        wbar = int(S[0] * 0.30)
        d.rounded_rectangle(((S[0] - wbar) // 2, y + 20, (S[0] + wbar) // 2, y + 46), 13, fill=(255, 212, 0))
    p = wd("render", f"s{i:02d}_{k}.png"); bg.convert("RGB").save(p); return p


def ts(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


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
            hl = ("&H00D4FF&", "&H7CFF4D&")[ci % 2]  # yellow / green highlight (BGR)
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
Style: Cap,Inter ExtraBold,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,7,3,2,70,70,470,1
Style: Hook,Inter ExtraBold,70,&H00000000,&H00000000,&H0000D4FF,&H0000D4FF,-1,0,0,0,100,100,0,0,3,18,0,8,90,90,210,1
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
        if img:
            z, fx, fy = [(f"1.02+0.16*on/{nk}+{kick}", "0.5", "0.42"), (f"1.20+{kick}", f"0.12+0.76*on/{nk}", "0.40"),
                         (f"1.26-0.18*on/{nk}+{kick}", "0.5", "0.44"), (f"1.14+0.10*on/{nk}+{kick}", f"0.88-0.76*on/{nk}", "0.38")][(i + k) % 4]
        else:
            z, fx, fy = [(f"1.0+0.10*on/{nk}+{kick}", "0.5", "0.42"), (f"1.12-0.10*on/{nk}+{kick}", "0.5", "0.42")][k % 2]
        src = still(i, sc, img, k if (len(imgs) > 1 or not img) else 0)
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
vf = f"color=c=0xFFD400:s={W}x14:r={FPS}[bar];[0:v][bar]overlay=x='-{W}+{W}*t/{dur:.2f}':y={H - 14}:shortest=1[vb];[vb]ass='{ass}'[v]"
cmd += ["-filter_complex", f"{vf};{af}", "-map", "[v]", "-map", "[a]", "-t", f"{dur:.2f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", video]
run(cmd)

# thumbnail: first still + hook
th = Image.open(first_still).resize((W, H)); d = ImageDraw.Draw(th)
f = ImageFont.truetype(FONT, 110); y = 1180
for ln in textwrap.wrap(script["hook_text"].upper(), 14):
    d.text((W / 2, y), ln, font=f, fill=(255, 212, 0), anchor="ma", stroke_width=10, stroke_fill="black"); y += 128
th.convert("RGB").save(path(*odir, "thumbnail.jpg"), quality=90)

research = load(wd("research.json"), {"images": []})
used = {x for sc in script["scenes"] for x in (sc.get("images") or [sc.get("image")])}
credits = [f"{im['title']} — {im['author']} ({im['license']}) {im['source']}" for im in research["images"] if im["file"] in used]
desc = script["description"].strip() + "\n\nFuentes:\n" + "\n".join(script["sources"])
if credits:
    desc += "\n\nImágenes (Wikimedia Commons):\n" + "\n".join(credits)
desc += "\n\nNarración generada con voz sintética (ElevenLabs).\n\n" + " ".join(script["hashtags"])
save(path(*odir, "metadata.json"), {"title": script["title"], "description": desc, "hashtags": script["hashtags"],
                                    "duration": timing["duration"], "draft": draft, "trend": script["trend"],
                                    "synthetic_voice_disclosure": True, "image_credits": credits})
print(f"{'DRAFT ' if draft else ''}rendered {video} ({timing['duration']:.1f}s)")
