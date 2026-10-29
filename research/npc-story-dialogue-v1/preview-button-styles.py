from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parent;S=B/'client-demo-button-styles-v5';A=S/'assets'
old=B/'client-demo-angular-v3/assets';fill=B/'client-demo-ornamental-v4/assets'
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',n)
def preview(style,w=1024,h=640):
    out=Image.new('RGBA',(w,h),(47,58,56,255));d=ImageDraw.Draw(out)
    for y in range(0,h,48):
        for x in range(0,w,48):
            if (x//48+y//48)%2:d.rectangle((x,y,x+47,y+47),fill=(57,65,60,255))
    d.text((22,18),'PREVISUALIZACION - NO ES CAPTURA DE L2',font=font(13),fill='#e1dccf')
    x0=(w-920)//2;y0=h-440-40
    def paste(path,x,y):out.alpha_composite(Image.open(path).convert('RGBA'),(x0+x,y0+y))
    paste(fill/'BackgroundSemi.png',295,140);paste(old/'Frame.png',295,140);paste(old/'Nameplate.png',320,150)
    paste(B/'client-demo-gamma-v2/assets/PortraitComp.png',0,10)
    d=ImageDraw.Draw(out)
    for x,y,t,n,color in [(355,164,'AMBER',13,'#eed4a4'),(330,205,'Hola. ¿Necesitás ayuda?',13,'#f2e7d7'),(330,248,'Conversación de prueba',11,'#b9a98f'),(330,382,'Fondo:',11,'#cbbd9e'),(330,112,'Botones:',11,'#eed4a4')]:
        d.text((x0+x,y0+y),t,font=font(n),fill=color)
    for n,x,y in [('Explore',330,272),('Greet',330,322),('Close',862,152),('Original',680,154),('Compensate',758,154),('Opaque',392,376),('Semi',480,376),('Clear',568,376)]:paste(A/(style+n+'Up.png'),x,y)
    for i,letter in enumerate('ABCD'):paste(A/('Style'+letter+'Up.png'),392+i*108,106)
    paste(A/('Current'+style+'.png'),824,108)
    d.text((22,h-24),'Estilo '+style+' - '+{'A':'Metal grabado','B':'Pergamino antiguo','C':'Cristal arcano','D':'Oro ornamental'}[style],font=font(13),fill='white')
    return out.convert('RGB')
board=Image.new('RGB',(2048,1280))
for i,style in enumerate('ABCD'):
    im=preview(style);im.save(S/('preview-'+style+'-1024.png'));board.paste(im,((i%2)*1024,(i//2)*640))
board.save(S/'comparacion-en-panel.jpg',quality=95)
preview('D',1280,720).save(S/'preview-D-1280.png')
strip=Image.new('RGBA',(630,560),(24,27,29,255));d=ImageDraw.Draw(strip)
for i,style in enumerate('ABCD'):
    y=i*140;d.text((12,y+8),style+' - NORMAL / HOVER / PULSADO',font=font(12),fill='white')
    strip.alpha_composite(Image.open(A/(style+'ExploreUp.png')),(12,y+30))
    strip.alpha_composite(Image.open(A/(style+'OpaqueUp.png')),(12,y+88))
    strip.alpha_composite(Image.open(A/(style+'OpaqueOver.png')),(102,y+88))
    strip.alpha_composite(Image.open(A/(style+'OpaqueDown.png')),(192,y+88))
    strip.alpha_composite(Image.open(A/(style+'CloseUp.png')),(292,y+88))
strip.convert('RGB').save(S/'botones-tamano-nativo.png')
print('Saved native-size button comparison and expected layouts for all 4 styles.')
