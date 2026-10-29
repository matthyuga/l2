#pragma once
#include "fog_field.h"
#include <memory>

namespace cloud9 {
constexpr int Tile=64, TileCols=fog4::AtlasW/Tile, TileRows=fog4::AtlasH/Tile;
constexpr int TileCount=TileCols*TileRows;
constexpr double Inner=.76, Outer=1.25, Distortion=.09;
struct Frame {
    std::vector<DWORD> pixels;
    std::array<unsigned long long,TileCount> tiles{};
    unsigned long long revision=0;
    unsigned player=0;
    size_t evaluated=0;
};
struct Box { int left=fog4::AtlasW,top=fog4::AtlasH,right=0,bottom=0;
    bool empty()const{return right<=left||bottom<=top;}
    void include(int x,int y){left=std::min(left,x);top=std::min(top,y);right=std::max(right,x+1);bottom=std::max(bottom,y+1);}
};
inline double worldX(int x){return (x+.5)*2048/fog4::AtlasW/fog4::Scale-131072;}
inline double worldY(int y){return (y+.5)*3072/fog4::AtlasH/fog4::Scale-262144;}
// Low frequency, world anchored distortion: rounded, softly uneven edges.
// Its bounded amplitude also gives an exact bound for the dirty rectangle.
inline double coverage(double dx,double dy,double noise) {
    double radius=std::sqrt(dx*dx+dy*dy);
    double edge=Outer+noise;
    double t=std::max(0.0,std::min(1.0,(edge-radius)/(edge-Inner)));
    return t*t*(3-2*t);
}
class Atlas {
    fog4::Snapshot previous{};
    std::vector<DWORD> base,pixels;
    std::vector<unsigned char> personal,global;
    std::array<unsigned long long,TileCount> tiles{};
    std::array<double,fog4::AtlasW> xs{},noiseX{};
    std::array<double,fog4::AtlasH> ys{},noiseY{};
    bool ready=false;
    size_t evaluated=0;
    void stamp(const fog4::Snapshot& s,int col,int row,Box& dirty) {
        const bool p=fog4::bit(s.personal,col,row)!=0,g=fog4::bit(s.global,col,row)!=0;
        if(!p&&!g)return;
        const double cx=col+.5,cy=row+.5,r=Outer+Distortion;
        int x0=std::max(0,static_cast<int>(std::floor((cx-r)*fog4::Cell*fog4::Scale/2048*fog4::AtlasW-.5)));
        int x1=std::min(fog4::AtlasW,static_cast<int>(std::ceil((cx+r)*fog4::Cell*fog4::Scale/2048*fog4::AtlasW+.5)));
        int y0=std::max(0,static_cast<int>(std::floor((cy-r)*fog4::Cell*fog4::Scale/3072*fog4::AtlasH-.5)));
        int y1=std::min(fog4::AtlasH,static_cast<int>(std::ceil((cy+r)*fog4::Cell*fog4::Scale/3072*fog4::AtlasH+.5)));
        for(int y=y0;y<y1;++y)for(int x=x0;x<x1;++x) {
            ++evaluated;
            auto a=static_cast<unsigned char>(coverage(xs[x]-cx,ys[y]-cy,noiseX[x]+noiseY[y])*255+.5);
            size_t i=static_cast<size_t>(y)*fog4::AtlasW+x;
            bool changed=false;
            if(p&&a>personal[i]){personal[i]=a;changed=true;}
            if(g&&a>global[i]){global[i]=a;changed=true;}
            if(changed)dirty.include(x,y);
        }
    }
public:
    explicit Atlas(std::vector<DWORD> initial):base(std::move(initial)),pixels(base),personal(base.size()),global(base.size()) {
        for(int x=0;x<fog4::AtlasW;++x){xs[x]=(worldX(x)+131072)/fog4::Cell;noiseX[x]=.045*std::sin(xs[x]*3.1);}
        for(int y=0;y<fog4::AtlasH;++y){ys[y]=(worldY(y)+262144)/fog4::Cell;noiseY[y]=.045*std::sin(ys[y]*2.7+.8);}
    }
    std::shared_ptr<const Frame> build(const fog4::Snapshot& s,unsigned long long revision) {
        evaluated=0;bool full=!ready||s.player!=previous.player;
        for(int i=0;!full&&i<fog4::Bytes;++i)
            if((previous.personal[i]&~s.personal[i])||(previous.global[i]&~s.global[i]))full=true;
        Box dirty;
        if(full) {
            std::fill(personal.begin(),personal.end(),static_cast<unsigned char>(0));std::fill(global.begin(),global.end(),static_cast<unsigned char>(0));
            pixels=base;dirty={0,0,fog4::AtlasW,fog4::AtlasH};
        }
        for(int i=0;i<fog4::Bytes;++i) {
            unsigned changed=full?(s.personal[i]|s.global[i]):((s.personal[i]^previous.personal[i])|(s.global[i]^previous.global[i]));
            for(int bit=0;changed;++bit,changed>>=1)if(changed&1){int cell=i*8+bit;stamp(s,cell%fog4::Columns,cell/fog4::Columns,dirty);}
        }
        if(!dirty.empty()) {
            for(int y=dirty.top;y<dirty.bottom;++y)for(int x=dirty.left;x<dirty.right;++x) {
                size_t i=static_cast<size_t>(y)*fog4::AtlasW+x;
                double a=(255-personal[i])*(1-.45*global[i]/255.0);
                auto alpha=static_cast<DWORD>(std::min(a,static_cast<double>(base[i]>>24))+.5);
                DWORD next=(base[i]&0xffffff)|(alpha<<24);
                if(full||next!=pixels[i]){pixels[i]=next;tiles[(y/Tile)*TileCols+x/Tile]=revision;}
            }
        }
        previous=s;ready=true;
        auto frame=std::make_shared<Frame>();frame->pixels=pixels;frame->tiles=tiles;frame->revision=revision;frame->player=s.player;frame->evaluated=evaluated;
        return frame;
    }
};
inline Box changedBox(const Frame& f,const std::array<unsigned long long,TileCount>& uploaded) {
    Box box;
    for(int i=0;i<TileCount;++i)if(f.tiles[i]!=uploaded[i]) {
        int x=i%TileCols*Tile,y=i/TileCols*Tile;
        box.include(x,y);box.include(x+Tile-1,y+Tile-1);
    }
    return box;
}
}
