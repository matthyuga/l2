# Corrección de colisión de Dust2 — 14/10/2026

Kevin informó que veía el suelo pero caía al vacío inmediatamente después de `.dust2`. La prueba transitoria de servidor anterior no validaba física del cliente: no certifica aterrizaje ni soporte ingame. El reporte del usuario invalida cualquier interpretación de la primera integración como navegable ya comprobada.

Geodata existente presente y cargada; pisos y comandos del servidor siguen siendo válidos. La corrección aplicada afecta solo dos archivos del cliente: HGDust2Arena.usx y24_19.unr. No se ha identificado aún de forma concluyente la única causa del fallo; se prepara compatibilidad nativa y configuración de colisión, con confirmación pendiente en cliente.

Se convirtió el paquete UE2 123/license0 al layout Interlude123/license28. Se conservaron posiciones, índices y UV de las 37 mallas. Se añadieron endpoints de lazy arrays para colisión, metadatos nativos L2 e identidad de transformación de colisión; se rebasaron todos los punteros absolutos de esas arrays y de mipmaps. Materiales reciben los cuatro bytes nativos correspondientes. No se trata de cambiar solo el número de licencia en la cabecera.

Los 37 actores declaran explícitamente bWorldGeometry, bStatic, bCollideWorld y bloqueo de actores/traces; bUseCylinderCollision=false. Se conservan los otros 5.067 payloads del mapa byte por byte, incluido myLevel sin cambio de referencias.

Verificación fuera del juego:

- L2unreal deserializa íntegramente las 37 mallas como Interlude28: 9.932 caras y10.191 nodos de colisión, y datos de triángulos no vacíos. Advierte propiedad importada UseSimpleBoxCollision sin template; otras propiedades son nativas y la geometría/arrays se leen completas. No se confunde esa advertencia con una prueba de física.
- 68 imágenes/materiales vuelven a cargar con UModel-L2.
- Geometría antes/después idéntica. Rayos verticales contra mallas nativas encuentran soporte a la altura prevista bajo los40 puntos CT/T (con la calibración de altura usada por el proyecto).
- Cifrado Ver121, CRC y payload completo comprobados antes de instalar.

Instalado con cliente cerrado a las13:35 locales. Respaldo `E:/l2-local/backups/dust2-collision-fix-20261014-133504`. Manifest de integración principal actualizado para que su restore.py siga comprobando los hashes correctos. GameServer21308 no se reinició: no hubo cambios de servidor/geodata.

**Pendiente: Kevin debe volver a abrir el cliente y comprobar `.dust2` para confirmar si el aterrizaje quedó corregido.** Se solicitó esa prueba por pregunta asíncrona. No afirmar resuelto ingame solo a partir de lectores offline.
