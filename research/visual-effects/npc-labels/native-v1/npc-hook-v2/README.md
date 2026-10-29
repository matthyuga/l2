# Etiqueta: enlace explicito desde el NPC

14/10/2026. El usuario informa que ni etiqueta ni halo nativo aparecen tras wrapper111/control. No se ha podido inspeccionar la ventana oculta de L2: Computer Use no conecta al pipe y el escritorio muestra VS Code.

Se preparo HGLabelNpcV2.u a partir del paquete aislado athenas.u de Custom NPC With Logo. Su clase Npc hereda LineageWarrior.LineagePawn; PostSetPawnResource crea un Emitter, lo adjunta a Bip01 Neck1 y ajusta su posicion. Los metodos Detach, ClearL2Game y Destroyed limpian la referencia y retiran el efecto. Se reviso el texto del script y se cambio exclusivamente la constante de clase de Spawn de athenas.effect a HellgamesLabelsV1.EventGold. Longitud de bytecode identica; funciones y clase pasan lectura nativa. Se conserva el resto del paquete como referencia; sus efectos originales no se invocan en la clase Npc modificada.

El display59030 cambia solo class_name a HGLabelNpcV2.Npc y retira los dos deco_effect de la prueba anterior. Malla/texturas originales preservadas. HGLabelNpcV2.int copia la configuracion de animaciones del trader humano original en seccion Npc. Paquete/int en wrapper111 y npcgrp413, con roundtrip exacto; todas las otras6522filas identicas. No cambia servidor, spawn o stats.

Pendiente revisar carga real, aparicion de cartel/motas, orientacion, altura y retirada al alejarse del NPC. El attachment al cuello puede necesitar ajustar el offset del cartel tras ver el resultado. No afirmar que esta via ya funciona en nuestro juego sin una captura de prueba.

install.py requiere L2 cerrado y hashes de origen exactos. Respalda npcgrp y actualiza el manifiesto de restauracion completo para incluir los dos archivos nuevos. No reejecutar builders/instaladores historicos sobre versiones nuevas del cliente.
