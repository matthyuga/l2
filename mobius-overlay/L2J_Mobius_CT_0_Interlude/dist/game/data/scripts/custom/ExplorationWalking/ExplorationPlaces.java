package custom.ExplorationWalking;
import java.nio.file.*;
import java.util.*;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.*;

/** Exploration-only geometry: never modifies combat, peace, teleport or spawn zones. */
public final class ExplorationPlaces {
    interface Shape {boolean contains(int x,int y,int z);}
    static int number(Element e,String key){return Integer.parseInt(e.getAttribute(key));}
    public static final class Place {
        public final String id,name;
        final List<Shape> shapes=new ArrayList<>();
        final List<int[]> anchors=new ArrayList<>();
        Place(String id,String name){this.id=id;this.name=name;}
        boolean contains(int x,int y,int z){for(Shape s:shapes)if(s.contains(x,y,z))return true;return false;}
        double distance(int x,int y,int z){double best=Double.MAX_VALUE;for(int[] a:anchors){double dx=x-a[0],dy=y-a[1],dz=(z-a[2])*2.0;best=Math.min(best,dx*dx+dy*dy+dz*dz);}return best;}
    }
    private final List<Place> places=new ArrayList<>();
    public ExplorationPlaces(Path file) throws Exception {
        var factory=DocumentBuilderFactory.newInstance();factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl",true);
        var list=factory.newDocumentBuilder().parse(file.toFile()).getDocumentElement().getElementsByTagName("place");
        Set<String> ids=new HashSet<>();
        for(int i=0;i<list.getLength();i++) {
            Element e=(Element)list.item(i);Place p=new Place(e.getAttribute("id"),e.getAttribute("name"));
            if(p.id.isEmpty()||p.name.isBlank()||!ids.add(p.id))throw new IllegalArgumentException("Invalid/duplicate place");
            for(Node n=e.getFirstChild();n!=null;n=n.getNextSibling())if(n instanceof Element s) {
                if(s.getTagName().equals("circle")) {
                    int x=number(s,"x"),y=number(s,"y"),z=number(s,"z"),r=number(s,"radius"),h=number(s,"height");
                    p.anchors.add(new int[]{x,y,z});p.shapes.add((px,py,pz)->Math.abs((long)pz-z)<=h&&Math.pow((double)px-x,2)+Math.pow((double)py-y,2)<=((double)r*r));
                } else if(s.getTagName().equals("polygon")) {
                    int low=number(s,"minZ"),high=number(s,"maxZ");var nodes=s.getElementsByTagName("node");int[] xs=new int[nodes.getLength()],ys=new int[nodes.getLength()];
                    if(xs.length<3)throw new IllegalArgumentException("Invalid polygon");
                    for(int j=0;j<xs.length;j++){xs[j]=number((Element)nodes.item(j),"x");ys[j]=number((Element)nodes.item(j),"y");}
                    p.shapes.add((x,y,z)->z>=low-200&&z<=high+200&&inside(xs,ys,x,y));
                }
            }
            places.add(p);
        }
    }
    static boolean inside(int[] xs,int[] ys,int x,int y){
        boolean in=false;for(int i=0,j=xs.length-1;i<xs.length;j=i++)if((ys[i]>y)!=(ys[j]>y)&&x<(double)(xs[j]-xs[i])*(y-ys[i])/(ys[j]-ys[i])+xs[i])in=!in;return in;
    }
    public int size(){return places.size();}
    public Place find(int x,int y,int z){Place best=null;double score=Double.MAX_VALUE;for(Place p:places)if(p.contains(x,y,z)){double d=p.distance(x,y,z);if(d<score){best=p;score=d;}}return best;}
    /** Require two observations and a cooldown to avoid border notification spam. */
    public static final class Tracker {
        private String candidate="",current="";private int ticks;private long lastNotice=-12000;
        public boolean enter(String key,long now){
            if(!key.equals(candidate)){candidate=key;ticks=1;return false;}
            if(++ticks<2||key.equals(current))return false;
            if(key.isEmpty()){current="";return false;}
            if(now-lastNotice<12000)return false;
            current=key;lastNotice=now;return true;
        }
    }
}
