"""Prepare the seven other native Dion building types, without substituting designs."""
from pathlib import Path
import bpy,json,sys,runpy,shutil
ROOT=Path(__file__).resolve().parent;CAT=ROOT.parent/'model-catalog';OUT=CAT/'exports/dion-city-rubble-v2';OUT.mkdir(parents=True,exist_ok=True)
types={4:['StaticMeshActor492_0','StaticMeshActor493_0'],5:['StaticMeshActor491_0','StaticMeshActor494_0'],6:['StaticMeshActor1352_0','StaticMeshActor2_0'],7:['StaticMeshActor403_0','StaticMeshActor1122_0'],8:['StaticMeshActor10_0','StaticMeshActor70_0'],9:['StaticMeshActor671_0','StaticMeshActor69_0'],10:['StaticMeshActor527_0','StaticMeshActor793_0']}
slim=OUT/'source-buildings.blend'
if not slim.exists():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    source=ROOT.parent/'scenario-batches/library_fe488fdfccee/scene-with-terrain.blend'
    with bpy.data.libraries.load(str(source),link=False) as (available,target):target.objects=[name for names in types.values() for name in names]
    for obj in target.objects:
        assert obj is not None
        bpy.context.scene.collection.objects.link(obj)
    bpy.ops.wm.save_as_mainfile(filepath=str(slim))
    print('SLIM SOURCE READY',flush=True)
staging=OUT/'raw';staging.mkdir(exist_ok=True)
for number,names in types.items():
    target=staging/f'house{number}.glb'
    if target.exists():continue
    output=f'dion-city-type{number}-raw-v2'
    sys.argv=['blender','--','--output',output,'--actors',*names,'--static','--source',str(slim)]
    runpy.run_path(str(ROOT/'build-dion-collapse.py'),run_name='__main__')
    shutil.copy2(CAT/f'exports/{output}/ruins.glb',target)
    print('RAW TYPE READY',number,flush=True)
missing=[i for i in types if not (OUT/f'house{i}.glb').exists()]
if missing:
    sys.argv=['blender','--','--source-dir',str(staging),'--output','dion-city-rubble-v2','--houses',*map(str,missing)]
    runpy.run_path(str(ROOT/'build-dion-rubble-v2.py'),run_name='__main__')
print('EXTRA BUILDINGS COMPLETE',flush=True)
