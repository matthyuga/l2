"""Read downloaded PMX data without executing model content; retain evidence."""
from pathlib import Path
import struct,json,hashlib,collections
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'reference-models/amber-web-2026-10-23'
class Reader:
 def __init__(self,path):self.data=path.read_bytes();self.offset=0
 def read(self,fmt):
  fmt='<'+fmt;n=struct.calcsize(fmt);assert self.offset+n<=len(self.data)
  result=struct.unpack_from(fmt,self.data,self.offset);self.offset+=n
  return result[0] if len(result)==1 else result
 def skip(self,n):assert n>=0 and self.offset+n<=len(self.data);self.offset+=n
 def text(self):
  n=self.read('i');assert 0<=n<=len(self.data)-self.offset
  result=self.data[self.offset:self.offset+n].decode(self.encoding);self.offset+=n;return result
 def index(self,kind):return self.read({1:'B' if kind=='vertex' else 'b',2:'H' if kind=='vertex' else 'h',4:'i'}[self.sizes[kind]])
def parse(path):
 r=Reader(path);assert r.data[:4]==b'PMX ';r.offset=4;version=r.read('f');n=r.read('B');flags=r.data[r.offset:r.offset+n];r.skip(n)
 r.encoding='utf-16-le' if flags[0]==0 else 'utf-8';extra=flags[1];r.sizes=dict(zip(['vertex','texture','material','bone','morph','rigid'],flags[2:8]))
 names=[r.text() for _ in range(4)];verts=[];normals=[];uv=[];weights=[];deforms=collections.Counter()
 for _ in range(r.read('i')):
  verts.append(r.read('3f'));normals.append(r.read('3f'));uv.append(r.read('2f'));r.skip(16*extra);kind=r.read('B');deforms[kind]+=1
  if kind==0:b=[r.index('bone')];w=[1.0]
  elif kind in (1,3):
   b=[r.index('bone') for _ in range(2)];w0=r.read('f');w=[w0,1-w0]
   if kind==3:r.skip(36)
  elif kind in (2,4):b=[r.index('bone') for _ in range(4)];w=list(r.read('4f'))
  else:raise ValueError(kind)
  weights.append(list(zip(b,w)));r.skip(4)
 count=r.read('i');assert count%3==0
 indices=[r.index('vertex') for _ in range(count)];assert all(0<=v<len(verts) for v in indices)
 textures=[r.text() for _ in range(r.read('i'))];materials=[]
 for _ in range(r.read('i')):
  m=dict(name=r.text(),english=r.text(),diffuse=r.read('4f'),specular=r.read('3f'),specular_power=r.read('f'),ambient=r.read('3f'),flags=r.read('B'),edge_color=r.read('4f'),edge_size=r.read('f'),texture=r.index('texture'),sphere_texture=r.index('texture'),sphere_mode=r.read('B'))
  m['shared_toon']=r.read('B');m['toon']=r.read('B') if m['shared_toon'] else r.index('texture');m['memo']=r.text();m['index_count']=r.read('i');materials.append(m)
 assert sum(m['index_count'] for m in materials)==count
 bones=[]
 for _ in range(r.read('i')):
  b=dict(name=r.text(),english=r.text(),position=r.read('3f'),parent=r.index('bone'),layer=r.read('i'),flags=r.read('H'));f=b['flags']
  b['tail']=r.index('bone') if f&1 else r.read('3f')
  if f&0x300:b['inherit']=[r.index('bone'),r.read('f')]
  if f&0x400:r.skip(12)
  if f&0x800:r.skip(24)
  if f&0x2000:r.skip(4)
  if f&0x20:
   target=r.index('bone');loops=r.read('i');angle=r.read('f');links=[]
   for _ in range(r.read('i')):
    link=r.index('bone');limits=r.read('B')
    if limits:r.skip(24)
    links.append(link)
   b['ik']=dict(target=target,loops=loops,links=links)
  bones.append(b)
 morphs=[]
 for _ in range(r.read('i')):
  m=dict(name=r.text(),english=r.text(),panel=r.read('B'),type=r.read('B'),count=r.read('i'));kind=m['type']
  for _ in range(m['count']):
   if kind in (0,9):r.index('morph');r.skip(4)
   elif kind==1:r.index('vertex');r.skip(12)
   elif kind==2:r.index('bone');r.skip(28)
   elif kind in range(3,8):r.index('vertex');r.skip(16)
   elif kind==8:r.index('material');r.skip(1+112)
   elif kind==10:r.index('rigid');r.skip(25)
   else:raise ValueError(kind)
  morphs.append(m)
 frames=r.read('i')
 for _ in range(frames):
  r.text();r.text();r.skip(1)
  for _ in range(r.read('i')):r.index('morph' if r.read('B') else 'bone')
 rigid_count=r.read('i')
 for _ in range(rigid_count):r.text();r.text();r.index('bone');r.skip(61)
 joint_count=r.read('i')
 for _ in range(joint_count):r.text();r.text();r.skip(1);r.index('rigid');r.index('rigid');r.skip(96)
 assert r.offset==len(r.data) or version>2.05,(path,r.offset,len(r.data))
 tex=[]
 for name in textures:
  p=path.parent/Path(name.replace('\\','/'));entry=dict(name=name,exists=p.exists())
  if p.exists():
   with Image.open(p) as im:entry.update(size=list(im.size),mode=im.mode)
   entry['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  tex.append(entry)
 active=collections.Counter(b for v in weights for b,w in v if w>1e-6 and b>=0)
 report=dict(path=str(path),sha256=hashlib.sha256(r.data).hexdigest(),format_version=version,names=names,vertices=len(verts),triangles=count//3,materials=materials,textures=tex,bones=bones,weighted_bones=len(active),morphs=morphs,rigid_bodies=rigid_count,joints=joint_count,deform_types=dict(deforms),bbox=[[min(v[a] for v in verts),max(v[a] for v in verts)] for a in range(3)],parsed_bytes=r.offset,total_bytes=len(r.data))
 geometry=dict(vertices=verts,normals=normals,uv=uv,indices=indices,weights=weights)
 return report,geometry
def main():
 reports={}
 for label in ['v10','v14']:
  paths=list((BASE/label).rglob('*.pmx'));assert len(paths)==1
  report,geometry=parse(paths[0]);reports[label]=report
  (BASE/(label+'-analysis.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
  (BASE/(label+'-geometry.json')).write_text(json.dumps(geometry),encoding='utf-8')
  print(label,json.dumps({k:report[k] for k in ['vertices','triangles','weighted_bones','rigid_bodies','joints','parsed_bytes','total_bytes']}),'bones',len(report['bones']),'materials',len(report['materials']),'morphs',len(report['morphs']))
 for label,r in reports.items():assert all(t['exists'] for t in r['textures']),'missing texture '+label
 a=reports['v10'];b=reports['v14']
 print('Same PMX SHA256?',a['sha256']==b['sha256'])
 print('All referenced textures found; complete PMX files parsed.')
if __name__=='__main__':main()
