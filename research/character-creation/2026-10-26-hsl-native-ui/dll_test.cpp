#define NOMINMAX
#include "hsl_picker.h"
#include <cstdio>
#include <vector>
struct Events{std::vector<unsigned> codes;NexusHslState last;};
void __stdcall callback(uint32_t e,const NexusHslState* state,void* context){auto out=static_cast<Events*>(context);out->codes.push_back(e);out->last=*state;}
int main(int argc,char** argv){
    if(argc!=2)return 2;HMODULE dll=LoadLibraryA(argv[1]);if(!dll)return 3;
    auto open=reinterpret_cast<decltype(&NexusHslOpen)>(GetProcAddress(dll,"NexusHslOpen"));auto read=reinterpret_cast<decltype(&NexusHslRead)>(GetProcAddress(dll,"NexusHslRead"));auto set=reinterpret_cast<decltype(&NexusHslSet)>(GetProcAddress(dll,"NexusHslSet"));auto finish=reinterpret_cast<decltype(&NexusHslFinish)>(GetProcAddress(dll,"NexusHslFinish"));if(!open||!read||!set||!finish)return 4;
    NexusHslState initial;initial.hue=120;initial.saturation=60;initial.lightness=40;Events e;HWND w=open(nullptr,&initial,callback,&e,1);if(!w||IsWindowVisible(w))return 5;NexusHslState next;if(!read(w,&next))return 6;next.hue=240;if(!set(w,&next)||e.codes.size()!=1||e.codes.back()!=NexusPreview)return 7;if(!finish(w,FALSE)||e.codes.back()!=NexusCancel||e.last.hue!=120)return 8;
    DWORD gdi=GetGuiResources(GetCurrentProcess(),GR_GDIOBJECTS),user=GetGuiResources(GetCurrentProcess(),GR_USEROBJECTS);
    for(int i=0;i<50;i++){w=open(nullptr,&initial,callback,&e,1);if(!w)return 9;next.hue=static_cast<float>(i*7);if(!set(w,&next)||!finish(w,TRUE))return 10;}
    if(GetGuiResources(GetCurrentProcess(),GR_GDIOBJECTS)>gdi||GetGuiResources(GetCurrentProcess(),GR_USEROBJECTS)>user)return 11;
    FreeLibrary(dll);std::puts("PASS: x86 DLL exports and callbacks; 50 open/preview/apply/close cycles without GDI/USER handle growth.");return 0;
}
