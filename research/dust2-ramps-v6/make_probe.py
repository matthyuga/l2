from pathlib import Path
import json
D=Path(__file__).resolve().parent;ramps=json.loads((D/'ramps.json').read_text())
rows=[[f['axis'],f['sign'],f['a'],f['b'],f['start'],f['end'],f['low'],f['high']] for f in ramps]
code='''import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
public class AllRampsProbe {
 public static void agentmain(String dir,Instrumentation i)throws Exception {
  var g=GeoEngine.getInstance();if(!g.reloadRegion(24,19))throw new AssertionError("Geo reload failed");
  double[][] ramps=@RAMPS@;StringBuilder out=new StringBuilder();int checks=0,fail=0;
  for(int n=0;n<ramps.length;n++){
   double[] f=ramps[n];int axis=(int)f[0],sign=(int)f[1],run=(int)Math.abs(f[5]-f[4]);
   for(int along:new int[]{(int)f[2]+8,(int)((f[2]+f[3])/2),(int)f[3]-8}){
    for(int step=-8;step<run+8;step+=8){
     int u=(int)f[4]+sign*step,nu=u+sign*8;
     int x=axis==0?u:along,y=axis==0?along:u,tx=axis==0?nu:along,ty=axis==0?along:nu;
     int ref=(int)(f[6]+(u-f[4])/(f[5]-f[4])*(f[7]-f[6])+43.35);
     int tref=(int)(f[6]+(nu-f[4])/(f[5]-f[4])*(f[7]-f[6])+43.35);
     int z=g.getHeight(x,y,ref),tz=g.getHeight(tx,ty,tref);
     boolean up=g.canMoveToTarget(x,y,z,tx,ty,tz,0),down=g.canMoveToTarget(tx,ty,tz,x,y,z,0);checks+=2;
     if(!up||!down){fail++;out.append("FAIL ramp="+n+" "+x+","+y+","+z+" -> "+tx+","+ty+","+tz+" up="+up+" down="+down+"\\n");}
    }
   }
  }
  out.append("ramps="+ramps.length+" bidirectional_checks="+checks+" failed_segments="+fail+"\\n");Files.writeString(Path.of(dir,"server-probe.txt"),out);
  if(fail>0)throw new AssertionError("Ramp path failures: "+fail);
 }
}'''
code=code.replace('@RAMPS@','{'+','.join('{'+','.join(map(str,row))+'}' for row in rows)+'}')
(D/'AllRampsProbe.java').write_text(code)
