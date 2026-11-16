---
description: Ciclo diario autónomo: un tema → Short + versión TikTok (cada día) y vídeo largo de YouTube (días de `long_weekdays`), con QA, miniatura, publicación y comentarios
argument-hint: "[tema opcional]"
---
Ejecuta un ciclo completo desde la raíz del proyecto, sin pedir aprobación en ningún paso.
Tema forzado (si se indicó): $ARGUMENTS

**Formatos del día** (`config/channel.json`): `formats` dice cuáles se producen. El Short y su copia para TikTok salen todos los días. El vídeo largo (8-10 min, horizontal) sale los días de la semana de `long_weekdays` (0 = lunes), porque cada uno gasta unos 9.000 caracteres de voz; si hoy no toca, sáltalo y dilo en el resumen.

0. Si `state/published.json` tiene vídeos → agente `retention-analyst`. Si YouTube no está conectado, se salta.
1. Si `state/channels.json` no existe o tiene más de 7 días → agente `channel-analyst`.
2. Agente `trend-scout` → `state/pick.json`. Si hoy toca vídeo largo, el tema debe dar para 8-10 minutos (varias pruebas, fechas, documentos, 20 o más imágenes).
3. Agente `scriptwriter`:
   - Día con largo: investiga con `wiki.py <slug>-largo ...` (hasta 30 imágenes), escribe `work/<slug>-largo/script.json` con `"format": "long"`, luego `derive.py <slug>-largo <slug>` y escribe el Short en `work/<slug>/script.json` como la versión de 45 s del mismo caso (su mejor gancho, no un resumen).
   - Día sin largo: investiga con `wiki.py <slug> ...` y escribe solo el Short.
4. Agente `qa-reviewer` en modo guion, una vez por guion. Si `fail`: vuelve al `scriptwriter` (máximo 2 rondas por guion; a la tercera, descarta el tema y vuelve al paso 2 con el siguiente candidato).
5. Agente `producer`, una vez por guion aprobado → `output/<fecha>-<slug>/` (Short: `video.mp4`, `tiktok.mp4`, `tiktok.txt`) y `output/<fecha>-<slug>-largo/` (largo: `video.mp4` 1920x1080).
6. Agente `qa-reviewer` en modo vídeo, una vez por vídeo. Si `fail` por algo visual, el `producer` corrige y vuelve a renderizar una vez.
7. Agente `thumbnail-maker` para cada vídeo.
8. Agente `publisher` → sube a YouTube el Short y el largo aprobados (tope `publish.max_uploads_per_day`). TikTok no se publica por API: `tiktok.mp4` y `tiktok.txt` se entregan al usuario para subirlos a mano. Si YouTube no está conectado, todo queda en `output/` y se anota "sin publicar".
9. Agente `community-manager` → responde comentarios pendientes (se salta sin conexión o con `community.enabled` en false).
10. Añade una línea por vídeo a `state/runs.log` (fecha, formato, tema, resultado, enlace o "sin publicar", caracteres gastados); regenera el panel con `python3 plugins/video-factory/scripts/office.py`; envía al usuario como archivos el Short, el `tiktok.mp4` con su `tiktok.txt` y el largo; haz commit y push a `main` solo de `config/`, `state/` y `oficina/`; termina con un resumen de 3 líneas.

Un fallo en un formato no detiene los otros: se informa y se sigue.
