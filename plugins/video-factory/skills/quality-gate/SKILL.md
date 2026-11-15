---
name: quality-gate
description: Lista de control para aprobar o rechazar un guion y un vídeo antes de darlo por terminado - hechos, originalidad, políticas de plataforma y calidad visual. Úsala al revisar.
---
# Control de calidad

## Modo guion → `work/<slug>/qa.json`
Para cada afirmación factual del guion:
1. Localízala en `research.json` o en una URL de `sources`. Si es una cifra, que coincida.
2. Si solo depende de Wikipedia y es sorprendente, confírmala con una búsqueda web.

Rechaza (`fail`) si:
- hay un dato sin respaldo o que contradice la fuente;
- el gancho promete algo que el vídeo no cumple;
- toca un tema de `avoid_topics` (config/channel.json) o habla de una persona viva de forma negativa o especulativa;
- el texto se parece demasiado a una fuente (frases copiadas) o a un vídeo concreto de otro canal;
- el tema ya está en `state/history.json`;
- una imagen asignada no corresponde a lo que se narra (míralas con Read).

```json
{"verdict": "pass" | "fail",
 "claims": [{"text": "...", "supported_by": "url o research.json", "ok": true}],
 "problems": ["motivo concreto y cómo arreglarlo"]}
```

## Modo vídeo → `output/<carpeta>/qa_video.json`
Extrae 4 fotogramas (1 s, 33 %, 66 %, último segundo) y míralos:
- subtítulos legibles, sin salirse ni tapar el sujeto;
- el gancho se lee entero en el primer fotograma;
- ninguna imagen pixelada, con marca de agua o fuera de contexto;
- duración 40-60 s, audio presente (`ffprobe`), sin la marca BORRADOR.

`metadata.json` debe incluir fuentes, créditos de imagen y el aviso de voz sintética.

Mismo formato de veredicto. Un vídeo con `fail` no se cuenta como terminado.
