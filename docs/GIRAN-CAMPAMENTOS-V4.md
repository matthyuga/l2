# Giran: campamentos separados y avance — 11/10/2026

Los cuatro clanes atacantes salen de bases distintas dentro de la zona nativa permitida para Build Headquarters. Las bases vecinas quedan a más de 2.100 unidades, fuera del radio inicial de búsqueda de rivales de 1.500 unidades.

| Clan | Sector de reunión | Coordenadas base |
| --- | --- | --- |
| Holly | Norte exterior | 110000, 142000 |
| Fury | Oeste, aproximación norte | 111200, 144100 |
| Sacred | Oeste, aproximación sur | 110000, 146200 |
| Waves | Sur exterior | 111700, 147500 |

La altura se obtiene de la geodata y los miembros usan pequeños desplazamientos de formación. El propietario conserva la sala nativa de resurrección. Se escalonan las salidas por clan en intervalos de 5 segundos; cada escuadrón llega desde su sector y conserva su agenda de puertas, guardias, cristales, guardianes y artefacto.

Antes de superar la entrada y el patio, una pelea entre atacantes tiene una ventana de 10 segundos. Después el escuadrón dedica al menos 20 segundos a retomar sus objetivos del castillo. Los defensores y un líder que esté grabando el artefacto conservan prioridad y no están sujetos a esa pausa. Los clanes siguen siendo enemigos según el motor nativo; esta es una decisión de sus agendas, no una tregua ni invulnerabilidad. En el interior disputan la conquista.

## Campamentos y resurrección

Los líderes usan Build Headquarters nativo, con 4 segundos de casteo, 300 Gemstone C por intento y reutilización nativa de 30 minutos. Un casteo iniciado ya consume materiales y puede activar la reutilización aunque se interrumpa. La IA comprueba la existencia real de una bandera viva; vuelve a intentarlo cerca de su base cuando el skill esté disponible. No se borra la reutilización durante una partida.

La reaparición automática de los pilotos tras 30 segundos utiliza el campamento construido si sigue vivo; si falta o fue destruido, vuelve a la base de su clan. El laboratorio mantiene esa reaparición de respaldo para la prueba. Los pilotos recuperan su esquema físico o mágico también después de una resurrección de compañero; no se llena su HP/MP por esa vía. Hellkevin mantiene las reglas nativas, sin este reset de pilotos.

Las puertas siguen siendo pasos obligados. La separación y las prioridades reducen la pelea repetida en la entrada, pero el resultado y el balance requieren una partida completa. No se atraviesan puertas cerradas ni se acelera la conquista.

## Validación

Compilación y prueba nativa aislada: **347 checks PASS**. Las cuatro bases se construyeron con Build Headquarters real, gastando 300 Gemstone C por intento; se comprobaron separación, recorridos nativos hacia la aproximación, elección de bandera viva para respawn, rebuff tras muerte y vuelta a objetivos del castillo después de una escaramuza real. La comparación persistente conserva personaje/inventario, clanes, castillo/fecha y guardias; los 19 pilotos quedaron offline nivel 80. La verificación opt-in usa los 19 pilotos, sin cargar a Hellkevin, y restaura propietario, fecha del siege, reputación y Blood Alliance. Comprueba construcción nativa de las cuatro bases, rutas, resurrección y prioridades; conserva las comprobaciones de Amber y guardianes. Solo para probar el reintento se acelera la reutilización del piloto de prueba.

Fuentes: `research/giran-camps-v4`; respaldo privado: `backups/giran-camps-v4-2026-10-11`. El flag de prueba sigue siendo `Start-L2Local.ps1 -VerifyGiranDefense`, desactivado por defecto. Los Java finales son la referencia; no ejecutar los generadores históricos V3 para recrear V4.
