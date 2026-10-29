# Amber: Koikatsu a Lineage II Interlude

2026-10-08. Proyecto: `E:\l2-local`. Laboratorio: `E:\l2-local\research\amber-l2`.

Se reutilizo Amber VRM de KoiVatar Forge. Prototipo adaptado al esqueleto humano femenino de L2
(847 -> 76 huesos), dos atlas y 33.240 triangulos. Compilacion UCC de L2Editor, lectura/exportacion
de retorno con UModel, shaders y referencia nativa a animaciones originales verificados.
La importacion PSA del editor produce datos incompatibles; evitarla. La ruta que paso las pruebas
conserva los datos de Fighter.ukx en una copia y vincula SkeletalMesh.Animation sin recompilarlos.

Instalado cliente separado `E:\l2\system-amber`, NPC 902500/display 59001, XML en servidor y fuente.
Acceso `E:\l2-local\13-PROBAR-AMBER.cmd`. Invocar con `//reload npc` y `//spawn 902500`.
No hay spawn automatico ni cambios en el perfil habitual system-hud.

**No probado visualmente dentro del cliente.** Previews de reposo/caminata en Blender disponibles;
todavia hay detalles de manos, cara/texturas y ropa por pulir. No es una skin jugable terminada.
Paquetes sin compresion DXT por ausencia de xDxTex.exe; recurso de movimiento aun contiene material extra.

Leer `research\amber-l2\README.md` y `reports\validation.json` antes de continuar.

Segunda prueba: el usuario mostro un conejo con nombre Amber. Se corrigio npcgrp class_name a LineageNPC.a_traderB_FHuman (clase Core.Class comprobada en LineageNPC.u) y se agrego display 59001 a NpcName-e.dat. Instalado solo en system-amber; archivos previos guardados en research/amber-l2/backups/before-npc-class-fix. Ambos catalogos pasan roundtrip binario. Pendiente reiniciar cliente con 13-PROBAR-AMBER y comprobar visualmente; no asumir resuelto a partir de UModel.

Revision visual v3 instalada: el usuario confirmo Amber dentro de L2, con geometria degradada y pose rigida. Se encontro que UCC generaba cuatro LOD (ultimo solo 3154 triangulos) y los alias de animacion eran genericos. Ahora L2AmberNPCv3.ukx usa un solo LOD completo (52153 triangulos), 76 huesos y maximo cuatro influencias nativas por vertice. Ropa vinculada al campo del cuerpo, 9406 caras internas de piel retiradas, menos decimacion, atlas con margen correcto. L2AmberMotionv3.ukx conserva animaciones de Fighter y usa los nombres reales Wait_Hand/walk_hand/Run_Hand de la comerciante. Shader de ropa difuso; cuerpo iluminacion propia; profundidad y alpha explicitos. Texturas RGBA comprobadas pixel a pixel; geometria y pesos nativos validados. Perfil system-amber ya apunta a v3. Falta reiniciar el cliente con 13-PROBAR-AMBER y confirmar imagen/animaciones. Restore-AmberV2.ps1 permite volver al catalogo v2.
