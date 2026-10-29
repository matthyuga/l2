# L2 Lab / Hellgames / Academy — 17/10/2026

Kevin pidió separar tres versiones. Implementación en `E:\l2-local\research\environments`; guía `E:\l2-local\L2-LAB-HELLGAMES-ACADEMY.md` y resultados `research\environments\VERIFICACION.md`.

- Lab actual permanece `E:\l2-local`, dirección 127.0.0.1, base/personajes/clientes actuales conservados. GameServer original PID17892 no se reinició.
- Hellgames independiente `E:\l2-hellgames`, 127.0.0.2; futura versión para jugadores, todavía local y sin publicar. Nace en muelle compartido; script HellgamesArrival evita tripulación experimental del Lab. Falta selector, servicios públicos y economía.
- Academy independiente `E:\l2-academy`, 127.0.0.3; servicios locales, un jugador y Coliseo. AcademyWorld limita coordenadas/altura/instancia y retorna tras salir. Roster y arena disponibles con `.roster preparar`, `.roster estado`, `.arena iniciar`; adaptación Academy permite preparar sin GM y telemetría pasiva sin benchmarks automáticos del Lab.

Cada copia tiene Java/MariaDB/core/cliente/config/base/logs/lanzadores propios, sin hardlinks ni sincronización automática. Bases inicializadas vacías desde esquemas nativos, sin importar cuentas/personajes del Lab; Academy puede crear perfiles técnicos propios. Tres servidores arrancaron simultáneamente en sus loopbacks. Puertos por dirección 3307/2106/19014/7777. No se tocaron firewall/router ni pagos. Cambios solo locales; no commit/push.

`E:\l2-local\17-ELEGIR-VERSION-L2.cmd` elige versión. Cada raíz nueva tiene `2-JUGAR.cmd`, `1-INICIAR.cmd`, `3-ESTADO.cmd`, `5-DETENER.cmd`. No ejecutar de nuevo el preparador sobre raíces existentes; es un constructor inicial, no actualizador.

Decisiones de Hellgames: nivel1, todas las clases del sistema actual, raza inicial cuenta, apariencia y origen de stats separados; VIP cambiará cada módulo, aún falta servicio público (comando racial actual es GM). Equipo A + joyería A + arma A con SA aprobada expresamente. Modelos propuestos Tallum heavy/Majestic light/DC robe y Majestic jewelry +0. Shop solo armas S comunes; customs categorías SS/SSS todavía sin representación técnica (Interlude llega a S). Propuesta Hellcoin=Goldenbar=1kkk Adena, precio USD1 o ARS1000: documentada, sin banco ni cobros. Fuente `E:\l2-hellgames\DECISIONES-INICIALES.md`.

Investigación Damage ya guardada `research\damage-onboarding`: no repetir REA ni asumir equivalencia entre iconos y efectos comprobados. Computer Use nativo sin conexión; no hubo validación visual de nuevos clientes. Ver informe de verificación para estado final de pruebas y servicios.

Cierre: ambos manifests `state=verified`, ambos entornos nuevos detenidos tras pruebas; Lab siguió PID17892. Academy: retorno real Giran/muelle PASS, 39 perfiles NPC preparados/verificados tras recarga, 46 personajes técnicos propios, cero cuentas y cero online. Hellgames cero cuentas/personajes. Logs finales sin excepciones/SEVERE. SQL de durabilidad temporal durante generación restaurado a1 y DB cerrada ordenadamente. No afirmar que selector A/VIP/economía estén implementados: siguen pendientes en Hellgames.

## Alcance confirmado para decoracion del muelle
Kevin confirma que el trabajo de decoracion/edicion visual del muelle aereo se realizara en L2 Lab, que conserva todos los experimentos: servidor/proyecto E:\l2-local y cliente E:\l2 (lanzador system-hud). Hellgames y Academy permanecen separados; no propagar estos cambios a esas copias sin una indicacion posterior. Esta confirmacion fija el entorno; todavia no se inicio la decoracion.


## Copia para editor del muelle (Lab)
Preparada en E:\l2-local\research\gludio-editor; acceso 18-EDITOR-MUELLE-LAB.cmd. Original cifrado +80 dependencias con hashes; copia Working con camara orientada al muelle, cliente sin cambios. Carga UCC completa tras fallback de textura editor-only para watertest ausente. Resumen UCC 0 warnings es enganoso: log GludioLoad.log contiene Engine incompleto, conversion Skins y Missing StaticMesh water.Water01 (export real water.test.Water01). Ocho piezas HGGludioDock exportadas con sus mallas. Mapconvert preserva 41185 actores activos pero cambia license28 a0 y elimina exports; NO instalar resultados. UnrealEd lanzado sobre copia, proceso10296; no se observo GUI (Computer Use pipe os error2 tras reset). Falta validar visual y Guardar GUI; camino conservador exportar decoracion T3D y transferir actores al mapa original con pipeline. Detalles README.md del espacio aislado.


Captura de Kevin confirma UnrealEd abierto y Load Errors de Engine/Water01. Corregida Water01 SOLO en Working-v2 y paquete privado HGEditorWater (export raiz); acceso18 actualizado. UCC v2 ya no indica Missing StaticMesh Water01; siete incompatibilidades Engine y conversion Skins permanecen. Prueba waterfix-proof.json. No modificar Engine del cliente ni instalar mapa guardado por editor sin validar. Cliente intacto; revision visual v2 pendiente.


Diagnostico transversal Computer Use: captura del chat desktop reporta enumeracion/restauracion de ventanas funcional, pero captura Explorador y UnrealEd falla en SetIsBorderRequired con E_NOINTERFACE0x80004002. Registro local confirma Windows10 Enterprise20H2 build19042.1466. Microsoft documenta GraphicsCaptureSession.IsBorderRequired desde build20348, posterior a este host: explicacion fuertemente compatible, no traza independiente de ejecucion desde esta sesion. Fuente https://learn.microsoft.com/en-us/uwp/api/windows.graphics.capture.graphicscapturesession.isborderrequired . No seguir cambiando permisos ni modificar helper; no atribuir fallo exclusivamente a UnrealEd. Kevin vio overlay celeste de control; ImprPant interrumpio modo segun observacion del usuario.


## Taller de escenarios propio
Kevin pide programa propio para editar mapas/aeronaves; prioridad confirmada ambos, empezando por muelle. Implementado prototipo local research/scene-editor, acceso19-EDITOR-ESCENAS-L2.cmd, http://127.0.0.1:32290. Arquitectura muelle8 piezas y aeronave Gracia4 componentes, biblioteca2286 recursos, transformaciones con gizmos/campos, duplicar, ocultar/bloquear, undo/redo, colocacion en superficies y proyectos JSON versionados. Render y operaciones verificadas en Chrome headless (verification.json); capturas preview-muelle/decoracion/aeronave.png. Solo compositor visual; NO edita vertices ni importa/guarda UNR ni instala proyectos ingame; puente nativo/geodata pendiente de implementar y validar cuando se apruebe decoracion. Materiales aproximados; nave Gracia no es Aurelia/Vigilia. Cliente Lab hash sin cambios, Hellgames/Academy intactos. README local tiene uso y limites. Sin commit/push.


Preferencia UI de Kevin: editor tipo Chara Studio, fondo negro y paneles semitransparentes, opciones/busqueda a izquierda, trabajo3D derecha. Implementado en Taller research/scene-editor: pestanas Biblioteca/Escena/Vista, opacidad ajustable, grid opcional, auto recuperacion borrador. QA WebGL y operaciones paso, recarga conserva escena4 piezas, layout1360x768 comprobado. Refrescar navegador tras guardar version para recibir interfaz.


Analisis REA CharaStudio solicitado por Kevin para futura adaptacion: informe E:\l2-local\research\studio-ui-analysis\ANALISIS-CHARA-STUDIO.md. REA inspeccion admin Assembly-CSharp RX22 hash361ee4c5..., 14controladores +CameraSelector/GuideInput; lectura UnityPy level1:2389GO/2376RectTransform/13identidades de controlador. Verificados menus contextuales, arbol padres/hijos/multiseleccion, local/global,10slots camara y canvases independientes. Propuesta barra categorias izquierda+panel contextual plegable+memoriascamara+arbol, Workspace derecha solo opcional para preservar preferencia izquierda. Captura usuario como referencia visual; no runtime observado ni plugins individuales atribuidos. No se modifico editor ni Chara en este analisis; implementacion posterior. Evidencias persistidas JSON y hashes intactos. Reusar informe en vez de repetir REA.


Taller actualizado por pedido Kevin: navegacionraton estiloStudio (izq orbita, derX distancia/derYaltura, centralpan, L+Rprofundidad, Shift4x/Ctrl0.6), C trae objeto al foco respetabloqueo, F focoalnodo, Q pivotes seleccionables, W/E/R; panel190px/rail44px yMostrar panel;10slotsSave/recall persistidos enJSON/borrador, actualcamara tambienpersistida. Servervalidacamaras opcionales, mantiene proyectosviejos. QA completo verify.cjs y especifico verify-studio-controls.cjs PASS, capturapreview-studio-controls.png. Evidencia originalCIL y KKUS(config/patch) enresearch/studio-ui-analysis/NAVEGACION-CHARA-STUDIO.md. C es alpuntodeenfoque,no posicionliteralcamara; Q nodosdeobjeto,no huesos/vertices. Guardarversion antesCtrlF5 para actualizar. Labclienteoriginalintacto.


Taller: biblioteca modular implementada asset-library.js/css. Icono Anadir abre ventana movible/redimensionable/maximizable con cuadricula de miniaturas, categoria y filtros. Elegir recurso cierra e inicia colocacion; Escape/cerrar devuelve escena. Nombres espanoles parciales (equivalencias comunes y terminos orientativos marcados), originales siempre visibles, busqueda bilingue y selector idioma. No cambia IDs ni traduce clienteL2. QA verify-library.cjs, verify.cjs y studio-controls PASS; preview-biblioteca.png. Guardarversion y CtrlF5 para actualizar. Sin cambios mapas ni entornos Hellgames/Academy.

