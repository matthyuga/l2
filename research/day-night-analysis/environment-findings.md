# Entorno del cliente Interlude: evidencia de paquetes

Fecha: 2026-10-21. Lectura estática de `E:\l2`; no se ejecutó ni modificó el cliente. Las salidas están exclusivamente en esta carpeta.

### Alcance activo verificado

La variante habitual de arranque es `system-hud`, según Start-L2Local/2-JUGAR inspeccionados por el principal. Comparación directa guardada en `active-system-comparison.json`: sus cuatro timeenv0..3.int son idénticos byte a byte (mismo tamaño y SHA-256) a los decodificados desde `system`; por tanto las tablas de este informe sí corresponden a la configuración activa.

Engine.u difiere: `system` tiene 2805255 bytes SHA-256 `50576d69253236ab33532994e91419343eeed439289a11de05dc5ced29b6d5e1`; `system-hud` tiene 2805259 bytes SHA-256 `9b04ff5cb4258e84dfa8efbdd85d9121f3bdcb5822a9a21ca69d200d05a69761`. Ambos son v123/licencia30, 7058 nombres y 10647 exports; sus tablas no son idénticas y no debe trasladarse un offset entre variantes. Se comprobó directamente el ScriptText de las 13 clases relevantes (Actor, Light, NSun, NMoon, NMovableSunLight, SkyZoneInfo, L2NEnvLight, L2NTimeLight, ZoneInfo, LevelInfo, L2FogInfo, GameEngine, ParticleEmitter): los 13 textos son idénticos, con hashes de cada variante en `active-engine-comparison.json`. Los offsets de Engine citados en los inventarios originales pertenecen a `system`; las declaraciones corroboradas también existen en `system-hud`.

## Resultado

El cliente ya separa el sol visible, la luna, la luz direccional móvil y el cielo. No hace falta inventar esta arquitectura desde cero. Está confirmado por actores serializados del mapa y por texto UnrealScript conservado dentro de Engine.u. El movimiento efectivo y las fórmulas de interpolación son nativos y requieren corroboración en Engine.dll; este informe no atribuye ejecución a los datos.

## Reloj, colores y tamaños

Se decodificaron `system/timeenv0.int` a `timeenv3.int` con la herramienta existente `tools/open-l2encdec-1.3.9/l2encdec_win.exe -c decode -o <salida> <original>`. Protocolo detectado: Lineage2Ver111. Copias decodificadas `.decoded.int`, copias legibles UTF-8 `.utf8.int`; inventario con valores y hashes en `sources-timeenv.json`.

Cada perfil tiene `EnvType=0`, `1`, `2` o `3`; son perfiles de entorno, no las cuatro fases del día (cada uno ya contiene su propio conjunto horario completo). La asignación semántica de cada perfil a zonas o eventos permanece pendiente.

Secciones comunes: SunColor, SunScale, MoonColor, MoonScale, SkyBoxColor, HazeringColor, CloudColor1/2/3, TerrainAmbient, ActorAmbient, StaticMeshAmbient, BSPAmbient, HSVTerrainLight, HSVActorLight, HSVStaticMeshLight y HSVBSPLight.

En timeenv0 las curvas de color/iluminación tienen generalmente 25 claves, T=0..24; sol y luna tienen cinco claves cada uno. Ejemplos textuales:

- SunColor T=6 RGB 255/122/23; T=8 y 15 RGB 255/219/151; T=20 RGB 255/174/125; T=24 RGB 162/65/0.
- SunScale T=6 S=2; T=8 S=0.5; T=15 y 20 S=0.2; T=24 S=2.
- MoonScale T=0 S=4.5; T=2 S=3.5; T=3 S=2.5; T=4 S=3.5; T=6 S=4.5.
- SkyBoxColor T=0 RGB 40/49/70; T=6 81/75/146; T=7 126/158/241; T=12 66/124/176; T=22 98/107/159; T=24 40/49/70.
- `HSVTerrainLight` usa Hue/Sat/Bri, con brillo flotante (hay valores 450); no debe limitarse artificialmente a RGB 0..255.

Detalles que un editor debe preservar: timeenv1 y timeenv3 contienen dos secciones llamadas HSVTerrainLight; timeenv3 SkyBoxColor declara NUM=1 aunque conserva múltiples líneas COLOR. No asumir que todo el archivo es una tabla homogénea sin analizar cómo consume NUM el nativo.

Las declaraciones retenidas de `L2NTimeLight` confirman structs NTimeColor(int Time, byte R/G/B), NTimeHSV(int Time, byte Hue/Sat, float Bri), NTimeScale(float Time, float Scale). L2NEnvLight native hereda esas curvas y añade las de cielo, haze, nube, estrellas, sol/luna y ambiente. Fuentes y metadatos en `*.uc` y `Engine.selected-classes.json`.

## Actores reales en Maps/24_19.unr

Éste es el mapa instalado del muelle según `research/gludio-sky/installation.json`. Paquete UE2 v123 licencia28; propiedades completas en `24_19.inventory.json`. Offsets siguientes son del paquete descifrado, sin cabecera Lineage.

| Actor / export | Offset / bytes | Propiedades relevantes explícitas |
| --- | --- | --- |
| NMovableSunLight0 / 1 | 136621 / 145 | LightBrightness=70; bSunAffect=true; Location=(164707.39,31850.24,15592.13); Rotation=(-8846,25324,0); DrawScale=100 |
| LevelInfo0 / 2 | 136766 / 221 | AmbientVector=(0.04569948,0.04569948,0.04569948); no KillZ explícito |
| ZoneInfo0 / 3 | 136987 / 126 | bTerrainZone=true; bDistanceFog=true; DistanceFogEnd=15000; Location=(148283.25,48340.68,-126.72) |
| SkyZoneInfo0 / 78 | 984935 / 316 | Location=(516.20,264627.16,24727.02); TexUPanSpeed=0.2; TexVPanSpeed=0.2; DrawScale=0.2; nueve LensFlare y sus offsets/escalas |
| NMoon0 / 642 | 1696262 / 118 | Radius=245; bSunAffect=true; Location=(482.12,264583.91,24762.84); Skins[0]=L2_Skies.moon.moon |
| NSun0 / 643 | 1696380 / 159 | Radius=350; LimitMaxRadius=50; bSunAffect=true; bDirectional=true; Location=(498.32,264599.75,24766.68); Rotation=(-5944,-39696,0); Skins[0]=L2_Skies.FlareSet.Sun01 |

Los actores anteriores NO serializan bStatic, bMovable, bDynamicLight ni bShadowCast. Ausencia significa herencia/default pendiente, no false. NSun/NMoon tampoco serializan Latitude, Longitude ni Position aunque las clases los declaran.

`Actor.uc` extraído confirma que esos cuatro flags son propiedades heredadas; comenta bShadowCast como "Casts static shadows" y bStaticLighting como "Uses raytraced lighting". `Actor.uc` y `Light.uc` no conservan un bloque defaultproperties en ScriptText; determinar sus valores por defecto requiere parsear los datos de clase, no deducirlos del texto. Hashes de todos los scripts extraídos en `script-hashes.json`.

`NMovableSunLight.uc` conservado en Engine.u literalmente describe "Movable Directional sunlight" y declara native extends Light. NSun/NMoon native extends Actor declaran Radius, Latitude, Longitude, LimitMaxRadius, SunScale/MoonScale, bMakeLightmap y Position; NMoon añade bMoonLight, EnvType, Flame[12] y valores de luz.

El cielo tiene su propia referencia de zona y objetos cercanos entre sí en coordenadas, lejos de los actores del mundo. No demuestra una altura jugable máxima ni obliga a ubicar un sol en la altura de vuelo. La fuente ZoneInfo.LinkToSkybox busca actores SkyZoneInfo y enlaza SkyZone según DetailMode.

Cruce con el análisis de servidor realizado por el agente principal: éste halló un umbral anticheat de Z=20000 para jugadores. NSun0 Z=24766.68 y SkyZoneInfo0 Z=24727.02 ya lo superan: ese umbral de jugador no define el alcance de cielo/actores del cliente. La referencia del código del servidor la mantiene el informe principal.

Hay zonas interiores con `bSunAffect=false`, por ejemplo ZoneInfo39 (hall), ZoneInfo1 y ZoneInfo2. La iluminación del mapa puede excluir el sol por zona.

## Materiales de cielo independientes

`Textures/l2_skies.utx`: v123 licencia28, 66 exports; inventario completo `l2_skies.inventory.json`.

- FlareSet.Sun01 es textura independiente 128x128 (export57; inicio propiedades 12505994).
- moon.moon es textura independiente 512x512 (export6); MoonFinal la referencia como Diffuse.
- SkybackgroundColor es ColorModifier sobre Textures.WhiteChip (export48).
- Cloud_Final es ColorModifier sobre Shaders.Cloud (49); Cloud usa un TexPanner que mueve WhiteCloud, PanRate=0.002.
- HazeRing_Final es ColorModifier sobre Shaders.HazeRing (50), con WhiteRing como Diffuse/Opacity.
- Estrellas: shaders StarField01/02, TexRotator y ColorModifier.
- Hay también materiales de luna animada y lobby; no confundirlos con el cielo jugable base.

Por tanto, el cielo nativo no es solamente una fotografía completa con sol pintado. Los panoramas descargados son otra clase de recurso y deben adaptarse para convivir con el sol nativo sin duplicarlo.

## Niebla y clima

ZoneInfo declara DistanceFogColor/Start/End/BlendTime, banderas bDistanceFog/bFogZone y ambiente. L2FogInfo native declara AffectRange, cinco FogRange, TextureDistance, CloudTexture y una lista de L2EnvironmentColorInfo(Time,FogColor,SkyColor,CloudColor[],HazeRingColor[]). Esto permite datos locales de entorno; falta corroborar selección y mezcla nativa.

Engine.u conserva además propiedades ParticleEmitter.LevelOfWeather, CheckLevelOfWeather, WeatherEffect, WeatherRangeTime y WeatherSoundCheck. GameEngine conserva Wind[] y GSkyLevel. La mera existencia no demuestra lluvia o tormenta funcional, ni eventos de servidor. Ver fuentes extraídas si están presentes.

## Desconocidos y límites

- Fórmula de órbita, vínculo reloj-servidor y unidades de Radius frente a Position: confirmar en nativo.
- Interpolación exacta de curvas, elección EnvType, tratamiento de NUM y duplicados: confirmar en nativo.
- Sombras realmente recalculadas del sol sobre mallas/terreno y compatibilidad con lightmaps: no comprobadas en ejecución.
- Clima activo, rayos y audio sincronizado: datos de soporte encontrados; no verificados funcionalmente.
- No hay máximo Z ni altura de vuelo demostrados por este inventario; coordenadas de cámaras guardadas hasta 528551 son posiciones de editor, no límites de jugador.
