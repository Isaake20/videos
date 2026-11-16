---
name: shorts-scriptwriting
description: Estructura, estilo y esquema JSON del guion de un Short narrado de 40-55 s. Úsala al escribir o corregir work/<slug>/script.json.
---
# Guion de un Short

## Estructura (≈ 105-143 palabras en total)
| Escena | Función | Duración |
|---|---|---|
| 1 | **Gancho**: la afirmación sorprendente, sin saludo ni "¿sabías que…?" | 3-4 s |
| 2 | **Contexto**: por qué se habla de esto hoy, en una frase | 5-7 s |
| 3-5 | **Desarrollo**: 2-3 datos, cada uno más fuerte que el anterior; al menos uno con cifra | 20-30 s |
| 6 | **Giro**: el dato que recontextualiza el gancho | 6-8 s |
| 7 | **Cierre en bucle**: una frase que enlaza con la primera, o una pregunta para comentarios | 3-5 s |

## Estilo
- Español neutro, frases de menos de 12 palabras, voz activa, tuteo.
- Tono entretenido, no de enciclopedia: habla como quien le cuenta algo increíble a un amigo. Sorpresa, contraste y una pizca de humor que salga del propio dato; al menos una pregunta directa al espectador a mitad de vídeo. La voz del canal es rápida y enérgica: escribe frases que se puedan decir con ganas.
- Escribe para el oído: números en palabras si son cortos ("ocho mil millones"), sin paréntesis ni siglas sin explicar.
- Una idea por escena; cada escena cambia la imagen. El vídeo no puede tener pantallas estáticas: el render corta cada ~2 s, así que dale material.
- `hook_text` (máx. 9 palabras) repite el gancho en pantalla: mucha gente ve el primer segundo sin sonido.
- Nada de exageraciones que el dato no sostenga ("nadie lo sabe", "te va a volar la cabeza").

## Visual de cada escena
- `image`: un archivo de `work/<slug>/img/` (míralo antes: que sea reconocible y encaje con lo que se dice).
- o `images`: lista de 2-4 archivos para una escena de más de 4 s; se muestran en cortes rápidos. Úsalo en las escenas largas siempre que tengas imágenes pertinentes.
- o `card`: 1-4 palabras o una cifra enorme ("8.000 MILLONES") cuando el dato *es* el visual. Usa 1-3 tarjetas por vídeo, nunca dos seguidas si puedes evitarlo.
- Pide a `wiki.py` artículos de sobra para tener al menos 8 imágenes útiles; un vídeo con menos de 5 imágenes distintas queda frío.
- No repitas la misma imagen.

## Esquema
```json
{
  "slug": "chip-videojuegos-ia",
  "title": "Título ≤ 70 caracteres, sin clickbait falso",
  "hook_text": "Máx. 9 palabras",
  "trend": {"topic": "tema tal como aparece en trends.json", "source": "wikipedia_top", "why_now": "..."},
  "scenes": [
    {"text": "Narración de la escena.", "image": "img/03.jpg"},
    {"text": "Otra escena.", "card": "1999"}
  ],
  "music_prompt": "Descripción en inglés de la música de fondo: género, tempo, ánimo",
  "description": "2-3 frases para la descripción del vídeo.",
  "hashtags": ["#shorts", "#ciencia", "#curiosidades"],
  "sources": ["https://es.wikipedia.org/wiki/...", "https://..."]
}
```
Al guardar, un hook ejecuta `validate_script.py`; corrige lo que indique.
