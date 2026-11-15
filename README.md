# video-factory

Sistema de agentes de Claude Code que produce Shorts verticales en español a partir de las tendencias del día.

```
tendencias ──► trend-scout ──► scriptwriter ──► qa-reviewer ──► producer ──► qa-reviewer ──► output/
                   ▲                ▲                                │
           channel-analyst ──► playbook.md                  ElevenLabs + ffmpeg
```

| Pieza | Dónde |
|---|---|
| Plugin (agentes, skills, comandos, hooks, scripts) | `plugins/video-factory/` |
| Marketplace local para instalar el plugin | `.claude-plugin/marketplace.json` |
| Carga automática en este proyecto | `.claude/` (enlaces al plugin + `settings.json`) |
| Configuración del canal y canales de referencia | `config/` |
| Estado y bitácora | `state/` |
| Vídeos terminados | `output/<fecha>-<slug>/` (`video.mp4`, `thumbnail.jpg`, `metadata.json`) |

## Uso
- `/produce-video` — un ciclo completo y autónomo.
- `/produce-video <tema>` — fuerza un tema.
- `/analyze-channels` — reanaliza la competencia.

## Requisitos del entorno
- Red permitida: `trends.google.com`, `www.youtube.com`, `wikimedia.org`, `es.wikipedia.org`, `en.wikipedia.org`, `commons.wikimedia.org`, `upload.wikimedia.org`, `thumb.wikimedia.org`, `hacker-news.firebaseio.com`.
- Clave de ElevenLabs guardada como secreto de red para `api.elevenlabs.io` (cabecera `xi-api-key`).
- `ffmpeg`, Python 3 con Pillow.
