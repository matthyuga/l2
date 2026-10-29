# Ritmo de combate y repertorio por clase ?15/10/2026

Instalado y activo enGameServer3064. No se reinicio ronda/servidor, se movio Hellkevin ni se cambiaron parties humanas. No se toco Amber,cliente,core ni animaciones.

## Hallazgos y cambios

El bot tenia decision cada500ms y un bloqueo artificial de900ms tras habilidad aceptada; los fisicos intentaban toda la lista de skills antes de establecer ataque normal. Ahora el cerebro tactico revisa cada100ms, cacheando seleccion de objetivo400ms. Ataque normal se establece antes de tejer skills y PlayerAI nativo conserva/restaura la intencion tras CAST. Nunca se reinician relojes de ataque ni se fuerza da?o. Micropersecucion nativa en alcance+160 si el tramo es transitable; rutas persistentes para distancias/obstaculos mayores. No se reenvia un ataque durante isAttackingNow ni se aborta por cada tick.

Fisicos alternan ataque sostenido con ventanas de habilidades(aproximadamente3s arqueros,1.9s otros mas variacion0..300ms); defensas urgentes y preparacion pueden anticiparlas. Reaccion de caster reducida a100ms despues de aceptar skill, bajo casteo/reutilizacion nativos. El retry de debuff no danino evita insistir cada100ms. Movimiento de separacion no corta una animacion fisica en curso.

Potas verificadas antes de retornar por casting:CP<90% y faltante>=200,MP<65%,HP<75% si falta su efecto de regeneracion. Nativos ItemSkills y timestamps determinan si pueden usarse; no se fuerza recuperaci?n ni inventario infinito. Se mantiene la bolsa ligera finita de la etapa anterior y su reposicion al preparar/reaparecer; no se rellenan potas continuamente durante combate.

## Repertorio

Solo skills realmente aprendidas y permitidas:
- Arquero:Snipe313/DeadEye414 con distancia y sin amenaza proxima, RapidFire413 segun distancia, StunShot101 ante movimiento/casteo enemigo. Alcance usa getPhysicalAttackRange nativo. Snipe se retira mediante stopSkillEffects REMOVED si el enemigo sale del alcance,se acerca<250 o no hay objetivo,permitiendo volver a moverse; no se devuelve su reuse/coste.
- Dagger:Trick11/Switch12/Bluff358 ante foco enemigo, Mirage445/UE111 con presion/HP, Dash4 para acercarse/escapar. Se conserva posicion de Backstab y flanqueo.
- Tanque:control ante casteo; UD y defensas previas.
- Guerrero:Frenzy176/Guts139 a HP bajo,SonicMove451 para acercarse,skills ofensivas previas entre ataques.
- MysticMuse:IceVortex1340,LightVortex1342,SolarSpark1264,HydroBlast1235,AuraFlare1231. Spellhowler incluye WindVortex1341/ShadowSpark1266; Sorcerer FireVortex1339; Necro DarkVortex1343. Surrender y utilidades anteriores se conservan. No se cambia el skill tree para darselos a quien no los aprendio.
- Overlord/Dominator:seals con2enemigos cercanos(1246,1208,1366,1096,1104,1108,1209,1248),ademas de drain/support. Lista de areas revisada y acotada. Se valida el targetList nativo completo contra membresia/instancia/propiedad/enemistad y se exige al menos2receptores validos; aliados,clientes reales,monstruos u objetivos ajenos cancelan esa eleccion. El core tambien filtra/protege aliados al aplicar el efecto. No se habilitan indiscriminadamente todas las areas del servidor.

## Pruebas nativas

pressure-trial.txt:fixture de instancia vacia,Primeval,dummy invulnerable y mismos actores por controlador.12s por ensayo; basico y candidato intercambiados secuencialmente,sin normalizar DPS. Summons/cubics se deshabilitaron SOLO en el fixture para aislar el ritmo; builds/equipo nativos y potas reales. Datos:
- ArenaEryndor arquero:baseline1inicio de ataque normal,candidato5. Candidato mantuvo skills99/343/354/369 y potas. No equivale a5veces el DPS ni prueba ventaja universal.
- ArenaMyrentha mago:baseline9ejecuciones de skills<2000,candidato12(con ShadowSpark);0ataques normales en ambos. Eventos nativos ejecutados,no solo solicitudes aceptadas.
- SealOfBinding1208 ejecutado con2enemigos y1aliado:targetList excluyo aliado y este no recibio el efecto. Guard rechazo el escenario con un solo enemigo. No se fuerza exito contra resistencias.
- Registro del lobby,instancia/party de Hellkevin intactos. cleanup.txt confirma retiro de perfiles yfixture.

potions.txt/status:otro perfil reservado,CP/MP bajos solo para el escenario controlado;8usos CP en4s,minimo503ms entre eventos,frente a reuse nativo500ms. MP se recupero por handler nativo. Actor retirado con snapshot restaurado.

live-navigation-audit.txt:tres muestras durante40s del encuentroFREE real enPrimeval. Se observaron ataques normales,skills entre ataques y hechizos nuevos. Los contadores tacticos/nativos conservan actividad anterior; rhythm se agrega en esta etapa y sus skills son solicitudes aceptadas. Un intervalo entre ataques en campo puede incluir desplazamiento,muerte,casteos o controles; no interpretarlo como intervalo de arma. El ajuste final de micropersecucion/cancelacion deSnipe es posterior a esa auditoria; compilo y se activo,pero no se certifico un duelo especifico deSnipe en esta etapa.

## Instalacion y limites

15fuentes sincronizadas runtime/source/overlay:3controladores modificados y2helpers nuevos. installation.json guarda backup/hash;82hashes de la cadena verificados. startup-check compilo todas las fuentes de ElvenPvpRoom. PressureBaseline,PressureCandidate,PressureTrial y agentes permanecen solo enresearch.

No se certifican todas las combinaciones de clase,skills/pets/areas,navegacion ni balance; no se hizo prueba de cuatro salas llenas. Las habilidades activas del servitor y todas las rotaciones especializadas no estan completas. Esta IA es por reglas y sensores del servidor, no aprendizaje humano. Respeta recursos,reuse y resistencia del pack instalado.

Rollback rapido:.salas bots cerebro clasico conserva cambios de infraestructura/bolsas; usa decision500ms pero el helper de potas mantiene nuevos umbrales. Rollback completo:retirar bots normalmente,detenerGameServer,ejecutar restore.py y arrancar por lanzador normal. Snapshot de roster aun no es persistente ante crash.
