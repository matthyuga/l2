# Orco: reparaci?n de cabeza v13

Instalada el 26/10/2026. V12 provoc? un critical error confirmado por el usuario al mostrar el rostro del orco. La traza sit?a el fallo en SetVertexStreams / DrawSection, durante el dibujo de una secci?n esquel?tica.

Se detect? una diferencia respecto a la cabeza custom de elfo oscuro ya instalada: todas las secciones LOD de MOrc_ModernFace v12 ten?an Material=None. Faltaba importar una textura predeterminada y asignarla con MESHMAP SETTEXTURE. V13 incorpora FaceDefault (textura MOrc m001 t03) y la asigna al material 0, conservando geometr?a, UV y esqueleto. El hook sigue aplicando las texturas D/E/F seleccionadas encima del predeterminado. Las cuatro secciones LOD tienen ahora material expl?cito y ning?n Material=None. Es una correcci?n de un defecto real del paquete; la causalidad completa del crash y su ausencia despu?s del cambio todav?a requieren la prueba del usuario dentro del juego.

Paquete nuevo: E:/l2/Animations/NexusOrcFaceV13.ukx. Ambos engine.dll cambian s?lo la ruta UTF16 NexusOrcFaceV12.MOrc_ModernFace por NexusOrcFaceV13.MOrc_ModernFace. No se cambiaron las instrucciones, la UI, el servidor, las texturas de cabello, colores o personajes. Los materiales v12 de DarkElf G y FOrc J se conservaron.

Verificado: 206 puntos, 386 tri?ngulos, UV sin cambios, esqueleto id?ntico; todos los cuatro LOD con FaceDefault; textura RGBA exacta tras compilar; carga/exportaci?n UCC nativa correcta. Pasaron 2303 regresiones de hooks, 15486 casos de Tanda 2 y 5824 casos de conteo con 112 ejecuciones del bucle nativo de materiales. Esas pruebas no sustituyen el renderer D3D del cliente real.

Copias: installation.json y backup. La reversi?n global de Tanda 2 se actualiz? para conservar v13 y las reparaciones independientes de Tanda 1. Los scripts de rollback anteriores est?n protegidos por hashes y requieren revertir v13 primero; no deben ejecutarse forzando los hashes. Para retirar s?lo v13 se dispone de rollback.py. Pendiente: comprobar D/E/F en 2-JUGAR sin critical error, despu?s el resultado visual y los dos cabellos de v12.
