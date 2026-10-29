"""Inspect native L2 animation tracks; never modifies original Fighter.ukx."""
import pathlib,struct,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Reader:
    def __init__(self,data):self.data=data;self.p=0
    def ci(self):
        b=self.data[self.p];self.p+=1;v=b&63;neg=b&128;more=b&64;shift=6
        while more:b=self.data[self.p];self.p+=1;v|=(b&127)<<shift;more=b&128;shift+=7
        return -v if neg else v
    def ints(self,n=1):v=struct.unpack_from('<'+'i'*n,self.data,self.p);self.p+=4*n;return v[0] if n==1 else v
    def floats(self,n):v=struct.unpack_from('<'+'f'*n,self.data,self.p);self.p+=4*n;return v
    def track(self):
        flags=self.ints();n=self.ci();qpos=self.p;self.p+=16*n;npos=self.ci();ppos=self.p;self.p+=12*npos;nt=self.ci();tpos=self.p;self.p+=4*nt
        assert 0<=n<10000 and 0<=npos<10000 and 0<=nt<10000
        return dict(flags=flags,quat_offset=qpos,quat_count=n,pos_offset=ppos,pos_count=npos,time_offset=tpos,time_count=nt)
if __name__=='__main__':
    names=(ROOT/'reports/archer-animation-names.txt').read_text().splitlines()
    r=Reader((ROOT/'reports/archer-animation-native.bin').read_bytes());print('properties',r.ci(),'version',r.ints())
    bones=[(names[r.ci()],r.ints(2)) for _ in range(r.ci())];print('bones',len(bones),bones[:5],'position',r.p)
    roughend=r.ints();count=r.ci();print('roughend',roughend,'moves count',count,'position',r.p)
    moves=[]
    for i in range(count):
        end=r.ints();start=r.p;root=r.floats(4);sb,flags=r.ints(2);indices=[r.ints() for _ in range(r.ci())];tracks=[r.track() for _ in range(r.ci())];rt=r.track()
        moves.append(dict(index=i,start=start,end=r.p,absolute_end=end,duration=root[3],indices=indices,tracks=tracks))
        if i<3:print('move',i,'duration',root[3],'indices',len(indices),'tracks',len(tracks),'end',r.p,'absolute',end)
    print('moves end',r.p,'next',r.data[r.p:r.p+80].hex())
    (ROOT/'reports/archer-native-tracks.json').write_text(json.dumps(dict(bones=bones,moves=moves,sequence_offset=r.p),indent=2))
