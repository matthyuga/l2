import ct0.XDAT
import ct0.Window

if (args.length < 1 || args.length > 2) {
	System.err.println('Usage: inspect-xdat.groovy <Interface.xdat> [window regex]')
    System.exit(2)
}

def xdat = new XDAT()
new File(args[0]).withInputStream { input ->
    xdat.read(new BufferedInputStream(input))
}
def windowPattern = args.length == 2 ? ~/(?i)${args[1]}/ : ~/(?i)target|olympiad/

def dump
dump = { node, int depth ->
    def indent = '  ' * depth
    def fields = [
        "type=${node.class.simpleName}",
        "name=${node.name}",
        "super=${node.superName}",
        "size=${node.size ? "${node.size_absolute_width}x${node.size_absolute_height}" : '-'}",
        "anchor=${node.anchor ? "${node.anchor_parent}/${node.anchor_this}:${node.anchor_ctrl}@${node.anchor_x},${node.anchor_y}" : '-'}"
    ]
    ['foreTexture', 'backTexture', 'file', 'text', 'backTex', 'uSize', 'vSize', 'alpha'].each { prop ->
        if (node.hasProperty(prop)) {
            fields << "${prop}=${node."${prop}"}"
        }
    }
    println(indent + fields.join(' | '))
    if (node instanceof Window) {
        node.children.each { child -> dump(child, depth + 1) }
    }
}

println("windows=${xdat.windows.size()} shortcuts=${xdat.shortcuts.size()}")
xdat.windows.findAll { window ->
	windowPattern.matcher(window.name ?: '').find()
}.each { window ->
    println('\nWINDOW')
    dump(window, 0)
}
