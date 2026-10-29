# Enchant directo de skills - laboratorio GM

Abrir `.enchantskills` o `.encantar` con Hellkevin GM.
El menu lista skills aprendidas al nivel normal maximo que pertenecen a la
clase activa y tienen rutas de enchant definidas. Seleccionar una skill muestra
su icono, rutas, descripcion y diferencias numericas del datapack.
Cada boton aplica directamente el maximo de UNA ruta; reemplaza la anterior.
No consume libros, EXP, SP ni adena; no hay tirada ni riesgo de fallo.
No modifica la probabilidad del enchant normal ni las definiciones de skills.

Ejemplos: Hydro Power+30 potencia108->127; Cost+30 MP69->38.
Surrender Chance+30 activacion80->100: en este core100 omite la tirada de
resistencia, advertencia para balance. Empower Time+30 duracion1200->2400s,
NO aumenta su multiplicador de MAtk. Ice Vortex/Arcane Power no tienen ruta.

Solo nivel76+, tercera profesion, fuera de combate/casteo/eventos(instancia0).
El boton incluye el slot activo; un menu viejo de otra subclase se rechaza.
La skill se guarda mediante Player.addSkill(...,true), se verifica en DB y
se actualizan lista de skills y shortcuts. No reaplica buffs ya existentes:
reutilizar la skill para observar la nueva duracion/potencia.
Cambiar de ruta vuelve a sustituir la skill por el maximo elegido, sin sumar
las dos mejoras. Persistencia en el slot activo; al cambiar de clase rigen
los topes acumulativos existentes del core, sin modificar sus reglas.

Audit: lab_skill_enchant_actions registra la solicitud antes del guardado;
log ENCHANT_LAB APPLIED solo tras verificar persistencia. Si se interrumpe el
proceso, una fila de audit por si sola no prueba que se aplico el cambio.
No se han encantado skills de Hellkevin automaticamente: el usuario elige.

Validacion: compilacion contra core instalado y2438 checks del catalogo PASS,
484 rutas maximas extraidas del XML real. Backup skill-enchant-lab-2026-10-10.
Las dos rutas Power de algunas pasivas se distinguen por numero, y se muestran
los cambios de enchant effects (por ejemplo velocidad/critico con BLUNT).
Pendiente ensayo visual y aplicacion manual de una skill mediante el cliente.
Modulo cargado sin errores en arranque normal 10/10/2026 13:10, routes=484.
Audit0 al entregar; no se selecciono una ruta por el usuario automaticamente.
Modulo aislado custom/SkillEnchantLab; fuente/runtime/overlay sincronizados.
No cambiar core/Amber ni hacer commit/push automaticamente.
