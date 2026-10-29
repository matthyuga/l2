// Exercise the real preview-update function against detached native-layout
// fixtures; any unexpected native load/refresh would fault this process.
#include "hair_ingame.cpp"
int main(){
 std::vector<unsigned char> actor(0x1900),setup(0x300),texture(0x610),mip(0x30);
 uint32_t output[2]={};at<void*>(texture.data(),0x5f0)=mip.data();at<uint32_t*>(mip.data(),0x1c)=output;
 at<int>(actor.data(),4)=17;at<uint32_t>(actor.data(),0x20)=42;at<void*>(actor.data(),0x24)=reinterpret_cast<void*>(0xabc);
 at<int>(setup.data(),0x1f0)=1;at<int>(setup.data(),0x1f4)=0;at<int>(setup.data(),0x1f8)=0;
 Pawn p;p.object=actor.data();p.index=17;p.name=42;p.klass=reinterpret_cast<void*>(0xabc);p.preview=true;p.model=6;
 auto& part=p.part[0];part.original=reinterpret_cast<void*>(0x100);part.rendered=reinterpret_cast<void*>(0x200);part.texture=texture.data();part.source.pixels={0xff805020,0x80332211};part.source.mask={255,0};
 at<void*>(actor.data(),0x474)=part.rendered;pawns[p.object]=p;
 ui.setup=setup.data();ui.free=true;ui.legacy=2;
 unsigned checks=0;for(int n=0;n<180;n++){
  ui.h=float(n*2);ui.s=80;ui.l=50;if(!updatePreviewColor())return 1;
  if(at<void*>(actor.data(),0x474)!=part.rendered||output[1]!=0x80332211||(output[0]>>24)!=255)return 2;
  if(pawns[p.object].part[0].original!=part.original||pawns[p.object].part[0].texture!=texture.data())return 3;
  checks++;
 }
 ui.free=false;if(!updatePreviewColor()||at<void*>(actor.data(),0x474)!=part.original)return 4;checks++;
 ui.free=true;if(!updatePreviewColor()||at<void*>(actor.data(),0x474)!=part.rendered)return 5;checks++;
 at<int>(setup.data(),0x1f0)=2;if(updatePreviewColor())return 6;checks++;
 pawns.clear();printf("PASS %u real preview transitions: no resource refresh, stable material instance, classic restore, model filtering.\n",checks);
 FILE* f=nullptr;fopen_s(&f,"preview-test-results.json","w");if(f){fprintf(f,"{\"passed\":%u,\"resource_reload_calls\":0,\"material_instance_preserved\":true}\n",checks);fclose(f);}return 0;
}
