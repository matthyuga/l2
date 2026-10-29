import acmi.l2.clientmod.io.UnrealPackage
def root=new File(args[0])
def motion=new File(root,'exports/L2AmberArcherMotion.ukx');motion.bytes=new File('E:/l2/animations/Fighter.ukx').bytes
def aliases=['Wait_Bow_FFighter':'Wait_Hand','Walk_Bow_FFighter':'walk_hand','Run_Bow_FFighter':'Run_Hand','AtkWait_Bow_FFighter':'AtkWait_Hand','Atk01_Bow_FFighter':'atk01_Hand','SpAtk01_Bow_FFighter':'SpAtk01_Hand','SpAtk02_Bow_FFighter':'SpAtk02_Hand','Death_FFighter':'Death_Hand','DeathWait_FFighter':'deathwait_Hand','Damage_FFighter':'Damage_Hand']
new UnrealPackage(motion,false).withCloseable {up->
    def anim=up.exportTable.find{it.objectInnerFullName=='FFighter_anim'}
    def patched=new File(root,'exports/archer-sky-native.bin').bytes
    assert patched.length==anim.objectRawData.length
    anim.setObjectRawData(patched)
    up.updateNameTable{names->for(int i=0;i<names.size();i++){def name=names[i];if(aliases.containsKey(name.name))names[i]=new UnrealPackage.NameEntry(up,i,aliases[name.name],name.flags)}}
}
def mesh=new File(root,'exports/L2AmberArcher.ukx');mesh.bytes=new File(root,'exports/L2AmberNPCv4.ukx').bytes
def decode={byte[] d,int p->int b=d[p++]&255;boolean neg=(b&128)!=0;int v=b&63;boolean more=(b&64)!=0;int s=6;while(more){b=d[p++]&255;v|=(b&127)<<s;more=(b&128)!=0;s+=7};[neg?-v:v,p]}
def encode={int v->boolean n=v<0;v=Math.abs(v);def o=[(byte)((v&63)|(n?128:0)|((v>>>6)!=0?64:0))];v>>>=6;while(v){o<<(byte)((v&127)|((v>>>7)!=0?128:0));v>>>=7};o as byte[]}
new UnrealPackage(mesh,false).withCloseable {up->
    up.addImportEntries(['L2AmberArcherMotion.FFighter_anim':'Engine.MeshAnimation'])
    def old=up.importTable.find{it.objectFullName=='L2AmberMotionv3.FFighter_anim'}
    def replacement=up.importTable.find{it.objectFullName=='L2AmberArcherMotion.FFighter_anim'}
    def entry=up.exportTable.find{it.objectInnerFullName=='AmberNPC'};byte[] data=entry.objectRawData
    def expected=new File(root,'reports/expected-bones.txt').readLines();def matches=[]
    for(int p=0;p<data.length-5000;p++){try{def count=decode(data,p);if(count[0]!=expected.size())continue;int at=count[1];boolean ok=true;for(String name:expected){def bone=decode(data,at);if(bone[0]!=up.nameReference(name)){ok=false;break};at=bone[1]+56};if(ok&&decode(data,at)[0]==old.objectReference)matches<<at}catch(Exception ignored){}}
    assert matches.size()==1
    int p=matches[0];def end=decode(data,p)[1];def value=encode(replacement.objectReference);def stream=new ByteArrayOutputStream();stream.write(data,0,p);stream.write(value);stream.write(data,end,data.length-end);entry.setObjectRawData(stream.toByteArray())
}
println 'Archer packages built; original NPC v4 unchanged.'
