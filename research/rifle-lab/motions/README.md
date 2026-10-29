# Rifle motion source evidence — 2026-10-15

Found actual rifle animation family in the installed Koikatsu zipmod:
`K:\JUEGOS\KOIKATSU 22\mods\Sideloader Modpack - Animations\AgiShark\[AgiShark] Mixamo animations for CharaStudio v3.1.2.zipmod`.

The source's README identifies these as Mixamo animations adapted for CharaStudio; these are not native Koikatsu-authored motions. CSV `abdata/studio/info/Kohai/Anime_00_1011_06.csv` records the exact display names, Studio IDs, bundle, controller and clip names. Rifle clips are category 6 in group 1011. No per-model AK-47/M16 association is encoded in those rows; weapon alignment still needs verification on the selected model.

## Extracted clips

All six decode at 60 fps against the same original `oo_base.unity3d` cf rig (580 bones). Each has 384/384 transform bindings resolved by path CRC32, zero unknown bindings. The previous extractor was imported unchanged and its `decode_clip()` was reused. Motion files keep the existing `bones/rest/frames/transforms` local-transform schema used by the dust2 retargeter.

| Studio ID | Exact clip | Seconds | JSON |
| --- | --- | --- | --- |
| 42 | Idle Aiming | 2.0833 | Idle_Aiming.motion.json |
| 25 | Fire Rifle | 1.0167 | Fire_Rifle.motion.json |
| 99 | Rifle Idle 1 | 10.6000 | Rifle_Idle_1.motion.json |
| 82 | Reload 1 | 6.8333 | Reload_1.motion.json |
| 103 | Rifle Run In Place | 0.6500 | Rifle_Run_In_Place.motion.json |
| 149 | Taking Cover | 2.2500 | Taking_Cover.motion.json |

`rifle_clip_catalog.json` additionally retains rifle, aim, reload and cover rows across all animation categories; `Anime_00_1011_06.csv` preserves the full original 168-entry gun category, including pistol clips that must not be mislabeled rifle. `extraction_summary.json` records exact durations, counts and rig identity. `source_manifest.json` records SHA256 of the source zipmod, copied bundles and CSV.

## Limits

This is extraction and numeric validation, not an in-game result. Runtime CharaStudio IK, constraints and look-at are not evaluated. No magazine or prop motion is inferred from a character clip. Hand contact, stock position, recoil and L2 weapon socket must be checked on the target character. A static rifle mesh alone cannot depict a detachable magazine during reload.

No live L2, server files or original extraction scripts were modified by this worker. All outputs stay in this directory.
