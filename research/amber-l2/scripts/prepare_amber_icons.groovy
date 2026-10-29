import javax.imageio.ImageIO
import java.awt.image.BufferedImage
import java.awt.RenderingHints
import java.awt.Color

def root = new File(args[0]); def stage = new File(root, 'exports/contract/visual-v3')
def assets = new File(stage, 'icons'); assets.mkdirs()
def properties = new Properties(); new File(stage, 'icon-sources.properties').withReader { properties.load(it) }
def sources = [icons:['Contract','Fire','Rain','Break'].collect { [name:it, source:properties.getProperty(it)] }]
sources.icons.each { spec ->
    def source = new File(spec.source)
    def original = new File(assets, spec.name + '-source.png'); original.bytes = source.bytes
    def image = ImageIO.read(source); assert image != null
    def icon = new BufferedImage(32, 32, BufferedImage.TYPE_INT_RGB)
    def graphics = icon.createGraphics()
    graphics.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_BICUBIC)
    graphics.drawImage(image, 0, 0, 32, 32, null); graphics.dispose()
    ImageIO.write(icon, 'png', new File(assets, spec.name + '.png'))
    def tga = new ByteArrayOutputStream()
    // This UE2 UCC ignores top-origin TGA descriptors: feed standard bottom-origin rows.
    byte[] header = new byte[18]; header[2] = 2; header[12] = 32; header[14] = 32; header[16] = 24
    tga.write(header)
    for (int y = 31; y >= 0; y--) for (int x = 0; x < 32; x++) {
        int rgb = icon.getRGB(x, y); tga.write(rgb & 255); tga.write((rgb >>> 8) & 255); tga.write((rgb >>> 16) & 255)
    }
    new File(assets, spec.name + '.tga').bytes = tga.toByteArray()
    println spec.name + ': original saved; 32x32 PNG and RGB TGA prepared.'
}
def preview = new BufferedImage(512, 160, BufferedImage.TYPE_INT_RGB)
def view = preview.createGraphics(); view.setColor(new Color(18,22,29)); view.fillRect(0,0,512,160)
sources.icons.eachWithIndex { spec, index ->
    def icon = ImageIO.read(new File(assets, spec.name + '.png'))
    view.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_NEAREST_NEIGHBOR)
    view.drawImage(icon, index * 128 + 16, 8, 96, 96, null)
    view.drawImage(icon, index * 128 + 48, 114, 32, 32, null)
}
view.dispose(); ImageIO.write(preview, 'png', new File(stage, 'icons-preview.png'))
def editor = new File(root, 'tools/l2editor/L2Editor')
def packageDir = new File(editor.parentFile, 'AmberIconsV1/Classes'); packageDir.mkdirs()
String imports = sources.icons.collect { '#exec TEXTURE IMPORT NAME=' + it.name + ' FILE="' + new File(assets, it.name + '.tga').absolutePath.replace('\\','/') + '" MIPS=OFF' }.join('\n')
new File(packageDir, 'IconAssets.uc').text = 'class IconAssets extends Object;\n' + imports + '\n'
new File(editor, 'AmberIconsV1.ini').text = new File(editor, 'UT2003.ini').getText('ISO-8859-1') + '\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=AmberIconsV1\n'
