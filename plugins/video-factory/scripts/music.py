#!/usr/bin/env python3
"""Background music bed via ElevenLabs. usage: music.py <slug> "<prompt>"
Writes work/<slug>/music.mp3. Optional: the render works without it."""
import sys
from common import http, load, path, die

slug, prompt = sys.argv[1], sys.argv[2]
t = load(path("work", slug, "timing.json")) or die("run tts.py first")
ms = int(min(max(t["duration"] + 2, 10), 120) * 1000)
H = {"xi-api-key": "proxy-injected"}
try:
    audio = http("https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128", headers=H, timeout=300,
                 data={"prompt": prompt + " Instrumental only, no vocals.", "music_length_ms": ms})
except Exception as e:
    print(f"music endpoint failed ({e}); trying a looping sound bed")
    try:
        audio = http("https://api.elevenlabs.io/v1/sound-generation", headers=H, timeout=300,
                     data={"text": prompt + " instrumental loop", "duration_seconds": 22, "loop": True})
    except Exception as e2:
        die(f"no music generated ({e2}); render will proceed with voice only", 3)
open(path("work", slug, "music.mp3"), "wb").write(audio)
print(f"music -> work/{slug}/music.mp3")
