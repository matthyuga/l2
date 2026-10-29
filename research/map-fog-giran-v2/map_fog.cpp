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

static HMODULE selfModule,realD3D;
static std::wstring folder,configFile;
static std::once_flag initializeOnce;
static unsigned char* nwindow=nullptr;
static bool installed=false,rejected=false,drawFailed=false;
static EntryDetour worldDetour,townDetour;
using WorldDraw=void(__thiscall*)(void*,void*);
using TownDraw=void(__thiscall*)(void*,void*,void*);
using TextureDraw=void(__thiscall*)(void*,int,int,int,int,int,int,int,int,void*,int,int);
using TextureLoad=void*(__thiscall*)(void*,const wchar_t*,int);
static WorldDraw originalWorld=nullptr;
static TownDraw originalTown=nullptr;
struct Settings {int mode=2,alpha=180;};
static Settings settings;
static ULONGLONG lastSettings=0;
static void* cloudTexture=nullptr;
static void* giranTexture=nullptr;
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
    if(!cloudTexture||!giranTexture) {
        auto load=reinterpret_cast<TextureLoad>(nwindow+0x3f630);
        cloudTexture=load(mapObject,L"NexusMapFogV2.CloudTile",0);
        giranTexture=load(mapObject,L"NexusMapFogV2.GiranClear",0);
        if(!cloudTexture||!giranTexture){drawFailed=true;logLine("DISABLED: V2 fog assets could not be loaded.");return;}
        logLine("V2 cloud and Giran alpha-mask textures loaded.");
    }
    // Native world-to-map conversion handles both continental and city projection.
    using Project=void(__thiscall*)(void*,int*,int*,int);
    auto project=reinterpret_cast<Project>(nwindow+0x187c10);
    int left=72000,top=136000,right=96000,bottom=160000;
    project(mapObject,&left,&top,mapId);project(mapObject,&right,&bottom,mapId);
    if(right<=left||bottom<=top||right-left>1000000||bottom-top>1000000){drawFailed=true;logLine("DISABLED: invalid native map projection.");return;}
    if(!loggedProjection.count(mapId)) {
        char line[220];sprintf_s(line,"GIRAN projection map=%d patch=%d,%d..%d,%d viewport=%dx%d town=%d",mapId,left,top,right,bottom,width,height,town?1:0);logLine(line);loggedProjection[mapId]=true;
    }
    auto draw=reinterpret_cast<TextureDraw>(nwindow+0x21a00);
    const int alpha=settings.mode==2?255:settings.alpha;
    const int px=left-scrollX,py=top-scrollY,pw=right-left,ph=bottom-top;
    // Cloud UVs use world-map coordinates in both projections, avoiding window-relative drift.
    constexpr double scale=0.0050048828125;
    const double globalLeft=(72000+131072)*scale,globalTop=(136000+262144)*scale;
    const double gxPerPixel=24000*scale/pw,gyPerPixel=24000*scale/ph;
    auto outside=[&](int x,int y,int w,int h){
        if(w<=0||h<=0)return;
        int u=static_cast<int>(globalLeft+(x+scrollX-left)*gxPerPixel)%512;
        int v=static_cast<int>(globalTop+(y+scrollY-top)*gyPerPixel)%512;
        if(u<0)u+=512;if(v<0)v+=512;
        int ul=std::max(1,static_cast<int>(w*gxPerPixel+0.5));
        int vl=std::max(1,static_cast<int>(h*gyPerPixel+0.5));
        draw(device,x,y,w,h,u,v,ul,vl,cloudTexture,alpha,1);
    };
    fog::Rect hole=fog::clipRect(px,py,pw,ph,width,height);
    if(hole.w<=0||hole.h<=0){outside(0,0,width,height);return;}
    outside(0,0,width,hole.y);
    outside(0,hole.y+hole.h,width,height-hole.y-hole.h);
    outside(0,hole.y,hole.x,hole.h);
    outside(hole.x+hole.w,hole.y,width-hole.x-hole.w,hole.h);
    const int u=bounded(static_cast<int>((hole.x-px)*512.0/pw),0,511);
    const int v=bounded(static_cast<int>((hole.y-py)*512.0/ph),0,511);
    const int ul=bounded(static_cast<int>(hole.w*512.0/pw+0.5),1,512-u);
    const int vl=bounded(static_cast<int>(hole.h*512.0/ph+0.5),1,512-v);
    draw(device,hole.x,hole.y,hole.w,hole.h,u,v,ul,vl,giranTexture,alpha,1);
    if(!loggedDraw){loggedDraw=true;logLine("DRAW V2: continent covered; Giran polygon revealed through alpha texture. Visual check pending.");}
}
static void paint(void* map,void* device,bool town) {
    // Fail closed on an unexpected client structure instead of crashing further frames.
    __try{paintUnchecked(map,device,town);}
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
    installed=true;logLine("INSTALLED: native world/town map Giran V2 hooks, exact verified client.");
}

using CreateDevice=HRESULT(WINAPI*)(IDirect3D9*,UINT,D3DDEVTYPE,HWND,DWORD,D3DPRESENT_PARAMETERS*,IDirect3DDevice9**);
using Present=HRESULT(WINAPI*)(IDirect3DDevice9*,const RECT*,const RECT*,HWND,const RGNDATA*);
static std::map<void**,CreateDevice> factoryMethods;
static std::map<void**,Present> presentMethods;
static std::mutex methodMutex;
static bool replaceSlot(void** table,int slot,void* replacement) {
    DWORD old;if(!VirtualProtect(table+slot,sizeof(void*),PAGE_READWRITE,&old))return false;
    InterlockedExchangePointer(table+slot,replacement);DWORD unused;VirtualProtect(table+slot,sizeof(void*),old,&unused);return true;
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
        if(!presentMethods.count(table)) {
            auto original=reinterpret_cast<Present>(table[17]);presentMethods.emplace(table,original);
            if(!replaceSlot(table,17,reinterpret_cast<void*>(hookedPresent)))logLine("Present fallback unavailable; map hooks will only install if NWindow was already loaded.");
        }
    }
    return result;
}
static void initialize() {
    wchar_t path[MAX_PATH];GetModuleFileNameW(selfModule,path,MAX_PATH);folder=path;folder=folder.substr(0,folder.find_last_of(L"\\/")+1);configFile=folder+L"NexusMapFog.ini";
    GetSystemDirectoryW(path,MAX_PATH);std::wstring system=std::wstring(path)+L"\\d3d9.dll";realD3D=LoadLibraryW(system.c_str());
    logLine("START map fog Giran V2; native cloud coverage, original D3D9 forwarding.");
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
