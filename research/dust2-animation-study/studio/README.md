# CharaStudio motion extraction proof — 2026-10-15

Original bundles were read only. This directory contains an independent offline transform extraction; no game files were installed or changed.

## Extracted candidates

| JSON file | Studio UI label (from shipped info/00.unity3d) | Duration | Samples at 30 Hz | Intended experiment |
|---|---|---:|---:|---|
| `mc_m_squat_00_00_01.motion.json` | しゃがみ (crouching) | 3 s | 91 | Lower body crouch loop |
| `f_suwari_00_10_M.motion.json` | ゲームをする (play a video game) | 5 s | 151 | Upper body hand manipulation |
| `f_suwari_00_09_01_M.motion.json` | フリック操作 (flick operation) | 4.8333 s | 146 | Upper body hand manipulation |

The actual squat exercise is a different clip, `m_action_00_00` (スクワット); our first extracted candidate is crouching, not an exercise.

`animation_ui_metadata.json` preserves the source Studio animation metadata, including labels, clip identifiers, controller names and source bundle paths.

## Format

Each motion JSON contains `fps`, `duration_seconds`, `bones`, `frames`, `source` and `validation`.

- `bones`: 580 source transforms from `p_cf_body_bone`, each with `name`, `path`, integer `parent` index (`-1` for root), CRC32 `hash`, and `rest`.
- `rest` and each frame's `transforms`: `position` XYZ, `rotation` quaternion XYZW, and `scale` XYZ in bone local space.
- `frames`: time in seconds and a `transforms` array in the same order as `bones`.
- Coordinates are original Unity left handed, X right, Y up, Z forward, metres. Coordinate conversion belongs in the retarget importer.
- Unanimated transforms use actual Transform object local rest values from `oo_base.unity3d`, **not** the Avatar internal pose, which uses a different sign convention.
- Streamed curves are evaluated as cubic polynomials; dense values are sampled/interpolated; constant values are copied. Rotations are normalized.

## Verification

Each clip has 963 transform bindings (321 transforms, three property bindings each). 951/963 bindings resolve to the extracted hierarchy. Four transform hashes remain unknown; all main body joints resolve. The 17 helper transform paths absent from the Avatar TOS are resolved from CRC32 of actual hierarchy paths, verified against every known Avatar hash.

For the crouching clip:

- 229 streamed scalar curves + 206 dense scalar curves + 2775 constant scalars = 3210, exactly matching the binding dimensions.
- 2240 adjacent streamed polynomial endpoints agree with the next source key value to maximum absolute error `7.914803257e-10`.
- Maximum source quaternion norm error before normalization: `2.006061294e-6`.
- Hip world height remains between 0.48205 and 0.48240 m, compared with rest height 1.14350 m. This corroborates the crouching UI label.
- No nonfinite samples or invalid quaternions were accepted.

The two hand motion candidates also pass dimension, finite-value and quaternion checks. Their chairs/phones/controllers are not exported. They are **candidate source gestures**, not final bomb animations.

## Reproduce

Use the installed Python310 with UnityPy:

```powershell
python .\extract_motion.py
python .\extract_motion.py --clip f_suwari_00_10_M
python .\extract_motion.py --clip f_suwari_00_09_01_M
python .\verify_stream.py
python .\motion_metrics.py
```

## Remaining limits

This exports the clip's transform tracks, not runtime CharaStudio IK, constraints, look-at or procedural corrections. Bomb manipulation needs artistic retargeting, contact correction, and client playback validation. Source root motion and scale must be handled deliberately for L2. No claim is made that these outputs can already be installed as Interlude player animations.
