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
#include "native_texture_identity.h"
#include "fog_draw_state.h"

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
static bool matchesHash(HMODULE module,bool driver=false) {
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
    static const unsigned char expected[32]={0xa4,0xde,0x43,0xd5,0xd3,0x12,0x41,0xda,0xae,0x7d,0xac,0x07,0x21,0x34,0xc0,0x11,0xab,0xdd,0x03,0x6b,0x0d,0x1e,0xe2,0x91,0xee,0xad,0x0b,0xb5,0xe9,0xc6,0xca,0x7d};
    static const unsigned char driverExpected[32]={0x2b,0x49,0x6d,0x23,0x5c,0xca,0x52,0x9b,0x61,0x80,0x58,0x8a,0x98,0x7c,0xa0,0x05,0x96,0x00,0xa2,0x32,0x31,0x93,0xd9,0x6e,0x87,0xb9,0x00,0x14,0x10,0x5b,0xe0,0xc2};
    return ok&&!memcmp(digest,driver?driverExpected:expected,32);
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
using UpdateTexture=HRESULT(WINAPI*)(IDirect3DDevice9*,IDirect3DBaseTexture9*,IDirect3DBaseTexture9*);
using Reset=HRESULT(WINAPI*)(IDirect3DDevice9*,D3DPRESENT_PARAMETERS*);
using Present=HRESULT(WINAPI*)(IDirect3DDevice9*,const RECT*,const RECT*,HWND,const RGNDATA*);
static std::map<void**,CreateDevice> factoryMethods;
static std::map<void**,Present> presentMethods;
static std::map<void**,SetTexture> textureMethods;
static std::map<void**,UpdateTexture> uploadMethods;
static std::map<void**,Reset> resetMethods;
static std::map<IDirect3DDevice9*,walking::Device*> graphics;
static std::mutex methodMutex;
using Primitive=HRESULT(WINAPI*)(IDirect3DDevice9*,D3DPRIMITIVETYPE,UINT,UINT);
using Indexed=HRESULT(WINAPI*)(IDirect3DDevice9*,D3DPRIMITIVETYPE,INT,UINT,UINT,UINT,UINT);
using PrimitiveUP=HRESULT(WINAPI*)(IDirect3DDevice9*,D3DPRIMITIVETYPE,UINT,const void*,UINT);
using IndexedUP=HRESULT(WINAPI*)(IDirect3DDevice9*,D3DPRIMITIVETYPE,UINT,UINT,UINT,const void*,D3DFORMAT,const void*,UINT);
static std::map<void**,Primitive> primitiveMethods;static std::map<void**,Indexed> indexedMethods;
static std::map<void**,PrimitiveUP> primitiveUPMethods;static std::map<void**,IndexedUP> indexedUPMethods;
static IDirect3DTexture9* activeAtlas(IDirect3DDevice9* device){std::lock_guard<std::mutex> lock(methodMutex);auto d=graphics.find(device);return d==graphics.end()?nullptr:d->second->live;}
static void refreshAtlasBeforeDraw(IDirect3DDevice9* device,IDirect3DTexture9* atlas){
    walking::Device* state=nullptr;
    {std::lock_guard<std::mutex> lock(methodMutex);auto d=graphics.find(device);if(d!=graphics.end())state=d->second;}
    if(!state||state->live!=atlas)return;
    // A native cache can retain our substituted atlas indefinitely. In that
    // case SetTexture no longer sees the original marker, and the renderer can
    // present through a swap chain instead of IDirect3DDevice9::Present.
    // Refresh only at an actual fog draw, not for unrelated world geometry.
    // Unchanged snapshots are a cheap no-op.
    auto before=state->built;walking::update(device,*state);
    if(state->built!=before)logLine("UPDATED V7 exploration atlas before draw; new discoveries visible without texture rebinding.");
}
static void reportDraw(fogNative::FogDrawState& guard){static bool logged=false;if(guard.saved&&!logged){logged=true;char line[140];sprintf_s(line,"DRAW V6 atlas alpha; native blend=%lu alphaOp=%lu; restored after draw.",guard.priorBlend,guard.priorAlphaOp);logLine(line);}}
static HRESULT WINAPI hookedPrimitive(IDirect3DDevice9* d,D3DPRIMITIVETYPE t,UINT s,UINT n){auto fn=primitiveMethods[*reinterpret_cast<void***>(d)];fogNative::FogDrawState guard(d,activeAtlas(d),refreshAtlasBeforeDraw);reportDraw(guard);return fn(d,t,s,n);}
static HRESULT WINAPI hookedIndexed(IDirect3DDevice9* d,D3DPRIMITIVETYPE t,INT b,UINT m,UINT v,UINT s,UINT n){auto fn=indexedMethods[*reinterpret_cast<void***>(d)];fogNative::FogDrawState guard(d,activeAtlas(d),refreshAtlasBeforeDraw);reportDraw(guard);return fn(d,t,b,m,v,s,n);}
static HRESULT WINAPI hookedPrimitiveUP(IDirect3DDevice9* d,D3DPRIMITIVETYPE t,UINT n,const void* v,UINT stride){auto fn=primitiveUPMethods[*reinterpret_cast<void***>(d)];fogNative::FogDrawState guard(d,activeAtlas(d),refreshAtlasBeforeDraw);reportDraw(guard);return fn(d,t,n,v,stride);}
static HRESULT WINAPI hookedIndexedUP(IDirect3DDevice9* d,D3DPRIMITIVETYPE t,UINT m,UINT v,UINT n,const void* idx,D3DFORMAT f,const void* data,UINT stride){auto fn=indexedUPMethods[*reinterpret_cast<void***>(d)];fogNative::FogDrawState guard(d,activeAtlas(d),refreshAtlasBeforeDraw);reportDraw(guard);return fn(d,t,m,v,n,idx,f,data,stride);}
using NativeCache=int(__thiscall*)(void*,void*,void*);
static NativeCache originalCache=nullptr;
static EntryDetour cacheDetour;
static bool cacheRejected=false;
static bool isFogSource(void* source) {
    if(!source||!atlasMaterial)return false;
    return fogNative::materialOf(source)==atlasMaterial;
}
static void selectNativeTexture(void* cache,void* source) {
    if(!isFogSource(source))return;
    auto gpu=fogNative::gpuOf(cache);
    if(!gpu)return;
    IDirect3DDevice9* device=nullptr;if(FAILED(gpu->GetDevice(&device)))return;
    walking::Device* state=nullptr;
    {std::lock_guard<std::mutex> lock(methodMutex);auto d=graphics.find(device);if(d!=graphics.end())state=d->second;}
    if(state&&state->selected!=gpu){
        if(state->selected)state->selected->Release();state->selected=gpu;gpu->AddRef();walking::update(device,*state);
        D3DSURFACE_DESC desc{};gpu->GetLevelDesc(0,&desc);char line[160];sprintf_s(line,"MATCHED V6 native UTexture identity; GPU=%ux%u format=%u pool=%u; exploration atlas enabled.",desc.Width,desc.Height,static_cast<unsigned>(desc.Format),static_cast<unsigned>(desc.Pool));logLine(line);
    }
    if(state&&fogNative::wireAtlas(cache,state->live))logLine("WIRED V6 exploration atlas into verified native fog texture cache.");
    device->Release();
}
static int __fastcall hookedCache(void* self,void*,void* source,void* output) {
    int result=originalCache(self,source,output);
    __try{selectNativeTexture(self,source);}__except(EXCEPTION_EXECUTE_HANDLER){logLine("V6 native cache inspection failed; original cache preserved.");}
    return result;
}
static void maybeInstallCache() {
    if(originalCache||cacheRejected)return;HMODULE module=GetModuleHandleW(L"D3DDrv.dll");if(!module)return;
    if(!matchesHash(module,true)){cacheRejected=true;logLine("REJECTED V6 native cache: D3DDrv.dll SHA256 differs.");return;}
    if(!cacheDetour.install(reinterpret_cast<unsigned char*>(module)+0x32ac0,reinterpret_cast<void*>(hookedCache),true)){cacheRejected=true;logLine("REJECTED V6 native cache: verified prologue mismatch.");return;}
    originalCache=reinterpret_cast<NativeCache>(cacheDetour.trampoline);logLine("INSTALLED V6 native texture identity hook.");
}
static bool replaceSlot(void** table,int slot,void* replacement) {
    DWORD old;if(!VirtualProtect(table+slot,sizeof(void*),PAGE_READWRITE,&old))return false;
    InterlockedExchangePointer(table+slot,replacement);DWORD unused;VirtualProtect(table+slot,sizeof(void*),old,&unused);return true;
}
static HRESULT WINAPI hookedUpdateTexture(IDirect3DDevice9* device,IDirect3DBaseTexture9* source,IDirect3DBaseTexture9* destination) {
    UpdateTexture original=nullptr;walking::Device* state=nullptr;
    {std::lock_guard<std::mutex> lock(methodMutex);auto table=*reinterpret_cast<void***>(device);auto it=uploadMethods.find(table);if(it!=uploadMethods.end())original=it->second;auto d=graphics.find(device);if(d!=graphics.end())state=d->second;}
    if(!original)return D3DERR_INVALIDCALL;
    HRESULT result=original(device,source,destination);
    if(SUCCEEDED(result)&&state&&walking::uploaded(device,*state,source,destination))logLine("MATCHED V6 overlay at system-memory upload; GPU atlas enabled.");
    return result;
}
static HRESULT WINAPI hookedSetTexture(IDirect3DDevice9* device,DWORD stage,IDirect3DBaseTexture9* texture) {
    SetTexture original=nullptr;walking::Device* state=nullptr;
    {std::lock_guard<std::mutex> lock(methodMutex);auto table=*reinterpret_cast<void***>(device);auto it=textureMethods.find(table);if(it!=textureMethods.end())original=it->second;auto d=graphics.find(device);if(d!=graphics.end())state=d->second;}
    if(!original)return D3DERR_INVALIDCALL;
    if(state){if(!state->selected&&walking::identify(device,*state,texture))logLine("MATCHED V4 overlay; dynamic exploration atlas enabled.");
        if(texture&&texture==state->selected){walking::update(device,*state);if(state->live){texture=state->live;static bool reported=false;if(!reported){reported=true;logLine("BOUND V6 dynamic exploration atlas in SetTexture.");}}}}
    return original(device,stage,texture);
}
static HRESULT WINAPI hookedReset(IDirect3DDevice9* device,D3DPRESENT_PARAMETERS* params) {
    Reset original=nullptr;
    {std::lock_guard<std::mutex> lock(methodMutex);auto it=resetMethods.find(*reinterpret_cast<void***>(device));if(it!=resetMethods.end())original=it->second;auto d=graphics.find(device);if(d!=graphics.end())d->second->clear();}
    return original?original(device,params):D3DERR_INVALIDCALL;
}
static HRESULT WINAPI hookedPresent(IDirect3DDevice9* device,const RECT* src,const RECT* dst,HWND window,const RGNDATA* dirty) {
    maybeInstall();maybeInstallCache();Present fn=nullptr;walking::Device* state=nullptr;
    {std::lock_guard<std::mutex> lock(methodMutex);auto it=presentMethods.find(*reinterpret_cast<void***>(device));if(it!=presentMethods.end())fn=it->second;auto d=graphics.find(device);if(d!=graphics.end())state=d->second;}
    // The engine can retain a texture binding across frames. Refresh the atlas
    // even when it has no reason to issue another SetTexture call.
    if(state&&state->selected){auto before=state->built;walking::update(device,*state);if(state->built!=before)logLine("UPDATED V6 exploration atlas at Present.");}
    return fn?fn(device,src,dst,window,dirty):D3DERR_INVALIDCALL;
}
static HRESULT WINAPI hookedCreateDevice(IDirect3D9* factory,UINT adapter,D3DDEVTYPE type,HWND window,DWORD flags,D3DPRESENT_PARAMETERS* params,IDirect3DDevice9** output) {
    maybeInstallCache();
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
            uploadMethods.emplace(table,reinterpret_cast<UpdateTexture>(table[31]));replaceSlot(table,31,reinterpret_cast<void*>(hookedUpdateTexture));
            primitiveMethods.emplace(table,reinterpret_cast<Primitive>(table[81]));indexedMethods.emplace(table,reinterpret_cast<Indexed>(table[82]));
            primitiveUPMethods.emplace(table,reinterpret_cast<PrimitiveUP>(table[83]));indexedUPMethods.emplace(table,reinterpret_cast<IndexedUP>(table[84]));
            replaceSlot(table,81,reinterpret_cast<void*>(hookedPrimitive));replaceSlot(table,82,reinterpret_cast<void*>(hookedIndexed));
            replaceSlot(table,83,reinterpret_cast<void*>(hookedPrimitiveUP));replaceSlot(table,84,reinterpret_cast<void*>(hookedIndexedUP));
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
    logLine("START map fog V7; draw-time refresh of personal/global exploration.");
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
