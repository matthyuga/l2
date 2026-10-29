import ct0.Alignment
import ct0.XDAT

if (args.length != 2) {
    System.err.println('Usage: patch-native-hud.groovy <input Interface.xdat> <output Interface.xdat>')
    System.exit(2)
}

def xdat = new XDAT()
new File(args[0]).withInputStream { input ->
    xdat.read(new BufferedInputStream(input))
}

def hud = xdat.windows.find { it.name == 'OlympiadTargetWnd' }
if (hud == null) {
    throw new IllegalStateException('OlympiadTargetWnd was not found')
}

// Place the native CP/HP target panel just below Interlude's normal target header.
// This keeps both the target name/selection controls and the exact combat vitals visible.
hud.anchor = true
hud.anchor_parent = Alignment.TOP_CENTER
hud.anchor_this = Alignment.TOP_CENTER
hud.anchor_ctrl = ''
hud.anchor_x = 0
hud.anchor_y = 48

new File(args[1]).withOutputStream { output ->
    def buffered = new BufferedOutputStream(output)
    xdat.write(buffered)
    buffered.flush()
}

println("Patched ${hud.name}: ${hud.anchor_parent}/${hud.anchor_this} @ ${hud.anchor_x},${hud.anchor_y}")
