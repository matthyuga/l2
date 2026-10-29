# Etiqueta compacta y transparente V3

14/10/2026. Captura real del usuario confirma que NPC hook V2 hizo visible el cartel. No atribuir la solucion a TriggerDisabled o wrapper111 por separado: ambas pruebas previas seguian invisibles.

Usuario solicita compacto y/o transparencia; efectos se agregaran despues. Preparada textura512x256 con fondo alpha48/255 (81% transparente) y borde alpha130. Dos lineas HELLGAMES/EVENTO, sin el espaciado ancho anterior. Sprite StartSizeRange20x10 (antes55x13.75) y altura local18 (antes90); UniformSize=False y UseRegularSizeScale=False explicitos para evitar escala uniforme/deformacion. El cartel sigue orientado a la camara. Motes Disabled=True por ahora. HGLabelArtV3.u contiene solo la textura nueva; HellgamesLabelsV1.EventGold conserva clase/nombre para que el hook instalado siga funcionando.

Lectura nativa verifica tamaños, altura, referencia de textura y estado de emisores; paquetes en wrapper111 con roundtrip exacto. No modifica NPC hook, npcgrp, stats ni servidor. La proporcion/altura dentro de L2 necesita otra captura; los valores nativos no prueban el aspecto final.

install.py necesita L2 cerrado y hash del paquete vigente igual a la preparacion. Respaldo y rollback completo se actualizan para incluir la textura nueva. No ejecutar instaladores historicos sobre cambios posteriores.
