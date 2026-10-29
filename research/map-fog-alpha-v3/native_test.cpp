#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <cstdio>
#include "detour.h"
#include "geometry.h"
#include "alpha_scope.h"

static int checks=0;
static void check(bool condition){++checks;if(!condition){printf("FAIL check %d\n",checks);ExitProcess(1);}}
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
int main() {
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
