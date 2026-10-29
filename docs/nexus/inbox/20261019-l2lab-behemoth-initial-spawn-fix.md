# L2 Lab: Behemoth sigue sin validaci?n visual


## Segunda prueba real: segu?a elevado; correcci?n de inicializaci?n

El usuario volvi? a confirmar separaci?n del suelo. Inspecci?n en vivo: Hellkevin (83190,148920,-3455), geoZ=-3455, seated=false, movementDisabled=false. NPC (83049,148950,-3495), geoZ=-3495, colisi?n54/radio63. El NPC no ten?a Z por encima de su propia geodata. Esto no prueba la colocaci?n del modelo cliente.

El adaptador anterior modificaba dimensiones DESPU?S de summon/spawnMe: el m?dulo vivo segu?a creando primero con altura120. Un NpcInfo posterior no demuestra que SetSpawnResource recalcule el origen del Pawn existente. Se corrigi? el c?digo activo recargando ?nicamente custom.BehemothTransport.BehemothTransport mediante Instrumentation.redefineClasses; ning?n core fue redefinido. Estructura de clases conservada. Ahora el constructor NpcTemplate recibe radio63/altura54 ANTES del primer spawnMe. El servidor fr?o usa ese mismo fuente.

ReloadBehemothModule intent? reconstruir cliente-side los NPC existentes, pero en ese momento el mapa owned ya estaba vac?o (el usuario hab?a salido). El smoke V3 us? actores temporales, confirm? los valores iniciales y pas?16 checks; elimin? sus actores al finalizar. No son clientes reales y no certifica que se haya eliminado la flotaci?n. Evidencias: live-height-inspection.txt, module-reload.txt, server-smoke.json. Pr?xima verificaci?n visual debe distinguir altura de geodata y altura de dibujo; no seguir ajustando Z al azar. Subir/conducir siguen bloqueados.
