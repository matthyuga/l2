import java.nio.ByteBuffer
import java.nio.ByteOrder

def root=new File(args[0]); def project=root.parentFile.parentFile
def client=new File(project.parentFile,'l2/system-hud')
def stage=new File(root,'exports/contract/native-controls');stage.mkdirs()
def schemas=new File(root,'tools/L2ClientDat/dist/data/structure/dats')
def codec=new File(project,'tools/open-l2encdec-1.3.9/l2encdec_win.exe')
def run={List<String> command->
 def p=new ProcessBuilder(command).redirectErrorStream(true).start();String out=p.inputStream.text
 if(p.waitFor()!=0)throw new IllegalStateException(out)
}
def before=new File(stage,'actionname.before.raw')
run([codec.path,'-o',before.path,new File(client,'actionname-e.dat').path])
def cat=new AmberCatalog(before,schemas,'actionname.xml','ScionsOfDestiny')
assert Arrays.equals(cat.data,cat.patch{null})
def ids=[19021,19022];assert cat.rows.every{!(it.id.intValue() in ids)}:'Native controls already present; use staged installer.'
byte[] patched=cat.patch{row->
 if(row.id==22 && !row.category2_items.any{it.'class'==59002}){
  row.category2_items=row.category2_items+[['class':59002]];row.category2=row.category2_items.size();return row
 }
 null
}
def first=new File(stage,'actionname.attack.raw');first.bytes=patched
def attack=new AmberCatalog(first,schemas,'actionname.xml','ScionsOfDestiny')
def additions=[]
for(def spec:[[19021,'Flechas de fuego','Fire','Amber: +25% dano fisico durante 15s. 60 MP de Amber. Recarga 30s.','amber fuego'],
              [19022,'Lluvia de flechas','Rain','Selecciona un enemigo PvP visible. Carga 3,5s; area fija, tres impactos. 120 MP y 3 Beast Soulshots. Recarga 45s.','amber lluvia']]){
 def row=new LinkedHashMap(cat.rows.find{it.id==1016})
 row.id=spec[0];row.category2=1;row.category2_items=[['class':59002]]
 row.cmd=spec[1];row.icon='AmberIconsV1.'+spec[2];row.name=spec[3];row.desc=spec[4]
 additions<<row
}
def stream=new ByteArrayOutputStream();stream.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(cat.count+2).array())
stream.write(patched,4,attack.end-4);additions.each{stream.write(cat.encode(it))}
stream.write(patched,attack.end,patched.length-attack.end)
def raw=new File(stage,'actionname.raw');raw.bytes=stream.toByteArray()
def check=new AmberCatalog(raw,schemas,'actionname.xml','ScionsOfDestiny')
assert check.count==cat.count+2
cat.rows.each{old->
 def fresh=check.rows.find{it.id==old.id}
 if(old.id!=22)assert Arrays.equals(Arrays.copyOfRange(cat.data,old._start,old._end),Arrays.copyOfRange(check.data,fresh._start,fresh._end))
 else assert fresh.category2_items.findAll{it.'class'!=59002}==old.category2_items
}
for(int id:ids){def row=check.rows.find{it.id==id};assert row.category==5 && row.category2_items==[['class':59002]]}
def encoded=new File(stage,'actionname-e.dat');run([codec.path,'-c','encode','-p','413','-o',encoded.path,raw.path])
def roundtrip=new File(stage,'actionname.roundtrip.raw');run([codec.path,'-o',roundtrip.path,encoded.path]);assert Arrays.equals(raw.bytes,roundtrip.bytes)
String config=new File(root,'exports/contract/visual-v3/LineageNpc.raw').getText('windows-1252')
def match=config =~ /(?ms)^\[AmberArcher\]\r?\n(.*?)(?=^\[[A-Za-z_]|\z)/
assert match.find();String section=match.group(1)
def ini=new File(stage,'AmberActorsV1.raw');ini.setText('[AmberArcher]\r\n'+section+'\r\n','windows-1252')
run([codec.path,'-c','encode','-p','111','-o',new File(stage,'AmberActorsV1.int').path,ini.path])
println 'Amber native controls: Attack enabled, Fire/Rain actions scoped to display59002; all other action records preserved.'
println 'AmberActorsV1.int: dedicated animation localization beside the custom actor package.'
