---
name: channel-analysis
description: Cómo leer state/channels.json para extraer patrones de canales de referencia y convertirlos en mejoras propias. Úsala al actualizar el manual de estilo.
---
# Analizar canales de referencia

`channels.py` solo lee metadatos públicos del feed RSS (últimos ~15 vídeos por canal): título, fecha, vistas, si es Short.

## Qué mirar
- **`outlier_score`** = vistas/día del vídeo ÷ mediana del canal. Lo que importa son los vídeos ≥ 3×: ¿qué tienen en común sus títulos y temas?
- **Forma del título**: longitud, pregunta vs. afirmación, números, palabras en mayúsculas.
- **Ritmo**: `uploads_per_week` y `shorts_share`.
- Para entender el *porqué* de un vídeo atípico, busca en la web el tema; no descargues ni transcribas el vídeo.

## Qué escribir en `state/playbook.md`
1. **Patrones que funcionan** (con el vídeo de ejemplo y su outlier_score).
2. **Fórmulas de título** abstraídas, p. ej. "¿Por qué [cosa cotidiana] [hecho raro]?".
3. **Cómo lo mejoramos**: para cada patrón, qué haremos distinto y mejor (fuentes citadas en la descripción, dato numérico en pantalla, subtítulos palabra a palabra, gancho en el primer segundo, 40-55 s).
4. **Qué evitar**: patrones con outlier_score < 0,5 de forma repetida.

Mantén el playbook por debajo de 80 líneas; reemplaza conclusiones viejas en vez de acumularlas.

## Límite
Inspirarse en una estructura es legítimo; reproducir el guion, el título literal, las imágenes o el audio de otro creador no. Cada vídeo nuestro parte de investigación propia.
