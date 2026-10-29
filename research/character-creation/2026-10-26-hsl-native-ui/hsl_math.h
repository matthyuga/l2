#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
namespace hsl {
inline float clamp(float x,float lo,float hi){return std::max(lo,std::min(hi,x));}
inline bool valid(float h,float s,float l){return std::isfinite(h)&&std::isfinite(s)&&std::isfinite(l)&&h>=0&&h<360&&s>=0&&s<=100&&l>=0&&l<=100;}
inline uint32_t rgb(float hue,float saturation,float lightness){
    float h=hue/30.0f,s=saturation/100.0f,l=lightness/100.0f,a=s*std::min(l,1-l);
    auto c=[&](float n){float k=std::fmod(n+h,12.0f);return static_cast<uint32_t>(std::lround(clamp(l-a*std::max(-1.0f,std::min({k-3,9-k,1.0f})),0,1)*255));};
    return c(0)<<16|c(8)<<8|c(4);
}
inline void fromRgb(uint32_t rgb,float& h,float& s,float& l){
    float r=((rgb>>16)&255)/255.0f,g=((rgb>>8)&255)/255.0f,b=(rgb&255)/255.0f;
    float hi=std::max({r,g,b}),lo=std::min({r,g,b}),d=hi-lo;l=(hi+lo)/2;h=0;s=0;
    if(d>0){s=d/(1-std::abs(2*l-1));h=(hi==r?std::fmod((g-b)/d,6.0f):hi==g?(b-r)/d+2:(r-g)/d+4)*60;if(h<0)h+=360;}
    s*=100;l*=100;
}
inline COLORREF color(uint32_t rgb){return RGB((rgb>>16)&255,(rgb>>8)&255,rgb&255);}
}
