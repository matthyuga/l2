import groovy.xml.XmlSlurper
import java.nio.ByteBuffer
import java.nio.ByteOrder

/** Lossless Interlude DAT record reader/writer. Unchanged records stay byte-identical. */
class AmberCatalog {
    byte[] data
    ByteBuffer input
    def schema
    int count, end
    List<Map> rows = []
    AmberCatalog(File raw, File schemas, String schemaFile, String pattern) {
        data = raw.bytes; input = ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN)
        schema = new XmlSlurper().parse(new File(schemas, schemaFile)).file.find { it.@pattern.text() == pattern }.'for'[0]
        assert schema.size() > 0
        count = input.getInt()
        count.times { int start = input.position(); def row = parse(schema, [:]); row._start = start; row._end = input.position(); rows << row }
        end = input.position()
    }
    int compactRead() {
        int v = input.get() & 255; boolean neg = (v & 128) != 0; boolean more = (v & 64) != 0
        int result = v & 63, shift = 6
        while (more) { v = input.get() & 255; result |= (v & 127) << shift; more = (v & 128) != 0; shift += 7 }
        neg ? -result : result
    }
    static byte[] compact(int v) {
        boolean neg = v < 0; v = Math.abs(v)
        def bytes = [(byte)((v & 63) | (neg ? 128 : 0) | (v > 63 ? 64 : 0))]; v >>>= 6
        while (v) { bytes << (byte)((v & 127) | (v > 127 ? 128 : 0)); v >>>= 7 }
        bytes as byte[]
    }
    def read(String kind) {
        switch (kind) {
            case 'UINT': case 'RGBA': return Integer.toUnsignedLong(input.getInt())
            case 'INT': return input.getInt()
            case 'FLOAT': return input.getFloat()
            case 'CNTR': return compactRead()
            case 'UNICODE':
                byte[] bytes = new byte[input.getInt()]; input.get(bytes); return new String(bytes, 'UTF-16LE')
            case 'ASCF':
                int length = compactRead(); byte[] bytes = new byte[Math.abs(length) * (length < 0 ? 2 : 1)]; input.get(bytes)
                return new String(bytes, length < 0 ? 'UTF-16LE' : 'windows-1252').replaceAll('\u0000+$', '')
            default: throw new IllegalArgumentException(kind)
        }
    }
    Map parse(nodes, Map variables) {
        def result = [:]
        nodes.children().each { node ->
            String name = node.@name.text()
            if (node.name() == 'node') { result[name] = read(node.@reader.text()); variables[name] = result[name] }
            else result[name + '_items'] = (0..<(variables[node.@size.text().replace('#','')].intValue())).collect { parse(node, new LinkedHashMap(variables)) }
        }
        result
    }
    byte[] encode(Map row, nodes = schema) {
        def output = new ByteArrayOutputStream()
        nodes.children().each { node ->
            String name = node.@name.text()
            if (node.name() != 'node') { row[name + '_items'].each { output.write(encode(it, node)) }; return }
            def value = row[name]
            switch (node.@reader.text()) {
                case 'UINT': case 'RGBA': case 'INT': output.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(((Number)value).intValue()).array()); break
                case 'FLOAT': output.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putFloat(((Number)value).floatValue()).array()); break
                case 'CNTR': output.write(compact(((Number)value).intValue())); break
                case 'UNICODE':
                    byte[] bytes = value.getBytes('UTF-16LE'); output.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(bytes.length).array()); output.write(bytes); break
                case 'ASCF':
                    if (value) { output.write(compact(-(value.length() + 1))); output.write(value.getBytes('UTF-16LE')); output.write(new byte[2]) }
                    else output.write(compact(0)); break
                default: throw new IllegalArgumentException(node.@reader.text())
            }
        }
        output.toByteArray()
    }
    byte[] patch(Closure modify) {
        def output = new ByteArrayOutputStream(); output.write(data, 0, 4)
        rows.each { row ->
            def changed = modify(new LinkedHashMap(row))
            if (changed == null) output.write(data, row._start as int, (row._end - row._start) as int)
            else output.write(encode(changed))
        }
        output.write(data, end, data.length - end)
        output.toByteArray()
    }
}
