# HSL integrado en el creador: requisito corregido

El usuario quiere el selector DENTRO de Lineage II, arriba a la derecha del creador, con opción Clásico A–D / Libre HSL. Las demos web/Win32 no satisfacen esta integración. No volver a presentarlas como solución instalada.

REA sobre NWindow v14 identificó NCPawnCreateWnd (RTTI, vtable 0x102923c4), init 0x1019a2d0, hijo NCPawnSetupWnd en +0x1cc, color clásico en hijo+0x200 y setter 0x10197e70. El contenedor permite estudiar un hijo propio; el panel izquierdo recorta su dibujo, no sirve dibujar a la derecha bajo ese recorte. El slot de dibujo heredado apunta a un método compartido: no hookearlo globalmente.

Informe y evidencias: E:\l2-local\research\character-creation\2026-10-26-hsl-ingame-rea\README.md. Pendientes ABI/eventos, material dinámico por instancia con alpha/máscaras, persistencia y sincronización. No meter RGB en el índice clásico. No se instaló ningún cambio; NWindow de ambos perfiles conserva hash v14 cba1831bb0c6c28b0ab18db47d861a5b87f6f3ac0de85cc55bf8606cac4c2c2d. Mantener retirada la cara problemática del orco.
