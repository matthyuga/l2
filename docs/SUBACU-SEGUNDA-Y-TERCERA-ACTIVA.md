# SubAcumulativas: segunda acumulada y tercera activa

Regla corregida según aclaración del usuario, 2026-10-08:

- Se acumulan los skills y pasivos aprendidos hasta segunda profesión de la
  principal y las tres subs, conservando raza y perfil FIGHTER/MYSTIC.
- Las cuatro clases pueden evolucionar a tercera. Sólo se activan los skills
  de tercera de la clase en uso. Los de las otras terceras siguen aprendidos
  y guardados en su slot; no se borran.
- Si tercera mejora un skill que ya existía, el slot inactivo aporta como
  máximo el nivel de segunda. No basta con filtrar IDs exclusivos nuevos.
- Un skill compartido usa un solo nivel, el mayor permitido por estas reglas.
  Las masteries repetidas por nombre mantienen una sola ganadora, como en
  la protección anterior: no sumar dos Light Armor Mastery. Masteries distintas
  siguen teniendo las condiciones normales de su equipo.
- La raza no cambia al activar clase/sub ni al evolucionar a tercera.

Ejemplo: con Sagittarius activo y Adventurer guardado, las utilidades y
pasivos del linaje del daguero hasta Treasure Hunter están disponibles si
fueron aprendidos. Los skills o niveles nuevos de Adventurer requieren
activar ese slot. Dash, si se aprende antes de tercera, no se pierde por
estar en Sagittarius. Las restricciones normales de arma y coste siguen
aplicando a cada habilidad.

## Implementación

`CumulativeSubclassSkills=True` y
`CumulativeSubclassThirdSkillsActiveOnly=True` en Player.ini.
`Player.restoreSkills` lee también class_index: el slot activo aporta sus
skills aprendidos completos; cada slot inactivo aporta sólo lo que existe
en el árbol completo de su antecesor de segunda, limitado a esos niveles.
Luego se resuelven niveles compartidos y masteries sin duplicarlas.
La carga, recarga y cambio de sub usan esta misma regla.

La opción False de acumulación usada en el commit 48166c1 fue demasiado
amplia y queda reemplazada. Sus estadísticas son de la regla anterior.
Las capturas actuales usan `fixed-racial-hybrid-third-v1`; el panel oculta
lecturas de las reglas anteriores o de una clase activa diferente.

Las combinaciones de los siete pilotos se conservan por ahora: esta corrección
cambia la regla de skills, no el reparto de clases. RealHumanPilots migra la
receta a `human-pilots-v3-hybrid-third`, recorre los cuatro slots y verifica
los niveles permitidos, skills de segunda heredados, exclusión de terceras
inactivas, deduplicación de masteries y origen racial. Recarga Sub3 y retorna
a principal, comparando stats antes y después de recargar.

Validación real completada: 35/35 checks en los siete pilotos, incluyendo
recarga de Sub3; sin terceras inactivas presentes ni masteries duplicadas.
Raíces raciales constantes y cifras iguales antes/después de recarga.
Caelan con Sagittarius activo pasa de 54 a 111 skills efectivos; Ignara
de 74 a 158. Es acumulación de utilidades/passivos de segunda, sin conceder
todo el catálogo de tercera. Core completo (1.617 fuentes) y scripts compilados.

El respaldo previo está en
`E:\l2-local\backups\hybrid-third-active-2026-10-08` e incluye jar, fuentes
y dump SQL completo. El dump y binarios no se publican.
