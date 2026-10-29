from pathlib import Path
import subprocess,json,hashlib
D=Path(__file__).resolve().parent;P=Path('E:/l2-local');root=P/'source/L2J_Mobius_CT_0_Interlude/java'
rels=['org/l2jmobius/gameserver/network/clientpackets/CharacterCreate.java']+['org/l2jmobius/gameserver/network/serverpackets/'+n+'.java' for n in ['UserInfo','CharInfo','CharSelectionInfo']]
baseline={}
for rel in rels:
 src=root/rel;text=src.read_text(encoding='utf-8');baseline[rel]=hashlib.sha256(src.read_bytes()).hexdigest()
 if rel.endswith('CharacterCreate.java'):
  text=text.replace('_hairColor = (byte) readInt();','_hairColor = org.l2jmobius.gameserver.custom.HairColorHsl.read(this, readInt());')
  old='\t\tnewChar.setCurrentHp(newChar.getMaxHp());';assert old in text
  text=text.replace(old,'\t\torg.l2jmobius.gameserver.custom.HairColorHsl.finish(this, newChar);\n'+old)
 else:
  if rel.endswith('CharSelectionInfo.java'):
   text=text.replace('buffer.writeInt(charInfoPackage.getHairColor());','buffer.writeInt(org.l2jmobius.gameserver.custom.HairColorHsl.selection(charInfoPackage.getObjectId(), charInfoPackage.getHairColor()));')
  else:text=text.replace('buffer.writeInt(appearance.getHairColor());','buffer.writeInt(org.l2jmobius.gameserver.custom.HairColorHsl.wire(_player, appearance.getHairColor()));')
 dest=D/'server-source'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding='utf-8')
(D/'server-baseline.json').write_text(json.dumps(baseline,indent=2))
java=P/'tools/jdk-25.0.4.1+1/bin';compiled=D/'compiled';compiled.mkdir(exist_ok=True)
files=[str(x) for x in (D/'server-source').rglob('*.java')]
subprocess.run([str(java/'javac.exe'),'-encoding','UTF-8','-cp',str(P/'server/libs/*'),'-d',str(compiled),*files],check=True)
print('Compiled server helper and four existing packet classes; schema unchanged.')
