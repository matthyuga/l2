"""Stage minimal server integration against the current live sources."""
from pathlib import Path
import json,hashlib,copy,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parents[1];OUT=ROOT/'exports/mmd-variants-20261023';DEST=OUT/'server/custom/AmberContract';DEST.mkdir(parents=True,exist_ok=True)
baseline={}
def source(name):
 p=PROJECT/'server/game/data/scripts/custom/AmberContract'/name;baseline[str(p.relative_to(PROJECT)).replace('\\','/')]=hashlib.sha256(p.read_bytes()).hexdigest();return p.read_text(encoding='utf-8-sig')
contract=source('AmberContract.java');needle='new AmberServitor(NpcData.getInstance().getTemplate(SUMMON),p)';assert contract.count(needle)==1
contract=contract.replace(needle,'new AmberServitor(NpcData.getInstance().getTemplate(AmberModelVariants.templateId(p)),p)')
needle='html+="Beast Soulshots: "';assert contract.count(needle)==1
contract=contract.replace(needle,'html+=button("Comparar modelos de Amber","voice .ambers")+"Beast Soulshots: "')
(DEST/'AmberContract.java').write_text(contract,encoding='utf-8')
servitor=source('AmberServitor.java');needle='    @Override public int getWeapon(){return 6619;}';assert needle in servitor
extra='''    /** Cosmetic variant switch: preserve actor, HP/MP, effects, shots and reuse state. */
    void applyVisualTemplate(NpcTemplate model)
    {
        if(!AmberModelVariants.isTemplate(model.getId()))throw new IllegalArgumentException("Unknown Amber model");
        setTemplate(model);
        broadcastPacket(new org.l2jmobius.gameserver.network.serverpackets.DeleteObject(this));
        org.l2jmobius.gameserver.entity.World.forEachVisibleObject(this,Player.class,observer->{if(observer!=getOwner())sendInfo(observer);});
        sendInfo(getOwner());
    }
'''
servitor=servitor.replace(needle,extra+needle);(DEST/'AmberServitor.java').write_text(servitor,encoding='utf-8')
old=PROJECT/'server/game/data/scripts/custom/AmberContract/AmberModelVariants.java';baseline[str(old.relative_to(PROJECT)).replace('\\','/')]=hashlib.sha256(old.read_bytes()).hexdigest() if old.exists() else None
(DEST/'AmberModelVariants.java').write_text('''package custom.AmberContract;

import java.util.Locale;
import org.l2jmobius.gameserver.data.xml.NpcData;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.network.serverpackets.NpcHtmlMessage;

/** GM visual comparisons; combat remains the existing AmberServitor implementation. */
public class AmberModelVariants extends Script implements IVoicedCommandHandler
{
    static final String VARIABLE="AMBER_MODEL_VARIANT";
    static final int[] TEMPLATES={AmberContract.SUMMON,902520,902521};
    static final String[] LABELS={"Actual - Koikatsu","MMD 1.0 - detallada","MMD 1.4 - Amber 2.0"};
    public AmberModelVariants(){VoicedCommandHandler.getInstance().registerHandler(this);AmberContract.LOG.info("AmberModelVariants: .ambers selector enabled, three models, existing combat state preserved.");}
    static int selection(Player p){int v=p.getVariables().getInt(VARIABLE,1);return v>=1&&v<=3?v:1;}
    static int templateId(Player p){return TEMPLATES[selection(p)-1];}
    static boolean isTemplate(int id){return id==TEMPLATES[0]||id==TEMPLATES[1]||id==TEMPLATES[2];}
    @Override public String[] getCommandList(){return new String[]{"ambers"};}
    @Override public boolean onCommand(String command,Player p,String params)
    {
        if(!p.isGM()){p.sendMessage("Amber: comparador de modelos solo GM.");return true;}
        String value=params==null?"":params.trim().toLowerCase(Locale.ROOT);
        int wanted=switch(value){case "1","actual"->1;case "2","mmd10"->2;case "3","mmd14"->3;default->0;};
        if(!value.isEmpty()&&wanted==0){p.sendMessage("Usa .ambers 1, .ambers 2 o .ambers 3.");menu(p);return true;}
        if(wanted!=0)synchronized(AmberContract.session(p)){
            if(p.isDead()||p.isMounted()||p.isInDuel()||p.isInOlympiadMode()||p.isInCombat()||p.isAttackingNow()||p.isCastingNow()){
                p.sendMessage("Cambia el modelo fuera de combate y sin acciones en curso.");menu(p);return true;
            }
            if(p.hasSummon()&&!(p.getSummon() instanceof AmberServitor)){p.sendMessage("Retira tu otro summon primero.");menu(p);return true;}
            AmberServitor a=p.getSummon() instanceof AmberServitor amber?amber:null;
            if(a!=null&&(a.isDead()||a.charging||a.isInCombat()||a.isAttackingNow()||a.isCastingNow())){
                p.sendMessage("Espera a que Amber termine el combate o la habilidad.");menu(p);return true;
            }
            var model=NpcData.getInstance().getTemplate(TEMPLATES[wanted-1]);
            if(model==null){p.sendMessage("El modelo todavia no esta cargado en el servidor.");return true;}
            if(a!=null)a.applyVisualTemplate(model);
            p.getVariables().set(VARIABLE,wanted);
            if(a==null&&AmberContract.contracted(p))AmberContract.order(p,AmberContract.INVOKE);
            p.sendMessage("Amber: "+LABELS[wanted-1]+" seleccionada.");
        }
        menu(p);return true;
    }
    static String html(Player p){
        String h="<html><body><center><font color=LEVEL>Tres modelos de Amber</font><br>Seleccionado: "+LABELS[selection(p)-1]+"<br><br>";
        for(int i=0;i<3;i++)h+="<button value=\\\""+(i+1)+". "+LABELS[i]+"\\\" action=\\\"bypass -h voice .ambers "+(i+1)+"\\\" width=280 height=28 back=\\\"L2UI_ch3.smallbutton2_over\\\" fore=\\\"L2UI_ch3.smallbutton2\\\"><br>";
        return h+"La seleccion cambia su apariencia.<br>Conserva habilidades, recursos y recargas.<br>Fuera de combate puedes alternar al instante.<br>Si no tienes contrato, firma primero con Amber.<br><br><button value=\\\"Menu de Amber\\\" action=\\\"bypass -h voice .amber\\\" width=240 height=24 back=\\\"L2UI_ch3.smallbutton2_over\\\" fore=\\\"L2UI_ch3.smallbutton2\\\"></center></body></html>";
    }
    private static void menu(Player p){NpcHtmlMessage packet=new NpcHtmlMessage(0);packet.setHtml(html(p));p.sendPacket(packet);}
    public static void main(String[] args){new AmberModelVariants();}
}
''',encoding='utf-8')
xmlpath=PROJECT/'server/game/data/stats/npcs/custom/amber_summon.xml';baseline[str(xmlpath.relative_to(PROJECT)).replace('\\','/')]=hashlib.sha256(xmlpath.read_bytes()).hexdigest()
tree=ET.parse(xmlpath);prototype=next(n for n in tree.getroot() if n.get('id')=='902501')
new=ET.Element('list',{'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':'../../../xsd/npcs.xsd'})
existing=set()
for path in (PROJECT/'server/game/data/stats/npcs').rglob('*.xml'):
 try:existing.update(n.get('id') for n in ET.parse(path).getroot().iter('npc'))
 except ET.ParseError:pass
for npc,display in [(902520,59020),(902521,59021)]:
 assert str(npc) not in existing,'NPC id collision'
 clone=copy.deepcopy(prototype);clone.set('id',str(npc));clone.set('displayId',str(display));new.append(clone)
ET.indent(new);(OUT/'server/amber_model_variants.xml').write_bytes(b'<?xml version="1.0" encoding="UTF-8"?>\n'+ET.tostring(new,encoding='utf-8'))
(OUT/'server-baseline.json').write_text(json.dumps(baseline,indent=2))
print('Server staged: two identical-stat templates, .ambers1/2/3, cosmetic in-place switching.')
