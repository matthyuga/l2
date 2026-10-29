Estado vigente ? 24/10/2026: el usuario confirm? ?quedo perfecto? despu?s de instalar V5 y reiniciar L2. Sticker visible y colocado sobre la cabeza. Las 19 acciones usan Bip01_head y bAbsolute=true. REA identific? que Bip01 Neck1 fallaba en AttachToBone y el motor eliminaba el emisor; el hueso correcto permite crearlo, y la orientaci?n absoluta corrige el desplazamiento lateral. Sin sondeo de teclado; apertura por bot?n. Duraci?n configurada: 3 segundos; espera entre env?os: 5 segundos. Seguimiento en movimiento, tiempo exacto y vista desde otro cliente no se comprobaron por separado. Respaldo V5: E:\l2-local\backups\stickers-rea-v5-20261024-175600. Rollback maestro actualizado.

# Investigación REA del sticker invisible

El chat confirma `Sticker enviado`, pero el usuario no observa el dibujo en el mundo. No se considera validado el render.

REA/Ghidra sobre Engine.dll: OnReceiveMagicSkillUse consulta GetMSData; con operate_type=0 carga SkillVisualEffect y llama TriggerTransientEffect. Este recorre CastingActions. SkillAction_LocateEffect crea un Emitter y, para AttachOn=3, exige AttachToBone satisfactorio; puede destruir el actor y devolver null si falla la unión o el contexto del skill.

La descompilación tiene limitaciones de recuperación de pila/parámetros. Las direcciones y llamadas se conservan en los JSON de Evidence. No se modificó Engine.dll.

Traza real: GetMSData encuentra19720/19721 con operate_type0; StaticLoadObject carga NexusStickerEffectsV3.Sticker0/1; CastingActions tiene una acción válida; SpawnActor crea el Emitter. AttachToBone con FName8307 (`Bip01 Neck1`) devuelve0 y el motor destruye el actor.

El hueso de cabeza del APawn activo está en offset0x450 y contiene FName2234 (`Bip01_head`), leído de la tabla de nombres de Core. Prueba reversible en memoria: sólo AttachBoneName de Sticker0Action/Sticker1Action cambió8307→2234. Mismo comando, mismo emisor y recursos: AttachToBone devuelve1, contexto de skill válido, LocateEffect devuelve el actor. Engine.dll y las funciones nativas no se parchearon como solución.

`fix-head.groovy` preparó el paquete con las19 acciones corregidas y verificó por parser nativo que los demás exports conservan sus bytes. Pendiente instalar en disco con cliente cerrado y confirmar aparición visual/posición/duración. El éxito de unión en REA aún no equivale a confirmación visual del usuario.

Corrección del usuario: el sticker aparece AL COSTADO, no sobre la cabeza. Render visible confirmado, posición correcta NO confirmada. Se instaló la revisión con Bip01_head y bAbsolute=true en las19 acciones. Hipótesis de posición: el desplazamiento local Z35 gira con el hueso de cabeza; bAbsolute debe evitar esa rotación. Verificación por parser y preservación de exports aprobadas; todavía requiere prueba visual. Respaldo: backups/stickers-rea-v5-20261024-175600.
