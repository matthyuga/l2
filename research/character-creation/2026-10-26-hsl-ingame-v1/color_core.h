#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <vector>
namespace hair {
constexpr uint32_t Tag=0x40000000u, TagMask=0xfc000000u;
inline bool custom(uint32_t v){return (v&TagMask)==Tag;}
inline uint32_t encode(uint32_t rgb,int legacy){return Tag|((legacy&3)<<24)|(rgb&0xffffff);}
inline int legacy(uint32_t v){return custom(v)?((v>>24)&3):static_cast<int>(v);}
inline float clamp(float x,float lo,float hi){return std::max(lo,std::min(hi,x));}
inline uint32_t rgb(float h,float s,float l){
 h/=30;s/=100;l/=100;float a=s*std::min(l,1-l);
 auto c=[&](float n){float k=std::fmod(n+h,12.f);return uint32_t(std::lround(clamp(l-a*std::max(-1.f,std::min({k-3,9-k,1.f})),0,1)*255));};
 return c(0)<<16|c(8)<<8|c(4);
}
inline void fromRgb(uint32_t c,float&h,float&s,float&l){
 float r=((c>>16)&255)/255.f,g=((c>>8)&255)/255.f,b=(c&255)/255.f;
 float hi=std::max({r,g,b}),lo=std::min({r,g,b}),d=hi-lo;l=(hi+lo)/2;h=s=0;
 if(d>0){s=d/(1-std::abs(2*l-1));h=(hi==r?std::fmod((g-b)/d,6.f):hi==g?(b-r)/d+2:(r-g)/d+4)*60;if(h<0)h+=360;}s*=100;l*=100;
}
inline uint32_t color565(uint16_t v){return 0xff000000u|(((v>>11)*255/31)<<16)|((((v>>5)&63)*255/63)<<8)|((v&31)*255/31);}
inline uint32_t interpolate(uint32_t a,uint32_t b,int wa,int wb,int divisor){
 uint32_t c=0xff000000;for(int k=0;k<3;k++){int shift=k*8;c|=(((a>>shift&255)*wa+(b>>shift&255)*wb)/divisor)<<shift;}return c;
}
// UE2 TEXF_DXT1=3, DXT3=7, DXT5=8; output FColor/BGRA bytes.
inline bool decode(const uint8_t* src,size_t bytes,int w,int h,int format,std::vector<uint32_t>& out){
 if(!src||w<1||h<1||w>4096||h>4096)return false;out.assign(size_t(w)*h,0);
 if(format==5){if(bytes<out.size()*4)return false;std::memcpy(out.data(),src,out.size()*4);return true;}
 if(format!=3&&format!=7&&format!=8)return false;
 int stride=format==3?8:16;size_t required=size_t((w+3)/4)*((h+3)/4)*stride;if(bytes<required)return false;
 for(int by=0;by<h;by+=4)for(int bx=0;bx<w;bx+=4,src+=stride){
  const uint8_t* c=src+(format==3?0:8);uint16_t a=uint16_t(c[0]|c[1]<<8),b=uint16_t(c[2]|c[3]<<8);
  uint32_t colors[4]={color565(a),color565(b),0,0};
  if(a>b||format!=3){colors[2]=interpolate(colors[0],colors[1],2,1,3);colors[3]=interpolate(colors[0],colors[1],1,2,3);}
  else{colors[2]=interpolate(colors[0],colors[1],1,1,2);colors[3]=0;}
  uint32_t indices=uint32_t(c[4])|uint32_t(c[5])<<8|uint32_t(c[6])<<16|uint32_t(c[7])<<24;
  uint8_t alphas[8]{};uint64_t abits=0;
  if(format==8){alphas[0]=src[0];alphas[1]=src[1];for(int k=0;k<6;k++)abits|=uint64_t(src[k+2])<<(k*8);
   if(alphas[0]>alphas[1])for(int k=2;k<8;k++)alphas[k]=uint8_t(((8-k)*alphas[0]+(k-1)*alphas[1])/7);
   else {for(int k=2;k<6;k++)alphas[k]=uint8_t(((6-k)*alphas[0]+(k-1)*alphas[1])/5);alphas[6]=0;alphas[7]=255;}}
  for(int k=0;k<16;k++){uint32_t value=colors[(indices>>(k*2))&3];
   if(format==7)value=(value&0xffffff)|uint32_t(((src[k/2]>>((k&1)*4))&15)*17)<<24;
   if(format==8)value=(value&0xffffff)|uint32_t(alphas[(abits>>(k*3))&7])<<24;
   int x=bx+(k&3),y=by+(k>>2);if(x<w&&y<h)out[size_t(y)*w+x]=value;}
 }return true;
}
inline void tint(const std::vector<uint32_t>& source,const std::vector<uint8_t>& mask,uint32_t color,uint32_t* out){
 float h,s,l;fromRgb(color,h,s,l);
 for(size_t i=0;i<source.size();i++){
  uint32_t c=source[i];if(i>=mask.size()||!mask[i]||!(c>>24)){out[i]=c;continue;}
  float lum=((c>>16&255)*.2126f+(c>>8&255)*.7152f+(c&255)*.0722f)/255.f;
  float detail=(lum-.4f)*1.3f*std::min(l,100-l);uint32_t tinted=rgb(h,s,clamp(l+detail,0,100));
  uint32_t result=c&0xff000000;for(int k=0;k<3;k++){int sh=k*8;result|=(((c>>sh&255)*(255-mask[i])+(tinted>>sh&255)*mask[i]+127)/255)<<sh;}out[i]=result;
 }
}
inline std::vector<uint8_t> differenceMask(const std::vector<std::vector<uint32_t>>& variants){
 if(variants.empty())return {};size_t n=variants[0].size();std::vector<uint8_t> mask(n,0);
 for(auto&v:variants){if(v.size()!=n)continue;for(size_t i=0;i<n;i++)for(int k=0;k<3;k++)if(std::abs(int(v[i]>>(k*8)&255)-int(variants[0][i]>>(k*8)&255))>6)mask[i]=255;}
 return mask;
}
}
