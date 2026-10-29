import javax.imageio.ImageIO
import java.awt.*
import java.awt.image.BufferedImage
def stage=new File(args[0]),editor=new File(args[1]);stage.mkdirs()
def large=new BufferedImage(128,128,BufferedImage.TYPE_INT_RGB),g=large.createGraphics()
g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON)
g.paint=new GradientPaint(0,0,new Color(99,22,30),128,128,new Color(17,21,37));g.fillRect(0,0,128,128)
g.color=new Color(238,183,79);g.stroke=new BasicStroke(5);g.drawRoundRect(5,5,117,117,12,12)
g.color=new Color(121,224,223);g.stroke=new BasicStroke(5);g.drawArc(19,15,86,102,-65,130);g.drawLine(80,22,80,109)
g.color=new Color(14,16,25);g.font=new Font('Arial',Font.BOLD,67);g.drawString('IA',24,89)
g.color=new Color(255,232,151);g.drawString('IA',22,86)
g.dispose();def icon=new BufferedImage(32,32,BufferedImage.TYPE_INT_RGB),d=icon.createGraphics()
d.setRenderingHint(RenderingHints.KEY_INTERPOLATION,RenderingHints.VALUE_INTERPOLATION_BICUBIC);d.drawImage(large,0,0,32,32,null);d.dispose()
ImageIO.write(icon,'png',new File(stage,'Assist.png'));ImageIO.write(large,'png',new File(stage,'Assist-preview.png'))
def tga=new ByteArrayOutputStream();byte[] header=new byte[18];header[2]=2;header[12]=32;header[14]=32;header[16]=24;tga.write(header)
for(int y=31;y>=0;y--)for(int x=0;x<32;x++){int rgb=icon.getRGB(x,y);tga.write(rgb&255);tga.write((rgb>>>8)&255);tga.write((rgb>>>16)&255)}
def texture=new File(stage,'Assist.tga');texture.bytes=tga.toByteArray()
def pkg=new File(editor.parentFile,'AmberAssistIconsV1/Classes');pkg.mkdirs()
new File(pkg,'IconAssets.uc').text='class IconAssets extends Object;\n#exec TEXTURE IMPORT NAME=Assist FILE="'+texture.absolutePath.replace('\\','/')+'" MIPS=OFF\n'
new File(editor,'AmberAssistIconsV1.ini').text=new File(editor,'UT2003.ini').getText('ISO-8859-1')+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=AmberAssistIconsV1\n'
println '32px code-drawn IA/bow icon and isolated texture package source prepared.'
