package custom.NexusTvControl;

import java.net.URI;
import java.net.URLEncoder;
import java.net.http.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.network.serverpackets.NpcHtmlMessage;

/** Local GM remote for the separate Nexus TV service. No token crosses the game protocol. */
public final class NexusTvControl extends Script implements IVoicedCommandHandler {
    private static NexusTvControl instance;
    private static final HttpClient HTTP=HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build();
    private static final Path TOKEN=Path.of("E:/l2-local/nexus-tv/run/control-token-8796.txt");
    private final Map<Integer,Long> last=new ConcurrentHashMap<>();
    public NexusTvControl(){
        if(instance!=null)throw new IllegalStateException("TV remote already loaded");
        instance=this;VoicedCommandHandler.getInstance().registerHandler(this);
    }
    public String[] getCommandList(){return new String[]{"tv","televisor"};}
    private static boolean allowed(Player p){
        if(p==null||p.getClient()==null||!p.isGM())return false;
        String ip=p.getClient().getIp();
        return "127.0.0.1".equals(ip)||"::1".equals(ip)||"0:0:0:0:0:0:0:1".equals(ip);
    }
    public boolean onCommand(String command,Player p,String params){
        if(!allowed(p)){if(p!=null)p.sendMessage("Nexus TV: control reservado al GM local del laboratorio.");return false;}
        long now=System.nanoTime();Long before=last.put(p.getObjectId(),now);
        if(before!=null&&now-before<300_000_000L)return true;
        String text=params==null?"":params.trim();
        if(text.length()>600){p.sendMessage("Control demasiado largo.");return true;}
        String[] parts=text.isEmpty()?new String[]{"panel"}:text.split("\\s+",2);
        String op=parts[0],arg=parts.length==2?parts[1]:"";
        if(!java.util.Set.of("panel","play","pause","next","previous","camera","off","volume","quality","loop","seek","select","local","youtube").contains(op)){
            p.sendMessage("Usa .tv para abrir el control.");return true;
        }
        ThreadPool.execute(()->{
            try{
                String token=Files.readString(TOKEN,StandardCharsets.US_ASCII).trim();
                String body="op="+URLEncoder.encode(op,StandardCharsets.UTF_8)+"&arg="+URLEncoder.encode(arg,StandardCharsets.UTF_8);
                var req=HttpRequest.newBuilder(URI.create("http://127.0.0.1:8796/api/game"))
                    .timeout(Duration.ofSeconds(8)).header("X-Nexus-Token",token)
                    .header("Content-Type","application/x-www-form-urlencoded")
                    .POST(HttpRequest.BodyPublishers.ofString(body)).build();
                var response=HTTP.send(req,HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
                if(!allowed(p)||!p.isOnline())return;
                if(response.statusCode()!=200){p.sendMessage("Nexus TV: no se pudo completar. Abri el control web para ver el detalle.");return;}
                if(response.body().length()>8100)throw new IllegalStateException("Remote panel exceeds client limit");
                p.sendPacket(new NpcHtmlMessage(response.body()));
            }catch(Exception error){if(p.isOnline())p.sendMessage("Nexus TV no responde. Abri el acceso L2 - Control Nexus TV y luego usa .tv.");}
        });
        return true;
    }
    public static void main(String[] args){if(instance==null)new NexusTvControl();}
}
