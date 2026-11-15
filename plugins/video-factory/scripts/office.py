#!/usr/bin/env python3
"""Build oficina/index.html: one desk per agent (mission, skills, prompt) plus the latest state. usage: office.py"""
import datetime as dt, glob, html, json, os, re
from common import load, path, ROOT

DESKS = [("retention-analyst", "📊", "Retención · Analítica"), ("channel-analyst", "🔭", "Competencia"), ("trend-scout", "📡", "Radar · Tendencias"),
         ("scriptwriter", "✍️", "Guionista · Guion"), ("qa-reviewer", "🧪", "Control de calidad"), ("producer", "🎙️", "Locutor y Animador · Voz y render"),
         ("thumbnail-maker", "🖼️", "Miniaturista · Miniaturas"), ("publisher", "🚀", "Studio · Publicación"), ("community-manager", "💬", "Comunidad · Comentarios")]
e = html.escape
agents = {}
for f in glob.glob(os.path.join(ROOT, "plugins", "video-factory", "agents", "*.md")):
    m = re.match(r"---\n(.*?)\n---\n(.*)", open(f, encoding="utf-8").read(), re.S)
    fm = dict(l.split(": ", 1) for l in m.group(1).splitlines() if ": " in l)
    agents[fm["name"]] = {**fm, "body": m.group(2).strip()}
hist = load(path("state", "history.json"), []); pub = load(path("state", "published.json"), [])
pick = load(path("state", "pick.json"), {})
try:
    runs = open(path("state", "runs.log"), encoding="utf-8").read().strip().splitlines()[-8:]
except FileNotFoundError:
    runs = []
yt = "conectado" if pub else "sin vídeos publicados todavía"
cards, panels = [], []
for name, icon, title in DESKS:
    a = agents.get(name)
    if not a:
        continue
    cards.append(f'<button class="desk" data-a="{name}"><span class="ic">{icon}</span><b>{e(title)}</b><small>{e(a["description"].split(". ")[1] if a["description"].count(". ") and len(a["description"].split(". ")[0]) < 30 else a["description"].split(". ")[0])}.</small><code>{name} · {e(a.get("model", ""))}</code></button>')
    panels.append(f'<section class="panel" id="p-{name}" hidden><h3>{icon} {e(title)}</h3><p>{e(a["description"])}</p><p><b>Skills:</b> {e(a.get("skills", "—"))}</p><pre>{e(a["body"])}</pre></section>')
flow = " → ".join(e(t.split(" · ")[0]) for n, i, t in DESKS if n in agents)
rows = "".join(f"<li>{e(r)}</li>" for r in reversed(runs)) or "<li>Aún no hay ciclos terminados.</li>"
vids = "".join(f'<li>{e(h["date"])} · {e(h["title"])}</li>' for h in reversed(hist[-8:])) or "<li>Ninguno todavía.</li>"
pubs = "".join(f'<li>{e(p["date"])} · <a href="https://youtu.be/{e(p["video_id"])}">{e(p["title"])}</a> ({e(str(p.get("privacy")))})</li>' for p in reversed(pub[-8:])) or "<li>Ninguno todavía.</li>"
page = f"""<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Oficina del canal</title>
<style>
:root{{--bg:#f6f5f1;--fg:#1c1b19;--mut:#6b675f;--card:#fff;--line:#dedbd2;--acc:#c2410c}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151412;--fg:#ecebe6;--mut:#a09c92;--card:#1f1e1b;--line:#33312c;--acc:#fb923c}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif}}
main{{max-width:980px;margin:auto;padding:24px 16px 64px}}h1{{margin:0 0 4px;font-size:26px}}h2{{font-size:15px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut);margin:28px 0 10px}}
.sub,.flow{{color:var(--mut);font-size:14px}}.flow{{margin-top:10px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}}
.desk{{all:unset;cursor:pointer;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;display:flex;flex-direction:column;gap:4px}}
.desk:focus-visible,.desk.on{{border-color:var(--acc);box-shadow:0 0 0 2px var(--acc)}}.ic{{font-size:24px}}.desk small{{color:var(--mut)}}.desk code{{font-size:12px;color:var(--mut)}}
.panel{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin-top:14px}}.panel h3{{margin:0 0 6px}}
pre{{white-space:pre-wrap;font:13px/1.5 ui-monospace,monospace;background:var(--bg);border-radius:8px;padding:12px;overflow-wrap:anywhere}}
ul{{margin:0;padding-left:18px}}li{{margin:3px 0;overflow-wrap:anywhere}}a{{color:var(--acc)}}
.cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}}
</style><main>
<h1>🎬 Oficina del canal · {e(load(path("config", "channel.json"), {}).get("channel_name", ""))}</h1>
<div class="sub">{len(cards)} agentes, cada uno en su puesto. Toca un escritorio para ver su misión y su prompt. Actualizado {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC.</div>
<div class="flow">{flow}</div>
<h2>El equipo</h2><div class="grid">{''.join(cards)}</div>{''.join(panels)}
<h2>Estado</h2><div class="cols">
<div><b>Tema en curso</b><ul><li>{e(str(pick.get("slug") or (pick.get("picks") or [{}])[0].get("slug") or "—"))}</li></ul><b>Últimos ciclos</b><ul>{rows}</ul></div>
<div><b>Vídeos producidos</b><ul>{vids}</ul><b>Publicados en YouTube</b> <small>({yt})</small><ul>{pubs}</ul></div></div>
</main><script>
document.querySelectorAll('.desk').forEach(b=>b.onclick=()=>{{document.querySelectorAll('.panel').forEach(p=>p.hidden=true);document.querySelectorAll('.desk').forEach(d=>d.classList.remove('on'));b.classList.add('on');const p=document.getElementById('p-'+b.dataset.a);p.hidden=false;p.scrollIntoView({{behavior:'smooth',block:'nearest'}})}});
</script></html>"""
out = path("oficina", "index.html")
open(out, "w", encoding="utf-8").write(page)
print("wrote", os.path.relpath(out, ROOT), f"({len(cards)} desks)")
