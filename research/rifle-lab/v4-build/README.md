# Rifle V4 — textured body and six states

2026-10-15. Supersedes blue V3 NPC. User rejected V3: floated, missing textures, only aiming.

Prepared in v4-textures: native Fighter female pieces with original FFighter.utx diffuse maps, and restored missing native FFighter_m000_f face. BodyAtlas RGBA retains hair alpha, plus existing RifleAtlas. 6003 faces, 76 bones; existing geometry/weights unchanged. Preview v4-build/six-states.png is offline Blender, not game validation.

Six original separate AgiShark/Mixamo CharaStudio clips: Rifle Idle1 (peace), Rifle Idle2 (alert), Rifle Walk In Place, Rifle Run In Place, Idle Aiming, Fire Rifle. Sources recorded in v4-motion/states.json. First retarget grounded evaluated boots to0 everyframe. Final v4-build/contact/* additionally fits left arm to fixed support point relative to right-hand rifle; anatomical segment lengths preserved, max wrist error <0.000006units. Finger articulation remains native bind pose, no exact trigger/magazine grip rig added.

Native static comparison: trader mesh originZ28.3/yaw49152, native Fighter mesh originZ26.5/yaw49152; prototype origin0/yaw0. Class trader collisionHeight25, server prototype23. V4 mesh compiled originZ25/yaw49152, demo collisionHeight25, root animation grounded0. This addresses probable engine vertical compensation; actual in-game foot contact still MUST be checked, no claim exact transform traced in native engine.

Main HGRifleV4.RifleMesh linked HGRifleMotionV4.Dust2Motion contains native observed trader names: wait_Hand/Wait_1HS, AtkWait_Hand/AtkWait_1HS, walk_hand/Walk_1HS, Run_Hand/Run_1HS, Social01/SpWait01 (aim demo selector), atk01_Hand/Atk01_1HS. These aliases exist in original trader animation package. No new bot decision logic or firearm damage implemented.

6 preview meshes share geometry/textures in HGRifleV4, each linked its own wait_Hand animation package so one temporary NPC can display each loop without attack packets or AI changes. Preview npcgrp IDs59084..59089, server npc902684, twelve seconds per stage, 20minute cleanup. Walk/run in place; fire animation only, no bullet/flash/damage. Name changes identify state. Main display59083 updated to normal aliased6state set. Item32580 remains original prototype BOW and standalone V3 rifle; not granted/changed this pass.

Native validation v4-build/native-validation.json: 19 checks; multi animation 12aliases +6single preview exports identical transforms/timing to sourcePSA; 6003faces/76bones preserved, two atlas images RGBA exact. Linking changes1byte permesh in original UCC payload, all offsets/sizes and unrelated exports preserved (link-validation.json). UCC mesh origin confirmed dump25/yaw49152. These are format checks, not actual client render validation.

Install: v4-build/stage.py prepared npcgrp6527->6533. Only existingrow59083 changed, all other prior rows byteexact, six new records. stage-manifest.json has expected SHA guards. install.py REQUIRES L2closed, copies8newpackages+catalog, backup then installation.json; do not repeat after success. No serverfiles, core, scripts, AI, DB, iteminventory, mainclient touched. Another session modifies botbrain: no restart.

Runtime: compiled m4-demo-v4.jar NOT attached at preparation time. Must check GameServer PID/commandline; wait any other AttachElven operation to finish, then attach once using existing AttachElven helper. Agent retires V3 and waits connectedHellkevin, spawns single NPC ahead65u using geodata (fallback30u if height difference>20). Writes rifle-runtime-v4.txt. Do not run duplicate agent; ensure client installed before attach. Client must reopen after installation.

V4 INSTALADO tras cierre confirmado por usuario. v4-build/install.py finalizo: backup y installation.json, solo cliente laboratorio, catalogo npcgrp6527->6533 y ocho paquetes nuevos; comprobados SHA. GS27412 confirmado mismo proceso, sin attach ajeno activo. m4-demo-v4.jar adjuntado una vez: retira V3, READY espera Hellkevin para ciclo6estados12s. Cliente lab solicitado abrir. Verificar procesoL2 y rifle-runtime-v4.txt; apariencia/altura ingame aun pendientes, no declarar solucionadas sin captura. Sin reinicio ni cambios AI/core/DB/inventario.
