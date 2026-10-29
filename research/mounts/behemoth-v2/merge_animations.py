"""Merge animation buffers only, keeping a single copy of mesh and textures."""
import json,struct,copy
def read(path):
 d=path.read_bytes();assert d[:4]==b'glTF';n=struct.unpack_from('<I',d,12)[0];j=json.loads(d[20:20+n]);offset=20+n;length,kind=struct.unpack_from('<II',d,offset);assert kind==0x004e4942;return j,bytearray(d[offset+8:offset+8+length])
def merge(files,out):
 base,blob=read(files[0][1]);base['animations']=[]
 for name,file in files:
  source,binary=read(file);assert [n.get('name') for n in source['nodes']]==[n.get('name') for n in base['nodes']]
  views={};accessors={}
  def acc(index):
   if index in accessors:return accessors[index]
   a=copy.deepcopy(source['accessors'][index]);v=a.get('bufferView')
   assert v is not None and not a.get('sparse')
   if v not in views:
    view=copy.deepcopy(source['bufferViews'][v]);assert view.get('buffer',0)==0
    start=view.get('byteOffset',0);payload=binary[start:start+view['byteLength']]
    while len(blob)%4:blob.append(0)
    view.update(buffer=0,byteOffset=len(blob));blob.extend(payload);views[v]=len(base['bufferViews']);base['bufferViews'].append(view)
   a['bufferView']=views[v];accessors[index]=len(base['accessors']);base['accessors'].append(a);return accessors[index]
  assert len(source.get('animations',[]))==1,(name,len(source.get('animations',[])))
  clip=copy.deepcopy(source['animations'][0]);clip['name']=name
  for sampler in clip['samplers']:
   sampler['input']=acc(sampler['input']);sampler['output']=acc(sampler['output'])
  base['animations'].append(clip)
 base['buffers'][0]['byteLength']=len(blob)
 while len(blob)%4:blob.append(0)
 text=json.dumps(base,separators=(',',':')).encode()
 while len(text)%4:text+=b' '
 out.write_bytes(struct.pack('<III',0x46546c67,2,12+8+len(text)+8+len(blob))+struct.pack('<II',len(text),0x4e4f534a)+text+struct.pack('<II',len(blob),0x004e4942)+blob)
