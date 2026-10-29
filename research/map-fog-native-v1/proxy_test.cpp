#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <d3d9.h>
#include <cstdio>
int wmain(int argc,wchar_t** argv) {
    if(argc!=2)return 2;
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
    int frames=0;for(int i=0;i<16;++i){device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff243446,1,0);hr=device->Present(nullptr,nullptr,nullptr,nullptr);if(FAILED(hr))break;++frames;}
    device->Release();DestroyWindow(window);api->Release();
    // Proxy stays loaded until exit: shared vtable hooks must not be unloaded early.
    if(frames!=16){printf("FAIL Present %d frames\n",frames);return 8;}
    printf("PASS D3D9 forwarding: factory, hidden HAL device and 16 Present calls. No NWindow in this host.\n");return 0;
}
