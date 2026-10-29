# Amber / GroupAgite: coordinación de compilación

Sesión Amber, proyecto real `E:\l2-local`, 09/10/2026 alrededor de 20:46.

Al reiniciar para probar movimiento/ataque/altura de Amber, el compilador global
rechazó GroupAgite.java (líneas 104 y 400): calculateDistance2D(x,y) no existe en
el core instalado. Se corrigieron SOLO esas dos llamadas agregando getZ() como
tercer argumento; la implementación 2D lo ignora y la lógica queda igual.
El archivo GroupAgite completo compiló contra el GameServer.jar actual.

No se cambiaron el core, sus conductas, roster ni configuración. La otra sesión
debe conservar estos dos ajustes si reemplaza el archivo; de lo contrario no se
carga ningún script del servidor. Se reinicia GameServer con verificación Amber
optativa y dos probes privados, tras confirmar L2 cerrado y cero conexiones.
