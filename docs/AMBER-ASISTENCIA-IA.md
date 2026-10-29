# Amber: asistencia autónoma — 10/10/2026

Implementación para el contrato GM de prueba. Al invocarla, Amber comienza en manual. Activa la habilidad temporal **Asistencia de Amber** para encender la IA; otro clic la apaga. En IA no necesita que el dueño seleccione a un enemigo.

## Uso

- `.amber` abre el menú y muestra el modo actual.
- **Asistencia de Amber** (Alt+K/barra) es un activable nativo: clic para encender/apagar, sin coste de MP. `.amber auto` activa el mismo estado; `.amber manual` lo apaga.
- `.amber manual` deja las decisiones de ataque y habilidades al dueño.
- Atacar desde el menú o desde la ventana nativa del summon fija ese blanco como prioridad. Si deja de ser válido, vuelve a buscar otro en modo IA.
- Seguir y Detener, tanto por menú como mediante sus botones nativos, desactivan la asistencia. Reactivar con el activable de la barra o `.amber auto`.
- Fuego y lluvia siguen disponibles manualmente. Las órdenes de habilidad manuales reservan seis segundos sin nuevos skills automáticos y se respeta una habilidad encolada en la IA nativa.
- Activar Beast Soulshots con clic derecho. El disparo usa el autoconsumo normal; la lluvia consume tres shots por lanzamiento.

Cambiar el modo no rompe el contrato. Una invocación nueva comienza en manual; el modo de control no se guarda entre invocaciones.

## Selección y límites

Cada 500 ms revisa Players y summons visibles dentro de 1100 unidades del dueño. Evita aliados de party, clan o alianza, amigos de asedio, personajes invisibles, paz, otras instancias, muertos e invulnerables. No selecciona al NPC del contrato ni mobs ambientales por su cuenta.

Puntúa cercanía, daño reciente recibido por el dueño o sus aliados y ataques/casts dirigidos contra ellos. Un summon enemigo obtiene una preferencia moderada; un enemigo que esté atacando al grupo puede superar esa preferencia. Detecta Ultimate Defense (110) y Vengeance (368) y baja su prioridad para disparos normales, buscando rivales menos protegidos. Mantiene el blanco al menos 2,5 segundos mientras siga válido y agrega estabilidad al puntaje para evitar cambios continuos. Una orden manual de ataque prevalece sobre la selección automática.

Amber vuelve hacia el dueño si se aleja más de 1200 unidades. Respeta línea de visión, diferencias de altura, las restricciones nativas de control y los estados de duelo/Olympiad/montura. La invulnerabilidad del dueño pausa el combate automático, incluidos los preparativos y descansos del TvT. No cambia el objetivo seleccionado por el jugador.

## Skills

Fuego se activa contra un blanco válido cercano cuando está disponible, no tiene ya el enchant y quedan al menos 180 MP: usa 60 y reserva 120 para lluvia. Conserva +25% PAtk, poder de fuego 20, duración 15 segundos y recarga 30 segundos.

Lluvia requiere 120 MP, tres Beast Soulshots, recarga disponible y ninguna lluvia anterior pendiente. Elige un blanco visible a 900 o menos de Amber:

- Root, stun o parálisis con un efecto activo que asegure al menos seis segundos restantes según el temporizador del servidor. Detecta el efecto realmente aplicado de Anchor, Lightning Strike, Binding Cubic y Spark Cubic; tener un cubic activo no equivale a haber inmovilizado al rival. El contador entero redondea el tiempo restante hacia arriba: se exige que muestre siete o más.
- Ultimate Defense o Vengeance activo con inmovilización real y tiempo suficiente. Reconoce que ese enemigo recibe menos daño por su defensa.
- O un blanco quieto observado durante tres segundos mientras ataca/castea; para uno inactivo se exigen cinco segundos. Un movimiento o un cambio acumulado de posición reinicia esa observación.
- Una concentración de al menos tres enemigos dentro de 175 unidades del blanco, aunque no haya inmovilización. La selección evalúa el radio de daño real de 200 y penaliza el riesgo de movimiento y de estar cerca del borde.

Primero prioriza anclas con control duradero sin UD. Si no hay ninguna, prefiere una ancla con UD; puede elegir otro blanco si su área ofrece más del doble del rendimiento estimado, justificando el riesgo de escape. Compara el daño esperado sobre todos los enemigos cubiertos a partir del PAtk actual de Amber, la PDef y resistencia elemental de cada víctima, inmovilización/movimiento y margen dentro del círculo. Son pesos heurísticos para tomar decisiones, no probabilidades calibradas ni una promesa de daño final. No cambia las fórmulas de daño real del servidor.

Al evaluar cada enemigo como centro, puede elegir al del medio para cubrir más rivales. Con un foco manual, limita la selección de lluvia a ese foco. Activa fuego primero cuando puede, así la lluvia captura su enchant al iniciar.

**Es una predicción, no una garantía de impacto.** Un blanco quieto puede moverse, cancelar su cast, recibir un desplazamiento o perder su inmovilización. El área sigue fija: carga 3,5 segundos, caída 650 ms y tres oleadas separadas 500 ms, radio 200. No persigue al enemigo con el área ni le aplica un root artificial.

## Validación y continuidad

**Resultado final: 104 comprobaciones PASS**, con la política de UD y panorama solicitada por el usuario. Evidencia: `backups/amber-assist-2026-10-10/verification-104-checks.log`. Incluye cuatro fuentes reales de control, prioridad de root frente a UD, centro de grupo, grupo desprotegido frente a UD aislado y mantenimiento de Seguir después de una habilidad. Compilado contra el core instalado, que conserva SHA256 `2e35d88f6050eb22619adf00ee0070494126ae0ed535dc33b0e4c1e18bc99349`.

Verificador optativo: `powershell -NoProfile -ExecutionPolicy Bypass -File Start-L2Local.ps1 -VerifyAmberContract`, con el servidor detenido y el cliente cerrado. Utiliza únicamente AmberOwnerProbe, AmberTargetProbe, AmberAreaMiddleProbe y AmberAreaEdgeProbe de la cuenta reservada ambercontracttest, más un summon de prueba, dentro de una instancia privada del Coliseo. No utiliza Hellkevin ni modifica sus consumibles.

Comprueba daño real de arco autónomo contra un summon, autoconsumo de shots, fuego y lluvia con los mismos recursos/recargas, objetivo del dueño intacto, prioridad manual, controles nativos, pérdida del foco, inmovilización real y limpieza. También conserva la regresión de contrato, buffs, áreas, carga, interrupciones y cancelación.

Scripts propios: `server/game/data/scripts/custom/AmberContract/AmberAssist.java`, `AmberServitor.java`, `AmberContract.java` y `AmberContractVerification.java`. Copias de source/dist y cloud-repo sincronizadas. No cambia el core, paquetes cliente, stats del summon ni los pilotos del 4vs4. La revisión visual de los paquetes V4 conserva su estado previo.

Registro de decisiones en `logs/game-stderr.log`: líneas `AMBER_AI` con modo, blanco, preferencia por summon y uso de fuego/lluvia; `AMBER_RAIN` registra daño e impactos. Sirven para analizar el próximo TvT junto con su telemetría. Respaldos y pruebas: `backups/amber-assist-2026-10-10/`.

La asistencia no consume un hilo propio por summon: el controlador global procesa solamente las Amber presentes. Retirar, morir o desconectarse elimina su actividad; las tareas de lluvia mantienen su cancelación habitual. El contrato sigue siendo GM, gratuito y de laboratorio.

## Activable añadido después de la validación IA

La versión actual añade la quinta habilidad temporal 19014 y cambia el inicio a manual. El resultado 104 PASS de arriba corresponde a la IA anterior; la evidencia ampliada del activable está en `AMBER-ASISTENCIA-ACTIVABLE.md`.
