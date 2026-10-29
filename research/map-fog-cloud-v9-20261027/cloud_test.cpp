#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "cloud_atlas.h"
#include <cstdio>
#include <cstdlib>
#include <chrono>
#include <fstream>

static int checks=0;
static void check(bool b,const char* why){++checks;if(!b){printf("FAIL %s\n",why);std::exit(1);}}
static void mark(fog4::Bits& bits,int x,int y){int i=y*fog4::Columns+x;bits[i/8]|=1<<(i%8);}
static double ms(){using namespace std::chrono;return duration<double,std::milli>(steady_clock::now().time_since_epoch()).count();}
int main() {
    // Circular falloff, exact clear core, smooth edge, no square diagonal.
    check(cloud9::coverage(0,0,0)==1,"clear center");
    check(cloud9::coverage(.5,.5,-.09)==1,"whole visited cell clear");
    check(cloud9::coverage(1,0,0)>cloud9::coverage(1,1,0),"round outline");
    check(cloud9::coverage(1.35,0,.09)==0,"bounded edge");
    for(int i=0;i<100;++i)check(cloud9::coverage(i*.02,0,0)>=cloud9::coverage((i+1)*.02,0,0),"monotone fade");
    std::vector<DWORD> base(fog4::AtlasW*fog4::AtlasH,0xff4e5860);
    // A fixed clear patch remains clear under every exploration layer.
    for(int y=80;y<120;++y)for(int x=40;x<70;++x)base[y*fog4::AtlasW+x]&=0xffffff;
    cloud9::Atlas incremental(base);fog4::Snapshot s;s.player=42;
    auto f=incremental.build(s,1);auto upload=f->pixels;auto uploaded=f->tiles;
    auto old=f;const auto oldPixels=f->pixels;
    size_t sparseEvaluated=0,sparseUpload=0;double worstBuild=0;
    for(int pass=0;pass<14;++pass) {
        if(pass==5){s.personal.fill(0);} // removal must remove stale reveal
        else if(pass==8){s=fog4::Snapshot{};s.player=43;} // no inherited reveal
        else {int x=pass==12?0:(pass==13?99:12+pass),y=pass==12?0:(pass==13?149:100-pass);mark(s.global,x,y);if(pass%3)mark(s.personal,x,y);}
        double begin=ms();auto next=incremental.build(s,pass+2);worstBuild=std::max(worstBuild,ms()-begin);
        cloud9::Atlas reference(base);auto whole=reference.build(s,pass+2);
        check(next->pixels==whole->pixels,"incremental equals complete reconstruction including removal/player/edges");
        auto box=cloud9::changedBox(*next,uploaded);
        if(!box.empty())for(int y=box.top;y<box.bottom;++y)
            memcpy(upload.data()+y*fog4::AtlasW+box.left,next->pixels.data()+y*fog4::AtlasW+box.left,(box.right-box.left)*sizeof(DWORD));
        check(upload==whole->pixels,"partial upload equals complete atlas");
        if(pass==1){sparseEvaluated=next->evaluated;sparseUpload=static_cast<size_t>(box.right-box.left)*(box.bottom-box.top);check(sparseEvaluated<3000,"single discovery local CPU work");check(sparseUpload<=4*64*64,"single discovery local upload");}
        check(old->pixels==oldPixels,"published frame immutable");
        // Independent point oracle: combine nearby round stamps directly.
        for(int sample=0;sample<24;++sample) {
            int x=(sample*41+pass*13)%fog4::AtlasW,y=(sample*83+pass*27)%fog4::AtlasH;
            double gx=(cloud9::worldX(x)+131072)/4096,gy=(cloud9::worldY(y)+262144)/4096;
            double noise=.045*std::sin(gx*3.1)+.045*std::sin(gy*2.7+.8);int pa=0,ga=0;
            for(int row=static_cast<int>(gy)-2;row<=static_cast<int>(gy)+2;++row)
                for(int col=static_cast<int>(gx)-2;col<=static_cast<int>(gx)+2;++col) {
                    int a=static_cast<int>(cloud9::coverage(gx-col-.5,gy-row-.5,noise)*255+.5);
                    if(fog4::bit(s.personal,col,row))pa=std::max(pa,a);
                    if(fog4::bit(s.global,col,row))ga=std::max(ga,a);
                }
            size_t i=static_cast<size_t>(y)*fog4::AtlasW+x;
            DWORD expected=static_cast<DWORD>(std::min((255-pa)*(1-.45*ga/255.0),static_cast<double>(base[i]>>24))+.5);
            check((next->pixels[i]>>24)==expected,"independent radial alpha oracle");
        }
        uploaded=next->tiles;
    }
    // Render can skip publications; tile versions must include earlier changes.
    auto skipped=incremental.build(s,50);mark(s.personal,70,20);auto newest=incremental.build(s,51);
    auto box=cloud9::changedBox(*newest,f->tiles);auto caught=f->pixels;
    for(int y=box.top;y<box.bottom;++y)memcpy(caught.data()+y*fog4::AtlasW+box.left,newest->pixels.data()+y*fog4::AtlasW+box.left,(box.right-box.left)*4);
    check(caught==newest->pixels,"skipped generations catch up");
    auto same=incremental.build(s,52);
    check(same->evaluated==0&&cloud9::changedBox(*same,newest->tiles).empty(),"unchanged snapshot needs no pixels or upload");
    // Preview uses the exact production mask, without texture interpolation.
    cloud9::Atlas preview(base);fog4::Snapshot route;route.player=44;
    for(int i=0;i<10;++i){mark(route.personal,30+i,60+i/3);mark(route.global,30+i,60+i/3);}
    mark(route.global,36,57);auto image=preview.build(route,1);
    std::ofstream raw("build/cloud-preview.bgra",std::ios::binary);raw.write(reinterpret_cast<const char*>(image->pixels.data()),image->pixels.size()*4);raw.close();
    printf("PASS %d cloud checks. One discovery: %zu radial evaluations, %zu upload pixels vs 2097152. Worst build incl full reset %.3fms (background).\n",checks,sparseEvaluated,sparseUpload,worstBuild);
    return 0;
}
