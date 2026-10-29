import java.nio.ByteBuffer
import java.nio.ByteOrder
import acmi.l2.clientmod.io.UnrealPackage

def root = new File(args[0])
def client = new File(root.parentFile.parentFile.parentFile, 'l2')
new UnrealPackage(new File(client, 'system-hud/AmberParticles.u'), true).withCloseable { up ->
    def entry = up.exportTable.find { it.objectInnerFullName == 'FireShot.Arrows' }
    def compact = { ByteBuffer b ->
        int v = b.get() & 255; boolean neg = (v & 128) != 0; boolean more = (v & 64) != 0
        int result = v & 63; int shift = 6
        while (more) { v = b.get() & 255; result |= (v & 127) << shift; more = (v & 128) != 0; shift += 7 }
        neg ? -result : result
    }
    Closure read
    read = { ByteBuffer b ->
        def result = [:]
        while (b.hasRemaining()) {
            String name = up.nameReference(compact(b)); if (name == 'None') break
            int info = b.get() & 255; int type = info & 15; int sizeType = (info >> 4) & 7
            if (type == 10) compact(b)
            int size = sizeType < 5 ? [1,2,4,12,16][sizeType] : sizeType == 5 ? b.get() & 255 : sizeType == 6 ? b.getShort() & 65535 : b.getInt()
            if ((info & 128) != 0 && type != 3) compact(b)
            if (type == 3) { result[name] = (info & 128) != 0; continue }
            byte[] payload = new byte[size]; b.get(payload)
            def nested = ByteBuffer.wrap(payload).order(ByteOrder.LITTLE_ENDIAN)
            result[name] = type == 10 ? read(nested) : type == 4 ? nested.getFloat() : type == 1 ? nested.get() & 255 : payload
        }
        result
    }
    def props = read(ByteBuffer.wrap(entry.objectRawData).order(ByteOrder.LITTLE_ENDIAN))
    assert props.CoordinateSystem == 1
    assert props.StartVelocityRange.X.Min == 1400f && props.StartVelocityRange.X.Max == 1400f
    assert props.StartVelocityRange.Z.Min == 0f && props.StartVelocityRange.Z.Max == 0f
    assert props.LifetimeRange.Min == 0.5f
    println 'FireShot: compiled local X velocity 1400, vertical velocity 0, lifetime 0.5s.'
}
def chunks = { File file ->
    def buffer = ByteBuffer.wrap(file.bytes).order(ByteOrder.LITTLE_ENDIAN)
    def result = [:]
    while (buffer.remaining() >= 32) {
        byte[] tag = new byte[20]; buffer.get(tag)
        String name = new String(tag, 'US-ASCII').replaceAll('\u0000.*', '')
        buffer.getInt(); int size = buffer.getInt(); int count = buffer.getInt()
        byte[] data = new byte[size * count]; buffer.get(data)
        result[name] = data
    }
    result
}
for (String name : ['ArrowFire', 'ArrowWhite', 'ArrowSky']) {
    def before = chunks(new File(root, 'exports/particles-verified/AmberParticles/StaticMesh/' + name + '.pskx'))
    def after = chunks(new File(root, 'exports/particles-w11-verified/AmberParticles/StaticMesh/' + name + '.pskx'))
    if (!Arrays.equals(before.PNTS0000, after.PNTS0000)) throw new AssertionError(name + ': vertices')
    // UCC's stripifier can reorder wedges/triangles. LWO without a UV map also
    // has non-deterministic UV padding (irrelevant for these flat color textures).
    // Compare triangles by vertex connectivity rather than export byte order.
    def triangles = { map ->
        def wedges = ByteBuffer.wrap(map.VTXW0000).order(ByteOrder.LITTLE_ENDIAN)
        def faces = ByteBuffer.wrap(map.FACE0000).order(ByteOrder.LITTLE_ENDIAN)
        def result = []
        for (int offset = 0; offset < faces.limit(); offset += 12) {
            def indices = (0..<3).collect { wedges.getShort((faces.getShort(offset + it * 2) & 65535) * 16) & 65535 }
            result << indices.sort().join(',')
        }
        result.sort()
    }
    if (triangles(before) != triangles(after)) throw new AssertionError(name + ': connectivity')
    println name + ': vertex positions and triangle connectivity preserved.'
}
def shot = chunks(new File(root, 'exports/particles-w11-verified/AmberParticles/StaticMesh/ArrowShot.pskx'))
def points = ByteBuffer.wrap(shot.PNTS0000).order(ByteOrder.LITTLE_ENDIAN)
float tipX = -Float.MAX_VALUE
while (points.remaining() >= 12) { float x = points.getFloat(); points.getFloat(); points.getFloat(); tipX = Math.max(tipX, x) }
assert tipX == 32f
println 'ArrowShot: arrow tip points along local +X, matching the fire tracer velocity.'
