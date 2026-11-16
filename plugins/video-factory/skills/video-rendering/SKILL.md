---
name: video-rendering
description: Cómo funciona y cómo depurar el render vertical 1080x1920 (ffmpeg + Pillow) con subtítulos palabra a palabra. Úsala al producir o corregir un vídeo.
---
# Render

`pipeline.py <slug> [--draft]` encadena: validar → voz → música → `render.py` → comprobaciones técnicas → `state/history.json`.

## Qué hace `render.py`
- Nada de pantallas estáticas: cada escena se corta en planos de ~2 s, cada uno con otro encuadre (acercar, alejar, barrido a izquierda o derecha) y un pequeño golpe de zoom en el corte. Si la escena trae `images` (2-4 archivos), los planos alternan esas imágenes.
- Fondo de color vivo distinto en cada plano; la imagen va como "pegatina" inclinada con borde blanco y sombra; las escenas `card` llevan texto gigante sobre el mismo tipo de fondo.
- Efectos de sonido sintetizados (barrido en cada cambio de escena, toque en los cortes internos, "pop" en las tarjetas) y barra de progreso amarilla abajo.
- Los cortes caen en la pausa entre escenas según `timing.json`.
- Subtítulos ASS: bloques de hasta 3 palabras en el tercio inferior, la palabra que suena resaltada en amarillo.
- `hook_text` en una banda amarilla arriba durante los primeros ~3,5 s.
- Audio: voz normalizada a -14 LUFS; la música baja automáticamente cuando hay voz.
- Salida en `output/<fecha>-<slug>/`: `video.mp4`, `thumbnail.jpg`, `metadata.json` (título, descripción con fuentes y créditos de imagen, hashtags).

## Revisar el resultado
```bash
ffmpeg -y -loglevel error -ss 1 -i output/<carpeta>/video.mp4 -frames:v 1 -vf scale=540:-1 /tmp/f1.jpg
```
Saca fotogramas en el segundo 1, a mitad y cerca del final, y además dos fotogramas separados 2,5 s dentro de la escena más larga, y míralos con Read. Si esos dos se ven iguales, hay una pantalla estática: es un fallo. Comprueba: texto dentro de márgenes, imagen reconocible, subtítulo legible sobre el fondo, gancho sin cortar.

## Arreglos habituales
- Imagen irreconocible o con mucho texto → cambia `image` por otra o por una `card`.
- Subtítulo que tapa lo importante → elige otra imagen; no muevas los estilos por un solo vídeo.
- Duración > 60 s → recorta el guion (el texto manda sobre la duración), nunca aceleres el audio.

Zonas seguras de Shorts: no pongas nada esencial en los 250 px superiores ni en los 420 px inferiores.
