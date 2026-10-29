#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <d3d9.h>
#include <cstdio>
#include <string>
#include "nexus_tv.h"
struct Vertex {float x,y,z,rhw,u,v;};
int wmain(int argc,wchar_t** argv){
 if(argc!=4)return 2;
 bool program=!_wcsicmp(argv[1],L"program"); bool source=!_wcsicmp(argv[1],L"source");bool offline=!_wcsicmp(argv[1],L"offline");bool unmarked=!_wcsicmp(argv[1],L"unmarked");
 WNDCLASSW wc{};wc.lpfnWndProc=DefWindowProcW;wc.hInstance=GetModuleHandleW(nullptr);wc.lpszClassName=L"NexusRelayNativeTest";RegisterClassW(&wc);
 HWND window=CreateWindowW(wc.lpszClassName,L"Nexus relay automated graphics test",WS_OVERLAPPEDWINDOW,0,0,640,480,nullptr,nullptr,wc.hInstance,nullptr);
 HMODULE proxy=LoadLibraryW(argv[2]);if(!proxy)return 3;
 using CreateFn=IDirect3D9*(WINAPI*)(UINT);auto create=(CreateFn)GetProcAddress(proxy,"Direct3DCreate9");if(!create)return 4;
 IDirect3D9* factory=create(D3D_SDK_VERSION);if(!factory)return 5;
 D3DPRESENT_PARAMETERS pp{};pp.Windowed=TRUE;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.BackBufferWidth=512;pp.BackBufferHeight=384;pp.BackBufferFormat=D3DFMT_X8R8G8B8;pp.hDeviceWindow=window;pp.PresentationInterval=D3DPRESENT_INTERVAL_IMMEDIATE;
 IDirect3DDevice9* device=nullptr;HRESULT hr=factory->CreateDevice(D3DADAPTER_DEFAULT,D3DDEVTYPE_HAL,window,D3DCREATE_SOFTWARE_VERTEXPROCESSING,&pp,&device);
 if(FAILED(hr))return 6;
 IDirect3DTexture9* texture=nullptr;IDirect3DSurface9* cpu=nullptr;
 if(!source){
  hr=device->CreateTexture(512,512,1,0,D3DFMT_A8R8G8B8,D3DPOOL_MANAGED,&texture,nullptr);if(FAILED(hr))return 7;
  D3DLOCKED_RECT r{};texture->LockRect(0,&r,nullptr,0);
  for(UINT y=0;y<512;y++){auto row=(DWORD*)((BYTE*)r.pBits+y*r.Pitch);for(UINT x=0;x<512;x++)row[x]=0xff101820;}
  if(!unmarked)memcpy(r.pBits,nxtv::Marker,sizeof(nxtv::Marker));texture->UnlockRect(0);
  device->CreateOffscreenPlainSurface(512,384,D3DFMT_X8R8G8B8,D3DPOOL_SYSTEMMEM,&cpu,nullptr);
  device->SetFVF(D3DFVF_XYZRHW|D3DFVF_TEX1);device->SetRenderState(D3DRS_LIGHTING,FALSE);device->SetRenderState(D3DRS_CULLMODE,D3DCULL_NONE);
  device->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_SELECTARG1);device->SetTextureStageState(0,D3DTSS_COLORARG1,D3DTA_TEXTURE);
 }
 HANDLE feed=program?OpenFileMappingW(FILE_MAP_READ,FALSE,L"Local\\NexusGiranTV_Program_v1"):nullptr; auto programFrame=feed?(nxtv::Frame*)MapViewOfFile(feed,FILE_MAP_READ,0,0,sizeof(nxtv::Frame)):nullptr;
 DWORD pixel=0;unsigned int correct=0,phaseA=0,phaseB=0;const DWORD expected=(offline||unmarked)?0x00101820:0x00129be7;
 for(int frame=0;frame<(source?600:180);frame++){
  MSG msg;while(PeekMessageW(&msg,nullptr,0,0,PM_REMOVE)){TranslateMessage(&msg);DispatchMessageW(&msg);}
  device->Clear(0,nullptr,D3DCLEAR_TARGET,source?(frame<60?0xff129be7:0xffc5426a):0xff000000,1,0);
  if(!source){
   device->BeginScene();device->SetTexture(0,texture);
   Vertex quad[]={{-.5f,-.5f,0,1,0,0},{511.5f,-.5f,0,1,1,0},{-.5f,383.5f,0,1,0,.75f},{511.5f,383.5f,0,1,1,.75f}};
   device->DrawPrimitiveUP(D3DPT_TRIANGLESTRIP,2,quad,sizeof(Vertex));device->EndScene();
   IDirect3DSurface9* back=nullptr;device->GetBackBuffer(0,0,D3DBACKBUFFER_TYPE_MONO,&back);
   if(SUCCEEDED(device->GetRenderTargetData(back,cpu))){D3DLOCKED_RECT r{};if(SUCCEEDED(cpu->LockRect(&r,nullptr,D3DLOCK_READONLY))){pixel=*((DWORD*)((BYTE*)r.pBits+192*r.Pitch)+256);DWORD rgb=pixel&0xffffff;if(program?(programFrame&&GetTickCount64()-programFrame->tick<3000&&rgb==(programFrame->pixels[192*512+256]&0xffffff)):(rgb==expected||(!offline&&!unmarked&&rgb==0x00c5426a)))correct++;if(rgb==0x00129be7)phaseA++;if(rgb==0x00c5426a)phaseB++;cpu->UnlockRect();}}
   back->Release();
  }
  hr=device->Present(nullptr,nullptr,nullptr,nullptr);if(FAILED(hr))break;Sleep(16);
 }
 FILE* report=nullptr;_wfopen_s(&report,argv[3],L"w");if(report){fprintf(report,"{\"source\":%s,\"correct_frames\":%u,\"phase_a\":%u,\"phase_b\":%u,\"last_pixel\":\"%08lx\",\"present_hresult\":\"%08lx\"}\n",source?"true":"false",correct,phaseA,phaseB,pixel,hr);fclose(report);}
 if(cpu)cpu->Release();if(texture)texture->Release();device->Release();factory->Release();DestroyWindow(window);
 return source?0:(correct>100&&(offline||unmarked||program||(phaseA>5&&phaseB>30)))?0:8;
}
