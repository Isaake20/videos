---
name: trend-scouting
description: Cómo convertir las señales de state/trends.json en un tema de Short con ángulo propio. Úsala al elegir de qué va el próximo vídeo.
---
# Elegir tema a partir de tendencias

Entrada: `state/trends.json` (Google Trends por país, artículos más vistos de Wikipedia, portada de Hacker News, efemérides) y `config/channel.json`.

## Método
1. **Descarta** lo que esté en `avoid_topics`, lo marcado `already_covered`, resultados deportivos sueltos y nombres de personas sin un ángulo de ciencia/tecnología/historia.
2. **Busca el puente**: el vídeo no cuenta la noticia, explica algo sorprendente y duradero *detrás* de la tendencia.
   - "Jensen Huang" es tendencia → por qué un chip de videojuegos acabó moviendo la IA.
   - Partido Lakers-Suns → por qué una pelota de baloncesto tiene exactamente esos puntitos.
3. **Puntúa** cada candidato de 0 a 5 en: señal (tráfico, aparece en varias fuentes o países), sorpresa (¿hay un dato contraintuitivo?), intriga (¿hay algo que no encaja, una versión oficial discutida o un "pero" con fechas, cifras y documentos que enseñar?), visual (¿hay imágenes libres en Wikipedia?), verificable (¿se sostiene con 2 fuentes?), vida útil (¿seguirá interesando en un mes?).
4. Si nada supera 19/30, usa una efeméride (`on_this_day`) con buen material visual: es mejor un evergreen sólido que una tendencia forzada.
5. Verifica con una búsqueda web rápida que el contexto de la tendencia es el que crees.

## Salida: `state/pick.json`
```json
{"date": "YYYY-MM-DD",
 "picks": [{"slug": "chip-videojuegos-ia", "topic": "Jensen Huang", "source": "wikipedia_top",
            "angle": "una frase con la promesa del vídeo", "score": 21,
            "wiki_articles": ["Nvidia", "Unidad de procesamiento gráfico"], "why_now": "..."}]}
```
El primer elemento es el elegido; los otros dos son reservas por si QA descarta el primero.
