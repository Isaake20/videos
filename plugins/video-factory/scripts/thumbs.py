#!/usr/bin/env python3
"""Thumbnail desk: make up to 10 vertical thumbnail variants and pick one.

usage:
  thumbs.py <slug> "TEXTO A" "TEXTO B" ...   variants (image x text x style) -> work/<slug>/thumbs/NN.jpg + sheet.jpg
  thumbs.py <slug> --pick N                  copy variant N to the newest output/*-<slug>/thumbnail.jpg

Texts: 1-3 words each, different words from the title (see the yt-package skill)."""
import glob, os, shutil, sys, textwrap
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from common import load, save, path, die, ROOT

slug, args = sys.argv[1], sys.argv[2:]
W, H = 1080, 1920
wd = lambda *a: path("work", slug, *a)
FONT = next(f for f in ("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf") if os.path.exists(f))
STYLES = [dict(fill="white", stroke="black", y=0.66, band=None),  # documentary look: dark, white and red
          dict(fill="white", stroke=None, y=0.70, band=(222, 44, 44)),
          dict(fill=(222, 44, 44), stroke="black", y=0.12, band=None),
          dict(fill="black", stroke=None, y=0.70, band=(236, 230, 214))]

if args[:1] == ["--pick"]:
    n = int(args[1]); src = wd("thumbs", f"{n:02d}.jpg")
    os.path.exists(src) or die(f"no variant {n}")
    outs = sorted(glob.glob(os.path.join(ROOT, "output", f"*-{slug}"))) or die("no finished video for this slug in output/")
    shutil.copy(src, os.path.join(outs[-1], "thumbnail.jpg"))
    meta = load(wd("thumbs", "variants.json"), {}); meta["picked"] = n; save(wd("thumbs", "variants.json"), meta)
    print(f"picked {n} -> {outs[-1]}/thumbnail.jpg"); sys.exit(0)

texts = [t for t in args if t.strip()] or die(__doc__)
script = load(wd("script.json")) or die("no script.json")
images = [x for sc in script["scenes"] for x in (sc.get("images") or ([sc["image"]] if sc.get("image") else []))] or die("the script has no images")
for t in texts:
    if len(t.split()) > 3:
        die(f'"{t}": three words maximum on a thumbnail')


def base(img):
    im = ImageOps.exif_transpose(Image.open(wd(img))).convert("RGB")
    bg = ImageOps.fit(im, (W, H)).filter(ImageFilter.GaussianBlur(30)).point(lambda v: v * 0.28)
    fg = ImageOps.contain(im, (W, int(H * 0.55)))
    if fg.width < W * 0.8:
        fg = ImageOps.fit(im, (W, int(H * 0.55)), centering=(0.5, 0.3))
    bg.paste(fg, ((W - fg.width) // 2, int(H * 0.42) - fg.height // 2))
    return bg


def draw(im, text, st):
    d = ImageDraw.Draw(im); lines = textwrap.wrap(text.upper(), 10)
    fs = 230 if max(map(len, lines)) <= 7 else 170
    f = ImageFont.truetype(FONT, fs)
    while fs > 80 and max(d.textlength(ln, font=f) for ln in lines) > W - 200:  # keep a safe margin on both sides
        fs -= 10; f = ImageFont.truetype(FONT, fs)
    y = int(H * st["y"])
    for ln in lines:
        if st["band"]:
            x0, y0, x1, y1 = d.textbbox((W / 2, y), ln, font=f, anchor="ma")
            d.rounded_rectangle((x0 - 36, y0 - 24, x1 + 36, y1 + 24), 28, fill=st["band"])
        d.text((W / 2, y), ln, font=f, fill=st["fill"], anchor="ma",
               stroke_width=12 if st["stroke"] else 0, stroke_fill=st["stroke"])
        y += int(fs * 1.2)
    return im


variants, n = [], 0
while n < 10 and n < len(images) * len(texts) * len(STYLES):
    img, text, st = images[n % len(images)], texts[n % len(texts)], n % len(STYLES)
    n += 1
    draw(base(img), text, STYLES[st]).save(wd("thumbs", f"{n:02d}.jpg"), quality=90)
    variants.append({"n": n, "image": img, "text": text, "style": st})
sheet = Image.new("RGB", (5 * 270, ((n + 4) // 5) * 480), "black")
for v in variants:
    t = Image.open(wd("thumbs", f"{v['n']:02d}.jpg")).resize((270, 480))
    ImageDraw.Draw(t).text((8, 6), str(v["n"]), font=ImageFont.truetype(FONT, 40), fill="white", stroke_width=4, stroke_fill="black")
    sheet.paste(t, (((v["n"] - 1) % 5) * 270, ((v["n"] - 1) // 5) * 480))
sheet.save(wd("thumbs", "sheet.jpg"), quality=85)
save(wd("thumbs", "variants.json"), {"variants": variants})
print(f"{n} variants -> work/{slug}/thumbs/ (look at sheet.jpg at feed size, then --pick N)")
