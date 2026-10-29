from pathlib import Path
root=Path(__file__).resolve().parents[2]
base=Path(__file__).parent
def edit(file,old,new):
 p=base/file;s=p.read_text(encoding='utf-8');assert old in s,(file,old);p.write_text(s.replace(old,new),encoding='utf-8')
edit('AmberContract/AmberScoutVerificationBridge.java','a.setExpPenalty(0);','')
edit('GiranSiegeLab/GiranRules.java','&&!d.isDead()','&&!d.isWall()&&!d.isDead()')
edit('AmberContract/AmberAssist.java','if(!eligible(target)||amber.calculateDistance3D(target)>900)continue;','if(target.isDoor()||!eligible(target)||amber.calculateDistance3D(target)>900)continue;')
edit('AmberContract/AmberAssist.java','if(target.calculateDistance3D(other)<=175)nearby++;','if(!other.isDoor()&&target.calculateDistance3D(other)<=175)nearby++;')
edit('AmberContract/AmberAssist.java','double distance=target.calculateDistance2D(other);','if(other.isDoor())continue;\n                double distance=target.calculateDistance2D(other);')
edit('AmberContract/AmberContract.java','if(!validVictim(p,a,victim)||Math.abs','if(victim.isDoor()||!validVictim(p,a,victim)||Math.abs')
edit('GiranSiegeLab/SiegeSquadBrain.java','a.nextHeadquarters=now+15000;if(GiranRules.castle().getSiege().getFlag(p.getClan()).isEmpty()', 'a.nextHeadquarters=now+15000;var flags=GiranRules.castle().getSiege().getFlag(p.getClan());if((flags==null||flags.isEmpty())')
edit('GiranSiegeLab/GiranGuardians.java','return System.currentTimeMillis()>=holdingUntil&&super.isAutoAttackable(attacker);','Player p=attacker.isSummon()?attacker.asSummon().getOwner():attacker.asPlayer();return p!=null&&GiranRules.castle().checkIfInZone(p.getX(),p.getY(),p.getZ())&&System.currentTimeMillis()>=holdingUntil&&super.isAutoAttackable(attacker);')
edit('GiranSiegeLab/GiranSiegeLab.java','castle ownership result preserved; no boss spawns remain','castle ownership result preserved; persistent owner guardians retained')
edit('GiranSiegeLab/GiranDefenseVerification.java','private final Map<Integer,Integer> rep=new HashMap<>();','private final Map<Integer,Integer> rep=new HashMap<>(),blood=new HashMap<>();')
edit('GiranSiegeLab/GiranDefenseVerification.java','rep.put(clan.getId(),clan.getReputationScore());','rep.put(clan.getId(),clan.getReputationScore());blood.put(clan.getId(),clan.getBloodAllianceCount());')
edit('GiranSiegeLab/GiranDefenseVerification.java','clan.addReputationScore(row.getValue()-clan.getReputationScore());','clan.addReputationScore(row.getValue()-clan.getReputationScore());var count=clan.getClass().getDeclaredField("_bloodAllianceCount");count.setAccessible(true);count.setInt(clan,blood.get(clan.getId()));clan.updateBloodAllianceCountInDB();')
startup=root/'Start-L2Local.ps1';s=startup.read_text(encoding='utf-8-sig');s=s.replace('[switch]$VerifyGiranAgenda,','[switch]$VerifyGiranAgenda, [switch]$VerifyGiranDefense,');s=s.replace("if($GameHeapMb -eq 0)","$GiranDefenseVerificationOption = '-Dlab.giran.v3.verify=' + $VerifyGiranDefense.IsPresent.ToString().ToLowerInvariant()\nif($GameHeapMb -eq 0)");s=s.replace("$GiranVerificationOption,'-XX:","$GiranVerificationOption,$GiranDefenseVerificationOption,'-XX:");(base/'Start-L2Local.ps1').write_text(s,encoding='utf-8-sig')
