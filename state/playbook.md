# Manual de estilo (análisis de canales del 2026-11-15)

Fuente: `state/channels.json` — últimos ~15 vídeos de 7 canales de referencia. `×N` = vistas/día respecto a la mediana del propio canal.

## Patrones que funcionan
1. **"¿Por qué [algo cotidiano o conocido] [hecho extraño]?"** es la fórmula más repetida entre los vídeos atípicos:
   CuriosaMente "¿Por qué los niños abandonan el idioma de sus padres?" ×20,9 · Un Mundo Inmenso "¿Por qué casi no hay islas en Sudamérica?" ×6,5 · Date un Vlog "¿Por qué MR. INCREÍBLE NO DEBERÍA poder hacer esto?" ×9,9.
2. **Superlativo concreto**: QuantumFracture "La Mejor Predicción de Toda la Ciencia" ×16,7; "La Velocidad de Este Chorro es MAYOR que la de la LUZ" ×8,4.
3. **Ciencia pegada a la cultura pop o a la actualidad** (Date un Vlog: 73 % Shorts, 80 % títulos en pregunta; El Robot de Platón con temas de actualidad).
4. **Pregunta práctica y visual en ≤ 40 caracteres** (Zack D. Films, 100 % Shorts, ~52 por semana): "How New NBA Basketballs Get Their Grip", "Can A Fired Bullet Beat A Dropped Bullet".
5. Títulos cortos: media de 33-53 caracteres; 1-2 palabras en MAYÚSCULAS como máximo.

## Cómo lo mejoramos
- **Gancho en el primer segundo, hablado y escrito** (banda superior), sin saludo.
- **Fuentes y créditos en la descripción** de cada vídeo: casi ningún canal de Shorts lo hace.
- **Cifra en pantalla** como tarjeta gigante al menos una vez por vídeo.
- **Subtítulos palabra a palabra** sincronizados con la voz.
- **40-55 s** con cambio de plano cada ~2 s (nunca una pantalla quieta más de 3 s) y cierre que enlaza con el gancho.
- **Puente con la tendencia del día**: el tema entra por lo que la gente ya está buscando.

## Fórmulas de título
- ¿Por qué [X] [hecho raro]?
- [X] no se inventó para [lo que crees]
- El/La [superlativo] de [campo]
- ¿Cómo [proceso cotidiano] en realidad?

## Qué evitar
- Entrevistas y directos reciclados como Short (rinden por debajo de la mediana).
- Títulos de más de 60 caracteres o con más de dos palabras en mayúsculas.
- "¿Sabías que…?" como apertura.

## Límite del análisis
El feed público solo da 15 vídeos por canal y vistas totales; no hay retención ni CTR. Son indicios, no pruebas.

## Dirección del propietario (2026-11-16): estilo documental con gráficos animados
El propietario pasó un vídeo de referencia y quiere que todos los vídeos se parezcan a él **en el formato**. Se estudia el formato; no se copian su guion, su tema, sus imágenes ni sus personas. Los temas vetados (`avoid_topics`: muertes recientes, personas privadas…) siguen vetados aunque la referencia sea un caso judicial.

**Qué hace la referencia (medido)**
- Fondo casi negro, tipografía condensada blanca en mayúsculas y un solo color de acento: rojo.
- **Cada frase tiene su propio gráfico**, nunca una foto quieta: fecha grande, documento mecanografiado con una frase marcada en rojo, cifra gigante, relojes y línea de tiempo con la diferencia en rojo, foto tipo expediente con etiqueta, palabra clave sola en pantalla.
- Los gráficos se **construyen por pasos** (aparece el papel, se escribe el texto, se marca el dato).
- Narración a 2,6 palabras por segundo, frases de 4 a 12 palabras, tono de intriga sobrio.
- Estructura: gancho con una cifra exacta y algo sin resolver → fecha y lugar → versión oficial → "pero hay algo que no cierra" → dos o tres pruebas, cada una con su gráfico → el dato que lo cambia todo → cierre con pregunta para comentarios.

**Cómo lo aplicamos, por puesto**
- **Radar**: a igualdad de señal, gana el tema con un misterio o una contradicción ("lo que no encaja") y con fechas, cifras y documentos que se puedan enseñar.
- **Guionista**: escribe con esa estructura y da a cada escena un gráfico (`doc`, `stat`, `timeline`, `card` o foto con `label`). Máximo dos escenas seguidas del mismo tipo. Todo texto en pantalla sale de la investigación.
- **Control de calidad**: rechaza si falta la intriga, si hay tres escenas seguidas del mismo tipo de gráfico, si un texto en pantalla no está respaldado o si un plano no cambia en más de 3 s.
- **Locutor y Animador**: voz "M - voz ágil" (decisión del propietario: no se cambia); `config/channel.json → style: "documental"`; música tensa y sobria, no alegre.
- **Miniaturista**: fondo oscuro, texto blanco o rojo, una cifra o una palabra.
- **Studio, Retención, Comunidad**: mismo tono sobrio en títulos, descripciones y respuestas; sin exclamaciones de relleno.

## Formatos y objetivo (2026-11-16): monetizar
El objetivo del canal es monetizar. Tres piezas por tema:
- **Vídeo largo de YouTube** (8-10 min, horizontal): es el que monetiza de verdad (anuncios intermedios a partir de 8 min, horas de visualización). Tiene que sostener la atención: capítulos de 60-90 s, cada uno abre una pregunta y la cierra; una promesa en los primeros 15 s y un "recordatorio de lo que falta" cada 2 minutos; nada de relleno.
- **Short de YouTube** (40-55 s, vertical): el mejor gancho del mismo caso; sirve para traer gente al largo ("el caso completo está en el canal").
- **TikTok** (el mismo vertical, con su propio texto): se sube a mano.
Todos deben quedar profesionales, entretenidos y con gancho: intriga, ritmo, gráficos por frase y cero pantallas quietas.

