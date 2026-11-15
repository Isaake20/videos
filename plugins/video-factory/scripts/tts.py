#!/usr/bin/env python3
"""Narration via ElevenLabs with word-level timestamps.
usage: tts.py <slug> [--draft]
Writes work/<slug>/voice.mp3 and timing.json (per-word start/end, per-scene range).
--draft: no API call; silent track with estimated timings, for layout previews only
(the render is then marked DRAFT and must never be published).
The API key is injected by the environment's network proxy; none is read here."""
import base64, subprocess, sys
from common import get_json, load, save, path, die

slug = sys.argv[1]; draft = "--draft" in sys.argv
cfg = load(path("config", "channel.json"), {}); el = cfg.get("elevenlabs", {})
script = load(path("work", slug, "script.json")) or die("no script.json")
texts = [sc["text"].strip() for sc in script["scenes"]]
full = " ".join(texts)
API = "https://api.elevenlabs.io"
H = {"xi-api-key": "proxy-injected"}
words = []

if draft:
    t, wps = 0.0, cfg.get("words_per_second", 2.6)
    for si, tx in enumerate(texts):
        for w in tx.split():
            d = (0.6 + 0.4 * min(len(w), 10) / 5) / wps
            words.append({"w": w, "s": round(t, 3), "e": round(t + d, 3), "scene": si}); t += d
        t += 0.25
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                    "-t", f"{t:.2f}", path("work", slug, "voice.mp3")], check=True)
else:
    if len(full) > el.get("max_chars_per_run", 2500):
        die(f"narration is {len(full)} chars, over the per-run budget")
    try:
        sub = get_json(f"{API}/v1/user/subscription", headers=H)
    except Exception as e:
        die(f"ElevenLabs unreachable ({e}). Add the API key for api.elevenlabs.io in the environment's "
            "network secrets (header xi-api-key). Not falling back to a fake voice.", 3)
    left = sub["character_limit"] - sub["character_count"]
    if left < len(full) * 2:
        die(f"ElevenLabs quota too low: {left} chars left", 3)
    vid = el.get("voice_id")
    if not vid:  # choose once: a Spanish narration voice from the account, then remember it
        vs = get_json(f"{API}/v1/voices", headers=H)["voices"]
        def rank(v):
            lb = v.get("labels") or {}
            langs = [lb.get("language", "")] + [x.get("language", "") for x in (v.get("verified_languages") or [])]
            return (("es" in langs) * 4 + (v.get("category") in ("cloned", "professional", "generated")) * 2
                    + (lb.get("use_case", "") in ("narration", "narrative_story", "social_media", "informative_educational")))
        v = max(vs, key=rank); vid = v["voice_id"]
        cfg["elevenlabs"]["voice_id"] = vid; cfg["elevenlabs"]["voice_name"] = v["name"]
        save(path("config", "channel.json"), cfg)
        print(f"voice chosen: {v['name']} ({vid})")
    r = get_json(f"{API}/v1/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_128", headers=H, timeout=180,
                 data={"text": full, "model_id": el.get("model_id", "eleven_multilingual_v2"),
                       "voice_settings": el.get("voice_settings", {})})
    open(path("work", slug, "voice.mp3"), "wb").write(base64.b64decode(r["audio_base64"]))
    al = r["alignment"]; ch, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    bounds, pos = [], 0
    for tx in texts:
        pos += len(tx) + 1; bounds.append(pos)
    cur, s0, e0, si = "", None, 0, 0
    for i, c in enumerate(ch + [" "]):
        if c.isspace():
            if cur:
                words.append({"w": cur, "s": round(s0, 3), "e": round(e0, 3), "scene": si}); cur = ""
            while si < len(bounds) - 1 and i + 1 >= bounds[si]:
                si += 1
        else:
            if not cur:
                s0 = st[i]
            cur += c; e0 = en[i]

scenes = []
for si in range(len(texts)):
    ws = [w for w in words if w["scene"] == si]
    scenes.append({"start": ws[0]["s"], "end": ws[-1]["e"]} if ws else {"start": 0, "end": 0})
for i in range(len(scenes) - 1):  # cut on the midpoint of the pause between scenes
    scenes[i]["end"] = scenes[i + 1]["start"] = round((scenes[i]["end"] + scenes[i + 1]["start"]) / 2, 3)
scenes[0]["start"] = 0.0; scenes[-1]["end"] = round(words[-1]["e"] + 0.6, 3)
save(path("work", slug, "timing.json"), {"draft": draft, "duration": scenes[-1]["end"], "chars": len(full),
                                         "words": words, "scenes": scenes})
print(f"{'DRAFT ' if draft else ''}voice: {scenes[-1]['end']:.1f}s, {len(words)} words, {len(full)} chars")
