from pathlib import Path
import subprocess,json
R=Path(__file__).parent;OLD=R.parent/'motions'
exe=r'D:\BlenderVersions\blender-3.5.1-windows-x64\blender.exe'
clips=[('peace_idle',OLD/'Rifle_Idle_1.motion.json'),('combat_idle',R/'Rifle_Idle_2.motion.json'),('walk',R/'Rifle_Walk_In_Place.motion.json'),('run',OLD/'Rifle_Run_In_Place.motion.json'),('aim',OLD/'Idle_Aiming.motion.json'),('fire',OLD/'Fire_Rifle.motion.json')]
manifest=[]
for state,src in clips:
 with (R/(state+'.log')).open('w') as log:
  p=subprocess.run([exe,'-b','--factory-startup','-t','3','--python',str(R/'retarget_v4.py'),'--',str(src)],stdout=log,stderr=subprocess.STDOUT,timeout=600)
 assert p.returncode==0,(state,p.returncode)
 stem=src.stem.replace('.motion','')+'_FFighter';assert (R/(stem+'.psa')).exists()
 a=json.loads((R/(stem+'-grounding.json')).read_text())
 manifest.append({'state':state,'source_motion':str(src),'source_clip':src.stem.replace('.motion','').replace('_',' '),'blend':str(R/(stem+'.blend')),'psa':str(R/(stem+'.psa')),'grounding_audit':str(R/(stem+'-grounding.json')),'frames':len(a['frames']),'fps':60,'max_abs_boot_ground_error':a['max_abs_boot_ground_error'],'source_kind':'direct separate source clip, retargeted; no blend'})
 (R/'states.json').write_text(json.dumps(manifest,indent=2))
 print('RETARGET_DONE',state,manifest[-1]['frames'],flush=True)
