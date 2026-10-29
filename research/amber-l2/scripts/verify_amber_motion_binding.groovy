import acmi.l2.clientmod.io.UnrealPackage
import java.nio.ByteBuffer
import java.nio.ByteOrder
def root=new File(args[0])
def required=['Wait_Hand','AtkWait_Hand','walk_hand','Run_Hand','atk01_Hand','SpAtk01_Hand','SpAtk02_Hand','Death_Hand','deathwait_Hand']
new UnrealPackage(new File(root,'exports/L2AmberArcherMotion.ukx'),true).withCloseable {up->
    def names=up.nameTable.collect{it.name.toLowerCase()}
    assert required.every{names.contains(it.toLowerCase())}
    println 'All nine distinct bow mappings resolve to existing animation names.'
}
for(def spec:[['L2AmberNPCv4','L2AmberNPCv5','L2AmberMotionv3.FFighter_anim'],['L2AmberArcher','L2AmberArcherV2','L2AmberArcherMotion.FFighter_anim']]) {
    new UnrealPackage(new File(root,'exports/'+spec[0]+'.ukx'),true).withCloseable {before->
        new UnrealPackage(new File(root,'exports/'+spec[1]+'.ukx'),true).withCloseable {after->
            assert before.exportTable.size()==after.exportTable.size()
            assert before.importTable.collect{it.objectFullName}==after.importTable.collect{it.objectFullName}
            assert after.importTable.any{it.objectFullName==spec[2]}
            for(int i=0;i<before.exportTable.size();i++) {
                def old=before.exportTable[i],fresh=after.exportTable[i]
                assert old.objectInnerFullName==fresh.objectInnerFullName
                byte[] a=old.objectRawData,b=fresh.objectRawData
                if(old.objectInnerFullName=='AmberNPC') {
                    assert a.length==b.length
                    assert (0..<a.length).every{it>=66&&it<90||a[it]==b[it]}
                    def bb=ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN)
                    assert bb.getFloat(74)==26.5f&&bb.getInt(82)==49152
                } else assert Arrays.equals(a,b)
            }
            println spec[1]+': geometry, materials, imports and every other export preserved; only mesh transform changed.'
        }
    }
}
