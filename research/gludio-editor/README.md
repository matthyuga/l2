# Muelle de Gludio: espacio aislado de edicion

## Revision tras captura de Load Errors

La captura del usuario confirma ventana de UnrealEd abierta con Working/24_19.unr y el listado de recursos faltantes. Se preparo Working-v2/24_19.unr sin sobrescribir esa copia abierta. El acceso 18-EDITOR-MUELLE-LAB.cmd ahora apunta a v2. La copia privada HGEditorWater.usx expone Water01 en la raiz (antes estaba en test.Water01) y v2 referencia ese paquete. Prueba nativa: ya no aparece Missing StaticMesh Water01; las siete incompatibilidades Engine y la conversion Skins permanecen. Evidencia waterfix-proof.json y System/GludioLoad-v2.log. Cliente y respaldos originales intactos. Falta comprobacion visual de v2 y no se autoriza instalar resultados del guardado completo del editor.

Preparado el 17/10/2026 para **L2 Lab**. No modifica Hellgames ni Academy.

## Abrir

Ejecutar `E:\l2-local\18-EDITOR-MUELLE-LAB.cmd`.

Abre la copia privada de UnrealEd/L2Editor con `Working/24_19.unr`.
La camara de perspectiva esta preparada cerca del muelle: 149000,42500,14700.
La orientacion y la imagen todavia requieren comprobacion en pantalla.
No instalar el mapa guardado por este editor directamente en el cliente.

## Copias

- `Original/`: respaldo cifrado del mapa actual y 80 dependencias. Conservar intacto.
- `snapshot.json`: rutas reales y SHA-256 de cada archivo original.
- `Packages/`: copias descifradas para el editor, con una compatibilidad local descrita debajo.
- `Working/24_19.unr`: mapa editable, con solo cinco propiedades de camara de LevelInfo0 cambiadas respecto de la copia descifrada.
- `System/`: editor y motor propios. GludioEditor.ini busca paquetes dentro de este espacio, no en los clientes.
- `Exports/myLevel.t3d`: exportacion nativa del mapa para inspeccion y comparacion.

El original capturado contiene otros experimentos (Coliseo, Dust2 y aeronaves), no solamente el muelle. Hay 52.855 exports y 41.185 actores exportados del nivel.

## Resultado real de las pruebas

1. Se comprobo SHA-256 del cliente y respaldos; originales intactos (`workspace-proof.json`).
2. La primera carga se detuvo por `watertest.water.Water01`, ausente en el cliente y referenciado desde water.usx.
3. Se sustituyo SOLO en Packages/water.usx esa dependencia de textura por L2_skies.Textures.WhiteCloud. Es una ayuda de compatibilidad del editor, no una textura original recuperada. Registro: editor-only-compatibility.json. No se instalo en el juego.
4. Con esa sustitucion, UCC batchexport carga/exporta el mapa y conserva las ocho piezas HGGludioDock con sus referencias de mallas y posiciones. Su resumen dice cero errores y advertencias, pero **el log detallado si contiene advertencias**: Engine con propiedades/funciones faltantes, conversion de Skins a array dinamico y `Missing StaticMesh water.Water01`. La malla real esta en water.test.Water01; no se corrigio el cliente.
5. `packageflag` no conserva el contenido completo al guardar este mapa: salida descartada en Roundtrip/. Esto no demuestra por si solo el comportamiento de Guardar en la interfaz.
6. `mapconvert` guarda y recarga, manteniendo 41.185 actores activos por nombre/clase, pero cambia license 28 a 0, reduce exports de 52.855 a 42.436, convierte brushes y no produce T3D identico. **Salida de diagnostico, no instalable**. Evidencia: mapconvert-proof.json, active-actor-comparison.json, Mapconvert/.
7. Se lanzo UnrealEd sobre Working/24_19.unr; solo se verifico que el proceso sigue activo. No se vio su ventana ni se valido carga, render o Guardar desde GUI.
8. Computer Use fallo antes y despues de reiniciar su kernel con `Computer Use native pipe is unavailable ... os error 2`. No hubo validacion visual automatizada.

## Como continuar

Inspeccionar el muelle en la copia aislada. Si se realizan colocaciones de adornos, conservar el trabajo en Working y exportarlo a T3D. El camino conservador es transferir los actores aprobados al mapa original mediante el pipeline de paquetes del laboratorio, preservando el resto del mapa y verificando geodata cuando corresponda. No copiar encima del cliente el mapa serializado por UnrealEd hasta validar expresamente sus diferencias.

No reejecutar constructores historicos sobre el mapa vivo. prepare.py vuelve a preparar Packages y no conserva sus ajustes manuales; prepare_workspace.py se niega a sobreescribir Working. Los scripts de prueba son diagnosticos; no son instaladores.

## Recuperacion de Computer Use solicitada por Kevin
El usuario pide manejar directamente UnrealEd; viewport v2 negro, causa visual aun no establecida. Prueba actual de sky.list_windows falla antes de enumerar ventanas con native pipe unavailable/os error2, incluso tras js_reset. SDK importable; no se confirma causa de la ausencia del transporte nativo. No lanzar helper manualmente ni automatizar ChatGPT. Documentacion oficial consultada: https://learn.chatgpt.com/docs/computer-use (Plugins > Computer Use > Enable, server/skill toggles, Try now). Proximo paso manual: comprobar/reiniciar conexion del plugin desde app y reintentar en este mismo hilo. Editor y mapa no modificados en este diagnostico.

