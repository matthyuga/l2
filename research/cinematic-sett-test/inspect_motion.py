import bpy,json,pathlib
p=pathlib.Path(r'E:\l2-local\research\cinematic-sett-test');s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE')
rows=[]
for f in range(1,2182,12):
 s.frame_set(f);rows.append([f]+[round(v,3) for n in ['bip001_l_foot','bip001_r_foot'] for v in rig.pose.bones[n].head])
(p/'feet.json').write_text(json.dumps(rows))
for f in [1080,1110,1140,1170,1230,1260,1560,1590,1620,1650,1710,1740]:
 s.frame_set(f);s.render.filepath=str(p/('detail-%04d.png'%f));bpy.ops.render.render(write_still=True)
