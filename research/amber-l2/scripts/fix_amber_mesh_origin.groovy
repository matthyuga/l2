import acmi.l2.clientmod.io.UnrealPackage
import java.nio.ByteBuffer
import java.nio.ByteOrder

// Preserve all native arrays and absolute offsets: change only 24 transform bytes.
def root=new File(args[0])
for(def spec:[['L2AmberNPCv4','L2AmberNPCv5'],['L2AmberArcher','L2AmberArcherV2']]) {
    def output=new File(root,'exports/'+spec[1]+'.ukx')
    output.bytes=new File(root,'exports/'+spec[0]+'.ukx').bytes
    new UnrealPackage(output,false).withCloseable {up->
        def mesh=up.exportTable.find{it.objectInnerFullName=='AmberNPC'}
        byte[] bytes=mesh.objectRawData
        def bb=ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN)
        def matches=[]
        for(int i=0;i<bytes.length-36;i++)
            if(bb.getFloat(i)==1f&&bb.getFloat(i+4)==1f&&bb.getFloat(i+8)==1f)matches<<i
        assert matches==[54]: 'Unexpected native MeshScale layout: '+matches
        int origin=matches[0]+12
        assert (0..<6).every{bb.getInt(origin+it*4)==0}: 'Source transform already changed'
        bb.putFloat(origin,0f);bb.putFloat(origin+4,0f);bb.putFloat(origin+8,26.5f)
        bb.putInt(origin+12,0);bb.putInt(origin+16,49152);bb.putInt(origin+20,0)
        mesh.setObjectRawData(bytes)
        println spec[1]+': Fighter MeshOrigin.Z=26.5, RotOrigin.Yaw=49152; native payload '+bytes.length+' bytes preserved'
    }
}
