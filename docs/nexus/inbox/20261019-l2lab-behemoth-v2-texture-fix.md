# Behemoth: correcci?n de cierre al invocar


## Correcci?n del cierre al invocar ? 19 octubre 2026

El cliente mostr? `Assertion failed: index < 5` en `User::GetNpcTexName` al invocar. El prototipo anterior ten?a ocho slots de textura. Se agruparon los seis materiales del equipo en un atlas, manteniendo las dos texturas del cuerpo: tres slots en total e ?ndices 0..2. Se ajustaron UVs y materiales de las caras/cu?as sin cambiar posiciones, pesos ni esqueleto.

Nuevo paquete instalado ?nicamente en client-lab/system, junto al npcgrp corregido. Los 6523 registros originales se conservan; DAT encode/decode exacto. UModel extrae 98 huesos y tres materiales; las tres texturas extra?das son id?nticas p?xel a p?xel al origen. Evidencia: texture-limit-fix.json, native-roundtrip-3mat.log. Scripts: pack_native_materials.py e install_3mat_fix.py; build_native.py y prepare_lab.py actualizados. Los informes anteriores de ocho materiales corresponden al prototipo que produjo el cierre y quedan superados por esta correcci?n.

Reabrir el cliente privado con 26-PROBAR-BEHEMOTH-L2.cmd para que lea ambos archivos nuevos; no requiere reiniciar el servidor. Si la montura sigue invocada puede mostrarse al entrar. La ejecuci?n visual dentro de L2 sigue pendiente hasta repetir la prueba.
