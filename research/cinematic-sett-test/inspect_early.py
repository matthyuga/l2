import bpy,json,pathlib
p=pathlib.Path(r'E:\l2-local\research\cinematic-sett-test');s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE')
rows=[]
for f in range(1,2182,12):
 s.frame_set(f);rows.append([f]+[round(v,3) for n in ['bip001_l_foot','bip001_r_foot'] for v in rig.pose.bones[n].head])
(p/'feet.json').write_text(json.dumps(rows))
for f in [30,60,90,120,150,180,210,270,300,330]:
 s.frame_set(f);s.render.filepath=str(p/('early-%04d.png'%f));bpy.ops.render.render(write_still=True)

