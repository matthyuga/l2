"""Modify exported geometry and re-import it through the installed UE2 editor."""
import pathlib,re,subprocess,json,shutil,struct,time
D=pathlib.Path(__file__).resolve().parent
S=D/'compiler';S.mkdir(exist_ok=True)
for p in (D/'system').iterdir():
    if p.is_file() and p.suffix.lower() in ('.u','.exe','.dll','.ini','.int'):shutil.copy2(p,S/p.name)
src=D/'export-Statues_S/statue_wingGirl_A.t3d'
text=src.read_text()
def vertex(m):
    return m[1]+f'{float(m[2])*1.25:.6f}'+m[3]
edited=re.sub(r'(^\s*Vertex \d+ )([-\d.]+)( .*$)',vertex,text,flags=re.M)
edited=re.sub(r'(BoundingBox\.(?:Min|Max)\.X=)([-\d.]+)',lambda m:m[1]+f'{float(m[2])*1.25:.6f}',edited)
asset=D/'statue_wingGirl_A_wider.t3d';asset.write_text(edited)
def chunk(tag,data):return tag+struct.pack('>I',len(data))+data+(b'\0' if len(data)%2 else b'')
def sub(tag,data):return tag+struct.pack('>H',len(data))+data+(b'\0' if len(data)%2 else b'')
def string(s):
    b=s.encode()+b'\0';return b+(b'\0' if len(b)%2 else b'')
vertices=[];uv=[];faces=[];materials=[];face_materials=[]
for tri in re.findall(r'Begin Triangle(.*?)End Triangle',edited,re.S):
    material=re.search(r'Texture (\S+)',tri)[1].split('.')[-1]
    if material not in materials:materials.append(material)
    face_materials.append(materials.index(material));face=[]
    for v in re.findall(r'Vertex \d+ ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)',tri):
        x,y,z,u,t=map(float,v);face.append(len(vertices));vertices.append((x,z,-y));uv.append((u,1-t))
    faces.append(face)
assert len(vertices)<65536
data=b'LWO2'+chunk(b'PNTS',b''.join(struct.pack('>fff',*v) for v in vertices))+chunk(b'POLS',b'FACE'+b''.join(struct.pack('>HHHH',3,*f) for f in faces))+chunk(b'TAGS',b''.join(string(m) for m in materials))+chunk(b'PTAG',b'SURF'+b''.join(struct.pack('>HH',i,m) for i,m in enumerate(face_materials)))+chunk(b'VMAP',b'TXUV'+struct.pack('>H',2)+string('Texture')+b''.join(struct.pack('>Hff',i,*v) for i,v in enumerate(uv)))
for material in materials:
    mapping=sub(b'IMAP',string('1')+sub(b'CHAN',b'COLR')+sub(b'ENAB',struct.pack('>H',1)))+sub(b'PROJ',struct.pack('>H',5))+sub(b'VMAP',string('Texture'))
    data+=chunk(b'SURF',string(material)+string('')+sub(b'COLR',struct.pack('>fffH',1,1,1,0))+sub(b'SIDE',struct.pack('>H',1))+sub(b'BLOK',mapping))
asset=D/'statue_wingGirl_A_wider.lwo';asset.write_bytes(b'FORM'+struct.pack('>I',len(data))+data)
classes=D/'HGStatueProbe/Classes';classes.mkdir(parents=True,exist_ok=True)
(classes/'StatueProbe.uc').write_text('class StatueProbe extends Actor;\n#exec OBJ LOAD FILE="'+(D/'packages/statues_t.utx').as_posix()+'"\n#exec STATICMESH IMPORT NAME=WingGirlWider FILE="'+asset.as_posix()+'"\ndefaultproperties\n{\n DrawType=DT_StaticMesh\n StaticMesh=StaticMesh\'HGStatueProbe.WingGirlWider\'\n}\n')
ini=(S/'Probe.ini').read_text()+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=HGStatueProbe\n'
(S/'StatueProbe.ini').write_text(ini)
if (S/'HGStatueProbe.u').exists():shutil.move(S/'HGStatueProbe.u',D/('trial-'+str(time.time_ns())+'.u'))
r=subprocess.run([str(S/'UCC.exe'),'make','-Silent','-NoBind','ini=StatueProbe.ini','-unattended'],cwd=S,capture_output=True,text=True,errors='replace',timeout=40)
(D/'statue-import.txt').write_text(r.stdout+r.stderr)
print('IMPORT',r.returncode,(r.stdout+r.stderr)[-3500:])
pkg=S/'HGStatueProbe.u'
if r.returncode==0 and pkg.exists():
    out=D/'roundtrip';out.mkdir(exist_ok=True)
    r=subprocess.run([str(S/'UCC.exe'),'batchexport',str(pkg),'StaticMesh','t3d',str(out),'ini=Probe.ini','-unattended'],cwd=S,capture_output=True,text=True,errors='replace',timeout=30)
    (D/'statue-roundtrip.txt').write_text(r.stdout+r.stderr)
    print('RELOAD',r.returncode,(r.stdout+r.stderr)[-2000:])
