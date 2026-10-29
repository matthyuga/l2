"""Native UE2 cloud sea: opaque blue haze + drifting alpha cloud mask.

WhiteCloud stores detail in alpha, so using its RGB alone makes a blank white
plane. A native Combiner uses that alpha to blend two opaque constant colors.
"""
from package_tools import *
def add_cloud_material(p):
    def mat(name,cl,raw):return p.add(name,'Engine.'+cl,raw+p.end()+b'\0'*4,flags=0xf0004)
    white=mat('AcademyCloudWhite','ConstantColor',p.prop('Color',10,bytes([245,246,249,255]),'Color'))
    haze=mat('AcademyCloudHaze','ConstantColor',p.prop('Color',10,bytes([198,185,172,255]),'Color'))
    cloud=p.imp('L2_Skies.Textures.WhiteCloud','Engine.Texture')
    scale=mat('AcademyCloudScale','TexScaler',p.obj('Material',cloud)+p.float('UScale',.07)+p.float('VScale',.07))
    drift=mat('AcademyCloudDrift','TexPanner',p.obj('Material',scale)+p.float('PanRate',.002))
    blend=mat('AcademyCloudBlend','Combiner',p.obj('Material1',white)+p.obj('Material2',haze)+p.obj('Mask',drift)+p.prop('CombineOperation',1,bytes([5]))+p.prop('AlphaOperation',1,bytes([3])))
    return mat('AcademyCloudSea','Shader',p.obj('Diffuse',blend)+p.obj('SelfIllumination',blend)+p.boolean('TwoSided',True)+p.boolean('ZWrite',True)+p.prop('OutputBlending',1,b'\0'))
