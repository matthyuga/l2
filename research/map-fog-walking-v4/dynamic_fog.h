#pragma once
#include "fog_field.h"
#include <mutex>
#include <d3d9.h>

namespace walking {
static std::mutex snapshotMutex;
static fog4::Snapshot snapshot;
static unsigned long long revision=1;
static std::array<DWORD,64*64> colors{};
static std::array<unsigned char,512*512> giran{};
static bool fieldLoaded=false;
static constexpr DWORD Marker[8]={0xff214365,0xffa31572,0xff7832c1,0xff09b4e2,0xffa1c307,0xff4421d7,0xffc35b19,0xff73a28d};
static bool loadField(const std::wstring& path) {
    HANDLE f=CreateFileW(path.c_str(),GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);if(f==INVALID_HANDLE_VALUE)return false;
    char magic[8];DWORD n=0;bool ok=ReadFile(f,magic,8,&n,nullptr)&&n==8&&!memcmp(magic,"NXFOG4\0\0",8);
    if(ok)ok=ReadFile(f,colors.data(),sizeof(colors),&n,nullptr)&&n==sizeof(colors);
    if(ok)ok=ReadFile(f,giran.data(),sizeof(giran),&n,nullptr)&&n==sizeof(giran);
    LARGE_INTEGER size{};ok=ok&&GetFileSizeEx(f,&size)&&size.QuadPart==8+sizeof(colors)+sizeof(giran);CloseHandle(f);fieldLoaded=ok;return ok;
}
static bool receive(const wchar_t* text,size_t length) {
    fog4::Snapshot next;if(!fog4::parse(text,length,next))return false;
    std::lock_guard<std::mutex> lock(snapshotMutex);
    if(next.player!=snapshot.player||next.global!=snapshot.global||next.personal!=snapshot.personal){snapshot=next;++revision;}
    return true;
}
static double giranAlpha(double worldX,double worldY) {
    double x=(worldX-72000)/24000*512-.5,y=(worldY-136000)/24000*512-.5;
    if(x<0||y<0||x>=511||y>=511)return 255;
    int ix=static_cast<int>(x),iy=static_cast<int>(y);double fx=x-ix,fy=y-iy;
    return (1-fy)*((1-fx)*giran[iy*512+ix]+fx*giran[iy*512+ix+1])+fy*((1-fx)*giran[(iy+1)*512+ix]+fx*giran[(iy+1)*512+ix+1]);
}
struct Device {
    IDirect3DTexture9* selected=nullptr;IDirect3DTexture9* live=nullptr;
    unsigned long long built=0;std::map<IDirect3DBaseTexture9*,bool> examined;
    void clear(){if(selected)selected->Release();if(live)live->Release();selected=live=nullptr;built=0;examined.clear();}
};
static void update(IDirect3DDevice9* d,Device& state) {
    if(!fieldLoaded||!state.selected)return;
    fog4::Snapshot copy;unsigned long long current;
    {std::lock_guard<std::mutex> lock(snapshotMutex);current=revision;if(current==state.built)return;copy=snapshot;}
    if(!state.live&&FAILED(d->CreateTexture(fog4::AtlasW,fog4::AtlasH,1,0,D3DFMT_A8R8G8B8,D3DPOOL_MANAGED,&state.live,nullptr)))return;
    D3DLOCKED_RECT rect{};if(FAILED(state.live->LockRect(0,&rect,nullptr,0)))return;
    for(int y=0;y<fog4::AtlasH;++y) {
        DWORD* pixels=reinterpret_cast<DWORD*>(static_cast<unsigned char*>(rect.pBits)+y*rect.Pitch);
        double mapY=(y+.5)*3072/fog4::AtlasH,worldY=mapY/fog4::Scale-262144;
        for(int x=0;x<fog4::AtlasW;++x) {
            double mapX=(x+.5)*2048/fog4::AtlasW,worldX=mapX/fog4::Scale-131072;
            DWORD color=colors[((static_cast<int>(mapY)/8)%64)*64+(static_cast<int>(mapX)/8)%64]&0xffffff;
            const double jitterX=(static_cast<int>((color>>16)&255)-62)*24.0;
            const double jitterY=(static_cast<int>(color&255)-80)*24.0;
            unsigned char a=fog4::alpha(copy,worldX+jitterX,worldY+jitterY,giranAlpha(worldX,worldY));
            pixels[x]=color|(static_cast<DWORD>(a)<<24);
        }
    }
    state.live->UnlockRect(0);state.built=current;
}
static bool identify(IDirect3DDevice9* d,Device& state,IDirect3DBaseTexture9* base) {
    if(!base||base->GetType()!=D3DRTYPE_TEXTURE||state.examined.count(base))return false;
    auto texture=static_cast<IDirect3DTexture9*>(base);D3DSURFACE_DESC desc{};
    if(FAILED(texture->GetLevelDesc(0,&desc))||desc.Width!=16||desc.Height!=16||(desc.Format!=D3DFMT_A8R8G8B8&&desc.Format!=D3DFMT_X8R8G8B8))return false;
    if(state.examined.size()>4096)state.examined.clear();
    D3DLOCKED_RECT rect{};if(FAILED(texture->LockRect(0,&rect,nullptr,D3DLOCK_READONLY)))return false;
    bool match=true;auto pixels=static_cast<DWORD*>(rect.pBits);
    for(int x=0;x<8;++x)if(pixels[x]!=Marker[x])match=false;
    texture->UnlockRect(0);state.examined.emplace(base,match);
    if(!match)return false;
    state.selected=texture;texture->AddRef();update(d,state);return true;
}
}
