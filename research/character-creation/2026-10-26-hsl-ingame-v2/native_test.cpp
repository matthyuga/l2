#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <cstdio>
#include <cstdlib>
#include "color_core.h"
static int checks=0;
static void check(bool v,const char* why){++checks;if(!v){printf("FAIL %s\n",why);exit(1);}}
int main(){
 for(int n=0;n<4096;n++){uint32_t color=(n*0x9e3779u)&0xffffff;float h,s,l;hair::fromRgb(color,h,s,l);check(hair::rgb(h,s,l)==color,"HSL roundtrip");for(int old=0;old<4;old++){auto v=hair::encode(color,old);check(hair::custom(v)&&hair::legacy(v)==old&&(v&0xffffff)==color,"wire roundtrip");}}
 for(int n:{-1,4,255,0x3fffffff,0x44000000,0x7fffffff})check(!hair::custom(uint32_t(n)),"reject untagged values");
 for(int n=0;n<4;n++)check(hair::legacy(n)==n&&!hair::custom(n),"classic colors");
 std::vector<uint32_t> a={0xff804020,0x00553322,0x80402010},b=a;b[0]=0xff112233;std::vector<std::vector<uint32_t>> variants={a,b};auto mask=hair::differenceMask(variants);check(mask==std::vector<uint8_t>({255,0,0}),"variant mask protects ornament and alpha");
 uint32_t output[3];hair::tint(a,mask,0x31a0e0,output);check(output[0]!=a[0]&&output[1]==a[1]&&output[2]==a[2],"only hair changes");for(int i=0;i<3;i++)check((output[i]&0xff000000)==(a[i]&0xff000000),"alpha preserved byte-for-byte");
 uint8_t bc1[8]={0x00,0xf8,0xe0,0x07,0,0,0,0};std::vector<uint32_t> pixels;check(hair::decode(bc1,8,4,4,3,pixels)&&pixels[0]==0xffff0000,"BC1 red block");check(!hair::decode(bc1,7,4,4,3,pixels),"truncated BC1");
 uint8_t bc2[16];memset(bc2,0xff,8);memcpy(bc2+8,bc1,8);bc2[0]=0x10;check(hair::decode(bc2,16,4,4,7,pixels)&&pixels[0]==0x00ff0000&&pixels[1]==0x11ff0000,"BC2 explicit alpha");
 uint8_t bc3[16]={255,0,0,0,0,0,0,0};memcpy(bc3+8,bc1,8);check(hair::decode(bc3,16,4,4,8,pixels)&&pixels[0]==0xffff0000,"BC3 alpha");
 check(hair::rgb(0,100,0)==0&&hair::rgb(240,100,100)==0xffffff,"black and white endpoints");
 HMODULE dll=LoadLibraryW(L"stage\\NexusHairHslGame.dll");check(dll!=nullptr,"DLL loads without game dependencies");for(const char* e:{"NexusHairDraw","NexusHairTexture","NexusHairUser","NexusHairPacket"})check(GetProcAddress(dll,e)!=nullptr,"native export");check(FreeLibrary(dll)!=0,"DLL unloads before callbacks");
 printf("PASS %d native checks\n",checks);FILE* f=nullptr;fopen_s(&f,"native-test-results.json","w");if(f){fprintf(f,"{\"passed\":%d,\"visual_game_test\":false}\n",checks);fclose(f);}return 0;
}
