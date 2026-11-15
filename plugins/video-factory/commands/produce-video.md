---
description: Ciclo completo y autónomo: tendencia → guion → QA → voz → render → QA de vídeo
argument-hint: "[tema opcional]"
---
Ejecuta un ciclo completo de producción desde la raíz del proyecto, sin pedir aprobación en ningún paso.
Tema forzado (si se indicó): $ARGUMENTS

1. Si `state/channels.json` no existe o tiene más de 7 días → agente `channel-analyst`.
2. Agente `trend-scout` → `state/pick.json` (si hay tema forzado, pásaselo como único candidato).
3. Agente `scriptwriter` → `work/<slug>/script.json`.
4. Agente `qa-reviewer` en modo guion. Si `fail`: devuelve los motivos al `scriptwriter` y repite (máximo 2 rondas; a la tercera, descarta el tema y vuelve al paso 2 con el siguiente candidato).
5. Agente `producer` → `output/<fecha>-<slug>/video.mp4`.
6. Agente `qa-reviewer` en modo vídeo. Si `fail` por algo visual, el `producer` corrige y vuelve a renderizar una vez.
7. Añade una línea a `state/runs.log` con fecha, tema, resultado y caracteres gastados, y termina con un resumen de 3 líneas.

Repite los pasos 2-7 `videos_per_run` veces (config/channel.json). Los vídeos terminados se quedan en `output/`; no se publica en ninguna plataforma.
