# Perfiles modulares de raza, cuerpo y sexo

Estado: preparado y compilado; pendiente de instalar después de confirmar la corrección del cabello. No presentar como activo hasta que existan `installation.json` con `live_installed=true`, `engine-verification.txt` y `live-install-proof.txt`.

El cálculo conserva el origen racial actual (nueve perfiles Fighter/Mystic) y añade una tabla pequeña de cuerpo y el ajuste de sexo. No suma otra plantilla racial completa. La profesión, subclases, habilidades, equipo y progreso se conservan.

Masculino: +1 STR/CON/INT, −1 DEX/WIT/MEN. Femenino: exactamente inverso. Cuerpos: ajustes de suma cero de magnitud máxima 2, editables en `stage/config/Custom/ModularAppearance.ini`. Tabla completa en la bitácora del proyecto.

El cuerpo elige raza visible y modelo Fighter/Mystic. El origen de atributos se elige por separado. Ejemplo admitido: cuerpo humano Mystic femenino, origen elfo Fighter, profesión Destroyer. El cliente recibe el modelo corporal en el campo de apariencia y la profesión real en el campo de clase activa; el servidor conserva sus IDs de clase reales.

Se añade `.cuerpo`, con enlace desde `.raza`. Conserva la autorización GM de ese laboratorio: no habilita automáticamente un servicio público ni crea cobros VIP. Permite elegir origen, cuerpo y sexo; comparar atributos y combate; confirmar; aplicar; cancelar; restaurar el estado previo. Cambiar cuerpo o sexo reinicia cara/cabello/color a 0 para evitar índices incompatibles. No repone HP/CP/MP. Los cambios se guardan en `character_variables`; no requieren modificar el esquema SQL.

Los personajes existentes conservan el modo heredado hasta aplicar. Los nuevos pueden iniciar con perfiles modulares según `EnableForNewCharacters`. El interruptor `Enabled` permite desactivar la mecánica tras reiniciar el servidor. El menú también permite elegir modo heredado por personaje.

Implementación preparada:

- Cinco clases de core: sólo 12 métodos; `graft-proof.txt` verifica que 845 cuerpos de métodos ajenos al cambio permanecen idénticos.
- Nueva utilidad `ModularAppearance`, sin mutar plantillas compartidas ni añadir campos/métodos a Player.
- Vista previa aislada por jugador e hilo, sin guardar selecciones hasta Aplicar.
- Persistencia verificada contra DB al aplicar y respaldo personal `MODULAR_BEFORE_V1` para restaurar.
- Actualización en vivo con captura previa de las seis clases afectadas; vuelve al código anterior si fallan las pruebas.

Validación preparada: 236 comprobaciones de presupuesto/sexo/modo heredado. El agente ejecutará 648 combinaciones en objetos desconectados con las fórmulas reales y comprobará persistencia/recarga/restauración exclusivamente en `BodySexProbe`, cuenta reservada `modular-test`. Ese personaje permanecerá desconectado, sin entrar al mundo ni pertenecer a una cuenta del usuario. No afirmar que estas pruebas pasaron antes de ejecutarlas.

Despliegue realizado: el instalador rechaza reaplicar una instalaci?n existente. `python research/modular-appearance-20261024/install.py`. Exige `hair-confirmation.json` con la confirmación del cabello; sincroniza fuente, runtime y overlay local, sin publicar a servicios externos.

Restauración completa, con GameServer activo y sin jugadores conectados: `python research/modular-appearance-20261024/rollback.py`. Primero restaura los perfiles personales y desactiva el módulo; después devuelve las clases vivas y los archivos respaldados. Comprueba hashes para no sobrescribir cambios posteriores. Conserva las correcciones del cabello. Sólo ejecutar si se decide retirar esta implementación.

La primera activaci?n restaur? autom?ticamente el core y los archivos al fallar el contexto del constructor del men?. Se corrigi? usando ScriptEngine.executeScript en InstallModularAgentV2. La segunda activaci?n y todas las comprobaciones posteriores pasaron. El respaldo global se rebas? conservando los JAR hist?ricos para que restaurar el m?dulo NO revierta la correcci?n posterior de H/I de la orca (CharacterCreate femenino hasta 8).
