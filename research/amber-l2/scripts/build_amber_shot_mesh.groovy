import java.nio.ByteBuffer
import java.nio.ByteOrder

// Derive the horizontal fire arrow from the existing approved particle mesh.
// LWO stores vertical Y; UCC maps it to game Z. Point the tip along local +X.
def root = new File(args[0])
byte[] mesh = new File(root, 'exports/contract/AmberFire.lwo').bytes
def buffer = ByteBuffer.wrap(mesh).order(ByteOrder.BIG_ENDIAN)
buffer.position(12)
boolean patched = false
while (buffer.remaining() >= 8) {
    byte[] id = new byte[4]; buffer.get(id); int size = buffer.getInt()
    int start = buffer.position()
    if (new String(id, 'US-ASCII') == 'PNTS') {
        for (int offset = start; offset < start + size; offset += 12) {
            float x = buffer.getFloat(offset), z = buffer.getFloat(offset + 4), y = buffer.getFloat(offset + 8)
            buffer.putFloat(offset, -z); buffer.putFloat(offset + 4, x); buffer.putFloat(offset + 8, y)
        }
        patched = true
    }
    buffer.position(start + size + (size & 1))
}
assert patched
new File(root, 'exports/contract/AmberShot.lwo').bytes = mesh
println 'AmberShot: original fire material and geometry, tip rotated to local +X.'
