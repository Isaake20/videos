---
description: Ciclo completo y autónomo: analítica → tendencia → guion → QA → voz y render → QA de vídeo → miniatura → publicación → comentarios
argument-hint: "[tema opcional]"
---
Ejecuta un ciclo completo de producción desde la raíz del proyecto, sin pedir aprobación en ningún paso.
Tema forzado (si se indicó): $ARGUMENTS

0. Si `state/published.json` tiene vídeos → agente `retention-analyst` (deja sus avisos en `state/playbook.md`). Si YouTube no está conectado, se salta.
1. Si `state/channels.json` no existe o tiene más de 7 días → agente `channel-analyst`.
2. Agente `trend-scout` → `state/pick.json` (si hay tema forzado, pásaselo como único candidato).
3. Agente `scriptwriter` → `work/<slug>/script.json`.
4. Agente `qa-reviewer` en modo guion. Si `fail`: devuelve los motivos al `scriptwriter` y repite (máximo 2 rondas; a la tercera, descarta el tema y vuelve al paso 2 con el siguiente candidato).
5. Agente `producer` → `output/<fecha>-<slug>/video.mp4`.
6. Agente `qa-reviewer` en modo vídeo. Si `fail` por algo visual, el `producer` corrige y vuelve a renderizar una vez.
7. Agente `thumbnail-maker` → deja la mejor miniatura en `output/<fecha>-<slug>/thumbnail.jpg`.
8. Agente `publisher` → sube el vídeo a YouTube (solo si el paso 6 dio `pass` y `publish.enabled` es true). Si YouTube no está conectado, el vídeo se queda en `output/` y se anota "sin publicar".
9. Agente `community-manager` → responde comentarios pendientes (se salta si YouTube no está conectado o `community.enabled` es false).
10. Añade una línea a `state/runs.log` con fecha, tema, resultado, enlace publicado (o "sin publicar") y caracteres gastados; regenera el panel con `python3 plugins/video-factory/scripts/office.py`; envía el vídeo final al usuario como archivo; haz commit y push a `main` solo de `config/`, `state/` y `oficina/`; y termina con un resumen de 3 líneas.

Repite los pasos 2-8 `videos_per_run` veces (config/channel.json). Un fallo de publicación o de comentarios no invalida el vídeo: queda en `output/` y se informa.
