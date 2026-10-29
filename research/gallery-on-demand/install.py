from pathlib import Path
from datetime import datetime
import shutil
root=Path(r'E:\l2-local')
backup=root/'backups'/('gallery-on-demand-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
roots=[root/'server/game',root/'source/L2J_Mobius_CT_0_Interlude/dist/game',root/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']
roster=(roots[0]/'data/scripts/custom/NormalNpcRoster/NormalNpcRoster.java').read_text(encoding='utf-8-sig')
roster=roster.replace('public class NormalNpcRoster extends Script','public class NormalNpcRoster extends Script implements org.l2jmobius.gameserver.handler.IVoicedCommandHandler')
roster=roster.replace('private NormalNpcRoster() { ThreadPool.schedule(this::prepareAndApply,45000); }','''private static volatile boolean preparing;
    private NormalNpcRoster() {
        org.l2jmobius.gameserver.handler.VoicedCommandHandler.getInstance().registerHandler(this);
        LOGGER.info("ROSTER_MANUAL_READY: combat profiles deferred; use .roster preparar when required.");
    }
    @Override public String[] getCommandList(){return new String[]{"roster"};}
    @Override public synchronized boolean onCommand(String command,Player player,String params){
        if(!player.isGM()){player.sendMessage("Roster: acceso de laboratorio GM.");return true;}
        if(params!=null && params.trim().equalsIgnoreCase("preparar") && !READY && !preparing){
            preparing=true;
            ThreadPool.execute(()->{try{prepareAndApply();}finally{preparing=false;}});
        }
        player.sendMessage(READY?"Roster listo para los combates.":preparing?"Preparando perfiles de combate; consulta .roster estado.":"Roster en reposo. Usa .roster preparar para habilitar los combates de prueba.");
        return true;
    }''')
assert 'ROSTER_MANUAL_READY' in roster
for base in roots:
    for rel in ['data/scripts/custom/EquipmentShowcase/EquipmentShowcase.java','data/scripts/custom/NormalNpcRoster/NormalNpcRoster.java','data/lab/world-spawns/EquipmentShowcase.xml']:
        path=base/rel
        dst=backup/path.relative_to(root);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dst)
        if rel.endswith('EquipmentShowcase.java'):
            shutil.copy2(root/'research/gallery-on-demand/EquipmentShowcase.java',path)
        elif rel.endswith('NormalNpcRoster.java'):path.write_text(roster,encoding='utf-8')
        else:path.write_text(path.read_text(encoding='utf-8-sig').replace('enabled="true"','enabled="false"',1),encoding='utf-8')
path=root/'Wait-L2LabReady.ps1';shutil.copy2(path,backup/path.name)
content=path.read_text(encoding='utf-8-sig')
content=content.replace('Roster Coliseo: 39 perfiles Player preparados','ROSTER_MANUAL_READY|Roster Coliseo: 39 perfiles Player preparados')
path.write_text(content,encoding='utf-8')
print(backup)
