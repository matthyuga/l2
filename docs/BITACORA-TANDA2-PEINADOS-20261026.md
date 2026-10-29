# Tanda 2 de peinados ? 26/10/2026

## Resultado visual comunicado por Kevin tras v10

Kevin informa que solo funciona uno de los dos peinados nuevos del elfo masculino y el de la enana; los otros cinco siguen viéndose mal. Ninguno cambia de color. Por tanto v10 NO resuelve visualmente la tanda completa; las pruebas anteriores de carga y emulación no equivalen a comprobación en el cliente.

Lectura de build_native.py confirma que colores 0..3 de Tanda 2 reciben los mismos materiales: no existen cuatro variantes de color en esta implementación. No atribuirlo a un selector roto. Kevin propone un selector como el de Windows, por matiz/saturación/luminosidad y RGB.

Pista pendiente de confirmar: MElf I y FDwarf J son las dos mallas de un único material; MElf H y los otros cuatro estilos tienen dos. Se preguntó si el elfo que funciona es H o I y si el resto presenta textura gris/equivocada o deformación. Coincidencia no establece todavía causa. No se modificaron cliente abierto, paquetes ni personajes en esta revisión.

Para tonalidades libres hay que distinguir UI de color de soporte real de material y persistencia/sincronización. El campo actual valida índices 0..3; un RGB arbitrario no funciona solo agregando un control. Preservar alfa, detalle del cabello y colores de gafas/máscaras/adornos mediante selección de material o máscara de región. No prometer tintado nativo continuo sin probarlo en este cliente.

Bit?cora creada antes de modificar los archivos activos. Autorizado: a?adir siete peinados concretos del paquete MEGA sin sustituir Original ni Tanda 1, dejando fuera la elfa clara femenina.

Selecci?n: elfo claro masculino origen D/E ? H/I; elfo oscuro masculino D ? H; orca Fighter C ? J; orco Fighter B ? H; orco Mystic D ? H; enana D ? J. Las capturas del usuario identifican estos siete dise?os.

Preparaci?n: manifiesto selection.json y hashes previos baseline.json en research/character-creation/2026-10-26-tanda2-v9. Se utilizar? un paquete nuevo con nombre propio. El selector y la validaci?n del servidor se ampliar?n s?lo para los modelos seleccionados. Originales, Tanda 1 y caras conservar?n sus recursos. No se tocar?n cuentas ni personajes de usuario.

Pruebas previstas: carga nativa de mallas/materiales, geometr?a/UV y esqueleto, hooks x86 y etiquetas, validaci?n Java por modelo/sexo, preservaci?n de entradas ajenas del JAR. Copias de seguridad antes de instalar y reversi?n registrada. La verificaci?n visual dentro del juego corresponde a la siguiente revisi?n del usuario.


## Instalaci?n final

# Tanda 2 v9 ? instalada el 26/10/2026

Siete peinados a?adidos, sin sustituir Original, Tanda 1 ni caras. Elfa clara femenina fuera de esta ampliaci?n por pedido del usuario.

| Modelo | Opci?n de origen | Letra nueva |
|---|---|---|
| MElf | D | H |
| MElf | E | I |
| MDarkElf | D | H |
| FOrc | C | J |
| MOrc | B | H |
| MShaman | D | H |
| FDwarf | D | J |

Nuevos paquetes: NexusHairT2V9.u en system-hud y system-camera-online; NexusHairT2M9.utx en SysTextures. Cada uno usa formato 121 ligado a su nombre, con CRC y descifrado id?ntico al original compilado. Los siete dise?os conservan sus texturas de origen. A/B/C/D de Hair Color apuntan a los mismos materiales para estos siete estilos en esta primera versi?n; los anteriores conservan sus colores.

Las mallas de esta tanda incluyen los adornos de las capturas (gafas, m?scaras y otros elementos). Sus materiales se compactaron de los ?ndices usados a 0/1, manteniendo geometr?a y texturas; las piezas originales con ?ndice 0 sin tri?ngulos se quitaron. Se adapt? el esqueleto al nativo. La malla MElf I tiene una variaci?n de UV inferior a 0.0001 por la uni?n de cu?as casi iguales que hace UCC; el informe num?rico est? en asset-test-results.json.

Verificaci?n: 2303 casos de regresi?n de hooks anteriores; 15486 casos nuevos de recursos, materiales, selector y ABI, con engine/UI reubicados; 15876 casos sobre el bytecode Java real; siete geometr?as orientadas y esqueletos; doce texturas RGBA id?nticas tras recompilar; doce materiales FinalBlend cargados/exportados por UCC nativo con cero errores/advertencias. La comprobaci?n visual en el cliente, movimiento, cascos y persistencia de un personaje real queda para la revisi?n del usuario. No se crearon ni modificaron personajes de usuario.

Se actualizaron fuentes locales y overlay, y ?nicamente las dos entradas de CharacterCreate en ambos JAR, preservando las dem?s. Clase principal redefinida en GameServer vivo con agente que comprueba que no haya clientes conectados. No se reinici? el servidor. Se actualizaron las bases de reversi?n del m?dulo corporal para que una reversi?n de ese m?dulo conserve esta ampliaci?n.

Preparaci?n: se corrigieron antes de instalar las banderas de los objetos FinalBlend, su paquete separado y la condici?n que evita duplicar opciones al reconstruir el selector. El modo -v del decodificador qued? esperando y se sustituy? por CRC independiente y descifrado comparado byte a byte. Ninguno de esos paquetes intermedios se instal?.

Reversi?n: python research/character-creation/2026-10-26-tanda2-v9/rollback.py, cliente cerrado y GameServer vivo. El script comprueba hashes, restaura la clase viva y archivos previos. No toca personajes: si ya se guardaron personajes con ?ndices de Tanda 2, revisar sus apariencias antes de revertir para no dejarlos con ?ndices sin modelo. No se ejecut? la reversi?n sobre la instalaci?n exitosa.

Copias y manifiestos: installation.json y su carpeta backup. Final: final-verification.json. Evidencia de REA del selector nativo: ev_b678f28a6d92239aa3a62b8a76b7b8f280f5e44a8ea16f4aafc31d462006eeb2; offsets UI raza 0x1f0, arquetipo 0x1f4, sexo 0x1f8 confirmados con el binario nativo.

Backup: E:\l2-local\backups\tanda2-v9-20261026-190956

La galer?a comparativa marca ahora los siete seleccionados con ?instalado como H/I/J?. Los restantes candidatos permanecen sin instalar.


## Fallo visual confirmado y reparaci?n v10

El usuario comprob? los siete y aport? capturas con materiales equivocados y grises. La integraci?n v9 no se considera visualmente v?lida. Causa comprobada: el PSK conserva VMaterial.TextureIndex=1/2 despu?s de compactar materiales a 0/1. UCC exporta MElf H con Tex1/material_1 y MElf I como material_0 sin textura. Las verificaciones anteriores comparaban geometr?a y las im?genes, pero no sus enlaces de material. Se corregir? TextureIndex y se ampliar? la carga nativa GetPcTexNum para los materiales de esta tanda. Preparaci?n separada en 2026-10-26-tanda2-v10. Cliente a?n abierto al iniciar; se solicit? cerrarlo antes de instalar.


## Reparaci?n v10 instalada

El usuario confirm? el cierre del cliente. Se instal? v10 en ambos perfiles, con paquetes nuevos y correcci?n de GetPcTexNum. Verificados los hashes y backups de los ocho archivos de instalaci?n; el manifiesto de reversi?n global de Tanda 2 est? actualizado y consistente. No se modific? servidor, selector, originales, Tanda 1 ni caras. Backup: E:\l2-local\backups\tanda2-v10-20261026-193622. La comprobaci?n visual de los siete estilos sigue pendiente.


## v10: resultado parcial y preparaci?n v11

Usuario: s?lo funciona uno de MElf y FDwarf J; los cinco de dos materiales siguen mal. Coincide con los dos dise?os de un material frente a los cinco de dos. La prueba anterior del bucle de asignaci?n no demuestra que el renderizador final aplique correctamente dos materiales en estas piezas. Se preparan atlas de una textura por peinado, conservando los p?xeles de ambas texturas con m?rgenes y remapeando UV; se seguir? la ruta de un material confirmada por el usuario. No se instalar? un selector RGB completo como parte de esta reparaci?n. Se pregunt? preferencia sobre recuperar A-D o conservar colores de origen.


## v11 instalada con A-D, pendiente visual

# Tanda 2 v11 ? instalada; comprobaci?n visual pendiente

El usuario confirm? que en v10 s?lo se ven correctamente MElf I y FDwarf J. Ambos usan un material; los otros cinco usan dos. La preparaci?n v11 cambia esos cinco a un atlas de un material. Las dos mallas confirmadas siguen referenciando sus objetos de NexusHairT2V10, sin recompilar ni reemplazar los recursos activos de v10.

Cada atlas conserva los p?xeles originales de ambos componentes, a?ade margen replicado y remapea las UV a su regi?n. La geometr?a orientada se conserva. UCC fusiona unas cu?as UV cercanas en MDarkElf y MShaman, con error inferior a medio p?xel del atlas. No se considera prueba de funcionamiento visual en el cliente: las pruebas de asignaci?n multi-material de v10 no bastaron para demostrarlo.

El usuario eligi? activar primero A-D naturales: A original, B casta?o, C rubio, D plateado. Siete texturas por color, 28 FinalBlend en total, con alfa id?ntico. Se aplican m?scaras de tinte para proteger gafas, m?scaras, adornos y el detalle tatuado del elfo corto. Las m?scaras son ajustes de las regiones de textura del donante; se pueden refinar despu?s de la revisi?n del usuario. Tonos-A-D.jpg y color-previews son renders de los recursos compilados fuera del juego.

Verificaci?n: geometr?as y UV, cinco atlas con regiones de p?xeles originales id?nticas; dos referencias de mallas confirmadas conservadas; 28 texturas RGBA id?nticas tras compilar; alfa y p?xeles protegidos sin cambios; 28 materiales cargados/exportados por UCC nativo con cero errores/advertencias. Pasan 2303 casos de regresi?n, 15486 de Tanda 2 y 5824 casos de conteo m?s 112 replays del bucle nativo para los colores A-D. El selector nativo ya contiene cuatro etiquetas de Hair Color (179..182), comprobado en 10198f73..10198fae.

Instalaci?n en system-hud y system-camera-online: engine.dll, NexusHairT2V11.u y NexusHairT2M11.utx en SysTextures. Formato 121, CRC independiente y descifrado exacto. No se cambi? NWindow, servidor, personajes, originales, Tanda 1 ni caras. Las letras de los siete siguen H/I, H, H, H, J y J. La elfa clara femenina permanece fuera.

El usuario pregunt? por un selector tipo Windows de tono, saturaci?n y luminosidad. No se implement? un selector libre RGB/HSL: el protocolo/estado actual usa un ?ndice 0..3, y esa ampliaci?n necesita interfaz, representaci?n, persistencia y transmisi?n del color independientes. Esta versi?n a?ade s?lo A-D, como eligi? el usuario.

Reversi?n global de Tanda 2: el script v9/rollback.py tiene el manifiesto actualizado para reconocer v11 y volver a los archivos anteriores a Tanda 2. Si ya hay personajes guardados con esos ?ndices nuevos, revisar sus apariencias antes de retirar los recursos; no se modifican autom?ticamente personajes de usuario. Las versiones v9/v10 y copias hist?ricas se conservan para diagn?stico. installation.json contiene el backup actual.

Backup: E:\l2-local\backups\tanda2-v11-20261026-200553


## An?lisis REA de los tres fallos restantes

Informe: research/character-creation/2026-10-26-rea-appearance-audit/README.md. REA confirm? las rutas de recursos en el engine instalado. MDarkElf G es Tanda 1 y tiene AlphaRef 5 frente a 160 del donante; material/depth es causa candidata del defecto visual. La orca J tiene un hueco real confirmado por el usuario; alfa/profundidad frente a cobertura geom?trica todav?a requiere prueba nativa localizada. MOrc Face F tiene incompatibilidad UV confirmada, tambi?n D/E; renders con cabeza donante m001 colocan las texturas correctamente. No se instalaron cambios durante el an?lisis.


## Reparaci?n v12 autorizada

El usuario pidi? encargarse de las tres correcciones despu?s del an?lisis REA. Preparaci?n antes de modificar cliente: restaurar AlphaRef 160 s?lo en G masculino DarkElf; material de recorte opaco para J de orca con AlphaTest 128, conservando su atlas y A-D; cabeza m001 del orco s?lo para caras D/E/F. Se conservar?n A/B/C y el resto de recursos. La reversi?n global de Tanda 2 se actualizar? para retener las dos reparaciones independientes de Tanda 1.


## v12 instalada

Se instalaron materiales dirigidos para MDarkElf G (AlphaRef 160) y FOrc J (recorte opaco 128), m?s cabeza MOrc m001 s?lo para D/E/F. Ambos perfiles actualizados; originales, Tanda 1 restante, texturas y colores de Tanda 2, NWindow y servidor conservados. Pasaron validaciones de activos, hooks y reversi?n. Pendiente revisi?n visual dentro de 2-JUGAR; no afirmar que la orca est? completamente corregida sin esa prueba. Backup: E:\l2-local\backups\appearance-v12-20261026-204628. Informe: research/character-creation/2026-10-26-appearance-v12/README.md.


## Critical error en cabeza de orco v12; reparaci?n v13

Usuario: al seleccionar el ?ltimo rostro de orco se cierra con General protection fault en FD3DRenderInterface::SetVertexStreams / USubSkeletalMeshInstance::DrawSection. Se constat? que MOrc_ModernFace v12 tiene Material=None en todas sus secciones LOD; a diferencia de MDarkElf_ModernFace v7 que tiene FaceDefault. Las comprobaciones anteriores no rechazaban una malla sin material predeterminado. Se preparar? un paquete nuevo con FaceDefault embebida, rutas nuevas s?lo para D/E/F de orco y verificaciones de materiales en todos los LOD. No se cambiar?n otros arreglos de cabello, colores ni A/B/C.


## V13 instalada

# Orco: reparaci?n de cabeza v13

Instalada el 26/10/2026. V12 provoc? un critical error confirmado por el usuario al mostrar el rostro del orco. La traza sit?a el fallo en SetVertexStreams / DrawSection, durante el dibujo de una secci?n esquel?tica.

Se detect? una diferencia respecto a la cabeza custom de elfo oscuro ya instalada: todas las secciones LOD de MOrc_ModernFace v12 ten?an Material=None. Faltaba importar una textura predeterminada y asignarla con MESHMAP SETTEXTURE. V13 incorpora FaceDefault (textura MOrc m001 t03) y la asigna al material 0, conservando geometr?a, UV y esqueleto. El hook sigue aplicando las texturas D/E/F seleccionadas encima del predeterminado. Las cuatro secciones LOD tienen ahora material expl?cito y ning?n Material=None. Es una correcci?n de un defecto real del paquete; la causalidad completa del crash y su ausencia despu?s del cambio todav?a requieren la prueba del usuario dentro del juego.

Paquete nuevo: E:/l2/Animations/NexusOrcFaceV13.ukx. Ambos engine.dll cambian s?lo la ruta UTF16 NexusOrcFaceV12.MOrc_ModernFace por NexusOrcFaceV13.MOrc_ModernFace. No se cambiaron las instrucciones, la UI, el servidor, las texturas de cabello, colores o personajes. Los materiales v12 de DarkElf G y FOrc J se conservaron.

Verificado: 206 puntos, 386 tri?ngulos, UV sin cambios, esqueleto id?ntico; todos los cuatro LOD con FaceDefault; textura RGBA exacta tras compilar; carga/exportaci?n UCC nativa correcta. Pasaron 2303 regresiones de hooks, 15486 casos de Tanda 2 y 5824 casos de conteo con 112 ejecuciones del bucle nativo de materiales. Esas pruebas no sustituyen el renderer D3D del cliente real.

Copias: installation.json y backup. La reversi?n global de Tanda 2 se actualiz? para conservar v13 y las reparaciones independientes de Tanda 1. Los scripts de rollback anteriores est?n protegidos por hashes y requieren revertir v13 primero; no deben ejecutarse forzando los hashes. Para retirar s?lo v13 se dispone de rollback.py. Pendiente: comprobar D/E/F en 2-JUGAR sin critical error, despu?s el resultado visual y los dos cabellos de v12.

Backup: E:\l2-local\backups\orc-face-v13-20261026-210332


## Retirada de caras nuevas del orco guerrero ? v14

Usuario pide eliminar la cara tras persistir el critical error v13. Se retiran D/E/F masculinas Orc Fighter del selector porque comparten la cabeza problem?tica. Cualquier ?ndice ya guardado D/E/F de ese modelo se dibujar? con cabeza/textura A nativa, sin tocar registros de personajes. Se conservan todos los cabellos y los otros modelos. No se seguir? intentando adaptar esa cabeza.


## v14 instalada: retirada de caras custom del orco

# Caras nuevas de orco retiradas ? v14

Por petici?n del usuario tras repetir el critical error v13, se retiran D/E/F del selector del orco guerrero masculino. Las tres compart?an la cabeza problem?tica; permanecen A/B/C. No se intenta una nueva cabeza custom.

El motor utiliza cabeza y textura A nativas para cualquier ?ndice D/E/F ya guardado en ese modelo. As? se evita cargar las cabezas v12/v13 aunque un personaje conserve su ?ndice. No se modific? ninguna fila de personaje ni el servidor. Las opciones de cabello, colores y caras de otros modelos se conservan.

Se actualizaron engine.dll y NWindow.dll en ambos perfiles, con backups. Los paquetes ?nicos v12/v13 se conservan inactivos para diagn?stico; no hay ninguna ruta hacia ellos en los nuevos engines. La reversi?n global de Tanda 2 tambi?n conserva la retirada de estas caras. Las revisiones anteriores y sus rollback est?n protegidos por hashes y no deben forzarse.

Pruebas: 2303 casos de recursos/ABI/selector; 15486 casos de Tanda 2, incluido mantener tres caras s?lo en Orc Fighter masculino; 5824 casos de conteo y 112 replays de materiales. Hashes instalados, backups y manifiesto global de rollback verificados. No se valid? visualmente el selector dentro del juego.

Backup: E:\l2-local\backups\orc-faces-removed-v14-20261026-211707


## Selector HSL ? prototipo e investigaci?n

Usuario eligi? selector libre HSL. Se prepara panel de vista previa con las siete mallas Tanda 2, colores y m?scaras reales. No se modifica cliente ni servidor. El almacenamiento actual PlayerAppearance usa byte y validaci?n 0..3; UserInfo/CharInfo transmiten un int. REA confirma UConstantColor::GetColor lee un color de 32 bits en offset 0x578, evidencia ev_5e843e43e7a2a0195de6ace877e005a89ef5f67e92647bcc4f3ae57b56d42c72. Eso demuestra un componente nativo de color, no una integraci?n HSL completa ni aplicable a todos los materiales.


Selector HSL: terminado prototipo local con siete modelos reales, H/S/L continuo, HEX, protecci?n de adornos, favoritos y exportaci?n JSON. Pruebas de navegador 20 PASS; 4096 conversiones HSL/RGB; v14 activo sin cambios. Ruta research/character-creation/2026-10-26-hsl-selector/index.html. Pendiente integraci?n en creador, motor, persistencia y sincronizaci?n; no presentarlo como instalado en juego. Enlace a?adido a galer?as abiertas.


## Preparaci?n de interfaz HSL nativa

Usuario pidi? preparar la interfaz propuesta. Se crear? ventana Win32 x86 estilo L2, componente DLL y demostraci?n, con eventos de preview/apply/cancel/reset para la integraci?n futura. Se comprobar? la restauraci?n exacta al cancelar. No instalar hooks incompletos de motor ni protocolo; v14 contin?a activo. El prototipo web anterior permanece disponible para las mallas reales.


Interfaz HSL nativa preparada: DLL y demo Win32 x86, HSL/HEX, botones y callbacks transaccionales. 4121 comprobaciones nativas, 50 ciclos DLL sin crecimiento de handles. Screenshot nativo revisado. No integrado/instalado al juego; v14 activo sin cambios. Paquete research/character-creation/2026-10-26-hsl-native-ui/Interfaz-HSL-nativa-preparada.zip, README con contrato y limitaciones.


## HSL dentro del creador: estudio REA

Usuario precisa panel integrado arriba a la derecha con modos Clasico A-D / Libre HSL. Identificados contenedor NCPawnCreateWnd, hijo NCPawnSetupWnd, selector y setter de color. Informe y evidencias en research/character-creation/2026-10-26-hsl-ingame-rea/README.md. Pendientes ABI/eventos, material por instancia y persistencia/sincronizacion. Sin instalacion; hashes NWindow v14 de ambos perfiles verificados sin cambios. Las demos externas no son la integracion solicitada.


## HSL ingame v1 en implementacion

Autorizado integrar. Preparados modulo x86 dentro del viewport, import hooks aditivos sobre v14, material por instancia, helper RGB separado en character_variables y cambios puntuales de cuatro paquetes servidor. 20506 checks nativos; 16394 protocolo; 26 PE/Unicorn. NO instalado en perfiles normales ni servidor. La preprueba runtime en perfil aislado detecto fallo de contrato de textura/material; pendiente diagnostico antes de instalar. Codigo e informes en research/character-creation/2026-10-26-hsl-ingame-v1. Computer Use native pipe no disponible.


HSL ingame v1 INSTALADO en ambos perfiles y cuatro clases de paquetes del GameServer activo 25292, sin reinicio. 20506 checks nativos, 16394 protocolo, 30 PE/Unicorn; preflight motor real PASS (textura dinamica, mascara/alpha, clon y panel); siete checks servidor real con probe reservado offline y limpieza exacta. Fog SHA guard actualizado para conservar compatibilidad. Backup hair-hsl-ingame-v1-20261026-230921; rollback.py con hashes. Visual de creador y creacion/relog pendiente del usuario. Codigo/manifest/final-verification en research/character-creation/2026-10-26-hsl-ingame-v1.


## HSL v2: destello y rendimiento

Usuario confirma funcionalidad visual v1 pero reporta destello original y lentitud. REA confirma setter nativo en cada arrastre y lectura INI en cada DrawTexture. V2 elimina consultas repetidas; cambia solo material por instancia durante RGB, preaplica tinte al cambiar apariencia y cachea plano H/S; LUT de luminancia acelera 524288 pixeles de 75.619 ms a 2.850 ms (~26.5x esa operacion, no FPS). 20506 checks +183 transiciones sin recarga; preflight motor real PASS. Instalada DLL en ambos perfiles, sin cambios servidor/hooks. Backup hair-hsl-ingame-v2-20261026-232116, rollback y manifest v1 rebased para retorno completo. Confirmacion visual v2 pendiente.


## Huecos de cabello: materiales alpha v3 preparados

Capturas usuario muestran huecos tambien en Clasico (MElf I). Inspeccion confirma 144 materiales custom mezclan FB_AlphaBlend2 con ZWrite=True; TwoSided ya activo. REA confirma campos nativos FinalBlend separados. Preparado FBOverwrite0 conservando recorte/alphaRef, texturas/mallas/referencias y HSLv2. UCC carga144 sin errores,395 checks y native121CRCroundtrip. Carpeta research/character-creation/2026-10-26-hair-alpha-v3. Pendiente instalar: cliente PID9256 abierto, pregunta de cierre enviada. No afirmar que todas las aberturas son blend; malla real puede requerir ajuste especifico.


2026-10-27: usuario confirma cliente cerrado. Instalado hair-alpha-v3 en tres paquetes compartidos SysTextures, 144 FinalBlend verificados en modo recorte opaco; HSLv2 intacto. Backup E:\l2-local\backups\hair-alpha-v3-20261027-001841. Manifiestos afectados actualizados, rollback.py listo. Verificacion visual de huecos pendiente.
