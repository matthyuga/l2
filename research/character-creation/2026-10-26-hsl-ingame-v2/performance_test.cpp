#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <chrono>
#include <cstdio>
#include "color_core.h"
#define hair hair_v1
#include "../2026-10-26-hsl-ingame-v1/color_core.h"
#undef hair
int main(){
 std::vector<uint32_t> src(1024*512),a(src.size()),b(src.size());std::vector<uint8_t> mask(src.size());
 for(size_t i=0;i<src.size();i++){src[i]=uint32_t(i*2654435761u);mask[i]=(i%7)?255:0;}
 auto run=[&](bool old){auto start=std::chrono::steady_clock::now();for(int n=0;n<8;n++){auto color=hair::rgb(n*41.f,75,45);if(old)hair_v1::tint(src,mask,color,a.data());else hair::tint(src,mask,color,b.data());}return std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count()/8;};
 run(false);double old=run(true),fast=run(false);unsigned delta=0;
 for(size_t i=0;i<src.size();i++){
  if((b[i]&0xff000000)!=(src[i]&0xff000000)||(!mask[i]&&b[i]!=src[i]))return 1;
  for(int k=0;k<3;k++)delta=std::max(delta,unsigned(std::abs(int(a[i]>>(8*k)&255)-int(b[i]>>(8*k)&255))));
 }
 if(delta>3||fast>=old)return 2;
 printf("PASS 524288 pixels: alpha/protected exact; RGB max delta %u; v1 %.3f ms -> v2 %.3f ms (%.2fx)\n",delta,old,fast,old/fast);
 FILE* f=nullptr;fopen_s(&f,"performance-results.json","w");if(f){fprintf(f,"{\"passed\":true,\"pixels\":524288,\"v1_ms\":%.4f,\"v2_ms\":%.4f,\"speedup\":%.3f,\"max_rgb_delta\":%u,\"alpha_protected_exact\":true}\n",old,fast,old/fast,delta);fclose(f);}return 0;
}
