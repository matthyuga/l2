# Damage: capturas de inicio localizadas

Origen: sesión de Lineage II del 17/10/2026. Proyecto real: `E:\l2-local`.

- Revisadas visualmente las 19 imágenes `E:\l2-damage\client\Lineage II\system\Shot00000.jpg` a `Shot00018.jpg`.
- `Shot00001.jpg` muestra Tutorial con selección de arma/SA. No se localizó entre estas imágenes el selector inicial de armadura A/B/C recordado por Kevin.
- Código actual Mobius confirma TutorialShowHtml y RequestTutorialLinkHtml; sirve como base para elegir clase/equipo sin NPC obligatorio. No implementado ni probado el recorrido nuevo.
- Informe, índice de imágenes, soporte local y pendientes: `E:\l2-local\research\damage-onboarding\ANALISIS-2026-10-17.md`. Manifiesto SHA256 junto al informe.
- Computer Use sigue sin pipe nativo (os error 2), incluso después de reset. Se lanzó el cliente Damage por autorización actual del usuario; ingreso de credenciales a cargo de Kevin. No hubo observación en vivo.

Acción sugerida: completar evidencia del selector de armaduras y entrega antes de definir el inicio del servidor. No deducir instancias a partir de destinos numerados ni copiar reglas no observadas.

Actualización posterior: Kevin aportó selector de armaduras (Tallum Heavy, Majestic Light, Dark Crystal Robe), paso a arma/SA y pantalla final ciudad/leveleo; son referencias, no implementación aprobada. Se extrajeron 9.323 registros itemname y se completó una consulta REA de execRequestMultiSellChoose, con evidencia guardada. Después se revisaron 82 capturas Shot00032..00113 de artículos seleccionados y precios. Catálogo en `E:\l2-local\research\damage-onboarding\items\CATALOGO-TIENDA-OBSERVADO.md`; dos costes tapados y dos repeticiones. Hero Crown aparece por 20 Donator Coin o 30 Festival Adena; Tattoo Legend por 30.000 Damage Coin + Tattoo Unique. Mantener separado lo anunciado de efectos medidos.
