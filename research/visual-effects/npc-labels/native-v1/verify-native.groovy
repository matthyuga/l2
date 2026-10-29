import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory

def project=new File(args[0]),stage=new File(project,'research/visual-effects/npc-labels/native-v1')
def factory=new UnrealSerializerFactory(new Environment(project,[
    'research/visual-effects/npc-labels/native-v1/*.u',
    '../l2/system-hud/*.u','../l2/system/*.u']))
def proof=[:]
new UnrealPackage(new File(stage,'HellgamesLabelsV1.u'),true).withCloseable{up->
    assert up.exportTable.find{it.objectInnerFullName=='EventGold'&&it.fullClassName=='Core.Class'}
    def emitters=up.exportTable.findAll{it.fullClassName=='Engine.SpriteEmitter'}
    assert emitters.size()==2
    emitters.each{e->
        def obj=factory.getOrCreateObject(e)
        def props=obj.@properties.collectEntries{p->[(p.name):p.getAt(0)]}
        assert props.ForcedMaxParticles==true
        assert props.CoordinateSystem==1
        assert props.Texture!=null
        assert props.MaxParticles in [1,16]
        proof[e.objectInnerFullName]=props.collectEntries{k,v->[(k):v.toString()]}
    }
    assert up.exportTable.findAll{it.fullClassName=='Engine.Texture'}.size()==2
    proof.exports=up.exportTable.size()
    proof.packageVersion=up.version
}
new File(stage,'native-properties.txt').text=proof.collect{k,v->k+' = '+v.toString()}.join('\n')+'\n'
println 'PASS: native class, two textures, two relative SpriteEmitters, forced counts verified.'
