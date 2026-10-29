// Continent fog with the actual Giran city polygon revealed; exact Interlude renderer.
// This is a transparent D3D9 loader plus two NWindow drawing hooks; no game rules.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <d3d9.h>
#include <bcrypt.h>
#include <string>
#include <map>
#include <mutex>
#include <cstdio>
#include <cstring>
#include "detour.h"
#include "geometry.h"
#include "alpha_scope.h"
#include "dynamic_fog.h"
#include "fog_transport.h"

static HMODULE selfModule,realD3D;
static std::wstring folder,configFile;
static std::once_flag initializeOnce;
static unsigned char* nwindow=nullptr;
static bool installed=false,rejected=false,drawFailed=false;
static EntryDetour worldDetour,townDetour,screenDetour;
using WorldDraw=void(__thiscall*)(void*,void*);
using TownDraw=void(__thiscall*)(void*,void*,void*);
using TextureDraw=void(__thiscall*)(void*,int,int,int,int,int,int,int,int,void*,int,int);
using TextureLoad=void*(__thiscall*)(void*,const wchar_t*,int);
static WorldDraw originalWorld=nullptr;
static TownDraw originalTown=nullptr;
struct Settings {int mode=2,alpha=180;};
static Settings settings;
static ULONGLONG lastSettings=0;
static void* atlasMaterial=nullptr;
static std::map<int,bool> loggedProjection;
static bool loggedWorld=false,loggedTown=false,loggedDraw=false;

static void logLine(const char* text) {
    HANDLE f=CreateFileW((folder+L"NexusMapFog.log").c_str(),FILE_APPEND_DATA,FILE_SHARE_READ|FILE_SHARE_WRITE,nullptr,OPEN_ALWAYS,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(f!=INVALID_HANDLE_VALUE){DWORD count;WriteFile(f,text,static_cast<DWORD>(strlen(text)),&count,nullptr);WriteFile(f,"\r\n",2,&count,nullptr);CloseHandle(f);}
}
static int bounded(int value,int lo,int hi){return value<lo?lo:value>hi?hi:value;}
static void readSettings() {
    ULONGLONG now=GetTickCount64();if(lastSettings&&now-lastSettings<1000)return;lastSettings=now;
    settings.mode=bounded(GetPrivateProfileIntW(L"MapFog",L"Mode",2,configFile.c_str()),0,2);
    settings.alpha=bounded(GetPrivateProfileIntW(L"MapFog",L"Alpha",180,configFile.c_str()),0,255);
}
static void paintUnchecked(void* mapObject,void* device,bool town) {
    readSettings();if(!settings.mode||drawFailed)return;
    auto map=static_cast<unsigned char*>(mapObject);
    const int mapId=*reinterpret_cast<int*>(map+0x250);
    const int scrollX=*reinterpret_cast<int*>(map+0x25c),scrollY=*reinterpret_cast<int*>(map+0x260);
    const float fw=*reinterpret_cast<float*>(map+0x88),fh=*reinterpret_cast<float*>(map+0x8c);
    if(!(fw>=16&&fw<=4096&&fh>=16&&fh<=4096))return;
    const int width=static_cast<int>(fw),height=static_cast<int>(fh);
    if(!atlasMaterial) {
        auto load=reinterpret_cast<TextureLoad>(nwindow+0x3f630);
        atlasMaterial=load(mapObject,L"NexusMapFogV4.Overlay",0);
        if(!atlasMaterial){drawFailed=true;logLine("DISABLED: V4 overlay material missing.");return;}
    }
    using Project=void(__thiscall*)(void*,int*,int*,int);
    auto project=reinterpret_cast<Project>(nwindow+0x187c10);
    int left=-131072,top=-262144,right=278129,bottom=351657;
    project(mapObject,&left,&top,mapId);project(mapObject,&right,&bottom,mapId);
    if(right<=left||bottom<=top||right-left>1000000||bottom-top>1000000)return;
    const int px=left-scrollX,py=top-scrollY,pw=right-left,ph=bottom-top;
    fog::Rect r=fog::clipRect(px,py,pw,ph,width,height);if(r.w<=0||r.h<=0)return;
    // NCGDevice::DrawTexture converts integer UVs before this same backend call.
    // Use floating UVs here so a city view samples a small part of the atlas accurately.
    using FloatDraw=void(__thiscall*)(void*,int,int,int,int,float,float,float,float,void*,int,int);
    auto bytes=static_cast<unsigned char*>(device);void* backend=*reinterpret_cast<void**>(bytes+0x34);
    auto table=*reinterpret_cast<void***>(backend);auto draw=reinterpret_cast<FloatDraw>(table[0xa0/4]);
    draw(backend,r.x+*reinterpret_cast<int*>(bytes+0x38),r.y+*reinterpret_cast<int*>(bytes+0x3c),r.w,r.h,
        static_cast<float>((r.x-px)*16.0/pw),static_cast<float>((r.y-py)*16.0/ph),
        static_cast<float>(r.w*16.0/pw),static_cast<float>(r.h*16.0/ph),atlasMaterial,settings.mode==2?255:settings.alpha,1);
    if(!loggedProjection.count(mapId)){char line[180];sprintf_s(line,"V4 map=%d plane=%d,%d..%d,%d town=%d",mapId,left,top,right,bottom,town?1:0);logLine(line);loggedProjection[mapId]=true;}
}
struct PacketStack {void** data;int position;int count;};
using ScreenMessage=void(__thiscall*)(void*,PacketStack*);
static ScreenMessage originalScreen=nullptr;
static fog4::Assembly packetAssembly;
static bool consumeScreenPacket(PacketStack* stack) {
    if(!stack||!stack->data||stack->position<0||stack->count-stack->position<11||stack->count>65536)return false;
    auto text=static_cast<const wchar_t*>(stack->data[stack->position+10]);
    if(!text)return false;
    if(!wcsncmp(text,L"#NXFC4|",7)) {
        std::wstring complete;
        int result=packetAssembly.accept(text,wcsnlen(text,231),complete);
        if(result==1&&walking::receive(complete.c_str(),complete.size()))logLine("RECEIVED complete chunked personal/global exploration snapshot.");
        else if(result<0)logLine("REJECTED malformed fog chunk.");
        stack->position+=11;return true;
    }
    if(wcsncmp(text,L"#NXFOG4|",8))return false;
    const size_t length=wcsnlen(text,5501);
    if(walking::receive(text,length))logLine("RECEIVED personal/global exploration snapshot.");
    else {char line[120];sprintf_s(line,"REJECTED legacy fog snapshot: length=%u (possible native string limit).",static_cast<unsigned>(length));logLine(line);}
    stack->position+=11;return true;
}
static void __fastcall hookedScreen(void* self,void*,PacketStack* stack) {
    bool consumed=false;
    __try{consumed=consumeScreenPacket(stack);}__except(EXCEPTION_EXECUTE_HANDLER){logLine("Fog packet inspection failed; passing normal message through.");}
    if(!consumed)originalScreen(self,stack);
}

struct PaintContext {void* map;void* device;bool town;};
static void paintBody(void* opaque) {
    auto context=static_cast<PaintContext*>(opaque);
    paintUnchecked(context->map,context->device,context->town);
}
static void paint(void* map,void* device,bool town) {
    // Fail closed on an unexpected client structure instead of crashing further frames.
    PaintContext context{map,device,town};
    __try{fog::withFullWindowAlpha(device,paintBody,&context);}
    __except(EXCEPTION_EXECUTE_HANDLER){drawFailed=true;logLine("DISABLED: exception in diagnostic PaintFog.");}
}
static void __fastcall hookedWorld(void* map,void*,void* device) {
    originalWorld(map,device);
    if(!loggedWorld){loggedWorld=true;logLine("WORLD map drawing reached.");}
    paint(map,device,false);
}
static void __fastcall hookedTown(void* map,void*,void* device,void* zone) {
    originalTown(map,device,zone);
    if(!loggedTown){loggedTown=true;logLine("TOWN map drawing reached.");}
    paint(map,device,true);
}
static bool matchesHash(HMODULE module) {
    wchar_t path[MAX_PATH];if(!GetModuleFileNameW(module,path,MAX_PATH))return false;
    HANDLE file=CreateFileW(path,GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(file==INVALID_HANDLE_VALUE)return false;
    BCRYPT_ALG_HANDLE alg=nullptr;BCRYPT_HASH_HANDLE hash=nullptr;
    unsigned char digest[32],buffer[65536];DWORD count=0;bool ok=false;
    if(BCryptOpenAlgorithmProvider(&alg,BCRYPT_SHA256_ALGORITHM,nullptr,0)>=0&&BCryptCreateHash(alg,&hash,nullptr,0,nullptr,0,0)>=0) {
        ok=true;
        for(;;){if(!ReadFile(file,buffer,sizeof(buffer),&count,nullptr)){ok=false;break;}if(!count)break;if(BCryptHashData(hash,buffer,count,0)<0){ok=false;break;}}
        if(ok)ok=BCryptFinishHash(hash,digest,sizeof(digest),0)>=0;
    }
    if(hash)BCryptDestroyHash(hash);if(alg)BCryptCloseAlgorithmProvider(alg,0);CloseHandle(file);
    static const unsigned char expected[32]={0xa8,0xbd,0xa7,0x7a,0x97,0xcd,0x3e,0x85,0x83,0xce,0x61,0xe2,0x27,0x38,0x03,0x03,0x21,0x2d,0xbf,0xc2,0x5a,0xe1,0x0f,0x89,0x07,0x10,0x63,0x79,0xfe,0xc3,0xf2,0x92};
    return ok&&!memcmp(digest,expected,32);
}
static void maybeInstall() {
    if(installed||rejected)return;
    HMODULE module=GetModuleHandleW(L"NWindow.dll");if(!module)return;
    if(!matchesHash(module)){rejected=true;logLine("REJECTED: NWindow.dll SHA256 differs; native hooks not installed.");return;}
    nwindow=reinterpret_cast<unsigned char*>(module);
    // Called synchronously before first device creation, or at Present after drawing.
    // Never patch the render entry concurrently from a worker thread.
    if(!worldDetour.install(nwindow+0x187910,reinterpret_cast<void*>(hookedWorld))) {
        rejected=true;logLine("REJECTED: world prologue mismatch or protection failure.");return;
    }
    originalWorld=reinterpret_cast<WorldDraw>(worldDetour.trampoline);
    if(!townDetour.install(nwindow+0x189130,reinterpret_cast<void*>(hookedTown))) {
        worldDetour.restore();originalWorld=nullptr;rejected=true;logLine("REJECTED: town prologue mismatch; world hook restored.");return;
    }
    originalTown=reinterpret_cast<TownDraw>(townDetour.trampoline);
    if(!screenDetour.install(nwindow+0x1696b0,reinterpret_cast<void*>(hookedScreen))) {
        townDetour.restore();worldDetour.restore();rejected=true;logLine("REJECTED: screen bridge prologue mismatch.");return;
    }
    originalScreen=reinterpret_cast<ScreenMessage>(screenDetour.trampoline);
    installed=true;logLine("INSTALLED: native map and server discovery bridge V4, exact verified client.");
}

using CreateDevice=HRESULT(WINAPI*)(IDirect3D9*,UINT,D3DDEVTYPE,HWND,DWORD,D3DPRESENT_PARAMETERS*,IDirect3DDevice9**);
using SetTexture=HRESULT(WINAPI*)(IDirect3DDevice9*,DWORD,IDirect3DBaseTexture9*);
using Reset=HRESULT(WINAPI*)(IDirect3DDevice9*,D3DPRESENT_PARAMETERS*);
using Present=HRESULT(WINAPI*)(IDirect3DDevice9*,const RECT*,const RECT*,HWND,const RGNDATA*);
static std::map<void**,CreateDevice> factoryMethods;
static std::map<void**,Present> presentMethods;
static std::map<void**,SetTexture> textureMethods;
static std::map<void**,Reset> resetMethods;
static std::map<IDirect3DDevice9*,walking::Device*> graphics;
static std::mutex methodMutex;
static bool replaceSlot(void** table,int slot,void* replacement) {
    DWORD old;if(!VirtualProtect(table+slot,sizeof(void*),PAGE_READWRITE,&old))return false;
    InterlockedExchangePointer(table+slot,replacement);DWORD unused;VirtualProtect(table+slot,sizeof(void*),old,&unused);return true;
}
static HRESULT WINAPI hookedSetTexture(IDirect3DDevice9* device,DWORD stage,IDirect3DBaseTexture9* texture) {
    SetTexture original=nullptr;walking::Device* state=nullptr;
    {std::lock_guard<std::mutex> lock(methodMutex);auto table=*reinterpret_cast<void***>(device);auto it=textureMethods.find(table);if(it!=textureMethods.end())original=it->second;auto d=graphics.find(device);if(d!=graphics.end())state=d->second;}
    if(!original)return D3DERR_INVALIDCALL;
    if(state){if(!state->selected&&walking::identify(device,*state,texture))logLine("MATCHED V4 overlay; dynamic exploration atlas enabled.");
        if(texture&&texture==state->selected){walking::update(device,*state);if(state->live)texture=state->live;}}
    return original(device,stage,texture);
}
static HRESULT WINAPI hookedReset(IDirect3DDevice9* device,D3DPRESENT_PARAMETERS* params) {
    Reset original=nullptr;
    {std::lock_guard<std::mutex> lock(methodMutex);auto it=resetMethods.find(*reinterpret_cast<void***>(device));if(it!=resetMethods.end())original=it->second;auto d=graphics.find(device);if(d!=graphics.end())d->second->clear();}
    return original?original(device,params):D3DERR_INVALIDCALL;
}
static HRESULT WINAPI hookedPresent(IDirect3DDevice9* device,const RECT* src,const RECT* dst,HWND window,const RGNDATA* dirty) {
    maybeInstall();Present fn=nullptr;
    {std::lock_guard<std::mutex> lock(methodMutex);auto it=presentMethods.find(*reinterpret_cast<void***>(device));if(it!=presentMethods.end())fn=it->second;}
    return fn?fn(device,src,dst,window,dirty):D3DERR_INVALIDCALL;
}
static HRESULT WINAPI hookedCreateDevice(IDirect3D9* factory,UINT adapter,D3DDEVTYPE type,HWND window,DWORD flags,D3DPRESENT_PARAMETERS* params,IDirect3DDevice9** output) {
    CreateDevice fn=nullptr;{std::lock_guard<std::mutex> lock(methodMutex);auto it=factoryMethods.find(*reinterpret_cast<void***>(factory));if(it!=factoryMethods.end())fn=it->second;}
    if(!fn)return D3DERR_INVALIDCALL;
    HRESULT result=fn(factory,adapter,type,window,flags,params,output);
    if(SUCCEEDED(result)&&output&&*output) {
        auto table=*reinterpret_cast<void***>(*output);
        std::lock_guard<std::mutex> lock(methodMutex);
        if(!graphics.count(*output))graphics[*output]=new walking::Device();
        if(!presentMethods.count(table)) {
            auto original=reinterpret_cast<Present>(table[17]);presentMethods.emplace(table,original);
            textureMethods.emplace(table,reinterpret_cast<SetTexture>(table[65]));resetMethods.emplace(table,reinterpret_cast<Reset>(table[16]));
            replaceSlot(table,65,reinterpret_cast<void*>(hookedSetTexture));replaceSlot(table,16,reinterpret_cast<void*>(hookedReset));
            if(!replaceSlot(table,17,reinterpret_cast<void*>(hookedPresent)))logLine("Present fallback unavailable; map hooks will only install if NWindow was already loaded.");
        }
    }
    return result;
}
static void initialize() {
    wchar_t path[MAX_PATH];GetModuleFileNameW(selfModule,path,MAX_PATH);folder=path;folder=folder.substr(0,folder.find_last_of(L"\\/")+1);configFile=folder+L"NexusMapFog.ini";
    GetSystemDirectoryW(path,MAX_PATH);std::wstring system=std::wstring(path)+L"\\d3d9.dll";realD3D=LoadLibraryW(system.c_str());
    if(!walking::loadField(folder+L"NexusFogFieldV4.bin"))logLine("ERROR: V4 field assets missing or invalid.");
    logLine("START map fog walking V4; personal/global snapshots and dynamic atlas.");
}
extern "C" IDirect3D9* WINAPI NexusDirect3DCreate9(UINT version) {
    std::call_once(initializeOnce,initialize);if(!realD3D)return nullptr;
    using Factory=IDirect3D9*(WINAPI*)(UINT);auto fn=reinterpret_cast<Factory>(GetProcAddress(realD3D,"Direct3DCreate9"));if(!fn)return nullptr;
    maybeInstall();auto factory=fn(version);if(!factory)return nullptr;
    auto table=*reinterpret_cast<void***>(factory);
    std::lock_guard<std::mutex> lock(methodMutex);
    if(!factoryMethods.count(table)) {
        factoryMethods.emplace(table,reinterpret_cast<CreateDevice>(table[16]));
        if(!replaceSlot(table,16,reinterpret_cast<void*>(hookedCreateDevice)))logLine("CreateDevice fallback unavailable.");
    }
    return factory;
}
BOOL WINAPI DllMain(HINSTANCE module,DWORD reason,LPVOID) {
    if(reason==DLL_PROCESS_ATTACH){selfModule=module;DisableThreadLibraryCalls(module);}return TRUE;
}
