from pathlib import Path
import shutil
R=Path(r'E:\l2-local');roots=[R/'server/game',R/'source/L2J_Mobius_CT_0_Interlude/dist/game',R/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game'];backup=sorted((R/'backups').glob('gallery-on-demand-*'))[-1]
for base in roots:
 p=base/'data/scripts/custom/RealHumanPilots/RealHumanPilots.java';q=backup/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 s=p.read_text(encoding='utf-8-sig').replace('private RealHumanPilots()','private static RealHumanPilots instance;\n    private static volatile boolean prepared;\n    private RealHumanPilots()').replace('ThreadPool.schedule(this::prepare, 15000);','instance=this;\n        LOGGER.info("REAL_HUMAN_PILOTS: deferred until .roster preparar");')
 s=s.replace('private void prepare()','public static synchronized void prepareOnDemand(){\n        if(instance==null)throw new IllegalStateException("RealHumanPilots not initialized");\n        if(!prepared)instance.prepare();\n        if(!prepared)throw new IllegalStateException("RealHumanPilots preparation failed");\n    }\n\n    private void prepare()')
 s=s.replace('        }\n        catch (Exception e)','            prepared=true;\n        }\n        catch (Exception e)',1)
 assert 'prepared=true' in s;p.write_text(s,encoding='utf-8')
 p=base/'data/scripts/custom/NormalNpcRoster/NormalNpcRoster.java';s=p.read_text(encoding='utf-8');s=s.replace('try{prepareAndApply();}','try{RealHumanPilots.prepareOnDemand();prepareAndApply();}');p.write_text(s,encoding='utf-8')
print('Deferred seven supporting real-player pilots; manual roster preparation invokes them first.')
