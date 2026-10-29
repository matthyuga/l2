from pathlib import Path
import subprocess,concurrent.futures
S=Path(r'E:\l2-local\research\npc-batch2');blender=r'D:\BlenderVersions\blender-3.5.1-windows-x64\blender.exe'
def render(i):
 p=subprocess.run([blender,'-b','-t','2','--python',str(S/'render_batch.py'),'--','--manifest='+str(S/('render-'+str(i)+'.json'))],capture_output=True,timeout=2400,creationflags=subprocess.CREATE_NO_WINDOW)
 (S/('render-'+str(i)+'.log')).write_bytes(p.stdout+p.stderr);return i,p.returncode
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 for r in ex.map(render,range(3)):print('RENDER',r,flush=True)
