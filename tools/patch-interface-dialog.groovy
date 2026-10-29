import ct0.XDAT
import acmi.l2.clientmod.util.IOUtil

if (args.length != 4) {
    throw new IllegalArgumentException('Uso: patch-interface-dialog.groovy <entrada> <salida> <ancho> <alto>')
}

InputStream.metaClass.readInt = { -> IOUtil.readInt(delegate as InputStream) }
InputStream.metaClass.readString = { -> IOUtil.readString(delegate as InputStream) }
InputStream.metaClass.readBoolean = { -> IOUtil.readBoolean(delegate as InputStream) }
InputStream.metaClass.readCompactInt = { -> IOUtil.readCompactInt(delegate as InputStream) }
InputStream.metaClass.readFloat = { -> IOUtil.readFloat(delegate as InputStream) }
OutputStream.metaClass.writeInt = { int value -> IOUtil.writeInt(delegate as OutputStream, value) }
OutputStream.metaClass.writeString = { String value -> IOUtil.writeString(delegate as OutputStream, value) }
OutputStream.metaClass.writeBoolean = { Boolean value -> IOUtil.writeBoolean(delegate as OutputStream, value) }
OutputStream.metaClass.writeCompactInt = { int value -> IOUtil.writeCompactInt(delegate as OutputStream, value) }
OutputStream.metaClass.writeFloat = { float value -> IOUtil.writeFloat(delegate as OutputStream, value) }

File inputFile = new File(args[0])
File outputFile = new File(args[1])
int width = Integer.parseInt(args[2])
int height = Integer.parseInt(args[3])

def xdat = new XDAT()
new FileInputStream(inputFile).withCloseable { input -> xdat.read(input) }

def dialogNames = ['TutorialViewerWnd', 'EventMatchGMCommandWnd']
dialogNames.each { dialogName ->
    def dialog = xdat.windows.find { window -> window.name == dialogName }
    if (dialog == null) {
        throw new IllegalStateException("No se encontro ${dialogName}")
    }
    println "Antes: ${dialog.name} ${dialog.size_absolute_width}x${dialog.size_absolute_height}"
    dialog.size = true
    dialog.size_absolute_values = true
    dialog.size_absolute_width = width
    dialog.size_absolute_height = height
    println "Despues: ${dialog.name} ${dialog.size_absolute_width}x${dialog.size_absolute_height}"
}

def tutorial = xdat.windows.find { window -> window.name == 'TutorialViewerWnd' }
tutorial.children.each { child ->
    if (child.name in ['texTutorialViewerBack1', 'texTutorialViewerBack2', 'texTutorialViewerBack3']) {
        child.size = true
        child.size_absolute_values = true
        child.size_absolute_width = width
    }
    if (child.name == 'HtmlTutorialViewer') {
        child.size = true
        child.size_absolute_values = true
        child.size_absolute_width = width - 15
        child.size_absolute_height = height - 41
    }
}

new FileOutputStream(outputFile).withCloseable { output -> xdat.write(output) }
println "Escrito: ${outputFile.absolutePath} (${outputFile.length()} bytes)"
