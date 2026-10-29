"""Pack six equipment slots into one atlas: L2 NPC texture index must be <5."""
import struct
from PIL import Image

def pack_materials(root, chunks):
    cell=512; pad=8
    atlas=Image.new('RGB',(cell*4,cell*2),(35,40,43))
    for old in range(2,8):
        x=((old-2)%4)*cell;y=((old-2)//4)*cell
        tile=Image.open(root/f'Mat{old}.tga').convert('RGB').resize((cell-2*pad,cell-2*pad),Image.Resampling.LANCZOS)
        atlas.paste(tile,(x+pad,y+pad))
        atlas.paste(tile.crop((0,0,1,tile.height)).resize((pad,tile.height)),(x,y+pad))
        atlas.paste(tile.crop((tile.width-1,0,tile.width,tile.height)).resize((pad,tile.height)),(x+cell-pad,y+pad))
        atlas.paste(atlas.crop((x,y+pad,x+cell,y+pad+1)).resize((cell,pad)),(x,y))
        atlas.paste(atlas.crop((x,y+cell-pad-1,x+cell,y+cell-pad)).resize((cell,pad)),(x,y+cell-pad))
    atlas.save(root/'EquipmentAtlas.tga')
    source=chunks(root/'BehemothTwoRiders.psk');result=bytearray()
    for name,(size,count,raw) in source.items():
        data=bytearray(raw)
        if name=='VTXW0000':
            for i in range(count):
                at=i*size;old=data[at+12]
                if old<2:continue
                u,v=struct.unpack_from('<ff',data,at+4)
                assert 0<=u<=1 and 0<=v<=1
                u=(((old-2)%4)*cell+pad+u*(cell-2*pad))/atlas.width
                v=(((old-2)//4)*cell+pad+v*(cell-2*pad))/atlas.height
                struct.pack_into('<ff',data,at+4,u,v);data[at+12]=2
        if name=='FACE0000':
            for i in range(count):
                at=i*size+6
                if data[at]>=2:data[at]=2
        if name=='REFSKELT':
            bone_names=[struct.unpack_from('<64s',data,i*size)[0].rstrip(b'\0') for i in range(count)]
            assert b'Bone15' not in bone_names
            parent=bone_names.index(b'Bip01 Spine1')
            seat=bytearray((root/'SeatBoneNativeRecord.bin').read_bytes());assert len(seat)==120 and seat[:64].rstrip(b'\0')==b'Bone15'
            struct.pack_into('<i',seat,72,parent)
            children=struct.unpack_from('<i',data,parent*size+68)[0];struct.pack_into('<i',data,parent*size+68,children+1)
            data+=seat;count+=1
        if name=='MATT0000':
            data=data[:size*3];count=3
            data[2*size:2*size+64]=b'EquipmentAtlas'.ljust(64,b'\0')
        result+=struct.pack('<20s3i',name.encode(),1999801,size,count)+data
    target=root/'BehemothTwoRiders-native-3mat.psk';target.write_bytes(result)
    check=chunks(target)
    assert check['MATT0000'][1]==3
    assert max(check['VTXW0000'][2][12::16])<3
    assert max(check['FACE0000'][2][6::12])<3
    assert check['REFSKELT'][1]==source['REFSKELT'][1]+1
    assert check['PNTS0000']==source['PNTS0000'] and check['RAWWEIGHTS']==source['RAWWEIGHTS']
    return target,{0:root/'Mat0.tga',1:root/'Mat1.tga',2:root/'EquipmentAtlas.tga'}
