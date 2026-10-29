#include "map_fog.cpp"
#include <cstdlib>

static std::wstring encoded(const fog4::Bits& bits) {
    DWORD n=0;CryptBinaryToStringW(bits.data(),static_cast<DWORD>(bits.size()),CRYPT_STRING_BASE64|CRYPT_STRING_NOCRLF,nullptr,&n);
    std::wstring text(n,L'\0');CryptBinaryToStringW(bits.data(),static_cast<DWORD>(bits.size()),CRYPT_STRING_BASE64|CRYPT_STRING_NOCRLF,text.data(),&n);text.resize(n);return text;
}
static bool send(const fog4::Snapshot& s,unsigned seq) {
    auto message=L"#NXFOG4|"+std::to_wstring(s.player)+L"|"+std::to_wstring(seq)+L"|"+encoded(s.global)+L"|"+encoded(s.personal);
    return walking::receive(message.c_str(),message.size());
}
static DWORD drawPixel(IDirect3DDevice9* d,double x,double y) {
    struct V {float x,y,z,rhw;DWORD color;float u,v;};
    float u=static_cast<float>((x+131072)*fog4::Scale/2048),v=static_cast<float>((y+262144)*fog4::Scale/3072);
    V quad[4]={{0,0,0,1,0xffffffff,u,v},{32,0,0,1,0xffffffff,u,v},{0,32,0,1,0xffffffff,u,v},{32,32,0,1,0xffffffff,u,v}};
    d->Clear(0,nullptr,D3DCLEAR_TARGET,0xff208020,1,0);
    d->SetRenderState(D3DRS_ZENABLE,FALSE);d->SetRenderState(D3DRS_ALPHABLENDENABLE,FALSE);
    d->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_SELECTARG2);d->SetTextureStageState(0,D3DTSS_ALPHAARG2,D3DTA_DIFFUSE);
    d->SetFVF(D3DFVF_XYZRHW|D3DFVF_DIFFUSE|D3DFVF_TEX1);d->BeginScene();
    HRESULT hr=d->DrawPrimitiveUP(D3DPT_TRIANGLESTRIP,2,quad,sizeof(V));d->EndScene();if(FAILED(hr))std::exit(11);
    IDirect3DSurface9 *rt=nullptr,*cpu=nullptr;d->GetRenderTarget(0,&rt);D3DSURFACE_DESC desc{};rt->GetDesc(&desc);
    if(FAILED(d->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&cpu,nullptr)))std::exit(12);
    if(FAILED(d->GetRenderTargetData(rt,cpu)))std::exit(13);D3DLOCKED_RECT rect{};cpu->LockRect(&rect,nullptr,D3DLOCK_READONLY);
    DWORD pixel=*(reinterpret_cast<DWORD*>(static_cast<unsigned char*>(rect.pBits)+8*rect.Pitch)+8)&0xffffff;
    cpu->UnlockRect();cpu->Release();rt->Release();return pixel;
}
int main() {
    selfModule=GetModuleHandleW(nullptr);
    auto api=NexusDirect3DCreate9(D3D_SDK_VERSION);if(!api)return 2;
    HWND wnd=CreateWindowExW(0,L"STATIC",L"Fog refresh regression",WS_POPUP,0,0,64,64,nullptr,nullptr,GetModuleHandleW(nullptr),nullptr);
    D3DPRESENT_PARAMETERS pp{};pp.Windowed=TRUE;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.hDeviceWindow=wnd;pp.BackBufferWidth=64;pp.BackBufferHeight=64;
    IDirect3DDevice9* d=nullptr;if(FAILED(api->CreateDevice(0,D3DDEVTYPE_HAL,wnd,D3DCREATE_SOFTWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&pp,&d)))return 3;
    IDirect3DTexture9* marker=nullptr;if(FAILED(d->CreateTexture(16,16,1,0,D3DFMT_A8R8G8B8,D3DPOOL_MANAGED,&marker,nullptr)))return 4;
    D3DLOCKED_RECT rect{};marker->LockRect(0,&rect,nullptr,0);
    for(int y=0;y<16;++y){auto row=reinterpret_cast<DWORD*>(static_cast<unsigned char*>(rect.pBits)+y*rect.Pitch);for(int x=0;x<16;++x)row[x]=0xff3e4850;if(y==0)for(int x=0;x<8;++x)row[x]=walking::Marker[x];}
    marker->UnlockRect(0);fog4::Snapshot snapshot;snapshot.player=42;if(!send(snapshot,1))return 5;
    d->SetTexture(0,marker);IDirect3DBaseTexture9* live=nullptr;d->GetTexture(0,&live);if(!live||live==marker)return 6;
    // Simulate the engine cache retaining the already substituted live atlas.
    // After this, do NOT rebind SetTexture and do NOT call device Present.
    d->SetTexture(0,live);
    // Reproduce the observed client: the active device uses an unhooked table
    // after initial creation. Keep the atlas binding, remove all proxy slots.
    auto originalTable=*reinterpret_cast<void***>(d);
    auto clientTable=originalTable;
    replaceSlot(clientTable,17,reinterpret_cast<void*>(presentMethods[originalTable]));
    replaceSlot(clientTable,16,reinterpret_cast<void*>(resetMethods[originalTable]));
    replaceSlot(clientTable,31,reinterpret_cast<void*>(uploadMethods[originalTable]));
    replaceSlot(clientTable,65,reinterpret_cast<void*>(textureMethods[originalTable]));
    replaceSlot(clientTable,81,reinterpret_cast<void*>(primitiveMethods[originalTable]));
    replaceSlot(clientTable,82,reinterpret_cast<void*>(indexedMethods[originalTable]));
    replaceSlot(clientTable,83,reinterpret_cast<void*>(primitiveUPMethods[originalTable]));
    replaceSlot(clientTable,84,reinterpret_cast<void*>(indexedUPMethods[originalTable]));

    for(int pass=0;pass<3;++pass){
        int col=12+pass*6,row=100-pass*4;double x=-131072+(col+.5)*4096,y=-262144+(row+.5)*4096;
        DWORD before=drawPixel(d,x,y);
        for(int dy=-1;dy<=1;++dy)for(int dx=-1;dx<=1;++dx){int index=(row+dy)*100+col+dx;snapshot.personal[index/8]|=1<<(index%8);snapshot.global[index/8]|=1<<(index%8);}
        if(!send(snapshot,pass+2))return 7;
        // The production map draw boundary will refresh and repair this table.
#ifdef V8_MAP_BOUNDARY
        refreshMapAtlases();
        if(clientTable[83]!=reinterpret_cast<void*>(hookedPrimitiveUP))return 15;
#endif
        DWORD after=drawPixel(d,x,y);
        if(before==after){printf("FAIL stale map after snapshot: pass=%d before=%06lx after=%06lx; cached atlas, no SetTexture/Present\n",pass,before,after);return 8;}
        DWORD stable=drawPixel(d,x,y);if(stable!=after)return 9;
        printf("PASS discovery%d updates framebuffer %06lx -> %06lx without rebinding or Present\n",pass,before,after);
    }
    snapshot=fog4::Snapshot{};snapshot.player=43;if(!send(snapshot,9))return 10;
#ifdef V8_MAP_BOUNDARY
    refreshMapAtlases();
#endif
    DWORD other=drawPixel(d,-131072+12.5*4096,-262144+100.5*4096);
    if(other==0x208020)return 14;
    printf("PASS second character remains covered; three moving discoveries refresh; no player data changed.\n");
    *reinterpret_cast<void***>(d)=originalTable;
    d->SetTexture(0,nullptr);live->Release();marker->Release();d->Release();api->Release();DestroyWindow(wnd);return 0;
}
