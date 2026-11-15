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
PALETTE = [((18, 24, 58), (94, 38, 140)), ((8, 44, 62), (16, 122, 110)), ((60, 20, 28), (170, 70, 30))]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        die("ffmpeg failed:\n" + r.stderr[-1500:])


def gradient(i):
    a, b = PALETTE[i % len(PALETTE)]
    g = Image.linear_gradient("L").resize((int(W * Z), int(H * Z)))
    return Image.composite(Image.new("RGB", g.size, b), Image.new("RGB", g.size, a), g)


def still(i, sc):
    size = (int(W * Z), int(H * Z))
    if sc.get("image"):
        im = ImageOps.exif_transpose(Image.open(wd(sc["image"]))).convert("RGB")
        bg = ImageOps.fit(im, size).filter(ImageFilter.GaussianBlur(40)).point(lambda v: v * 0.45)
        fg = ImageOps.contain(im, (size[0], int(size[1] * 0.62)))
        if fg.width < size[0] * 0.8:  # portrait/small image: let it fill more of the frame
            fg = ImageOps.fit(im, (size[0], int(size[1] * 0.62)), centering=(0.5, 0.3))
        bg.paste(fg, ((size[0] - fg.width) // 2, int(size[1] * 0.40) - fg.height // 2))
    else:
        bg = gradient(i)
        d = ImageDraw.Draw(bg)
        lines = textwrap.wrap(sc["card"].upper(), 12)
        fs = 210 if max(map(len, lines)) <= 8 else 150
        f = ImageFont.truetype(FONT, fs)
        y = int(size[1] * 0.40) - len(lines) * fs * 0.6
        for ln in lines:
            d.text((size[0] / 2, y), ln, font=f, fill="white", anchor="ma", stroke_width=6, stroke_fill=(0, 0, 0))
            y += fs * 1.15
    p = wd("render", f"s{i:02d}.png"); bg.save(p); return p


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
            txt = " ".join(("{\\c&H00D4FF&}" + x["w"].upper() + "{\\c&HFFFFFF&}") if j == k else x["w"].upper()
                           for j, x in enumerate(ch))
            pop = "{\\fscx88\\fscy88\\t(0,90,\\fscx100\\fscy100)}" if k == 0 else ""
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


segs = []
for i, (sc, tm) in enumerate(zip(script["scenes"], timing["scenes"])):
    n = max(int(round((tm["end"] - tm["start"]) * FPS)), 1)
    zexpr = f"1+{Z - 1:.2f}*on/{n}" if i % 2 == 0 else f"{Z:.2f}-{Z - 1:.2f}*on/{n}"
    out = wd("render", f"s{i:02d}.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-loop", "1", "-i", still(i, sc), "-frames:v", str(n),
         "-vf", f"scale={int(W*Z*2)}:-2,zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},format=yuv420p",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", out])
    segs.append(out)
lst = wd("render", "concat.txt")
open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))

day = dt.date.today().isoformat()
odir = ("output", "drafts", f"{day}-{slug}") if draft else ("output", f"{day}-{slug}")
video = path(*odir, "video.mp4")
ass = captions().replace("\\", "/").replace(":", "\\:")
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wd("voice.mp3")]
music = wd("music.mp3")
if os.path.exists(music) and not draft:
    cmd += ["-stream_loop", "-1", "-i", music]
    af = ("[1:a]asplit=2[v1][v2];[2:a]volume=0.5[m];[m][v1]sidechaincompress=threshold=0.03:ratio=10:attack=20:release=400[md];"
          "[v2][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
else:
    af = "[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[a]" if not draft else "[1:a]anull[a]"
cmd += ["-filter_complex", f"[0:v]ass='{ass}'[v];{af}", "-map", "[v]", "-map", "[a]", "-t", f"{timing['duration']:.2f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", video]
run(cmd)

# thumbnail: first still + hook
th = Image.open(wd("render", "s00.png")).resize((W, H)); d = ImageDraw.Draw(th)
f = ImageFont.truetype(FONT, 110); y = 1180
for ln in textwrap.wrap(script["hook_text"].upper(), 14):
    d.text((W / 2, y), ln, font=f, fill=(255, 212, 0), anchor="ma", stroke_width=10, stroke_fill="black"); y += 128
th.convert("RGB").save(path(*odir, "thumbnail.jpg"), quality=90)

research = load(wd("research.json"), {"images": []})
used = {sc.get("image") for sc in script["scenes"]}
credits = [f"{im['title']} — {im['author']} ({im['license']}) {im['source']}" for im in research["images"] if im["file"] in used]
desc = script["description"].strip() + "\n\nFuentes:\n" + "\n".join(script["sources"])
if credits:
    desc += "\n\nImágenes (Wikimedia Commons):\n" + "\n".join(credits)
desc += "\n\nNarración generada con voz sintética (ElevenLabs).\n\n" + " ".join(script["hashtags"])
save(path(*odir, "metadata.json"), {"title": script["title"], "description": desc, "hashtags": script["hashtags"],
                                    "duration": timing["duration"], "draft": draft, "trend": script["trend"],
                                    "synthetic_voice_disclosure": True, "image_credits": credits})
print(f"{'DRAFT ' if draft else ''}rendered {video} ({timing['duration']:.1f}s)")
