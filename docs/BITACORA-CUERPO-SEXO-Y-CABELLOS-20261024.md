# Bit?cora previa ? cuerpo, sexo y correcci?n de cabellos

24/10/2026. Usuario autoriza implementaci?n reversible y solicita corregir primero cabello invisible.

## Punto de partida y acuerdo
- Integraci?n anterior: research/character-creation/2026-10-24/integration; instalada en system-hud y system-camera-online, con respaldo character-appearance-20261024-005140.
- El usuario muestra cabello invisible y etiqueta Hairstyle vac?a en creaci?n (elfo masculino Fighter). La validaci?n previa no incluy? prueba visual real. Se investigar? antes de avanzar con estad?sticas.
- Sistema actual separa raza visual, origen de atributos (raza + Fighter/Mystic) y profesi?n. No existe selector de cuerpo independiente.
- Objetivo autorizado: combinaci?n modular de raza, cuerpo y profesi?n; el cuerpo aporta una diferencia peque?a con contrapartidas, evitando contar dos veces el perfil Fighter/Mystic.
- Sexo acordado: masculino +1 STR/CON/INT y -1 DEX/WIT/MEN; femenino inverso. WIT es casteo. Implementaci?n reversible.
- Propuesta concreta de cuerpo se documentar? antes de aplicar: base racial Fighter + desplazamiento parcial hacia perfil Mystic seg?n cuerpo elegido, conservando como modalidad heredada los perfiles actuales hasta elecci?n expl?cita. No migrar silenciosamente personajes existentes.

## Procedimiento
1. Investigar etiquetas y recursos de cabello; respaldar cada cambio y verificar en cliente real si el control de aplicaciones est? disponible.
2. Implementar elecciones modulares persistentes y vista previa en el servicio existente; sincronizar fuente, runtime y overlay.
3. Comprobar f?rmulas, persistencia, cambios de clase, modelo visual y restauraci?n; registrar limitaciones honestamente.

## Avances
- Bit?cora creada antes de modificar la integraci?n.

### Diagn?stico y correcciones de cabello
- v2 retir? una condici?n redundante de acceso a recursos y prob? etiquetas sobre IDs vac?os. El usuario confirm? que no alcanz?; no se considera resuelto.
- v3 produjo evidencia real en resource-trace.bin: el creador solicita los ?ndices nuevos y el motor ejecuta ambos hooks. Se usaron temporalmente etiquetas F/G existentes.
- Hallazgos comprobados: la UI dibuja etiquetas indexando una tabla FString de tama?o fijo; los IDs nuevos no pueden a?adirse como un DAT sin adaptar ese acceso. Las texturas importadas tienen bMasked=false y carec?an del FinalBlend de los cabellos nativos.
- v4 instalado: 112 materiales FinalBlend con FB_AlphaBlend, AlphaTest, TwoSided y AlphaRef=5, iguales al material nativo. Etiquetas directas F/G o H/I seg?n posici?n, preservando el camino original. Se retir? el diagn?stico del motor y se restaur? sysstring-e.dat original. Pruebas: 2179 escenarios x86, 10 escenarios de etiquetas incl. rebasing, carga de 112 materiales + 112 texturas sin fallo. Pendiente respuesta visual del usuario.

### Dise?o modular concreto preparado (sin instalar a?n)
Se conserva el origen racial actual de nueve perfiles, incluidos Fighter/Mystic. No se suma una segunda plantilla completa: se a?aden ajustes peque?os del cuerpo, con presupuesto neto cero. Este dise?o reemplaza la propuesta preliminar de partir siempre de Fighter, para conservar las elecciones anteriores del usuario.
Orden de columnas: STR, DEX, CON, INT, WIT, MEN.
- Humano Fighter: +1,0,+1,-1,-1,0.
- Humano Mystic: -1,0,-1,+1,+1,0.
- Elfo Fighter: -1,+2,-1,0,0,0.
- Elfo Mystic: -1,0,-1,0,+2,0.
- Elfo oscuro Fighter: +2,0,-1,0,0,-1.
- Elfo oscuro Mystic: -1,0,-1,+2,0,0.
- Orco Fighter: +1,-1,+2,-1,-1,0.
- Orco Mystic: 0,-1,+1,0,-1,+1.
- Enano: 0,-1,+2,-1,0,0.
- Masculino: +1,-1,+1,+1,-1,-1; femenino exactamente inverso.
Configuraci?n editable: ModularAppearance.ini. Clase, skills, equipo y progreso independientes. Cuerpo determina raza visible/modelo; origen determina atributos raciales. Cambiar cuerpo o sexo reinicia pelo/cara a 0 para evitar combinaciones incompatibles.
Men? preparado .cuerpo enlazado desde .raza, con autorizaci?n GM existente (sin a?adir acceso p?blico ni cobros); vista previa, confirmaci?n, persistencia y restauraci?n personal. Personajes existentes optan al aplicar; nuevos personajes pueden activarlo por configuraci?n.
Compilados cinco cambios de core y servicio. Se conservar?n byte por byte los 845 cuerpos de m?todos ajenos al cambio, mediante graft de s?lo 12 m?todos seleccionados; ver graft-proof.txt. Pasaron 236 comprobaciones de presupuesto de puntos y modo heredado. Pendientes pruebas en motor, persistencia y activaci?n en vivo, despu?s de resolver cabello.

### Ajuste de posici?n y rechazo del paquete
- v5: se detect? que el paquete compilado ten?a origen/rotaci?n/escala gen?ricos. Se copiaron los valores exactos de los 14 cuerpos originales a sus 28 cabellos (p. ej. humano masculino Z=25.2, escala 1.03, yaw=49152). Se verific? la coincidencia de las 28 transformaciones y se instal? con el cliente cerrado; geometr?a y texturas permanecen iguales.
- El usuario report? despu?s un aviso real: Files are corrupted, ../SysTextures/NexusHairMaterialsV2.utx. Por tanto NO se consider? resuelto el cabello.
- Los 112 FinalBlend cargaron y se exportaron correctamente con UCC nativo (0 errores/advertencias). Se prepar? v6 usando envoltorio Lineage2Ver121 ligado al nombre exacto, como los paquetes personalizados existentes, en lugar de 111. CRC32 independiente y bytes descifrados comprobados para ambos paquetes.
- v6 instalado en ambos perfiles y SysTextures. Evidencia: research/character-creation/2026-10-24/hair-native121-v6. Pendiente confirmaci?n de arranque y aspecto real; no activar todav?a estad?sticas modulares.
- Sistema modular: archivos compilados, men? paginado, respaldo personal, restaurador global y agente de instalaci?n preparados. A?n sin modificaciones al servidor. Instalador exige hair-confirmation.json con comprobaci?n del usuario para respetar el orden solicitado.

### Confirmaci?n del cliente y correcci?n de casos puntuales
- El usuario confirm?: ?bien ya funciona?. Indic? dos defectos: caras nuevas del elfo oscuro masculino y un peinado de orca Fighter (letra pendiente).
- Se comprob? que las texturas masculinas nuevas usan MDarkElf_m001 (atlas completo) y el modelo viejo usa m000 (medio atlas). Se descarg? el DarkElf.ukx del mismo distribuidor, se extrajo la cabeza m001, se adapt? al esqueleto nativo y se instal? como NexusDarkFaceV7.ukx. S?lo D/E/F masculinos usan esa cabeza; A/B/C y el femenino conservan la suya. Pruebas: 2263 casos x86 y 348 tri?ngulos con geometr?a/UV conservados. Pendiente verificaci?n visual del usuario.
- Con el fallo general de cabello resuelto seg?n el usuario, se iniciar? la validaci?n/despliegue del m?dulo mientras se comprueban esos dos detalles. No marcar completa la apariencia de todos los modelos todav?a.

### M?dulo activado y verificaci?n final
- Primera activaci?n: pruebas del motor aprobadas, pero el constructor Script del men? exig?a contexto de carga. El agente restaur? clases vivas y el instalador devolvi? los archivos originales autom?ticamente. No se modificaron personajes del usuario.
- Se corrigi? usando ScriptEngine.executeScript, la misma ruta de carga del servidor. Segunda activaci?n correcta: .cuerpo registrado y enlace desde .raza. Autorizaci?n GM/laboratorio conservada; no se public? ni se a?adieron cobros.
- Instalados 23 archivos entre fuente, runtime y overlay. Se conservaron 845 m?todos ajenos al cambio. Pruebas reales: dos pasadas de 648 combinaciones, 13.143 comprobaciones acumuladas (6.572 en la final), guardado/recarga/restauraci?n del personaje reservado BodySexProbe de modular-test. Adem?s 650 comprobaciones de men? y autorizaci?n. No se alteraron personajes, equipos o progreso del usuario.
- Respaldo activo: E:\l2-local\backups\modular-appearance-20261024-030347. Restaurador global: research/modular-appearance-20261024/rollback.py. Restauraci?n individual en .cuerpo, con confirmaci?n; no repone HP/CP/MP.
- El usuario precis? que la orca Fighter tiene hasta I: fallaba H; F, G e I s? se ve?an. El l?mite supuesto de cinco estilos era incorrecto: se corrigi? BASE[11] a siete originales y los dos nuevos son H=7 e I=8. Se restaur? el camino original de F/G y se corrigi? CharacterCreate para aceptar femenino hasta 8 sin excepci?n de orca.
- v8 instalado en ambos clientes, fuente/overlay y ambos JAR; clase CharacterCreate actualizada en vivo. Pruebas: 2.303 escenarios x86 y 13.608 escenarios de validaci?n del bytecode. Los respaldos originales del m?dulo se conservaron; se crearon bases de restauraci?n actualizadas para mantener esta correcci?n de cabello al revertir el m?dulo.
- Comprobaci?n final: hashes de 23 archivos del m?dulo y de las correcciones posteriores, clases presentes tanto en runtime como en sus bases de restauraci?n; puerto 7777 activo. Evidencia: research/modular-appearance-20261024/final-verification.json.
- Pendiente visual: comprobar H/I de la orca, D/E/F masculinos del elfo oscuro con la cabeza nueva y la interfaz .cuerpo. No afirmar que esas comprobaciones visuales ya se hicieron. El fallo general del cabello y el rechazo del archivo cifrado s? fueron confirmados resueltos por el usuario antes de estos ajustes puntuales.
