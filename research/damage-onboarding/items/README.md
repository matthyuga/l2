# Ítems del cliente Damage y alcance de la tienda

Análisis del 17/10/2026 solicitado por Kevin. Datos leídos del cliente instalado de Damage y comparados con la copia base Interlude previamente descargada. No se modificó el juego ni se realizaron canjes.

## Actualización: precios y pertenencia observados

Nueva tanda revisada: Shot00114–00140, votos, GMShop y servicios. 23 ofertas por Adena, aviso de requisito nivel 80 para voto, Symbol Maker e Information. Ver [GMSHOP-Y-SERVICIOS-114-140.md](GMSHOP-Y-SERVICIOS-114-140.md). Noblesse Letter aparece también por 200.000 Adena. El panel anuncia +20 y los pergaminos normales/blessed muestran [+16]; límites reales sin probar.

Después de la extracción, Kevin guardó 82 capturas adicionales con artículos seleccionados (Shot00032 a Shot00113). Se revisaron todas y se registraron productos, cantidades y monedas en [CATALOGO-TIENDA-OBSERVADO.md](CATALOGO-TIENDA-OBSERVADO.md), con enlaces a cada original. `shop-observations.json` conserva también SHA256 por imagen. Dos imágenes repiten una oferta y dos costes están tapados por tooltips. No se afirma que la tanda agote todas las entradas de la tienda.

Esto resuelve pertenencia y precios para los artículos legibles de esa tanda; las limitaciones de las secciones anteriores se refieren a lo que podía establecerse solo con DAT/REA. Los efectos siguen siendo textos anunciados, no mediciones. Hero Crown figura por 20 Donator Coin o 30 Festival Adena; Tattoo Legend por 30.000 Damage Coin más Tattoo Unique. Ring of Baium figura por **10** Donator Coin o 5.000 Damage Coin; se corrigió la primera lectura rápida de 1 Donator Coin.

## Resultado de extracción

- Damage: 9.323 registros de nombres/descripciones.
- Base de comparación: 9.144 registros.
- 179 registros con ID ausente en esa base y 1.139 registros distintos en algún campo.
- Los archivos se consumieron completos salvo el marcador explícito SafePackage de 13 bytes. Identidad SHA256 y cobertura en `manifest.json`.
- Estas cifras describen el catálogo local completo, no el inventario del NPC. Una diferencia respecto de esa base no demuestra que Damage haya creado el objeto ni que esté disponible en el servidor.

Archivos de resultados:

- `damage-items.csv`: catálogo local completo, ID, nombre, variante, descripción y textos de set.
- `baseline-items.csv`: catálogo base de comparación.
- `added-items.csv`: IDs presentes únicamente en Damage respecto de esa base.
- `changed-items.csv`: registros que difieren de la base.
- `keyword-candidates.csv`: selección por palabras clave; no prueba pertenencia a la tienda.

## Hallazgos concretos del catálogo

La tabla resume **lo anunciado en los textos del cliente**. No acredita efecto real, precio o venta actual por el NPC.

| ID | Nombre / variante | Descripción resumida |
|---|---|---|
| 5575 | Damage Coin | Anuncia obtención de monstruos en zonas de farmeo. El mismo ID en la base se llama Ancient Adena |
| 6673 | Festival Adena | Anuncia moneda de recompensa de eventos |
| 9501 | Voter Coin | Dice que se obtiene por votar y se canjea por objetos en Unique Shop |
| 9502 | Donator Coin | Anuncia obtención por donaciones en la web |
| 9500 | Hero Crown | Anuncia estatus hero con skills durante 24 horas |
| 9503 | Noblesse Letter | Anuncia otorgar estatus noblesse al usarlo |
| 10000 | Clan Reputation Crystal | Anuncia +1.000 puntos de reputación de clan |
| 487 | Tattoo of Resolve / Wind Walk | Anuncia velocidad de movimiento +33 |
| 492 | Tattoo of Soul / Haste | Anuncia Atk. Spd. +10% |
| 493 | Tattoo of Avadon / Acumen | Anuncia Casting Spd. +10% |
| 495 | Tattoo of Damage / Unique | Anuncia Atk. Spd. +10%, Casting Spd. +10%, movimiento +13 |
| 496 | Tattoo of Damage / Legend | Anuncia Atk. Spd. +13%, Casting Spd. +13%, movimiento +15 |
| 9999 | Rebirth List / Rebirth | Texto que lo vincula con un sistema rebirth |
| 50001–50003 | Book of Rebirth | Texto que lo vincula con aprendizaje de habilidades rebirth |

También hay registros de joyas épicas, accesorios visuales y armas llamadas Chaotic con variantes de SA. Su presencia no demuestra que se vendan aquí o que estén habilitadas. Los iconos de las capturas no bastan para asignar inequívocamente IDs, variantes o efectos.

## Qué se comprobó en la ventana de tienda

Se leyó el ScriptText previamente extraído de `E:\l2-damage\analysis\interface-scripttext\damage\MultiSellWnd.uc`:

- Registra eventos EV_MultiSellShopID, EV_MultiSellItemList, EV_MultiSellNeededItemList y EV_MultiSellItemListEnd.
- HandleItemList recibe classID y consulta UIDATA_ITEM.GetItemInfo para información local del objeto.
- HandleNeededItemList recibe ClassID, count y enchant para los requisitos. Obtiene nombre e icono con UIDATA_ITEM.
- OnClickItem llena los paneles de información y requisitos para la entrada seleccionada.
- m_itemList se inicializa y llena durante esos eventos; el ScriptText no contiene un catálogo fijo de Unique Shop.

Es evidencia de texto embebido extraído del paquete, no fuente original certificada ni observación del bytecode ejecutado. La ventana permite mostrar información de objetos definida localmente y requisitos recibidos por evento. No se recuperó una lista actual de venta de Damage a partir de este texto.

## Métodos y límites

Para DAT se usaron el decodificador 413 y el esquema Interlude de L2ClientDat ya disponibles en el proyecto, más un lector de solo lectura en `../analyze_items.py`. La extracción DAT no es evidencia producida por REA. El parser conserva hashes y comprueba número de filas, límites de lectura y marcador final.

REA abrió la copia de nwindow.dll del parche V3.4: PE x86, SHA256 `2ad19421ad55c3a24ad481eb511dd0d0331ad3fd0bb82bedce178bfd0b37313a`. Ghidra 12.1.4 completó la descompilación dirigida de execRequestMultiSellChoose, dirección `0x10103bf0` identificada en el inventario previo de exports. Evidencia nueva `ev_258d5e91bcfa4d1e73a20fa51efd0a120c39bed98c81ab35661f3e975e3781ae`, preservada completa en `rea-multisell-choose.json`.

El pseudocódigo lee los campos ShopID, ItemID, ItemCount, RefineryOp1 y RefineryOp2, los agrega a L2ParamStack y delega mediante llamada virtual en desplazamiento 0x414. Esta función no contiene una lista fija de productos ni precios. El destino final de esa llamada no se resolvió; no se atribuye un opcode al argumento 10 del constructor ni se afirma haber recuperado las reglas del servidor. El pseudocódigo es una reconstrucción de Ghidra, no código fuente original. No se ejecutó ninguna compra para obtener esta evidencia.

Los efectos efectivos los decide el servidor remoto. Para una lista exacta del NPC hacen falta los datos de la lista recibida o capturas seleccionando cada entrada y sus requisitos. No se hizo lectura de memoria del proceso, captura de credenciales, instrumentación ni envío de solicitudes inventadas al servidor.

Próxima evidencia útil: una captura con un ítem seleccionado, su nombre/tooltip y el panel Items required visible. Con eso se cruza el producto con el catálogo extraído y se registra su coste sin comprarlo.
