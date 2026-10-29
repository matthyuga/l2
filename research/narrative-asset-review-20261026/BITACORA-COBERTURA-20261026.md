# Bitácora: criaturas, facciones y cobertura narrativa

26/10/2026. Solicitud de Kevin: conservar lo conversado y mostrar por colores o grilla dónde ya recopilamos historias, personajes y trama, para identificar lo que falta.

## Lo conservado en esta ampliación

- Identificación probable de «skalators» como Stakato del entorno de Rune: colonia, reina y élite Proconsul. Falta confirmar el ejemplar recordado. Organización social no garantiza lenguaje humano.
- Valley of Saints: Ballard menciona Kel Mahums; los guardianes de Splendor usan modelos de esa familia. No identificarlos automáticamente como licántropos. La misión Heart in Search of Power afirma que las cuentas de obediencia controlan pensamientos de sus guardianes. Quién ejerce el control y la biografía de cada uno requieren investigación adicional.
- Ángeles del valle: Barakiel es un candidato concreto, sin identificar con certeza el grupo que recuerda Kevin. Considerar también la cercanía de Monastery of Silence.
- Tower of Insolence: Baium, ambición divina, castigo de Einhasad, encierro y transformación. Euclie describe la invasión de Hallate y sus seguidores Kernon y Longhorn General Golconda, enfrentados a Platinum Tribe y ángeles guardianes. No todos sirven a Baium. El objetivo exacto de Hallate no está identificado por Euclie.
- Criterio para futuras fichas: distinguir especie, facción, autoridad, autonomía y actitud. Aspecto angelical no implica alianza con el jugador; hostilidad no implica ausencia de inteligencia. Religión/conocimiento podrían reconocer filiaciones o señales de sometimiento: propuesta de diseño, sin implementar.

Evidencia y fuentes: [Rune, valle y torre](RUNE-VALLEY-TOWER.md), [revisión de modelos y tribus](REVISION.md).

## Grilla de seguimiento

Se creó [COBERTURA-NARRATIVA.md](COBERTURA-NARRATIVA.md), con 32 lugares o grupos y cuatro columnas independientes: historia, personajes, facciones y trama propia. Datos editables en cobertura-narrativa.json; grilla visual en cobertura-narrativa.html. El generador build-coverage.py conserva la procedencia de cada fila.

Verde D = recopilado; ámbar P = parcial; azul I = idea propuesta; gris — = pendiente. Recopilado no significa exhaustivo. Los estados corresponden al material localizado en los documentos revisados, no a un porcentaje del mundo ni a contenido implementado.

Se incorporaron también las propuestas anteriores de adaptación de El Último Bastión, festival y prólogo. Conservan su condición de propuestas: no se aprobaron como canon por incluirlas en el seguimiento. Hay referencias a Gludio como inicio y Giran como refugio; su relación necesita definirse, sin resolverla arbitrariamente aquí.

La entrega elegida es una grilla documental, una de las alternativas solicitadas. No se dibujaron posiciones ni distancias aproximadas sobre un falso mapa. No se modificaron cliente, NPC, misiones ni servidor.

Pendientes generales: dossier urbano de Rune y Heine, aldeas iniciales, Imperial Tomb, historia individual de tribus y guardianes. Las nueve ciudades investigadas tienen una base histórica, pero requieren convertir sus propuestas en personajes, encuentros y misiones concretas.

## Continuación: mapa ilustrado

Kevin aclaró que el pedido sí correspondía a esta sesión y solicitó continuar. Se añadió mapa-cobertura-narrativa.html, con 31 marcadores asociados a 29 de las 32 fichas y selector de capa: historia, personajes, facciones o trama propia. La selección muestra material disponible y próximo pendiente. Las ruinas de Gludio y el conjunto pantano/nido Stakato tienen dos puntos por ficha.

Base: mapa ilustrado Interlude ya disponible localmente en tmp/pdfs/l2-atlas, con procedencia registrada como https://www.l2satoshi.app/images/AdenWorldMapInterlude.png. Se trabajó sobre una copia optimizada dentro de esta carpeta; no se modificaron los archivos del atlas ni el trabajo de otra sesión. mapa-procedencia.json conserva hash y anclajes normalizados.

Los marcadores son anclajes manuales aproximados en sitios rotulados: no representan coordenadas de navegación, áreas exactas ni distancias. Hardin no se ubicó sin comprobarlo; Pagan Temple se remite al interior de Rune; las tribus de lagartos siguen sin un punto único. La grilla conserva sus 32 fichas.

Verificación con Chromium: imagen cargada, 31 marcadores, selección de Tower of Insolence, cambio a trama propia y ajuste a pantalla estrecha; sin errores JavaScript. Captura de revisión: mapa-verificado.png. No hay integración ni cambios en el juego.

## Exportación PDF

A pedido de Kevin se creó E:\l2-local\output\pdf\L2-mapa-cobertura-narrativa.pdf: seis páginas, cuatro mapas A3 (historia, personajes, facciones y trama propia) y dos páginas de grilla con las 32 fichas y próximos pendientes. Exportación reproducible con export-map-pdf.py. Se renderizaron y revisaron las seis páginas; leyenda, marcadores y tablas legibles, sin recortes. Conserva los límites de los anclajes ilustrativos y la condición provisional de las propuestas.

## Dossier ampliado para investigar

Kevin pidió profundizar y reunir la información en el PDF para poder investigarla. Se creó E:\l2-local\output\pdf\L2-atlas-dossier-narrativo-ampliado.pdf, 45 páginas, con índice enlazado, marcadores por capítulo, 46 enlaces URI, nueve ciudades, nombres y discrepancias, criaturas y testimonios locales, láminas de personajes, identidad/prólogo, creación/roles, propuesta regional, festival/rescates, agenda de 32 fichas y el atlas de seis páginas al final. El PDF corto se conserva.

Nueva revisión de fuentes históricas C4/C5, criaturas y geografía: AMPLIACION-DOSSIER-20261026.md. Añade base de Imperial Tomb y pistas de Rune, Stakato, monasterio, tierras heladas y aldeas; no cambia silenciosamente los estados de la instantánea cartográfica. Forest of the Dead, Beast Farm y Devil’s Pass se mencionan como nuevas líneas, fuera de las 32 fichas originales.

Generador: export-dossier-pdf.py. Se renderizaron las 45 páginas y revisaron láminas de contacto, tablas y páginas de agenda; verificación de texto, enlaces y marcadores completada. Las propuestas permanecen atribuidas y sin implementación. No se modificaron otros documentos narrativos originales ni el juego.
