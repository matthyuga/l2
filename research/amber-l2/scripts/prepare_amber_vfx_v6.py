"""Build sources separately from installed packages and preserve current Amber AI."""
from pathlib import Path
from PIL import Image
import hashlib, json

root = Path(__file__).resolve().parents[1]
project = root.parents[1]
stage = root / 'exports/contract/combat-vfx-v6'
stage.mkdir(parents=True, exist_ok=True)
flame = root / 'assets/external/effekseer-1.80.5/Flame01.png'
Image.open(flame).convert('RGBA').save(stage / 'EffekseerFlame.tga')
js = (root / 'scripts/build_amber_vfx_v4.js').read_text().replace('V4', 'V6').replace('v4', 'v6')
js = js.replace('Sixty independently', 'Fifty independently').replace('length:60', 'length:50')
js = js.replace('skyArrows:60', 'skyArrows:50')
js = js.replace('#exec TEXTURE IMPORT NAME=GlowFire FILE="${asset}/GlowFire.tga" MIPS=OFF',
                '#exec TEXTURE IMPORT NAME=GlowFire FILE="${root.replace(/\\\\/g,\'/\')}/exports/contract/combat-vfx-v6/EffekseerFlame.tga" MIPS=OFF')
start = js.index('for(const fire of [false,true]){')
end = js.index('// Fifty independently', start)
js = js[:start] + '''// Fifty falling arrows split across the three existing damage pulses.
const wavePositions=[positions.filter((p,i)=>i%3===0),positions.filter((p,i)=>i%3===1),positions.filter((p,i)=>i%3===2)];
for(const fire of [false,true])for(let wave=0;wave<3;wave++){
 const name=(fire?'FireRain':'Rain')+(wave+1),points=wavePositions[wave];
 fs.writeFileSync(path.join(pkg,name+'.uc'),actor(name,points.flatMap((p,i)=>[arrow(i*2,fire?'ArrowFire':'ArrowWhite',p.x,p.y,430,-600,.650,1.25),glow(i*2+1,fire,p.x,p.y,430,.650,fire?12:8,1).replace('StartVelocityRange=(X=(Min=-15,Max=15),Y=(Min=-15,Max=15),Z=(Min=10,Max=45))','StartVelocityRange=(Z=(Min=-600,Max=-600))')]),1));
 fs.writeFileSync(path.join(pkg,name+'Impact.uc'),actor(name+'Impact',points.map((p,i)=>glow(i,fire,p.x,p.y,8,.4,fire?15:8,4)),1));
}
''' + js[end:]
js = js.replace('skyReleaseIntervalMs:40,rainRadius', 'skyReleaseIntervalMs:40,waveArrowCounts:[17,17,16],rainArrowsTotal:50,rainRadius')
(root / 'scripts/build_amber_vfx_v6.js').write_text(js)

catalog = (root / 'scripts/build_amber_vfx_v5_catalogs.groovy').read_text().replace('V5', 'V6').replace('v5', 'v6').replace('19014', '19600')
catalog = catalog.replace("['Rain','FireRain','RainImpact','FireRainImpact','Mark','SkyVolley']", "['Mark','SkyVolley']+(1..3).collectMany{w->['Rain'+w,'FireRain'+w,'Rain'+w+'Impact','FireRain'+w+'Impact']}")
catalog = catalog.replace("(name in ['Rain','FireRain','RainImpact','FireRainImpact','Mark','NativeFire'])", "(name.startsWith('Rain')||name.startsWith('FireRain')||name in ['Mark','NativeFire'])")
catalog = catalog.replace("name == 'Rain' || name == 'FireRain'", "name.startsWith('Rain') || name.startsWith('FireRain')")
catalog = catalog.replace("19007:'Rain',19008:'FireRain'", "19007:'Rain'+row.skill_level,19008:'FireRain'+row.skill_level")
catalog = catalog.replace('cat.count+402', 'cat.count+406').replace('402 hidden visuals', '406 hidden visuals')
catalog = catalog.replace('extrasSpec.each{item->', '''extrasSpec.each{item->''')
catalog = catalog.replace('def mid=new File', '''for(int id:[19007,19008])for(int level:[2,3]){
  assert !cat.rows.any{it.skill_id==id&&it.skill_level==level}
  def original=cat.rows.find{it.skill_id==id&&it.skill_level==1}
  def row=new LinkedHashMap(original);row.skill_level=level
  if(spec[0]=='skillgrp'){
   instantFields.each{row[it]=nativeItem[it]}
   row.description='AmberEffectsV6.'+(id==19007?'Rain':'FireRain')+level
  }
  extra<<row
 }
 def mid=new File''')
(root / 'scripts/build_amber_vfx_v6_catalogs.groovy').write_text(catalog)

server_dir = stage / 'server/custom/AmberContract'
server_dir.mkdir(parents=True, exist_ok=True)
baselines = {}
for name in ['AmberContract.java', 'AmberServitor.java']:
    live = project / 'server/game/data/scripts/custom/AmberContract' / name
    baselines[str(live.relative_to(project)).replace('\\', '/')] = hashlib.sha256(live.read_bytes()).hexdigest()
    s = live.read_text()
    if name == 'AmberContract.java':
        s = s.replace('        a.broadcastPacket(new MagicSkillLaunched(a,19010,1,s.marker));\n', '')
        s = s.replace('        a.broadcastPacket(new MagicSkillLaunched(a,19006,1,a));\n', '')
        s = s.replace('        a.broadcastPacket(new MagicSkillUse(a,a,19006,1,3500,0));',
                      '        a.broadcastPacket(new MagicSkillUse(a,a,19012,1,0,0));\n        a.broadcastPacket(new MagicSkillUse(a,a,19006,1,3500,0));')
        s = s.replace('new MagicSkillUse(a,anchor,visual,1,0,0)', 'new MagicSkillUse(a,anchor,visual,pulse+1,0,0)')
        s = s.replace('                        a.broadcastPacket(new MagicSkillLaunched(a,visual,1,anchor));\n', '')
    else:
        s = s.replace('                    broadcastPacket(new MagicSkillLaunched(this,19009,level,target));\n', '')
    if 'new MagicSkillLaunched(' not in s:
        s = s.replace('import org.l2jmobius.gameserver.network.serverpackets.MagicSkillLaunched;\n', '')
    (server_dir / name).write_text(s)
(stage / 'server-baseline.json').write_text(json.dumps(baselines, indent=2))
numbers = stage / 'server/custom/WorldDamageNumbers'
numbers.mkdir(parents=True, exist_ok=True)
s = (root / 'templates/WorldDamageNumbers.java').read_text()
s = s.replace('60 flechas', '50 flechas').replace('19014','19600')
(numbers / 'WorldDamageNumbers.java').write_text(s)
print('V6 sources: Effekseer flame, 50 rising + 17/17/16 falling, native casting, current Amber AI preserved.')
