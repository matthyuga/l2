import ct0.XDAT
import acmi.l2.clientmod.util.IOUtil

InputStream.metaClass.readInt = { -> IOUtil.readInt(delegate as InputStream) }
InputStream.metaClass.readString = { -> IOUtil.readString(delegate as InputStream) }
InputStream.metaClass.readBoolean = { -> IOUtil.readBoolean(delegate as InputStream) }
InputStream.metaClass.readCompactInt = { -> IOUtil.readCompactInt(delegate as InputStream) }
InputStream.metaClass.readFloat = { -> IOUtil.readFloat(delegate as InputStream) }

if (args.length != 1) {
    throw new IllegalArgumentException('Uso: inspect-interface.groovy <Interface.xdat>')
}

def xdat = new XDAT()
use(IOUtil) {
    new File(args[0]).withInputStream { input -> xdat.read(input) }
}

def visit
visit = { node, String path ->
    String nodeName = node.name ?: '(sin nombre)'
    String nodePath = path ? path + '/' + nodeName : nodeName
    String searchable = nodePath.toLowerCase()
    if (searchable.contains('html') || searchable.contains('chat') || searchable.contains('npc') || searchable.contains('dialog')) {
        println String.format('%-70s %-14s size=%s %dx%d anchor=%s (%d,%d)', nodePath, node.class.simpleName,
            node.size, node.size_absolute_width, node.size_absolute_height, node.anchor, node.anchor_x, node.anchor_y)
    }
    if (node.metaClass.hasProperty(node, 'children')) {
        node.children.each { child -> visit(child, nodePath) }
    }
}

println 'windows=' + xdat.windows.size()
xdat.windows.each { window ->
    def htmlChildren = window.children.findAll { child -> child.class.simpleName == 'HtmlCtrl' }
    if (!htmlChildren.isEmpty() || (window.name ?: '').toLowerCase().contains('quest')) {
        println String.format('ROOT %-42s %dx%d children=%s', window.name, window.size_absolute_width,
            window.size_absolute_height, window.children.collect { it.name + ':' + it.class.simpleName }.join(', '))
    }
}
xdat.windows.findAll { it.name in ['TutorialViewerWnd', 'EventMatchGMCommandWnd'] }.each { window ->
    window.children.each { child ->
        println String.format('CHILD %-60s %-14s size=%s %dx%d anchor=%s (%d,%d)',
            window.name + '/' + child.name, child.class.simpleName, child.size,
            child.size_absolute_width, child.size_absolute_height, child.anchor, child.anchor_x, child.anchor_y)
    }
}
xdat.windows.each { window -> visit(window, '') }
println 'wndDefPos relevantes:'
xdat.wndDefPos.findAll { pos ->
    def n = (pos.wnd ?: '').toLowerCase()
    n.contains('html') || n.contains('chat') || n.contains('npc') || n.contains('dialog')
}.each { pos ->
    println String.format('%-45s %dx%d @ %d,%d align=%s', pos.wnd, pos.width, pos.height, pos.x, pos.y, pos.alignment)
}
