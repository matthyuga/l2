import javax.imageio.ImageIO
def stage=new File(args[0],'exports/contract/visual-v3')
for(String name:['Contract','Fire','Rain','Break']) {
 def image=ImageIO.read(new File(stage,'icons/'+name+'.png'))
 byte[] tga=new File(stage,'icons-roundtrip/AmberIconsV1/Texture/'+name+'.tga').bytes
 int stride=(tga[16]&255)/8,start=18+(tga[0]&255);boolean top=(tga[17]&32)!=0
 def matches=[identity:0,flipY:0,flipX:0,rotate180:0]
 for(int y=0;y<32;y++)for(int x=0;x<32;x++) {
  int offset=start+((top?y:31-y)*32+x)*stride
  int rgb=(tga[offset]&255)|((tga[offset+1]&255)<<8)|((tga[offset+2]&255)<<16)
  [identity:[x,y],flipY:[x,31-y],flipX:[31-x,y],rotate180:[31-x,31-y]].each{k,xy->if(rgb==(image.getRGB(xy[0],xy[1])&0xffffff))matches[k]++}
 }
 println name+' origin='+ (tga[17]&255)+' depth='+(tga[16]&255)+' '+matches
}
