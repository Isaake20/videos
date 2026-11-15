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

## Los puestos (oficina del canal)
`python3 plugins/video-factory/scripts/office.py` genera `oficina/index.html` con un escritorio por agente.

| Puesto | Agente | Qué hace |
|---|---|---|
| Retención · Analítica | `retention-analyst` | Métricas reales y avisos al guionista |
| Competencia | `channel-analyst` | Patrones de canales de referencia |
| Radar · Tendencias | `trend-scout` | Elige el tema del día |
| Guionista | `scriptwriter` | Investigación y guion con gancho |
| Control de calidad | `qa-reviewer` | Aprueba guion y vídeo |
| Locutor y Animador | `producer` | Voz, música y render |
| Miniaturista | `thumbnail-maker` | Hasta 10 miniaturas y elige una |
| Studio · Publicación | `publisher` | Sube a YouTube |
| Comunidad | `community-manager` | Responde comentarios |

## Conectar YouTube
Sin esto el ciclo funciona igual, pero los vídeos se quedan en `output/`.

1. En Google Cloud: crea un proyecto, activa **YouTube Data API v3** y **YouTube Analytics API**, configura la pantalla de consentimiento y pásala a **producción** (en modo prueba el token caduca a los 7 días), y crea un cliente OAuth de tipo "Aplicación de escritorio".
2. Obtén un token de refresco para la cuenta del canal con estos permisos: `https://www.googleapis.com/auth/youtube.upload`, `https://www.googleapis.com/auth/youtube.force-ssl`, `https://www.googleapis.com/auth/yt-analytics.readonly`.
3. En el entorno `video-factory`:
   - Secreto de red para `oauth2.googleapis.com`, tipo usuario/contraseña (Basic): usuario = ID de cliente, contraseña = secreto de cliente.
   - Variable de entorno `YT_REFRESH_TOKEN` con el token de refresco.
   - Hosts permitidos: `www.googleapis.com`, `youtubeanalytics.googleapis.com`.
4. Comprueba: `python3 plugins/video-factory/scripts/youtube.py check`.

Aviso de YouTube: los vídeos subidos por API desde un proyecto de Google Cloud **sin auditar** quedan bloqueados como privados. Para que salgan públicos hay que pasar la auditoría de cumplimiento de la API de YouTube.
