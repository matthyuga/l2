# Corrección de opacidad al abrir otras interfaces — V3, 25/10/2026

Kevin confirmó cobertura de Giran V2, pero aportó capturas donde abrir stickers, inventario o clan permite ver el mapa debajo de la niebla. El INI permanecía Mode2. Se investigó con REA/Ghidra, no se asumió que fuera un problema de z-order.

## Causa confirmada estáticamente

NCGDevice::GetFinalAlpha RVA21590 recibe un byte. Cuando vale255(0xff), hereda el byte del dispositivo en+0x74; si el dword+0x70 es distinto de0, además divide esa opacidad por2. Los valores0..254 se devuelven directamente. Por tanto, pasar255 NO fuerza opacidad máxima: solicita la opacidad contextual de la interfaz.

Evidencia de pseudocódigo ev_cab7227779222a3073cd7746d337be230c3c20bfd262c897c1668aacd2d98c90 y ensamblado ev_0a930eade92cef28ba8e24221cc5975ddd0c7f672b6fc56d339981b5b11fe244, exportadas en ../map-fog-giran-v2/rea-alpha-fix-evidence.json. NWindow SHA256 sigue siendo el de V1/V2.

## Cambio

Durante PaintFog se guarda exactamente el dword+70 y byte+74 del dispositivo; se establece0 y255 respectivamente; se dibuja la cobertura y se restauran los valores. La restauración usa __finally para ejecutarse también ante excepciones. El resto del mapa, botones y demás ventanas conserva su estado anterior. Se conserva el alfa por píxel de la máscara de Giran: el claro y sus bordes no se vuelven opacos.

No se cambiaron texturas, INI, región ni código del servidor. Los modos parcial/opaco/apagado siguen disponibles. Corrección confinada a una DLL nueva del proxy propio, con guardias e instalación con cliente cerrado.

## Pruebas

20396 comprobaciones nativas PASS: matriz de cinco opacidades y dos estados de foco, alfa explícito180, opacidad completa durante callback y restauración exacta después, incluyendo una excepción provocada deliberadamente. Incluye pruebas previas de recorte/proyección de franjas,20.000 llamadas a trampolines y restauración. Proxy D3D9 factory/HAL oculto/16 Present PASS.

Falta validación visual dentro de L2: abrir mapa con modo opaco, abrir/cerrar inventario, clan y stickers y confirmar que no reaparece terreno fuera de Giran; comprobar que el resto de ventanas no cambia de transparencia. Las pruebas de harness no acreditan esa comprobación visual.

installation.json registra el estado y el respaldo de V2 cuando se aplica. restore.py vuelve a V2 con el cliente cerrado; si se desea retirar toda la implementación, restaurar luego V2 y V1 en ese orden.
