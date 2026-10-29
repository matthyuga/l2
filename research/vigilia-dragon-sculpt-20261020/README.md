# Vigilia ? drag?n de proa recreado ? 20/10/2026

Estado: COMPLETADO EN EL TALLER. Tras comprobar que la descarga oficial requer?a autenticaci?n, Kevin autoriz? recrear la cabeza a partir de la referencia. Se cre? geometr?a propia; no se utiliz? la malla de Sketchfab. La nota anterior de archivo pendiente queda como hist?rico en README-descarga-pendiente-historico.md.

## Abrir

- Aeronave: http://127.0.0.1:32290/?project=vigiliadragon1.json
- Revisi?n sin globo y con referencias de personaje: http://127.0.0.1:32290/?project=vigiliadragon1-escala.json
- Vista 9 del proyecto: detalle del drag?n.

El nuevo mascar?n tiene anatom?a continua fusionada por v?xeles y suavizada, hocico perfilado, cejas pesadas, ojos estrechos de turquesa con pupila vertical, mand?bula abierta y colmillos curvos, placas superpuestas en cabeza/hocico/cuello, grandes cuernos barridos, abanicos nervados y corona dorsal. Acabados de bronce antiguo y p?tina verde. Es una interpretaci?n original de la referencia; no una r?plica exacta del esculpido de winner_77.

## Conservaci?n y alcance

Parte de research/vigilia-clan-renovada2/Vigilia-renovada2.blend, conservado por SHA-256. Se identificaron y retiraron ?nicamente las piezas del mascar?n anterior en VIG_00_Casco. La firma geom?trica de las otras 1.467 mallas se comprob? antes y despu?s sin cambios. La recreaci?n conserva 326 piezas en el m?ster; el export agrupa por material. En el proyecto nuevo, las otras 15 zonas conservan sus IDs, recursos, transformaciones y visibilidad. La cabeza es una zona independiente VIG_16_Dragon. Casco sin cabeza antigua y cabeza nueva se exportan a un recurso separado; los dem?s componentes reutilizan los recursos existentes.

Vigiliarenovada2, su JSON, su Blender y su export se conservan. No se alteraron borradores del navegador, Gludio, Academy/Hellgames ni el cliente nativo. Esta entrega est? en el editor visual; no instala el modelo en L2 ni modifica colisiones/geodata.

## Archivos

- M?ster editable: Vigilia-dragon-recreado.blend.
- Generador: recreate_dragon.py. No reejecutar tras ediciones manuales sin respaldarlas.
- Registro: register-recreation.cjs. Rechaza sobrescribir proyectos existentes sin --rebuild.
- Export: research/model-catalog/exports/vigilia-dragon-sculpt/dragon.gltf y dragon.bin.
- Proyecto: research/scene-editor/projects/vigiliadragon1.json; copia id?ntica en mapas editados/vigiliadragon1.
- Variante de escala: vigiliadragon1-escala.json, copia separada.
- Capturas del taller: mapas editados/vigiliadragon1/general.jpg, dragon-integrado.jpg, dragon-diseno.jpg, cubierta-conservada.jpg.
- Auditor?a: recreation-audit.json; verificaci?n: verification.json; registro: project-registration.json.
- Respaldo de cat?logos antes del registro: backups/vigilia-dragon-recreado-20261020.

## Validaci?n

verify-recreation.cjs PASS: carga WebGL de 17 objetos, conservaci?n exacta de las 15 zonas ajenas al mascar?n/casco, exportaci?n JSON, guardado API, recarga, variante con referencia de personaje y sin errores JavaScript/HTTP. Revisi?n visual del conjunto, detalle integrado y cabeza aislada. Aproximadamente 265.000 tri?ngulos en la vista general y 81 llamadas de dibujo. El export de reemplazo (casco + cabeza) contiene 168.682 tri?ngulos.

## Referencia art?stica

Dragon head 3D print model 57x50x57 ? winner_77.
https://sketchfab.com/3d-models/dragon-head-3d-print-model-57x50x57-9557cfecc9fc489295e23bc91a57d603
Autor: https://www.artstation.com/alex_v_s_77
El modelo de referencia figura como CC Attribution 4.0. La malla no se obtuvo; la imagen p?blica se us? como gu?a visual. Metadatos y vista previa conservados en source-metadata.json y source-preview.jpg. Esta recreaci?n utiliza topolog?a y detalles generados localmente.
