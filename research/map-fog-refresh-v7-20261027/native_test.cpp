#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <cstdio>
#include "detour.h"
#include "geometry.h"
#include "alpha_scope.h"
#include "fog_field.h"
#include "native_texture_identity.h"
#include <fstream>

static int checks=0;
static void check(bool condition){++checks;if(!condition){printf("FAIL check %d\n",checks);fflush(stdout);ExitProcess(1);}}
__declspec(naked) int targetWorld() {
    __asm {
        push ebp
        mov ebp,esp
        push -1
        mov eax,[ebp+8]
        add eax,7
        mov esp,ebp
        pop ebp
        ret 4
    }
}
__declspec(naked) int targetTown() {
    __asm {
        push ebp
        mov ebp,esp
        push -1
        mov eax,[ebp+8]
        add eax,[ebp+12]
        mov esp,ebp
        pop ebp
        ret 8
    }
}
using World=int(__thiscall*)(void*,int);
using Town=int(__thiscall*)(void*,int,int);
static World oldWorld;static Town oldTown;
static int __fastcall worldHook(void* self,void*,int a){return oldWorld(self,a)+100;}
static int __fastcall townHook(void* self,void*,int a,int b){return oldTown(self,a,b)+200;}
__declspec(naked) int targetCache() {
    __asm {
        push ebp
        lea ebp,[esp-70h]
        sub esp,70h
        mov eax,[ebp+78h]
        add eax,[ebp+7ch]
        add esp,70h
        pop ebp
        ret 8
    }
}
static Town oldCache;
static int __fastcall cacheProbeHook(void* self,void*,int a,int b){return oldCache(self,a,b)+300;}
struct FakeSource {void** table;void* result;};
static void* __fastcall fakeGetter(FakeSource* self,void*){return self->result;}
static unsigned char device[128];
static int callbackMode;
static unsigned char inheritedAlpha(void* p,unsigned char requested) {
    auto b=static_cast<unsigned char*>(p);
    if(requested!=255)return requested;
    unsigned char result=b[0x74];
    if(*reinterpret_cast<int*>(b+0x70))result>>=1;
    return result;
}
static void drawProbe(void* p) {
    check(inheritedAlpha(p,255)==255);
    check(inheritedAlpha(p,180)==180);
    if(callbackMode)RaiseException(0xe0421001,0,0,nullptr);
}
static void checkExceptionRestoration() {
    callbackMode=1;
    __try {fog::withFullWindowAlpha(device,drawProbe,device);}
    __except(GetExceptionCode()==0xe0421001?EXCEPTION_EXECUTE_HANDLER:EXCEPTION_CONTINUE_SEARCH) {}
    callbackMode=0;
}
#include "fog_transport.h"
int main(int argc,char** argv) {
    void* textureTable[21]{};void* sourceTable[6]{};
    textureTable[20]=reinterpret_cast<void*>(fakeGetter);sourceTable[5]=reinterpret_cast<void*>(fakeGetter);
    int material=123;FakeSource texture{textureTable,&material},source{sourceTable,&texture};
    check(fogNative::materialOf(nullptr)==nullptr);check(fogNative::materialOf(&source)==&material);
    source.result=nullptr;check(fogNative::materialOf(&source)==nullptr);source.result=&texture;
    unsigned char fakeCache[64]{};auto expectedGpu=reinterpret_cast<IDirect3DTexture9*>(0x123400);
    *reinterpret_cast<IDirect3DTexture9**>(fakeCache+0x38)=expectedGpu;check(fogNative::gpuOf(fakeCache)==expectedGpu);
    volatile Town cache=reinterpret_cast<Town>(targetCache);check(cache(nullptr,3,4)==7);
    EntryDetour cachePatch;check(!cachePatch.install(reinterpret_cast<void*>(targetCache),reinterpret_cast<void*>(cacheProbeHook)));
    check(cachePatch.install(reinterpret_cast<void*>(targetCache),reinterpret_cast<void*>(cacheProbeHook),true));oldCache=reinterpret_cast<Town>(cachePatch.trampoline);
    for(int i=0;i<10000;i++)check(cache(nullptr,i,2)==i+302);
    check(cachePatch.restore());check(cache(nullptr,3,4)==7);
    if(argc==3) {
        std::ifstream file(argv[2]);std::string line;std::vector<std::wstring> chunks;
        while(std::getline(file,line)){if(!line.empty()&&line.back()=='\r')line.pop_back();chunks.emplace_back(line.begin(),line.end());}
        check(chunks.size()>1);fog4::Assembly transport;std::wstring complete;
        // Missing, duplicate and reversed messages must not apply partial grids.
        check(transport.accept(chunks.back().c_str(),chunks.back().size(),complete)==0&&complete.empty());
        check(transport.accept(chunks.back().c_str(),chunks.back().size(),complete)==0&&complete.empty());
        for(size_t i=chunks.size()-1;i-->0;){int result=transport.accept(chunks[i].c_str(),chunks[i].size(),complete);check(result==(i==0?1:0));}
        fog4::Snapshot s;check(fog4::parse(complete.c_str(),complete.size(),s));check(s.player==268473899);
        check(fog4::alpha(s,147725,-56517,255)==0);
        check(fog4::alpha(s,-100000,240000,255)==255);
        std::wstring badChunk=L"#NXFC4|1|1|0|999|x";check(transport.accept(badChunk.c_str(),badChunk.size(),complete)==-1);
    }
    if(argc==2) {
        std::ifstream file(argv[1]);std::string encoded;std::getline(file,encoded);
        std::wstring packet(encoded.begin(),encoded.end());fog4::Snapshot actual;
        check(fog4::parse(packet.c_str(),packet.size(),actual));check(actual.player==123);
        check(fog4::alpha(actual,147725,-56517,255)==0);
        actual.personal.fill(0);check(fog4::alpha(actual,147725,-56517,255)==140);
        check(fog4::alpha(actual,-100000,240000,255)==255);
    }
    fog4::Snapshot snapshot;
    std::wstring empty=L"#NXFOG4|123|1||";
    check(fog4::parse(empty.c_str(),empty.size(),snapshot));
    check(snapshot.player==123);
    std::wstring known=L"#NXFOG4|456|2|AQ==|AQ==";
    check(fog4::parse(known.c_str(),known.size(),snapshot));check(snapshot.player==456&&snapshot.personal[0]==1&&snapshot.global[0]==1);
    check(!fog4::parse(L"#NXFOG4|0|1||",14,snapshot));
    std::wstring bad=L"#NXFOG4|1|1|!!!!|";check(!fog4::parse(bad.c_str(),bad.size(),snapshot));
    fog4::Snapshot field;int index=10*fog4::Columns+10;field.global[index/8]|=1<<(index%8);
    double wx=-131072+(10.5)*4096,wy=-262144+(10.5)*4096;
    check(fog4::alpha(field,wx,wy,255)==140);
    field.personal[index/8]|=1<<(index%8);check(fog4::alpha(field,wx,wy,255)==0);
    check(fog4::alpha(fog4::Snapshot{},wx,wy,0)==0);check(fog4::alpha(fog4::Snapshot{},wx,wy,255)==255);
    for(int focus: {0,1})for(int opacity: {0,32,127,180,255}) {
        *reinterpret_cast<int*>(device+0x70)=focus;device[0x74]=static_cast<unsigned char>(opacity);
        check(inheritedAlpha(device,255)==(focus?opacity>>1:opacity));
        fog::withFullWindowAlpha(device,drawProbe,device);
        check(*reinterpret_cast<int*>(device+0x70)==focus&&device[0x74]==opacity);
        checkExceptionRestoration();
        check(*reinterpret_cast<int*>(device+0x70)==focus&&device[0x74]==opacity);
    }
    auto r=fog::visibleRect(200,200,160,120,100,100,328,328);check(r.x==20&&r.y==40&&r.w==160&&r.h==120);
    r=fog::visibleRect(200,200,160,120,180,180,328,328);check(r.x==0&&r.y==0&&r.w==100&&r.h==80);
    r=fog::visibleRect(200,200,160,120,400,400,328,328);check(r.w==0&&r.h==0);
    r=fog::visibleRect(200,200,160,120,0,0,160,160);check(r.x==120&&r.y==140&&r.w==40&&r.h==20);
    // The city patch and the four cloud strips must partition the viewport exactly.
    for(int px=-450;px<=450;px+=75)for(int py=-450;py<=450;py+=75)for(int size: {120,1200}) {
        auto h=fog::clipRect(px,py,size,size,328,328);
        if(h.w<=0||h.h<=0)continue;
        int area=328*h.y+328*(328-h.y-h.h)+h.x*h.h+(328-h.x-h.w)*h.h+h.w*h.h;
        check(area==328*328);check(h.x>=0&&h.y>=0&&h.x+h.w<=328&&h.y+h.h<=328);
    }
    EntryDetour one,two;
    volatile World world=reinterpret_cast<World>(targetWorld);volatile Town town=reinterpret_cast<Town>(targetTown);
    check(world(nullptr,3)==10);check(town(nullptr,3,4)==7);
    check(one.install(reinterpret_cast<void*>(targetWorld),reinterpret_cast<void*>(worldHook)));oldWorld=reinterpret_cast<World>(one.trampoline);
    check(two.install(reinterpret_cast<void*>(targetTown),reinterpret_cast<void*>(townHook)));oldTown=reinterpret_cast<Town>(two.trampoline);
    for(int i=0;i<10000;++i){check(world(nullptr,i)==i+107);check(town(nullptr,i,2)==i+202);}
    check(one.restore());check(two.restore());check(world(nullptr,3)==10);check(town(nullptr,3,4)==7);
    printf("PASS %d checks: clipping, x86 thiscall/fastcall, 20000 detoured calls, trampoline and restoration.\n",checks);
    return 0;
}
