# Tanda 2 v11 ? instalada; comprobaci?n visual pendiente

El usuario confirm? que en v10 s?lo se ven correctamente MElf I y FDwarf J. Ambos usan un material; los otros cinco usan dos. La preparaci?n v11 cambia esos cinco a un atlas de un material. Las dos mallas confirmadas siguen referenciando sus objetos de NexusHairT2V10, sin recompilar ni reemplazar los recursos activos de v10.

Cada atlas conserva los p?xeles originales de ambos componentes, a?ade margen replicado y remapea las UV a su regi?n. La geometr?a orientada se conserva. UCC fusiona unas cu?as UV cercanas en MDarkElf y MShaman, con error inferior a medio p?xel del atlas. No se considera prueba de funcionamiento visual en el cliente: las pruebas de asignaci?n multi-material de v10 no bastaron para demostrarlo.

El usuario eligi? activar primero A-D naturales: A original, B casta?o, C rubio, D plateado. Siete texturas por color, 28 FinalBlend en total, con alfa id?ntico. Se aplican m?scaras de tinte para proteger gafas, m?scaras, adornos y el detalle tatuado del elfo corto. Las m?scaras son ajustes de las regiones de textura del donante; se pueden refinar despu?s de la revisi?n del usuario. Tonos-A-D.jpg y color-previews son renders de los recursos compilados fuera del juego.

Verificaci?n: geometr?as y UV, cinco atlas con regiones de p?xeles originales id?nticas; dos referencias de mallas confirmadas conservadas; 28 texturas RGBA id?nticas tras compilar; alfa y p?xeles protegidos sin cambios; 28 materiales cargados/exportados por UCC nativo con cero errores/advertencias. Pasan 2303 casos de regresi?n, 15486 de Tanda 2 y 5824 casos de conteo m?s 112 replays del bucle nativo para los colores A-D. El selector nativo ya contiene cuatro etiquetas de Hair Color (179..182), comprobado en 10198f73..10198fae.

Instalaci?n en system-hud y system-camera-online: engine.dll, NexusHairT2V11.u y NexusHairT2M11.utx en SysTextures. Formato 121, CRC independiente y descifrado exacto. No se cambi? NWindow, servidor, personajes, originales, Tanda 1 ni caras. Las letras de los siete siguen H/I, H, H, H, J y J. La elfa clara femenina permanece fuera.

El usuario pregunt? por un selector tipo Windows de tono, saturaci?n y luminosidad. No se implement? un selector libre RGB/HSL: el protocolo/estado actual usa un ?ndice 0..3, y esa ampliaci?n necesita interfaz, representaci?n, persistencia y transmisi?n del color independientes. Esta versi?n a?ade s?lo A-D, como eligi? el usuario.

Reversi?n global de Tanda 2: el script v9/rollback.py tiene el manifiesto actualizado para reconocer v11 y volver a los archivos anteriores a Tanda 2. Si ya hay personajes guardados con esos ?ndices nuevos, revisar sus apariencias antes de retirar los recursos; no se modifican autom?ticamente personajes de usuario. Las versiones v9/v10 y copias hist?ricas se conservan para diagn?stico. installation.json contiene el backup actual.
