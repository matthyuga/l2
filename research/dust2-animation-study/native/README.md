# Native animation packaging: offline proof

2026-10-15. All outputs stay within this research folder. No client, catalog, server, source or PvP rooms modified.

## Result

`Dust2Crouch.ukx` contains a NEW `Engine.MeshAnimation` export `Dust2Motion`, sequence `Dust2_Crouch_FFighter`. Input is the retargeted Studio clip `../retarget/StudioSquat_FFighter.psa`, 76 bones, 91 frames, 30 fps. It uses the authoritative FFighter PSK parent hierarchy. `roundtrip-validation.json` records **0.0 maximum error** for every position and quaternion after source PSA -> native UKX -> UModel PSA. This resolves the earlier UCC/PSA serialization obstacle for an offline UModel consumer. The output is not copied to the game.

Package is unencrypted UE2 version 123/licensee30, matching the decoded native Fighter header. Source structure from Gildor's UModel `Unreal/UnrealMesh/UnMesh2.h` and `UnAnim2.cpp`, especially `SerializeLineageMoves`: Lineage's TRoughArray writes an absolute global end position, compact move count and absolute local end before each MotionChunk. These positions cannot be copied after relocating exports. FMeshAnimSeq also requires Lineage extension fields and FLineageUnk4. New data uses plain float tracks and zeroed optional metadata; native client acceptance of these exact defaults remains untested.

`write_l2_animation.py` is dependency-free. Accepts PSA (`--sequence` selects one) or JSON `{bones:[{name,parent}],fps,frames:[{positions:[[x,y,z]],rotations:[[x,y,z,w]]}]}`. JSON positions/quaternions are native L2 local-space transforms. PSA input uses UModel/ActorX coordinates: mirror position Y and negate quaternion Y/W. `--skeleton path.psk` enforces bone names/order and imports real parents because an animation-only PSA may have placeholder parents. Output GUID is deterministic from contents.

## Reproduce

```powershell
python .\write_l2_animation.py ..\retarget\StudioSquat_FFighter.psa .\Dust2Crouch.ukx --skeleton E:\l2-local\research\amber-l2\exports\l2-reference\Fighter\SkeletalMesh\FFighter_m001_u.psk --name Dust2_Crouch_FFighter
E:\l2-local\research\amber-l2\tools\umodel.exe -export -game=l2 -out=.\roundtrip .\Dust2Crouch.ukx
```

`Dust2Motion.ukx` is an earlier serializer smoke test using one existing native clip. Use `Dust2Crouch.ukx` for the actual Studio movement.

## Client action route: observed vs unknown

`inspect_package.py` performs read-only package-table inspection and supports original Lineage2Ver111 XOR packages. `client-action-evidence.txt` extracts embedded Engine.u ScriptText and records original export numbers, offsets, sizes. Engine exposes `Actor.LinkSkelAnim(MeshAnimation, optional mesh)`, `Actor.PlayAnim(name, rate, tween, channel)` and `Pawn.PlayAnimUM`. It also has per-weapon arrays for CastShort/Mid/Long/End, Magic and SpAtk01..28.

The shipped SkillAction subclasses found are `SkillAction_LocateEffect` and `SkillAction_SwordTrail`. Their properties control emitter spawning and weapon trails, not arbitrary character animation. This does not justify inventing `SkillAction_PlayAnimation` or assuming skill.usk can invoke arbitrary motion names.

The Interlude skillgrp schema uses `cast_style` plus `animation` string; historical decoded catalog examples (`skillgrp-sample.json`) show short selectors: skill4=`X`, skill1059=`D`. The next string called `description` stores `skill.mo.4` / `skill.su.1059` SkillVisualEffect references. Thus the schema name `animation` is not evidence it accepts a new `Package.Sequence` path. Native selector mapping and animation attachment still need investigation/runtime validation.

An isolated mesh/NPC with this MeshAnimation linked can validate actual client decoding/reproduction before attempting player actions. Adding movement to player skeletons must preserve existing animation sets, all player mesh variants and observers; standalone package existence does not establish that integration. No player trigger or game binding is installed by this proof.

Primary source: https://github.com/gildor2/UModel/blob/master/Unreal/UnrealMesh/UnAnim2.cpp (SerializeLineageMoves), https://github.com/gildor2/UModel/blob/master/Unreal/UnrealMesh/UnMesh2.h (MotionChunk/FMeshAnimSeq). Local shipped Engine.u is the authority for available action classes.
