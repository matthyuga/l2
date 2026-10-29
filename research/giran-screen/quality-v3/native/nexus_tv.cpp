// Local, opt-in D3D9 relay. Only a texture with the exact Nexus marker is substituted.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <d3d9.h>
#include <vector>
#include <unordered_map>
#include <mutex>
#include <string>
#include <cstring>
#include "nexus_tv.h"

static HMODULE selfModule,realModule;
static std::once_flag initializeOnce;
enum Mode {Off,Source,Viewer};
static Mode mode=Off;
static std::wstring folder;
static std::wstring receiveChannel=nxtv::Channel;
static bool hdChannel=false, dynamicChannel=false;
static HANDLE mapping=nullptr;
static HANDLE sourceMutex=nullptr;
static nxtv::Frame* shared=nullptr;
static std::mutex logMutex;
static void log(const char* message){
 std::lock_guard<std::mutex> guard(logMutex);
 std::wstring path=folder+L"NexusTV.log";
 HANDLE f=CreateFileW(path.c_str(),FILE_APPEND_DATA,FILE_SHARE_READ|FILE_SHARE_WRITE,nullptr,OPEN_ALWAYS,FILE_ATTRIBUTE_NORMAL,nullptr);
 if(f!=INVALID_HANDLE_VALUE){DWORD written;WriteFile(f,message,(DWORD)strlen(message),&written,nullptr);WriteFile(f,"\r\n",2,&written,nullptr);CloseHandle(f);}
}
static void initialize(){
 wchar_t path[MAX_PATH];GetModuleFileNameW(selfModule,path,MAX_PATH);folder=path;folder=folder.substr(0,folder.find_last_of(L"\\/")+1);
 wchar_t value[32];GetPrivateProfileStringW(L"NexusTV",L"Mode",L"off",value,32,(folder+L"NexusTV.ini").c_str());
 if(!_wcsicmp(value,L"source"))mode=Source;else if(!_wcsicmp(value,L"viewer"))mode=Viewer;
 if(mode==Viewer){ wchar_t channel[128]; GetPrivateProfileStringW(L"NexusTV",L"Channel",nxtv::Channel,channel,128,(folder+L"NexusTV.ini").c_str()); if(wcsncmp(channel,L"Local\\NexusGiranTV",18)==0)receiveChannel=channel; hdChannel=receiveChannel==L"Local\\NexusGiranTV_Program_v2"; dynamicChannel=receiveChannel==L"Local\\NexusGiranTV_Program_v3"; }
 GetSystemDirectoryW(path,MAX_PATH);std::wstring system=std::wstring(path)+L"\\d3d9.dll";realModule=LoadLibraryW(system.c_str());
 log(mode==Source?"START source":mode==Viewer?"START viewer":"START passthrough");
}
static bool connectChannel(){
 if(shared)return true;
 if(mode==Source){
  if(!sourceMutex){
   sourceMutex=CreateMutexW(nullptr,FALSE,L"Local\\NexusGiranTV_Source_v1");
   if(!sourceMutex)return false;
   DWORD result=WaitForSingleObject(sourceMutex,0);
   if(result!=WAIT_OBJECT_0&&result!=WAIT_ABANDONED){CloseHandle(sourceMutex);sourceMutex=nullptr;return false;}
  }
  mapping=CreateFileMappingW(INVALID_HANDLE_VALUE,nullptr,PAGE_READWRITE,0,sizeof(nxtv::Frame),nxtv::Channel);
 }
 else if(mode==Viewer)mapping=OpenFileMappingW(FILE_MAP_READ,FALSE,receiveChannel.c_str());
 if(!mapping)return false;
 shared=(nxtv::Frame*)MapViewOfFile(mapping,mode==Source?FILE_MAP_ALL_ACCESS:FILE_MAP_READ,0,0,dynamicChannel?24+3840*2880*4:hdChannel?24+1280*960*4:sizeof(nxtv::Frame));
 if(!shared){CloseHandle(mapping);mapping=nullptr;return false;}
 return true;
}
using CreateDeviceFn=HRESULT(WINAPI*)(IDirect3D9*,UINT,D3DDEVTYPE,HWND,DWORD,D3DPRESENT_PARAMETERS*,IDirect3DDevice9**);
using PresentFn=HRESULT(WINAPI*)(IDirect3DDevice9*,const RECT*,const RECT*,HWND,const RGNDATA*);
using ResetFn=HRESULT(WINAPI*)(IDirect3DDevice9*,D3DPRESENT_PARAMETERS*);
using SetTextureFn=HRESULT(WINAPI*)(IDirect3DDevice9*,DWORD,IDirect3DBaseTexture9*);
struct DeviceState {
 void** table;PresentFn present;ResetFn reset;SetTextureFn setTexture;
 IDirect3DSurface9* captureTarget=nullptr;IDirect3DSurface9* cpu=nullptr;
 IDirect3DTexture9* selected=nullptr;IDirect3DTexture9* live=nullptr;
 std::unordered_map<IDirect3DBaseTexture9*,ULONGLONG> examined;
 std::vector<DWORD> pixels; UINT liveWidth=0,liveHeight=0;
 UINT textureSize=512; ULONGLONG lastCapture=0,lastFresh=0;LONG lastSequence=-1;bool firstFrame=false,errorLogged=false;
 void clear(){
  if(captureTarget){captureTarget->Release();captureTarget=nullptr;}if(cpu){cpu->Release();cpu=nullptr;}
  if(selected){selected->Release();selected=nullptr;}if(live){live->Release();live=nullptr;}
  examined.clear();lastSequence=-1;lastFresh=0;liveWidth=liveHeight=0;
 }
};
static std::unordered_map<IDirect3DDevice9*,DeviceState*> devices;
static std::unordered_map<void**,CreateDeviceFn> factories;
struct DeviceMethods {PresentFn present;ResetFn reset;SetTextureFn setTexture;};
static std::unordered_map<void**,DeviceMethods> originalMethods;
static std::mutex stateMutex;
static DeviceState* state(IDirect3DDevice9* d){std::lock_guard<std::mutex> lock(stateMutex);auto i=devices.find(d);return i==devices.end()?nullptr:i->second;}
static DeviceMethods methods(IDirect3DDevice9* d){std::lock_guard<std::mutex> lock(stateMutex);auto i=originalMethods.find(*(void***)d);return i==originalMethods.end()?DeviceMethods{}:i->second;}
static void replaceSlot(void** table,UINT slot,void* replacement){
 DWORD protection;if(!VirtualProtect(table+slot,sizeof(void*),PAGE_READWRITE,&protection))return;
 InterlockedExchangePointer(table+slot,replacement);
 DWORD unused;VirtualProtect(table+slot,sizeof(void*),protection,&unused);
}

static void capture(IDirect3DDevice9* d,DeviceState& s){
 ULONGLONG now=GetTickCount64();if(now-s.lastCapture<100)return;s.lastCapture=now;
 if(!connectChannel())return;
 IDirect3DSurface9* back=nullptr;HRESULT hr=d->GetBackBuffer(0,0,D3DBACKBUFFER_TYPE_MONO,&back);
 if(FAILED(hr))return;
 if(!s.captureTarget)hr=d->CreateRenderTarget(nxtv::Width,nxtv::Height,D3DFMT_X8R8G8B8,D3DMULTISAMPLE_NONE,0,FALSE,&s.captureTarget,nullptr);
 if(SUCCEEDED(hr)&&!s.cpu)hr=d->CreateOffscreenPlainSurface(nxtv::Width,nxtv::Height,D3DFMT_X8R8G8B8,D3DPOOL_SYSTEMMEM,&s.cpu,nullptr);
 if(SUCCEEDED(hr))hr=d->StretchRect(back,nullptr,s.captureTarget,nullptr,D3DTEXF_LINEAR);
 back->Release();
 if(SUCCEEDED(hr))hr=d->GetRenderTargetData(s.captureTarget,s.cpu);
 D3DLOCKED_RECT rect{};if(SUCCEEDED(hr))hr=s.cpu->LockRect(&rect,nullptr,D3DLOCK_READONLY);
 if(FAILED(hr)){if(!s.errorLogged){char msg[100];sprintf_s(msg,"CAPTURE ERROR 0x%08lx",hr);log(msg);s.errorLogged=true;}return;}
 InterlockedIncrement(&shared->sequence);MemoryBarrier();
 shared->magic=nxtv::Magic;shared->width=nxtv::Width;shared->height=nxtv::Height;shared->tick=now;
 for(UINT y=0;y<nxtv::Height;y++){
  auto src=(DWORD*)((BYTE*)rect.pBits+y*rect.Pitch);auto dst=shared->pixels+y*nxtv::Width;
  for(UINT x=0;x<nxtv::Width;x++)dst[x]=src[x]|0xff000000;
 }
 MemoryBarrier();InterlockedIncrement(&shared->sequence);s.cpu->UnlockRect();
 if(!s.firstFrame){log("PUBLISHED FIRST FRAME 512x384");s.firstFrame=true;}
}
static bool readFrame(DeviceState& s){
 if(!connectChannel())return false;
 const DWORD magic=dynamicChannel?0x3356544e:hdChannel?0x3256544e:nxtv::Magic;
 for(int attempt=0;attempt<3;attempt++){
  LONG seq=shared->sequence;if(seq&1)continue;
  MemoryBarrier();const UINT width=shared->width,height=shared->height;ULONGLONG tick=shared->tick;
  if(shared->magic!=magic||!width||!height||width>3840||height>2880||GetTickCount64()-tick>3000)return false;
  if(!dynamicChannel&&((width!=(hdChannel?1280:512))||(height!=(hdChannel?960:384))||s.textureSize<width))return false;
  if(seq==s.lastSequence){s.lastFresh=tick;return true;}
  s.pixels.resize((size_t)width*height);memcpy(s.pixels.data(),shared->pixels,(size_t)width*height*4);MemoryBarrier();
  if(seq!=shared->sequence)continue;
  if(dynamicChannel&&(!s.live||s.liveWidth!=width||s.liveHeight!=height)){
   IDirect3DDevice9* d=nullptr;s.selected->GetDevice(&d);if(!d)return false;
   IDirect3DTexture9* replacement=nullptr;
   HRESULT hr=d->CreateTexture(width,height,1,0,D3DFMT_A8R8G8B8,D3DPOOL_MANAGED,&replacement,nullptr);d->Release();
   if(FAILED(hr)){if(!s.errorLogged){log("UNSUPPORTED LIVE TEXTURE SIZE");s.errorLogged=true;}return false;}
   if(s.live)s.live->Release();s.live=replacement;s.liveWidth=width;s.liveHeight=height;
   char line[100];sprintf_s(line,"LIVE TEXTURE %ux%u",width,height);log(line);
  }
  RECT region{0,0,(LONG)width,(LONG)height};D3DLOCKED_RECT locked{};
  if(!s.live||FAILED(s.live->LockRect(0,&locked,&region,0)))return false;
  for(UINT y=0;y<height;y++)memcpy((BYTE*)locked.pBits+y*locked.Pitch,s.pixels.data()+y*width,width*4);
  s.live->UnlockRect(0);s.lastSequence=seq;s.lastFresh=tick;
  if(!s.firstFrame){log("RECEIVED PROGRAM FRAME");s.firstFrame=true;}
  return true;
 }
 return false;
}
static bool identify(IDirect3DDevice9* d,DeviceState& s,IDirect3DBaseTexture9* base){
 if(!base||base->GetType()!=D3DRTYPE_TEXTURE)return false;
 auto texture=static_cast<IDirect3DTexture9*>(base);D3DSURFACE_DESC desc{};
 if(FAILED(texture->GetLevelDesc(0,&desc))||(desc.Width!=512&&desc.Width!=2048)||desc.Height!=desc.Width)return false;
 if(desc.Format!=D3DFMT_A8R8G8B8&&desc.Format!=D3DFMT_X8R8G8B8)return false;
 ULONGLONG now=GetTickCount64();auto i=s.examined.find(base);if(i!=s.examined.end()&&now-i->second<1000)return false;s.examined[base]=now;
 D3DLOCKED_RECT rect{};if(FAILED(texture->LockRect(0,&rect,nullptr,D3DLOCK_READONLY)))return false;
 bool match=true;auto row=(DWORD*)rect.pBits;
 for(UINT x=0;x<8;x++)if((row[x]&0xffffff)!=(nxtv::Marker[x]&0xffffff))match=false;
 texture->UnlockRect(0);if(!match)return false;
 if(!dynamicChannel&&FAILED(d->CreateTexture(desc.Width,desc.Height,1,0,D3DFMT_A8R8G8B8,D3DPOOL_MANAGED,&s.live,nullptr)))return false;
 s.textureSize=desc.Width; s.selected=texture;s.selected->AddRef();log("MATCHED NEXUS SCREEN TEXTURE");readFrame(s);return true;
}
static HRESULT WINAPI hookedSetTexture(IDirect3DDevice9* d,DWORD stage,IDirect3DBaseTexture9* texture){
 DeviceState* s=state(d);if(!s){auto f=methods(d).setTexture;return f?f(d,stage,texture):D3DERR_INVALIDCALL;}
 if(mode==Viewer){
  if(!s->selected)identify(d,*s,texture);
  if(texture&&texture==s->selected&&s->live&&s->lastFresh&&GetTickCount64()-s->lastFresh<3000)texture=s->live;
 }
 return s->setTexture(d,stage,texture);
}
static HRESULT WINAPI hookedPresent(IDirect3DDevice9* d,const RECT* src,const RECT* dst,HWND window,const RGNDATA* dirty){
 DeviceState* s=state(d);if(!s){auto f=methods(d).present;return f?f(d,src,dst,window,dirty):D3DERR_INVALIDCALL;}
 if(mode==Source)capture(d,*s);else if(mode==Viewer&&s->selected)readFrame(*s);
 return s->present(d,src,dst,window,dirty);
}
static HRESULT WINAPI hookedReset(IDirect3DDevice9* d,D3DPRESENT_PARAMETERS* params){
 DeviceState* s=state(d);if(!s){auto f=methods(d).reset;return f?f(d,params):D3DERR_INVALIDCALL;}s->clear();return s->reset(d,params);
}
static HRESULT WINAPI hookedCreateDevice(IDirect3D9* factory,UINT adapter,D3DDEVTYPE type,HWND window,DWORD flags,D3DPRESENT_PARAMETERS* params,IDirect3DDevice9** device){
 CreateDeviceFn create;{std::lock_guard<std::mutex> lock(stateMutex);create=factories.at(*(void***)factory);}
 log("CREATE DEVICE ENTER"); HRESULT hr=create(factory,adapter,type,window,flags,params,device); if(FAILED(hr)){ char msg[80]; wsprintfA(msg,"CREATE DEVICE FAILED %08lx",(unsigned long)hr); log(msg); return hr; } if(mode==Off)return hr;
 auto s=new DeviceState();auto original=*(void***)(*device);s->table=original;
 {std::lock_guard<std::mutex> lock(stateMutex);
  auto entry=originalMethods.find(original);
  if(entry==originalMethods.end())entry=originalMethods.emplace(original,DeviceMethods{(PresentFn)original[17],(ResetFn)original[16],(SetTextureFn)original[65]}).first;
  s->present=entry->second.present;s->reset=entry->second.reset;s->setTexture=entry->second.setTexture;devices[*device]=s;
 }
 replaceSlot(original,16,(void*)hookedReset);replaceSlot(original,17,(void*)hookedPresent);replaceSlot(original,65,(void*)hookedSetTexture);
 if(window)SetWindowTextW(window,mode==Source?L"Lineage II | NexusCam - TRANSMISION":L"Lineage II | Pantalla Giran - ESPECTADOR");
 log("D3D9 DEVICE READY");return hr;
}
extern "C" IDirect3D9* WINAPI NexusDirect3DCreate9(UINT version){
 std::call_once(initializeOnce,initialize);if(!realModule)return nullptr;
 using Fn=IDirect3D9*(WINAPI*)(UINT);auto fn=(Fn)GetProcAddress(realModule,"Direct3DCreate9");if(!fn)return nullptr;
 log("CREATE FACTORY ENTER"); IDirect3D9* factory=fn(version); log(factory?"CREATE FACTORY OK":"CREATE FACTORY FAILED"); if(!factory||mode==Off)return factory;
 auto original=*(void***)factory;
 {std::lock_guard<std::mutex> lock(stateMutex);if(!factories.count(original))factories[original]=(CreateDeviceFn)original[16];}
 replaceSlot(original,16,(void*)hookedCreateDevice);return factory;
}
BOOL WINAPI DllMain(HINSTANCE module,DWORD reason,LPVOID){if(reason==DLL_PROCESS_ATTACH){selfModule=module;DisableThreadLibraryCalls(module);}return TRUE;}
