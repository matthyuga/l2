# Color libre dentro del creador de Lineage II

## Alcance y estado

Análisis solicitado del cliente instalado, mediante REA sobre una copia inmutable de NWindow.dll. El objetivo es un panel integrado en el espacio superior derecho del creador, con elección Clásico / Libre. Las demostraciones web y Win32 previas no satisfacen por sí mismas esta integración. Este estudio no instala todavía el selector: no se ha modificado ningún archivo del juego.

## Lo confirmado en el binario

Cliente x86. Direcciones virtuales referidas a ImageBase 0x10000000; al programar se deben utilizar RVA y la base real del módulo. SHA-256 de la copia: cba1831bb0c6c28b0ab18db47d861a5b87f6f3ac0de85cc55bf8606cac4c2c2d.

| Pieza | Dirección / campo | Evidencia |
|---|---|---|
| Contenedor del creador | NCPawnCreateWnd, vtable 0x102923c4 | RTTI PE .?AVNCPawnCreateWnd@@, constructor escribe la vtable en 0x1019a215 |
| Inicialización del contenedor | 0x1019a2d0 | REA ev_cf7a8939736f116aa36493221f67b21424b954cea661f0e7b01aefa3a72bec52 |
| Panel de opciones izquierdo | NCPawnSetupWnd, hijo en creador+0x1cc | Constructor 0x10199c80, inicialización 0x10199dc0 |
| Dibujo del panel izquierdo | 0x101977d0, slot vtable+0x18c | REA ev_16f57933801bafe0cdd74f02a05c23019417cb860b5b3ce07fe8d4c952c7c08a |
| Dibujo heredado del contenedor | slot +0x18c apunta a 0x10059eb0, que retorna 0 | REA ev_da3e5c975a15455965e554c47bce7431c241b23dc40acdb488a918845ad2ba34 y lectura PE de la vtable |
| Hair Color | control hijo +0x1dc, ID 0xf0a6b5 | REA ev_0e7289ccdfbc62bf05ebe69301922d53a8fa5a1f30f59ecfac977b04ef424f1e |
| Índice de color del creador | NCPawnSetupWnd+0x200 | Setter 0x10197e70, slot vtable+0x204 |
| Aplicación de apariencia | User::SetPawnResource | Setter de color copia User de previsualización y solicita de nuevo sus recursos |
| Confirmación de creación | 0x10198b10 | REA ev_326ebc3dc9686fbe6326b2591d038ec708196da7136dcee54633cdb3dd90c49a: lee hijo+0x200 y llama 0x10142000 |

El fondo izquierdo es L2UI_CH3.LobbyWnd.select2_back. La inicialización crea controles UObject y los registra como hijos con 0x10060d40. Esto respalda añadir un hijo al contenedor, con dibujo y eventos dentro del sistema de ventanas del juego. La convención de llamada exacta y el enrutamiento de ratón aún requieren validación antes de escribir un hook ejecutable.

El dibujo izquierdo limita su propio rectángulo de recorte. Dibujar el selector derecho desde ese bloque sin restaurar recorte/origen puede ocultarlo o afectar otros controles. Tampoco se debe modificar globalmente 0x10059eb0: es un método heredado compartido. La integración debe afectar solamente a NCPawnCreateWnd o a un nuevo hijo suyo.

## Interfaz propuesta para el área indicada

Panel de 274 × 296 unidades, anclado arriba a la derecha con margen 20 horizontal y 32 vertical. En un viewport 1024 × 668 su origen sería (730,32). Es una geometría inicial; debe comprobarse con el escalado real de L2, otras resoluciones y los controles inferiores.

1. Cabecera «Color del cabello» y selector «Clásico / Libre».
2. Clásico, seleccionado inicialmente: Hair Color A–D conserva su comportamiento; los controles HSL están plegados.
3. Libre: el panel muestra plano de tono/saturación, barra de luminosidad, valores H/S/L, muestra de color y HEX opcional. Hair Color A–D queda deshabilitado visualmente mientras este modo está activo.
4. Cambiar a Clásico recupera exactamente el último A–D. Cambiar a Libre recupera el último HSL de esta sesión del creador.
5. El color libre actualiza la previsualización al arrastrar. «Restablecer» recupera la selección inicial. «Create Character» confirma apariencia y color juntos; «Previous» descarta el estado de creación.

No se necesita una ventana de Windows independiente. Los cálculos HSL/RGB de la prueba anterior son reutilizables; su ventana HWND no es la interfaz que se integrará.

## Datos y materiales

Mantener un estado adicional: modo, índice clásico 0..3, HSL, RGB derivado y revisión de apariencia. No escribir RGB en +0x200: ese campo sigue utilizándose como índice para recursos. Al cambiar raza, sexo, arquetipo o peinado se debe invalidar el material temporal y reconstruirlo con el nuevo cabello.

La previsualización necesita un material por instancia que modifique solo el cabello, conservando alpha, piel, máscaras y adornos. La existencia de UColorModifier y UConstantColor está confirmada en engine.dll, pero aún no demuestra que el material compuesto y las máscaras funcionen para todos los cabellos. Hay que validar esa ruta en una malla antes de extenderla. No modificar texturas compartidas: podría cambiar el color de otros personajes.

Servidor y protocolo también forman parte de esta función: actualmente la creación valida 0..3 y PlayerAppearance utiliza byte para hairColor. Mantener ese dato clásico y guardar el color personalizado por separado es la propuesta de compatibilidad. La transmisión y lectura cliente de ese dato aún deben definirse y verificarse. Un selector que solo tiñe el creador no termina la función: el color debe sobrevivir creación, relog y ser visible para otros jugadores.

## Secuencia de implementación y comprobación

1. Añadir panel hijo exclusivo de NCPawnCreateWnd y validar dibujo, escala, ratón, arrastre y foco. Usar la v14 como base y conservar sus hooks de peinados y rostros.
2. Conectar Clásico/Libre al estado separado; comprobar restauración A–D y limpieza al salir del creador.
3. Validar material de cabello por instancia, alpha y protección de piel/adornos; probar original, tanda 1 y tanda 2. No reintroducir las caras retiradas del orco.
4. Implementar persistencia y sincronización del color separado, con fallback A–D para datos ausentes y validación de rangos.
5. Verificar creación, selección, relog, segundo cliente, cambios de raza/sexo/peinado y repetición de entradas/salidas sin fugas de recursos. Recién después instalar una versión con backup y rollback.

Las direcciones proceden de análisis estático, no de una prueba interactiva del panel en el juego. Permanecen pendientes el ABI completo de dibujo/eventos, el material dinámico y el recorrido de persistencia. La conclusión del estudio es que existe una ruta concreta de integración nativa; no que el selector ya esté conectado o probado en el cliente.
