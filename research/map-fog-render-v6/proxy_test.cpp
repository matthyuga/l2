#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <d3d9.h>
#include <cstdio>
#include "native_texture_identity.h"
int wmain(int argc,wchar_t** argv) {
    if(argc!=2&&argc!=3)return 2;
    bool staged=argc==3;
    HMODULE dll=LoadLibraryW(argv[1]);if(!dll){printf("FAIL LoadLibrary %lu\n",GetLastError());return 3;}
    using Factory=IDirect3D9*(WINAPI*)(UINT);
    auto create=reinterpret_cast<Factory>(GetProcAddress(dll,"Direct3DCreate9"));if(!create)return 4;
    IDirect3D9* api=create(D3D_SDK_VERSION);if(!api)return 5;
    HWND window=CreateWindowExW(0,L"STATIC",L"Fog proxy smoke test",WS_POPUP,0,0,320,240,nullptr,nullptr,GetModuleHandleW(nullptr),nullptr);
    if(!window)return 6;
    D3DPRESENT_PARAMETERS p={};p.Windowed=TRUE;p.SwapEffect=D3DSWAPEFFECT_DISCARD;p.hDeviceWindow=window;p.BackBufferWidth=320;p.BackBufferHeight=240;
    IDirect3DDevice9* device=nullptr;
    HRESULT hr=api->CreateDevice(D3DADAPTER_DEFAULT,D3DDEVTYPE_HAL,window,D3DCREATE_SOFTWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&p,&device);
    if(FAILED(hr)){printf("FAIL CreateDevice %08lx\n",static_cast<unsigned long>(hr));return 7;}
    IDirect3DTexture9* marker=nullptr;
    if(FAILED(device->CreateTexture(16,16,1,0,D3DFMT_A8R8G8B8,staged?D3DPOOL_SYSTEMMEM:D3DPOOL_MANAGED,&marker,nullptr)))return 9;
    D3DLOCKED_RECT locked{};if(FAILED(marker->LockRect(0,&locked,nullptr,0)))return 10;
    const DWORD signature[8]={0xff214365,0xffa31572,0xff7832c1,0xff09b4e2,0xffa1c307,0xff4421d7,0xffc35b19,0xff73a28d};
    for(int y=0;y<16;++y){auto row=reinterpret_cast<DWORD*>(static_cast<unsigned char*>(locked.pBits)+y*locked.Pitch);for(int x=0;x<16;++x)row[x]=0xff3e4850;if(!y)for(int x=0;x<8;++x)row[x]=signature[x];}
    marker->UnlockRect(0);
    if(staged){IDirect3DTexture9* gpu=nullptr;if(FAILED(device->CreateTexture(16,16,1,0,D3DFMT_A8R8G8B8,D3DPOOL_DEFAULT,&gpu,nullptr)))return 16;
        if(FAILED(device->UpdateTexture(marker,gpu)))return 17;marker->Release();marker=gpu;}
    if(FAILED(device->SetTexture(0,marker)))return 11;
    IDirect3DBaseTexture9* bound=nullptr;device->GetTexture(0,&bound);
    if(!bound||bound==marker){printf("FAIL dynamic atlas not substituted\n");return 12;}
    auto atlas=static_cast<IDirect3DTexture9*>(bound);D3DSURFACE_DESC desc{};atlas->GetLevelDesc(0,&desc);
    if(desc.Width!=1024||desc.Height!=2048)return 13;
    if(FAILED(atlas->LockRect(0,&locked,nullptr,D3DLOCK_READONLY)))return 14;
    constexpr double scale=.0050048828125;
    int gx=static_cast<int>((83400+131072)*scale/2048*1024),gy=static_cast<int>((147800+262144)*scale/3072*2048);
    auto row=reinterpret_cast<DWORD*>(static_cast<unsigned char*>(locked.pBits)+gy*locked.Pitch);
    bool clearGiran=(row[gx]>>24)==0;
    row=static_cast<DWORD*>(locked.pBits);bool opaqueUnknown=(row[0]>>24)==255;
    atlas->UnlockRect(0);
    unsigned char nativeCache[64]{};marker->AddRef();*reinterpret_cast<IDirect3DTexture9**>(nativeCache+0x38)=marker;
    if(!fogNative::wireAtlas(nativeCache,atlas)||fogNative::gpuOf(nativeCache)!=atlas||fogNative::wireAtlas(nativeCache,atlas))return 24;
    device->SetTexture(0,fogNative::gpuOf(nativeCache));fogNative::gpuOf(nativeCache)->Release();bound->Release();
    if(!clearGiran||!opaqueUnknown){printf("FAIL atlas alpha Giran=%d unknown=%d\n",clearGiran,opaqueUnknown);return 15;}
    // Verify final framebuffer pixels even when the source material selected an
    // opaque pipeline. Checking the texture's alpha alone misses this failure.
    struct Vertex {float x,y,z,rhw;DWORD color;float u,v;};
    for(int pass=0;pass<2;++pass){
        float u=pass?0.0f:static_cast<float>((83400+131072)*scale/2048),v=pass?0.0f:static_cast<float>((147800+262144)*scale/3072);
        Vertex quad[4]={{0,0,0,1,0xffffffff,u,v},{32,0,0,1,0xffffffff,u,v},{0,32,0,1,0xffffffff,u,v},{32,32,0,1,0xffffffff,u,v}};
        device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff208020,1,0);device->SetRenderState(D3DRS_ZENABLE,FALSE);
        device->SetRenderState(D3DRS_ALPHABLENDENABLE,FALSE);device->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_SELECTARG2);device->SetTextureStageState(0,D3DTSS_ALPHAARG2,D3DTA_DIFFUSE);
        device->SetFVF(D3DFVF_XYZRHW|D3DFVF_DIFFUSE|D3DFVF_TEX1);device->BeginScene();
        HRESULT drawn=device->DrawPrimitiveUP(D3DPT_TRIANGLESTRIP,2,quad,sizeof(Vertex));device->EndScene();if(FAILED(drawn))return 18;
        DWORD restored=TRUE;device->GetRenderState(D3DRS_ALPHABLENDENABLE,&restored);if(restored!=FALSE)return 19;
        IDirect3DSurface9* rt=nullptr;device->GetRenderTarget(0,&rt);D3DSURFACE_DESC surface{};rt->GetDesc(&surface);
        IDirect3DSurface9* cpu=nullptr;if(FAILED(device->CreateOffscreenPlainSurface(surface.Width,surface.Height,surface.Format,D3DPOOL_SYSTEMMEM,&cpu,nullptr)))return 20;
        if(FAILED(device->GetRenderTargetData(rt,cpu)))return 21;
        D3DLOCKED_RECT read{};if(FAILED(cpu->LockRect(&read,nullptr,D3DLOCK_READONLY)))return 22;
        DWORD pixel=*(reinterpret_cast<DWORD*>(static_cast<unsigned char*>(read.pBits)+8*read.Pitch)+8)&0xffffff;
        cpu->UnlockRect();cpu->Release();rt->Release();
        if((!pass&&pixel!=0x208020)||(pass&&pixel==0x208020)){printf("FAIL final framebuffer pass%d pixel=%06lx\n",pass,pixel);return 23;}
    }
    device->SetTexture(0,nullptr);marker->Release();
    int frames=0;for(int i=0;i<16;++i){device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff243446,1,0);hr=device->Present(nullptr,nullptr,nullptr,nullptr);if(FAILED(hr))break;++frames;}
    device->Release();DestroyWindow(window);api->Release();
    // Proxy stays loaded until exit: shared vtable hooks must not be unloaded early.
    if(frames!=16){printf("FAIL Present %d frames\n",frames);return 8;}
    printf("PASS D3D9 HAL (%s): live atlas, FINAL FRAMEBUFFER clear Giran / covered unknown, opaque-material override and restored render state,16Present. No NWindow in this host.\n",staged?"SYSTEMMEM upload to DEFAULT":"MANAGED");return 0;
}
