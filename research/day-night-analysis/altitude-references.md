# Plano de alturas y distancias — 21/10/2026

Se usa como cero local el punto de regreso al Coliseo (148900,46100,-3403), observado en `research/airship-integration/server-smoke.txt`. El muelle denominado Gludio está instalado en 24_19 sobre esta región; no se presenta como la ciudad geográfica de Gludio ni como suelo plano de todo el mapa.

Unidades nativas de L2, sin convertir a metros. Las marcas son referencias de pisos/accesos; no envolventes ni proyecciones de cascos. La planta usa cuadrícula de1000u con escala igual X/Y; el perfil usa escalas X/Z independientes y proyecta Y.

| Referencia | X | Y | Z | Z menos suelo |
|---|---:|---:|---:|---:|
| Suelo/Coliseo |148900|46100|-3403|0|
| Piso muelle |149000|46700|12016|15419|
| Nave original, cubierta |152000|46700|12040|15443|
| Aurelia, terraza |153400|55800|12040|15443|
| Vigilia, cubierta |146500|52000|12056|15459|
| Aurelia, piso B |156000|55000|10792|14195|
| Vigilia, galería |146700|52000|12760|16163|
| SkyZoneInfo0 técnico |516.20|264627.16|24727.02|28130.02|
| NSun0 inicial |498.32|264599.75|24766.68|28169.68|
| NMoon0 inicial |482.12|264583.91|24762.84|28165.84|

Pisos y llegadas: `research/gludio-sky/GludioSky.java`, `research/airship-integration/README.md` y server-smoke, `research/aurelia-integration/README.md` y server-smoke, y handler actual `server/game/data/scripts/custom/GludioSky/GludioSky.java` (az/dz son pisos nominales buscados en geodata). No confundir la altura de piso con el Z de llegada del personaje, que puede estar unos puntos por encima. Cielo/sol/luna: `research/day-night-analysis/24_19.inventory.json` y environment-findings.md.

Las diferencias Z del skybox se muestran solo como comparación de coordenadas de almacenamiento. No significan distancia a la atmósfera ni un recorrido volable: ese escenario está fuera de la planta local y se representa como cielo. Por eso no se calcula una distancia de viaje 3D entre él y una nave.

Sombras: pendientes, pospuestas expresamente por Kevin en esta sesión.
