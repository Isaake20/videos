#!/usr/bin/env python3
"""Validate work/<slug>/script.json. usage: validate_script.py <path-to-script.json>
Exit 0 = valid, 2 = invalid (problems on stderr, so it can run as a hook)."""
import json, os, re, sys
from common import load, path

p = sys.argv[1]
cfg = load(path("config", "channel.json"), {})
try:
    s = json.load(open(p, encoding="utf-8"))
except Exception as e:
    print(f"script.json is not valid JSON: {e}", file=sys.stderr); sys.exit(2)
errs = []
for k in ("slug", "title", "hook_text", "scenes", "sources", "description", "hashtags", "trend"):
    if not s.get(k):
        errs.append(f"missing field: {k}")
scenes = s.get("scenes") or []
words = sum(len(sc.get("text", "").split()) for sc in scenes)
lo, hi = cfg.get("target_seconds", [40, 55]); wps = cfg.get("words_per_second", 2.6)
if not lo * wps <= words <= hi * wps:
    errs.append(f"narration has {words} words; need {int(lo*wps)}-{int(hi*wps)} for {lo}-{hi}s")
if not 4 <= len(scenes) <= 9:
    errs.append(f"{len(scenes)} scenes; need 4-9 (a visual change every 5-9 s)")
wdir = os.path.dirname(os.path.abspath(p))
for i, sc in enumerate(scenes, 1):
    if not sc.get("text"):
        errs.append(f"scene {i}: no text")
    for im in (sc.get("images") or ([sc["image"]] if sc.get("image") else [])):
        if not os.path.exists(os.path.join(wdir, im)):
            errs.append(f"scene {i}: image {im} not found")
    if not sc.get("image") and not sc.get("images") and not sc.get("card"):
        errs.append(f"scene {i}: needs 'image', 'images' (2-3 files shown in quick cuts) or 'card' (big on-screen text)")
    if len(sc.get("images") or []) > 4:
        errs.append(f"scene {i}: at most 4 images per scene")
if len(s.get("hook_text", "").split()) > 9:
    errs.append("hook_text over 9 words")
if len(s.get("title", "")) > 70:
    errs.append("title over 70 characters")
first = scenes[0].get("text", "").lower() if scenes else ""
if re.match(r"\W*(sab[ií]as que|hola|en este video|bienvenid)", first):
    errs.append("weak opener: start with the surprising claim itself")
if len(s.get("sources") or []) < 2:
    errs.append("need at least 2 source URLs")
if errs:
    print("script.json rejected:\n- " + "\n- ".join(errs), file=sys.stderr); sys.exit(2)
print(f"script ok: {words} words, {len(scenes)} scenes, ~{words/wps:.0f}s")
