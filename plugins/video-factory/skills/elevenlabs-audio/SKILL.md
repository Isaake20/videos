---
name: elevenlabs-audio
description: Uso de ElevenLabs en la fábrica de vídeos - narración con marcas de tiempo, música, elección de voz, cuota y errores. Úsala al generar o depurar el audio de un vídeo.
---
# Audio con ElevenLabs

La clave **no** está en ninguna variable: el proxy de red del entorno la inyecta en las peticiones a `api.elevenlabs.io` (cabecera `xi-api-key`). Los scripts envían un valor de relleno. Nunca pidas ni escribas la clave.

## Scripts
- `tts.py <slug>` → `voice.mp3` + `timing.json`. Usa `/v1/text-to-speech/{voice}/with-timestamps`, una sola llamada para todo el guion (entonación coherente) y convierte la alineación por caracteres en tiempos por palabra para los subtítulos.
- `music.py <slug> "<prompt>"` → `music.mp3`. Opcional; si falla, el vídeo sale solo con voz.
- `tts.py <slug> --draft` → pista muda con tiempos estimados. Solo para previsualizar; el render queda marcado como BORRADOR.

## Voz
`config/channel.json → elevenlabs.voice_id`. Si está vacío, `tts.py` elige una voz en español de la cuenta y la guarda: la voz del canal debe ser siempre la misma. La voz actual es "M - voz ágil" (rápida, latinoamericana); el propietario pidió el 2026-11-16 usarla siempre: no la cambies. Ajustes: `stability` 0,3 (muy expresiva), `style` 0,55, `speed` 1,12, modelo `eleven_multilingual_v2`. El `music_prompt` debe pedir música de documental de intriga: tensa, sobria, con pulso (dark investigative documentary underscore, pulsing, ~100 bpm), no alegre.

## Cuota
Antes de generar, `tts.py` consulta `/v1/user/subscription` y se detiene si quedan menos del doble de caracteres necesarios. Tope por ejecución: `max_chars_per_run`. Un Short gasta ≈ 700-900 caracteres.

## Errores
| Síntoma | Qué hacer |
|---|---|
| Salida 3, "unreachable" o 403 del proxy | La clave no está guardada en el entorno. Deja un borrador (`--draft`) e informa; no sustituyas la voz. |
| 401 | Clave inválida o sin permisos: informa. |
| 429 | Espera 60 s y reintenta una vez. |
| Pronunciación rara | Reescribe la palabra fonéticamente en el guion (p. ej. "GPU" → "ge pe u"). |

Las pronunciaciones se corrigen en el texto; no regeneres más de 2 veces el mismo guion.
