# video-factory

Fábrica autónoma de Shorts en español guiados por tendencias. Canal y nicho: `config/channel.json`.

## Cómo trabajar aquí
- Un ciclo completo es `/produce-video` (ver `plugins/video-factory/commands/produce-video.md`). Se ejecuta **sin pedir aprobación**: decide, produce y deja el resultado en `output/`.
- Usa siempre los agentes (`trend-scout`, `channel-analyst`, `scriptwriter`, `qa-reviewer`, `producer`) y sus skills; no hagas su trabajo a mano.
- Ejecuta los scripts desde la raíz: `python3 plugins/video-factory/scripts/<script>.py`.
- La clave de ElevenLabs la inyecta el proxy del entorno para `api.elevenlabs.io`; no existe como variable y no se pide en el chat.

## Reglas que no se saltan
- Guion propio a partir de investigación propia. De otros canales solo se estudian patrones (`state/playbook.md`).
- Todo dato lleva fuente; las imágenes son de Wikimedia Commons con licencia libre y se acreditan en `metadata.json`.
- Sin voz real de ElevenLabs solo se generan borradores (`--draft`), marcados y nunca publicables.
- No se publica en ninguna plataforma: los vídeos quedan en `output/`.
- Temas vetados: `avoid_topics` en la configuración.

## Estado
`state/trends.json` señales · `state/channels.json` análisis · `state/playbook.md` manual de estilo · `state/pick.json` tema elegido · `state/history.json` vídeos hechos · `state/runs.log` bitácora.
