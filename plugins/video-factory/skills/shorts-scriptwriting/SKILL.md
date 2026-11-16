---
name: shorts-scriptwriting
description: Estructura de intriga, gráficos por escena y esquema JSON del guion de un Short documental de 40-55 s. Úsala al escribir o corregir work/<slug>/script.json.
---
# Guion de un Short

## Estructura (≈ 128-176 palabras: la voz del canal va a unas 3,2 palabras por segundo)
| Escena | Función | Duración |
|---|---|---|
| 1 | **Gancho**: la afirmación sorprendente, sin saludo ni "¿sabías que…?" | 3-4 s |
| 2 | **Contexto**: por qué se habla de esto hoy, en una frase | 5-7 s |
| 3-5 | **Desarrollo**: 2-3 datos, cada uno más fuerte que el anterior; al menos uno con cifra | 20-30 s |
| 6 | **Giro**: el dato que recontextualiza el gancho | 6-8 s |
| 7 | **Cierre en bucle**: una frase que enlaza con la primera, o una pregunta para comentarios | 3-5 s |

## Estilo
- Español neutro, frases de menos de 12 palabras, voz activa, tuteo.
- Tono de intriga, no de enciclopedia: plantea algo que no encaja y ve soltando pruebas. Frases secas, de 4 a 12 palabras. Usa un "pero" que gire la historia hacia la mitad y termina con una pregunta para comentarios. Sin chistes de relleno ni exclamaciones.
- Escribe para el oído: números en palabras si son cortos ("ocho mil millones"), sin paréntesis ni siglas sin explicar.
- Una idea por escena; cada escena cambia la imagen. El vídeo no puede tener pantallas estáticas: el render corta cada ~2 s, así que dale material.
- `hook_text` (máx. 9 palabras) repite el gancho en pantalla: mucha gente ve el primer segundo sin sonido.
- Nada de exageraciones que el dato no sostenga ("nadie lo sabe", "te va a volar la cabeza").

## Visual de cada escena (estilo documental)
Cada escena lleva **un** gráfico. El render lo construye por pasos y corta cada ~2 s. Varía: máximo dos escenas seguidas del mismo tipo.
| Campo | Qué se ve | Cuándo usarlo |
|---|---|---|
| `stat`: `{"over": "rótulo pequeño", "value": "11,5 KG", "label": "sello rojo"}` | Cifra o palabra gigante que se pone roja y recibe un sello | El dato *es* el visual: cifras, fechas, un símbolo |
| `doc`: `{"label": "tipo de documento", "text": "1-2 frases cortas", "highlight": "trozo exacto del text"}` | Hoja mecanografiada que se escribe y marca en rojo el `highlight` | Versiones oficiales, citas de la fuente, registros |
| `timeline`: `{"from": "1448", "to": "HOY", "label": "MÁS DE 5 SIGLOS"}` | Línea que crece entre dos momentos y la distancia en rojo | Tiempo entre dos hechos |
| `card`: `"2-4 PALABRAS"` | Palabras que aparecen una a una, la última en rojo | La frase que da el giro |
| `image` + `label` opcional | Foto tipo expediente con etiqueta mecanografiada | Solo si la imagen muestra de verdad lo que se narra |
| `images`: 2-4 archivos | Varias fotos en cortes rápidos | Escenas de más de 4 s con material |

- Todo texto en pantalla (`value`, `text`, `label`, `card`) debe estar respaldado por `research.json`: es un dato más. El `highlight` debe aparecer tal cual dentro de `text`.
- Mira cada imagen con Read antes de usarla. Si no hay imagen correcta, usa `doc` o `stat`: mejor un gráfico que una foto que no corresponde.
- No repitas la misma imagen.

## Vídeo largo (`"format": "long"`, slug `<tema>-largo`, 8-10 min ≈ 1.540-1.920 palabras, 60-150 escenas)
Es el formato que monetiza: cada minuto tiene que ganarse el siguiente.
- **0:00-0:15** gancho con cifra exacta + promesa de lo que se va a descubrir. Sin saludo ni presentación del canal.
- **Capítulos de 60-90 s** (6 a 8). Cada uno: una pregunta, dos o tres pruebas con su gráfico, y una frase final que abre el siguiente ("pero eso no explica…").
- **Cada ~2 min**, una línea que recuerde lo que falta por resolver.
- **Giro** hacia el 70 % del vídeo y **cierre** que responde a la promesa del gancho y pide opinión en comentarios.
- Escenas de 3-7 s: una frase, un gráfico. Alterna tipos; usa `images` con las 20-30 imágenes de la investigación.
- Añade `"chapters": [{"t": "00:00", "title": "..."}]` con 6-8 capítulos (el primero en 00:00) para la descripción.
- Mismo rigor: cada dato y cada texto en pantalla sale de `research.json`. Si el tema no da para 8 minutos sin relleno, dilo y propón otro: un largo estirado no retiene.
El Short del mismo día no es un resumen: es el mejor gancho del caso, con su propio cierre.

## Esquema
```json
{
  "slug": "chip-videojuegos-ia",
  "title": "Título ≤ 70 caracteres, sin clickbait falso",
  "hook_text": "Máx. 9 palabras",
  "trend": {"topic": "tema tal como aparece en trends.json", "source": "wikipedia_top", "why_now": "..."},
  "scenes": [
    {"text": "Gancho con cifra exacta.", "stat": {"over": "Rótulo", "value": "33 MIN", "label": "Sin explicar"}},
    {"text": "Lo que dice la fuente.", "doc": {"label": "Informe oficial", "text": "Frase corta de la fuente.", "highlight": "corta"}},
    {"text": "Lo que se ve.", "image": "img/03.jpg", "label": "Etiqueta de la foto"},
    {"text": "Cuánto pasó entre dos hechos.", "timeline": {"from": "1448", "to": "1971", "label": "523 AÑOS"}},
    {"text": "El giro.", "card": "NADIE LO USABA"}
  ],
  "music_prompt": "Descripción en inglés de la música de fondo: género, tempo, ánimo",
  "description": "2-3 frases para la descripción del vídeo.",
  "hashtags": ["#shorts", "#ciencia", "#curiosidades"],
  "sources": ["https://es.wikipedia.org/wiki/...", "https://..."]
}
```
Al guardar, un hook ejecuta `validate_script.py`; corrige lo que indique.
