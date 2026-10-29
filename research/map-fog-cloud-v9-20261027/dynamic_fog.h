#pragma once
#include "fog_field.h"
#include <mutex>
#include <d3d9.h>
#include <thread>
#include <condition_variable>
#include <atomic>
#include "cloud_atlas.h"

namespace walking {
static std::mutex snapshotMutex;
static fog4::Snapshot snapshot;
static unsigned long long revision=1;
static std::array<DWORD,64*64> colors{};
static std::array<unsigned char,512*512> giran{};
static bool fieldLoaded=false;
static constexpr DWORD Marker[8]={0xff214365,0xffa31572,0xff7832c1,0xff09b4e2,0xffa1c307,0xff4421d7,0xffc35b19,0xff73a28d};
static void startWorker();
static void queueSnapshot(const fog4::Snapshot&,unsigned long long);
static bool loadField(const std::wstring& path) {
    HANDLE f=CreateFileW(path.c_str(),GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);if(f==INVALID_HANDLE_VALUE)return false;
    char magic[8];DWORD n=0;bool ok=ReadFile(f,magic,8,&n,nullptr)&&n==8&&!memcmp(magic,"NXFOG4\0\0",8);
    if(ok)ok=ReadFile(f,colors.data(),sizeof(colors),&n,nullptr)&&n==sizeof(colors);
    if(ok)ok=ReadFile(f,giran.data(),sizeof(giran),&n,nullptr)&&n==sizeof(giran);
    LARGE_INTEGER size{};ok=ok&&GetFileSizeEx(f,&size)&&size.QuadPart==8+sizeof(colors)+sizeof(giran);CloseHandle(f);fieldLoaded=ok;if(ok)startWorker();return ok;
}
static bool receive(const wchar_t* text,size_t length) {
    fog4::Snapshot next;if(!fog4::parse(text,length,next))return false;
    std::lock_guard<std::mutex> lock(snapshotMutex);
    if(next.player!=snapshot.player||next.global!=snapshot.global||next.personal!=snapshot.personal){snapshot=next;++revision;queueSnapshot(next,revision);}
    return true;
}
static double giranAlpha(double worldX,double worldY) {
    double x=(worldX-72000)/24000*512-.5,y=(worldY-136000)/24000*512-.5;
    if(x<0||y<0||x>=511||y>=511)return 255;
    int ix=static_cast<int>(x),iy=static_cast<int>(y);double fx=x-ix,fy=y-iy;
    return (1-fy)*((1-fx)*giran[iy*512+ix]+fx*giran[iy*512+ix+1])+fy*((1-fx)*giran[(iy+1)*512+ix]+fx*giran[(iy+1)*512+ix+1]);
}
// This worker has process lifetime, like the proxy's device registry. No D3D
// method is called here. Publication never holds its mutex during calculation.
struct Worker {
    std::mutex mutex;std::condition_variable wake;
    fog4::Snapshot pending{};unsigned long long pendingRevision=1;
    std::atomic<unsigned> requestedPlayer{0};
    std::shared_ptr<const cloud9::Frame> published,covered;
    std::unique_ptr<cloud9::Atlas> atlas;
};
static Worker* worker=nullptr;
static void startWorker() {
    std::vector<DWORD> base(static_cast<size_t>(fog4::AtlasW)*fog4::AtlasH);
    for(int y=0;y<fog4::AtlasH;++y)for(int x=0;x<fog4::AtlasW;++x) {
        int mx=static_cast<int>((x+.5)*2048/fog4::AtlasW),my=static_cast<int>((y+.5)*3072/fog4::AtlasH);
        DWORD color=colors[((my/8)%64)*64+(mx/8)%64]&0xffffff;
        auto a=static_cast<DWORD>(giranAlpha(cloud9::worldX(x),cloud9::worldY(y))+.5);
        base[static_cast<size_t>(y)*fog4::AtlasW+x]=color|(a<<24);
    }
    worker=new Worker();worker->atlas=std::make_unique<cloud9::Atlas>(std::move(base));
    worker->published=worker->covered=worker->atlas->build(fog4::Snapshot{},1);
    auto w=worker;
    std::thread([w]{
        unsigned long long built=1;
        for(;;) {
            fog4::Snapshot next;unsigned long long current;
            {std::unique_lock<std::mutex> lock(w->mutex);w->wake.wait(lock,[&]{return w->pendingRevision!=built;});next=w->pending;current=w->pendingRevision;}
            auto result=w->atlas->build(next,current);
            {std::lock_guard<std::mutex> lock(w->mutex);w->published=std::move(result);}
            built=current;
        }
    }).detach();
}
static void queueSnapshot(const fog4::Snapshot& next,unsigned long long current) {
    if(!worker)return;
    {std::lock_guard<std::mutex> lock(worker->mutex);worker->pending=next;worker->pendingRevision=current;worker->requestedPlayer.store(next.player);}
    worker->wake.notify_one();
}
struct Device {
    IDirect3DTexture9* selected=nullptr;IDirect3DTexture9* live=nullptr;
    unsigned long long built=0;unsigned builtPlayer=0;
    std::array<unsigned long long,cloud9::TileCount> uploadedTiles{};
    size_t lastUploadedPixels=0;
    std::map<IDirect3DBaseTexture9*,bool> examined;
    void clear(){if(selected)selected->Release();if(live)live->Release();selected=live=nullptr;built=0;builtPlayer=0;uploadedTiles.fill(0);lastUploadedPixels=0;examined.clear();}
};
static void update(IDirect3DDevice9* d,Device& state) {
    if(!fieldLoaded||!state.selected||!worker)return;
    std::shared_ptr<const cloud9::Frame> frame;
    {std::unique_lock<std::mutex> lock(worker->mutex,std::try_to_lock);
     if(!lock.owns_lock()){if(state.live&&state.builtPlayer==worker->requestedPlayer.load())return;frame=worker->covered;}
     else {frame=worker->published;if(frame->player!=worker->requestedPlayer.load())frame=worker->covered;}}
    if(state.live&&frame->revision==state.built&&frame->player==state.builtPlayer)return;
    bool fresh=!state.live;
    if(fresh&&FAILED(d->CreateTexture(fog4::AtlasW,fog4::AtlasH,1,0,D3DFMT_A8R8G8B8,D3DPOOL_MANAGED,&state.live,nullptr)))return;
    auto box=cloud9::changedBox(*frame,state.uploadedTiles);
    if(fresh||frame->player!=state.builtPlayer)box={0,0,fog4::AtlasW,fog4::AtlasH};
    state.lastUploadedPixels=0;
    if(!box.empty()) {
        RECT region{box.left,box.top,box.right,box.bottom};D3DLOCKED_RECT rect{};
        if(FAILED(state.live->LockRect(0,&rect,&region,0)))return;
        size_t bytes=static_cast<size_t>(box.right-box.left)*sizeof(DWORD);
        for(int y=box.top;y<box.bottom;++y)
            memcpy(static_cast<unsigned char*>(rect.pBits)+(y-box.top)*rect.Pitch,frame->pixels.data()+static_cast<size_t>(y)*fog4::AtlasW+box.left,bytes);
        if(FAILED(state.live->UnlockRect(0)))return;
        state.lastUploadedPixels=static_cast<size_t>(box.right-box.left)*(box.bottom-box.top);
    }
    state.built=frame->revision;state.builtPlayer=frame->player;state.uploadedTiles=frame->tiles;
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
static bool uploaded(IDirect3DDevice9* d,Device& state,IDirect3DBaseTexture9* source,IDirect3DBaseTexture9* destination) {
    if(state.selected||!destination||destination->GetType()!=D3DRTYPE_TEXTURE)return false;
    if(!identify(d,state,source))return false;
    auto texture=static_cast<IDirect3DTexture9*>(destination);
    D3DSURFACE_DESC desc{};if(FAILED(texture->GetLevelDesc(0,&desc))||desc.Width!=16||desc.Height!=16){state.selected->Release();state.selected=nullptr;return false;}
    state.selected->Release();state.selected=texture;texture->AddRef();return true;
}
}
