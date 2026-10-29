Actualizaci?n: GameServer reiniciado el 25/10/2026 con cliente cerrado. Log confirma ExplorationLab V1 y puerto7777 listo. Comandos disponibles; prueba visual de descubrimiento/baliza pendiente del usuario.

# Exploración V1 — primer ensayo, 25/10/2026

Estado: fuentes preparadas en staging, compilación contra el GameServer actual PASS y 21 comprobaciones de estado PASS. NO instalado ni ejecutado dentro del servidor. No se reiniciaron juego/servidor, no se modificó el cliente y no se han escrito variables de personajes reales.

## Qué prueba

Una región circular de ensayo, anclada por el GM en el mundo compartido. Entrada dentro de radio600 y diferencia de altura máxima180: registra una visita personal y solicita un título nativo en pantalla una sola vez. Baliza VIRTUAL en el centro, activable por comando dentro de radio120, vivo, fuera de combate y en la misma instancia. No es todavía un cristal visible ni un NPC colocado.

Tres datos distintos: visita personal; baliza personal activada; recuperación global. Visitar no retira automáticamente la niebla. La región comienza globalmente oculta; recuperar permite distinguir cobertura PARTIAL/CLEAR según cada personaje. Si alguien activa su baliza antes de la recuperación global, guarda ese progreso, pero su cobertura sigue TOTAL hasta la recuperación.

## Comandos previstos tras integrar y cargar

Solo GM. No funcionan todavía en el juego abierto.

1. `.explora anclar`: fija centro en tu posición; rechaza instancias privadas, muerte o combate. Si existe región, exige `.explora anclar-nueva` para reemplazarla con una revisión diferente.
2. `.explora iniciar`: participa en el ensayo; primera entrada solicita `Lugar descubierto: Region de ensayo` por ExShowScreenMessage. Muestreo cada segundo, solo personajes GM inscritos.
3. `.explora activar`: activa tu baliza virtual estando a120 o menos del centro. Solicita un segundo aviso nativo.
4. `.explora recuperar`: estando cerca de la baliza, revela globalmente la región y avisa solo a los participantes de la prueba.
5. `.explora estado`: informa centro, visita, baliza, revelado global y cobertura calculada. No cambia el mapa gráfico.
6. `.explora salir`: deja de observar tu movimiento. Tras desconectar hay que volver a iniciar el ensayo; el descubrimiento personal permanece.

## Integración pendiente

Ubicación objetivo: server/game/data/scripts/custom/ExplorationLab, con las dos fuentes de src. Revisar el modo actual de config/Custom/WorldContent.ini: si CustomWorldOnly está activo, añadir ExplorationLab a CustomScriptFolders conservando el resto y guardando respaldo. La carpeta todavía no se ha copiado y la configuración no se ha modificado. Fuente distribuible correspondiente: source/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts/custom.

No usar carga en caliente sin verificar el ciclo de vida: el adaptador registra un handler y una tarea periódica. Cargar una única vez en el siguiente arranque controlado y comprobar el log. La carga por ScriptEngine, los avisos de pantalla, las variables de jugadores, el comportamiento al salir/reentrar y la persistencia real en DB siguen pendientes de validación dentro de L2. Compilar no acredita estas verificaciones.

Estado global previsto: data/exploration-lab-v1/region.properties, relativo al directorio de trabajo del GameServer. Escritura temporal y sustitución atómica en el mismo directorio, fallo explícito si no se puede persistir. Variables personales EXPLAB_VISIT_<revision> y EXPLAB_SURVEY_<revision>, usando el almacenamiento nativo de PlayerVariables. Reanclar crea revisión nueva para no reutilizar descubrimientos de otra ubicación. Es un laboratorio de una región, no el formato final del continente.

## Comprobaciones realizadas

Ejecutar `python verify.py`. Compila las fuentes del adaptador con server/libs/*. Luego ejecuta ExplorationStateTest, sin iniciar GameServer ni conectarse a DB. También se incluye verify.ps1, pero la política actual de Windows impide ejecutarlo; el verificador Python evita cambiar esa política.

21 comprobaciones cubren límites de geometría, altura, instancias, coordenadas extremas, estado global/personal independiente, recuperación idempotente, recarga del archivo global, claves por revisión, archivo corrupto y fallo de escritura. La distinción entre dos jugadores se prueba mediante los dos valores personales sobre el mismo estado global; no son dos clientes reales.

## Prueba siguiente dentro del juego

Anclar en una zona tranquila, iniciar y comprobar el título. Alejarse y regresar: no debe repetirse. Activar la baliza: debe guardar progreso personal. Otro GM sin baliza debe tener cobertura TOTAL antes de recuperar y PARTIAL después; el primero, CLEAR después. Reconectar, iniciar otra vez y comprobar ausencia de título repetido y persistencia de baliza. Activar desde lejos o desde otra altura/instancia debe rechazarse.

Después: reemplazar la activación por comando por un cristal/NPC interactivo y conectar la cobertura gráfica de ambos tamaños del mapa, siguiendo research/map-fog-analysis-20261025. No se promete niebla visible en esta entrega.

## Validaci?n visual del usuario ? 25/10/2026

Dos capturas aportadas por Kevin confirman:
- T?tulo nativo visible: Lugar descubierto: Region de ensayo.
- Centro de ensayo -14570,-46575,-10847; revisi?n b369e535-719b-4ab1-997f-4b20a610c816.
- Con visita=true, baliza=true y global=false, el comando informa TOTAL.
- Repetir activaci?n informa que ya estaba activada.
- Tras recuperar globalmente: global=true, visita=true, baliza=true y cobertura CLEAR.

La captura no acredita el t?tulo de activaci?n de baliza, una segunda cuenta con PARTIAL, ausencia de repetici?n al volver ni persistencia tras reconectar/reiniciar. Tampoco existe cobertura gr?fica todav?a. La visita se detect? al iniciar dentro de la regi?n; la entrada caminando desde fuera queda pendiente de probar.

Validaci?n posterior de Kevin: tras la reconexi?n solicitada, captura muestra saludo de entrada, .explora iniciar y estado de la misma revisi?n con global=true, visita=true, baliza=true, CLEAR. No aparece repetido el t?tulo en la captura. Reconexi?n validada; reinicio completo de servidor y segundo personaje siguen pendientes.
