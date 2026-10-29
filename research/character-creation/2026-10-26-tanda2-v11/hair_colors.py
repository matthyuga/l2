"""Deterministic hair tint masks; original alpha and protected ornaments stay exact."""
from PIL import Image,ImageDraw
import numpy as np
PALETTES=[None,(.34,.18,.09),(.88,.69,.32),(.82,.84,.87)]
def source_mask(model,variant,slot,im):
 mask=Image.new('L',im.size,255);draw=ImageDraw.Draw(mask)
 # Source UV islands contain hair alongside face/ornament details. Protect
 # those islands before tinting. Coordinates refer to the donor texture.
 exclusions={
  ('MElf',1,1):[(220,180,256,256)],
  ('MDarkElf',1,0):[(400,0,512,512)],
  ('MDarkElf',1,1):[(190,145,256,185)],
  ('FOrc',1,0):[(0,0,256,127),(0,0,64,160)],
  ('MOrc',1,0):[(64,232,220,256)],
  ('MOrc',1,1):[(95,230,256,256)],
  ('MShaman',1,0):[(50,78,242,256)],
  ('FDwarf',1,0):[(27,218,95,256),(80,200,125,256)],
 }
 for box in exclusions.get((model,variant,slot),[]):draw.rectangle(box,fill=0)
 if model=='MElf' and variant==2:
  draw.polygon([(83,53),(130,39),(231,49),(221,146),(183,178),(121,153),(91,118)],fill=0)
 a=np.asarray(im.convert('RGBA'));m=np.array(mask);m[a[:,:,3]==0]=0
 return Image.fromarray(m,'L')
def texture_mask(model,variant,im,proof,donor_root):
 regions=proof.get('atlas_regions',[])
 if not regions:return source_mask(model,variant,0,im)
 out=Image.new('L',im.size,0)
 for slot,(region,name) in enumerate(zip(regions,proof['atlas_source_textures'])):
  source=Image.open(next(donor_root.rglob(name+'.png'))).convert('RGBA');m=source_mask(model,variant,slot,source);x,y,w,h=[region[k] for k in ['x','y','width','height']];pad=4
  out.paste(m,(x,y));out.paste(m.crop((0,0,1,h)).resize((pad,h)),(x-pad,y));out.paste(m.crop((w-1,0,w,h)).resize((pad,h)),(x+w,y));out.paste(m.crop((0,0,w,1)).resize((w,pad)),(x,y-pad));out.paste(m.crop((0,h-1,w,h)).resize((w,pad)),(x,y+h))
 return out
def tint(im,mask,color):
 original=np.asarray(im.convert('RGBA'));out=original.copy();selected=(np.asarray(mask)>0)&(original[:,:,3]>0)
 if color==0:return im.copy()
 rgb=original[:,:,:3].astype(np.float32)/255;lum=rgb@np.array([.2126,.7152,.0722],dtype=np.float32);high=max(float(np.percentile(lum[selected],99)),.01);value=np.clip(.08+.92*(lum/high)**1.2,0,1)
 recolored=np.clip(value[:,:,None]*np.array(PALETTES[color])[None,None,:]*255,0,255).round().astype(np.uint8)
 out[:,:,:3][selected]=recolored[selected]
 assert np.array_equal(out[:,:,3],original[:,:,3]);assert np.array_equal(out[~selected],original[~selected])
 return Image.fromarray(out,'RGBA')
