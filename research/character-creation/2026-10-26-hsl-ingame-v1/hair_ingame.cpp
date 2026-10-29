#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <windowsx.h>
#include <intrin.h>
#include <cstdio>
#include <string>
#include <map>
#include <mutex>
#include <vector>
#include "color_core.h"
#include "client_offsets.h"

template<class T> static T& at(void* p,size_t off){return *reinterpret_cast<T*>(static_cast<unsigned char*>(p)+off);}
static unsigned char *nw,*eng;static HMODULE core;static std::wstring folder;static bool ready=false,failed=false;
static std::recursive_mutex guard;
static void log(const char* line){
 if(folder.empty()){wchar_t path[MAX_PATH];auto mod=GetModuleHandleW(L"NexusHairHslGame.dll");GetModuleFileNameW(mod,path,MAX_PATH);folder=path;folder=folder.substr(0,folder.find_last_of(L"\\/")+1);}
 HANDLE f=CreateFileW((folder+L"NexusHairHsl.log").c_str(),FILE_APPEND_DATA,FILE_SHARE_READ|FILE_SHARE_WRITE,nullptr,OPEN_ALWAYS,0,nullptr);
 if(f!=INVALID_HANDLE_VALUE){DWORD n;WriteFile(f,line,DWORD(strlen(line)),&n,nullptr);WriteFile(f,"\r\n",2,&n,nullptr);CloseHandle(f);}
}
template<class T>static T symbol(HMODULE m,const char* name){return reinterpret_cast<T>(GetProcAddress(m,name));}
using Construct=void*(__cdecl*)(void*,void*,uint32_t,uint32_t,void*,void*,void*);
using Transient=void*(__cdecl*)();using ObjVoid=void(__thiscall*)(void*);using InitTexture=void(__thiscall*)(void*,int,int);
using RawTexture=void*(__thiscall*)(void*,int);using GetRender=void*(__thiscall*)(void*);
using NameText=const wchar_t*(__thiscall*)(void*);using PcTexName=void*(__thiscall*)(void*,uint32_t*,int,int);
using LoadObject=void*(__cdecl*)(void*,void*,const wchar_t*,const wchar_t*,uint32_t,void*);
static Construct construct;static Transient transient;static ObjVoid addRoot,removeRoot;static InitTexture initTexture;
static RawTexture rawTexture;static GetRender getRender;static PcTexName pcTexName,originalTexName;static NameText nameText;static LoadObject loadObject;
static void *textureClass,*materialClass,*modifierClass,*shaderClass;static void** errorDevice;static int *screenX,*screenY;
using DrawNative=int(__thiscall*)(void*,void*);
using TextureNative=void(__thiscall*)(void*,int,int,int,int,int,int,int,int,void*,int,int);
using UserNative=void(__thiscall*)(void*);
static DrawNative originalDraw;static TextureNative originalTexture;static UserNative originalUser;static void* packetTrampoline;
static bool initialize(){
 if(ready)return true;if(failed)return false;
 nw=reinterpret_cast<unsigned char*>(GetModuleHandleW(L"NWindow.dll"));eng=reinterpret_cast<unsigned char*>(GetModuleHandleW(L"engine.dll"));core=GetModuleHandleW(L"Core.dll");if(!nw||!eng||!core)return false;
 originalDraw=reinterpret_cast<DrawNative>(nw+DRAW_TRAMP_RVA);originalTexture=reinterpret_cast<TextureNative>(nw+TEXTURE_TRAMP_RVA);originalUser=reinterpret_cast<UserNative>(eng+USER_TRAMP_RVA);packetTrampoline=nw+PACKET_TRAMP_RVA;
 originalTexName=reinterpret_cast<PcTexName>(eng+TEXNAME_TRAMP_RVA);
 construct=symbol<Construct>(core,"?StaticConstructObject@UObject@@SAPAV1@PAVUClass@@PAV1@VFName@@K1PAVFOutputDevice@@1@Z");
 transient=symbol<Transient>(core,"?GetTransientPackage@UObject@@SAPAVUPackage@@XZ");addRoot=symbol<ObjVoid>(core,"?AddToRoot@UObject@@QAEXXZ");removeRoot=symbol<ObjVoid>(core,"?RemoveFromRoot@UObject@@QAEXXZ");
 errorDevice=symbol<void**>(core,"?GError@@3PAVFOutputDeviceError@@A");screenX=symbol<int*>(core,"?GSEKScreenX@@3HA");screenY=symbol<int*>(core,"?GSEKScreenY@@3HA");
 auto e=reinterpret_cast<HMODULE>(eng);
 textureClass=symbol<void*>(e,"?PrivateStaticClass@UTexture@@0VUClass@@A");materialClass=symbol<void*>(e,"?PrivateStaticClass@UMaterial@@0VUClass@@A");
 modifierClass=symbol<void*>(e,"?PrivateStaticClass@UModifier@@0VUClass@@A");shaderClass=symbol<void*>(e,"?PrivateStaticClass@UShader@@0VUClass@@A");
 initTexture=symbol<InitTexture>(e,"?Init@UTexture@@UAEXHH@Z");getRender=symbol<GetRender>(e,"?GetRenderInterface@UTexture@@UAEPAVFBaseTexture@@XZ");
 rawTexture=symbol<RawTexture>(e,"?GetRawTextureData@FStaticTexture@@UAEPAXH@Z");
 pcTexName=symbol<PcTexName>(e,"?GetPcTexName@User@@QAE?AVFName@@HH@Z");
 nameText=symbol<NameText>(core,"??DFName@@QBEPBGXZ");loadObject=symbol<LoadObject>(core,"?StaticLoadObject@UObject@@SAPAV1@PAVUClass@@PAV1@PBG2KPAVUPackageMap@@@Z");
 if(!construct||!transient||!addRoot||!removeRoot||!errorDevice||!screenX||!screenY||!textureClass||!materialClass||!modifierClass||!shaderClass||!initTexture||!getRender||!rawTexture||!pcTexName||!nameText||!loadObject){failed=true;log("DISABLED: native export contract incomplete.");return false;}
 ready=true;log("READY HSL ingame v1: native textures, creator UI and packed color bridge.");return true;
}
static bool isA(void* o,void* klass){if(!o||!klass)return false;void* c=at<void*>(o,0x24);for(int i=0;c&&i<64;i++,c=at<void*>(c,0x34))if(c==klass)return true;return false;}
static void* make(void* klass,void* model=nullptr){void* o=construct(klass,transient(),0,0x4000,model,*errorDevice,nullptr);if(o)addRoot(o);return o;}
static void* newTexture(int w,int h,uint32_t flags=0){
 void* tex=make(textureClass);if(!tex)return nullptr;at<uint8_t>(tex,0x578)=5;initTexture(tex,w,h);at<uint32_t>(tex,0x5c0)=(flags&31)|0xc0;return tex;
}
static uint32_t* dataOf(void* tex){void* mip=at<void*>(tex,0x5f0);return mip?at<uint32_t*>(mip,0x1c):nullptr;}
static void dirty(void* tex){at<uint32_t>(tex,0x5c0)|=0x80;}
static void* bitmap(void* mat,int depth=0){
 if(!mat||depth>8)return nullptr;if(isA(mat,textureClass))return mat;
 if(isA(mat,modifierClass)||isA(mat,shaderClass))return bitmap(at<void*>(mat,0x578),depth+1);
 return nullptr;
}
static bool pixels(void* tex,std::vector<uint32_t>& out,int& w,int& h){
 if(!tex||!isA(tex,textureClass))return false;w=at<int>(tex,0x580);h=at<int>(tex,0x584);
 if(w<1||h<1||w>2048||h>2048||(w&(w-1))||(h&(h-1))||at<int>(tex,0x5f4)<1)return false;
 void* ri=getRender(tex);if(!ri)return false;auto src=static_cast<const uint8_t*>(rawTexture(ri,0));void* mip=at<void*>(tex,0x5f0);size_t size=at<unsigned>(mip,0x20);int format=at<uint8_t>(tex,0x578);
 if(format==0){if(!src||size<size_t(w)*h)return false;void* palette=at<void*>(tex,0x594);if(!palette||at<int>(palette,0x38)<256)return false;uint32_t* colors=at<uint32_t*>(palette,0x34);out.resize(size_t(w)*h);for(size_t i=0;i<out.size();i++)out[i]=(src[i]==0&&(at<uint32_t>(tex,0x5c0)&1))?0:colors[src[i]];return true;}
 return hair::decode(src,size,w,h,format,out);
}
struct Source {int w=0,h=0;std::vector<uint32_t> pixels;std::vector<uint8_t> mask;};
struct Part {void* original=nullptr;void* rendered=nullptr;void* texture=nullptr;void* rejected=nullptr;std::vector<void*> roots;Source source;uint32_t applied=0xffffffff;};
struct Pawn {void* object=nullptr;int index=0;uint32_t name=0;void* klass=nullptr;uint32_t color=0;Part part[4];int model=0,style=0;};
static std::map<void*,Pawn> pawns;
struct UI {void* setup=nullptr;bool free=false,rebuild=false,dirty=true;float h=30,s=55,l=45;int legacy=0;int x=0,y=36,w=274,height=94;int drag=0;ULONGLONG lastDraw=0,lastApply=0;void* tex=nullptr;};
static UI ui;static HWND gameWindow=nullptr;static WNDPROC oldProc=nullptr;
static void preflight();
static void drop(Part& p){for(void* o:p.roots)if(o)removeRoot(o);p=Part();}
static bool samePawn(const Pawn& p){return p.object&&at<int>(p.object,4)==p.index&&at<uint32_t>(p.object,0x20)==p.name&&at<void*>(p.object,0x24)==p.klass;}
static void gatherMask(void* user,int part,Source& src){
 std::vector<std::vector<uint32_t>> variants;auto saved=at<uint32_t>(user,0x244);
 for(int color=0;color<4;color++){
  at<uint32_t>(user,0x244)=color;uint32_t name=0;pcTexName(user,&name,part,0);if(!name)continue;
  const wchar_t* path=nameText(&name);if(!path||!path[0])continue;
  void* m=loadObject(materialClass,nullptr,path,nullptr,0x8000,nullptr);void* t=bitmap(m);int w=0,h=0;std::vector<uint32_t> p;
  if(pixels(t,p,w,h)&&w==src.w&&h==src.h)variants.push_back(std::move(p));
 }
 at<uint32_t>(user,0x244)=saved;src.mask=hair::differenceMask(variants);
 // Never tint an entire mixed atlas when no distinct hair colors can be proved.
 if(src.mask.size()!=src.pixels.size())src.mask.assign(src.pixels.size(),0);
}
static void* wrap(void* original,void* replacement,std::vector<void*>& roots,int depth=0){
 if(!original||depth>8)return nullptr;if(isA(original,textureClass))return replacement;
 if(!isA(original,modifierClass)&&!isA(original,shaderClass))return nullptr;
 void* child=wrap(at<void*>(original,0x578),replacement,roots,depth+1);if(!child)return nullptr;
 void* clone=make(at<void*>(original,0x24),original);if(!clone)return nullptr;roots.push_back(clone);at<void*>(clone,0x578)=child;return clone;
}
static bool buildPart(Part& p,void* original,void* user,int slot){
 drop(p);void* tex=bitmap(original);if(!pixels(tex,p.source.pixels,p.source.w,p.source.h))return false;
 gatherMask(user,slot,p.source);bool any=false;for(auto v:p.source.mask)if(v){any=true;break;}if(!any){log("SKIP hair material: no color-variant mask; preserving original.");return false;}
 addRoot(original);p.roots.push_back(original);p.original=original;
 p.texture=newTexture(p.source.w,p.source.h,at<uint32_t>(tex,0x5c0));if(!p.texture){drop(p);return false;}p.roots.push_back(p.texture);
 p.rendered=wrap(original,p.texture,p.roots);if(!p.rendered){drop(p);return false;}return true;
}
static void applyPawn(Pawn& p,void* user){
 if(!samePawn(p))return;
 const int offsets[]={0x474,0x478,0x5dc,0x5e0};
 for(int i=0;i<4;i++){
  void*& material=at<void*>(p.object,offsets[i]);Part& part=p.part[i];
  if(!hair::custom(p.color)){if(material==part.rendered&&part.original)material=part.original;continue;}
  if(!material)continue;
  if(material==part.rejected)continue;
  if(material!=part.rendered&&material!=part.original){if(!user)continue;if(!buildPart(part,material,user,4+(i&1))){part.rejected=material;continue;}}
  if(!part.rendered)continue;uint32_t c=p.color&0xffffff;
  if(part.applied!=c){uint32_t* out=dataOf(part.texture);if(!out)continue;hair::tint(part.source.pixels,part.source.mask,c,out);dirty(part.texture);part.applied=c;}
  material=part.rendered;
 }
}
// The copied User used by character creation is stack-lived. Keep a value copy,
// not its address, for resources that finish loading after SetPawnResource.
struct Pending {std::vector<uint32_t> user;};static std::map<void*,Pending> pending;
static void track(void* user,uint32_t value){
 void* object=at<void*>(user,0x204);if(!object)return;if(at<void*>(object,0x718))object=at<void*>(object,0x718);
 auto it=pawns.find(object);if(it!=pawns.end()&&!samePawn(it->second)){for(auto& p:it->second.part)drop(p);pawns.erase(it);pending.erase(object);}
 Pawn& p=pawns[object];p.object=object;p.index=at<int>(object,4);p.name=at<uint32_t>(object,0x20);p.klass=at<void*>(object,0x24);p.color=value;p.model=at<int>(object,0x698);p.style=at<int>(user,0x240);
 auto& copy=pending[object].user;copy.resize(0xc5);std::memcpy(copy.data(),user,0xc5*4);at<uint32_t>(copy.data(),0x244)=hair::legacy(value);
 if(pawns.size()>256){auto old=pawns.begin();if(old->first==object)++old;for(auto& part:old->second.part)drop(part);pending.erase(old->first);pawns.erase(old);}
}
static void pollBody(){
 if(!initialize())return;std::lock_guard<std::recursive_mutex> lock(guard);static ULONGLONG last=0;auto now=GetTickCount64();if(now-last<30)return;last=now;
 for(auto it=pawns.begin();it!=pawns.end();){auto& p=it->second;if(!samePawn(p)){for(auto& part:p.part)drop(part);pending.erase(it->first);it=pawns.erase(it);continue;}
  auto copy=pending.find(it->first);applyPawn(p,copy==pending.end()?nullptr:copy->second.user.data());++it;}
}
static void poll(){__try{pollBody();}__except(EXCEPTION_EXECUTE_HANDLER){failed=true;log("DISABLED HSL recoloring: unexpected native state; classic rendering preserved.");}}
extern "C" void __fastcall NexusHairTexture(void* device,void*,int x,int y,int w,int h,int u,int v,int uw,int vh,void* mat,int alpha,int flags){
 if(!nw)initialize();if(!failed)poll();if(originalTexture)originalTexture(device,x,y,w,h,u,v,uw,vh,mat,alpha,flags);preflight();
}
static void userBody(void* user,void* caller){
 initialize();if(!originalUser)return;std::lock_guard<std::recursive_mutex> lock(guard);
 uint32_t value=at<uint32_t>(user,0x244);bool preview=ui.setup&&caller>=nw+0x196000&&caller<nw+0x19a200;
 if(preview){ui.legacy=hair::legacy(value);if(ui.free)value=hair::encode(hair::rgb(ui.h,ui.s,ui.l),ui.legacy);}
 at<uint32_t>(user,0x244)=hair::legacy(value);originalUser(user);at<uint32_t>(user,0x244)=value;
 if(!failed)track(user,value);
}
extern "C" void __fastcall NexusHairUser(void* user,void*){userBody(user,_ReturnAddress());}
extern "C" void* __fastcall NexusHairTexName(void* user,void*,uint32_t* result,int slot,int index){
 if(!eng)initialize();if(!originalTexName){*result=0;return result;}
 uint32_t value=at<uint32_t>(user,0x244);at<uint32_t>(user,0x244)=hair::legacy(value);void* out=originalTexName(user,result,slot,index);at<uint32_t>(user,0x244)=value;return out;
}

static bool inside(int x,int y,int l,int t,int w,int h){return x>=l&&y>=t&&x<l+w&&y<t+h;}
static bool input(UINT msg,int x,int y){
 if(GetTickCount64()-ui.lastDraw>250)return false;
 x-=ui.x;y-=ui.y;bool in=inside(x,y,0,0,ui.w,ui.height);
 if(msg==WM_LBUTTONUP&&ui.drag){ui.drag=0;ReleaseCapture();return true;}
 if(msg==WM_LBUTTONDOWN&&in){
  if(inside(x,y,12,36,124,27)){ui.free=false;ui.dirty=ui.rebuild=true;return true;}
  if(inside(x,y,138,36,124,27)){ui.free=true;ui.dirty=ui.rebuild=true;return true;}
  if(ui.free&&inside(x,y,18,88,238,122))ui.drag=1;
  else if(ui.free&&inside(x,y,18,235,238,18))ui.drag=2;
  else if(ui.free&&inside(x,y,18,306,238,24)){ui.h=30;ui.s=55;ui.l=45;ui.dirty=ui.rebuild=true;}
  if(ui.drag)SetCapture(gameWindow);
 }
 if(ui.drag&&(msg==WM_MOUSEMOVE||msg==WM_LBUTTONDOWN)){
  if(ui.drag==1){ui.h=hair::clamp((x-18)*359.f/237,0,359);ui.s=hair::clamp((209-y)*100.f/121,0,100);}
  else ui.l=hair::clamp((x-18)*100.f/237,0,100);
  ui.dirty=ui.rebuild=true;return true;
 }
 return in&&(msg==WM_LBUTTONDOWN||msg==WM_LBUTTONUP||msg==WM_RBUTTONDOWN||msg==WM_RBUTTONUP||msg==WM_MOUSEWHEEL);
}
static LRESULT CALLBACK windowProc(HWND w,UINT msg,WPARAM wp,LPARAM lp){
 if(msg==WM_LBUTTONDOWN||msg==WM_LBUTTONUP||msg==WM_MOUSEMOVE||msg==WM_RBUTTONDOWN||msg==WM_RBUTTONUP){
  RECT r;GetClientRect(w,&r);int x=GET_X_LPARAM(lp),y=GET_Y_LPARAM(lp);if(r.right>0&&r.bottom>0&&screenX&&screenY){x=x*(*screenX)/r.right;y=y*(*screenY)/r.bottom;}if(input(msg,x,y))return 0;
 }
 if(msg==WM_KILLFOCUS||msg==WM_CANCELMODE||msg==WM_CAPTURECHANGED)ui.drag=0;
 return oldProc?CallWindowProcW(oldProc,w,msg,wp,lp):DefWindowProcW(w,msg,wp,lp);
}
static void attachWindow(){
 if(gameWindow&&IsWindow(gameWindow))return;HWND w=GetActiveWindow();DWORD pid=0;GetWindowThreadProcessId(w,&pid);if(!w||pid!=GetCurrentProcessId())return;
 SetLastError(0);auto prior=reinterpret_cast<WNDPROC>(SetWindowLongPtrW(w,GWLP_WNDPROC,reinterpret_cast<LONG_PTR>(windowProc)));if(prior){gameWindow=w;oldProc=prior;log("ATTACHED creator input to the existing game viewport.");}
}
static COLORREF gdiColor(uint32_t c){return RGB(c>>16&255,c>>8&255,c&255);}
static void rect(HDC dc,int x,int y,int w,int h,uint32_t c){RECT r{x,y,x+w,y+h};HBRUSH b=CreateSolidBrush(gdiColor(c));FillRect(dc,&r,b);DeleteObject(b);}
static void label(HDC dc,int x,int y,const wchar_t* text,uint32_t c=0xe0d9c7){SetTextColor(dc,gdiColor(c));TextOutW(dc,x,y,text,int(wcslen(text)));}
static void panelPixels(){
 if(!ui.tex)ui.tex=newTexture(512,512,2);if(!ui.tex)return;
 BITMAPINFO info{};info.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);info.bmiHeader.biWidth=512;info.bmiHeader.biHeight=-512;info.bmiHeader.biPlanes=1;info.bmiHeader.biBitCount=32;info.bmiHeader.biCompression=BI_RGB;
 void* bits=nullptr;HDC dc=CreateCompatibleDC(nullptr);HBITMAP bmp=CreateDIBSection(dc,&info,DIB_RGB_COLORS,&bits,nullptr,0);if(!dc||!bmp||!bits){if(bmp)DeleteObject(bmp);if(dc)DeleteDC(dc);return;}
 auto oldBmp=SelectObject(dc,bmp);HFONT font=CreateFontW(-13,0,0,0,FW_NORMAL,FALSE,FALSE,FALSE,DEFAULT_CHARSET,0,0,CLEARTYPE_QUALITY,0,L"Tahoma");auto oldFont=SelectObject(dc,font);SetBkMode(dc,TRANSPARENT);
 rect(dc,0,0,512,512,0x171a1b);rect(dc,0,0,ui.w,1,0x9e8b62);rect(dc,0,ui.height-1,ui.w,1,0x9e8b62);rect(dc,0,0,1,ui.height,0x9e8b62);rect(dc,ui.w-1,0,1,ui.height,0x9e8b62);
 label(dc,16,12,L"COLOR DEL CABELLO",0xe7d5a9);
 rect(dc,12,36,124,27,ui.free?0x252a2b:0x5c4e31);rect(dc,138,36,124,27,ui.free?0x5c4e31:0x252a2b);label(dc,37,42,L"Cl\u00e1sico A\u2013D");label(dc,175,42,L"Libre HSL");
 if(!ui.free)label(dc,15,73,L"Usa Hair Color en el panel izquierdo.",0xaaa89e);
 else {
  label(dc,18,70,L"Tono / saturaci\u00f3n",0xaaa89e);
  auto dst=static_cast<uint32_t*>(bits);for(int y=0;y<122;y++)for(int x=0;x<238;x++)dst[(y+88)*512+x+18]=hair::rgb(x*359.f/237,(121-y)*100.f/121,ui.l);
  int cx=18+int(ui.h*237/359),cy=209-int(ui.s*121/100);HPEN pen=CreatePen(PS_SOLID,1,RGB(255,255,255));auto oldPen=SelectObject(dc,pen);auto oldBrush=SelectObject(dc,GetStockObject(NULL_BRUSH));Ellipse(dc,cx-4,cy-4,cx+5,cy+5);SelectObject(dc,oldBrush);SelectObject(dc,oldPen);DeleteObject(pen);
  label(dc,18,218,L"Luminosidad",0xaaa89e);for(int x=0;x<238;x++){uint32_t c=hair::rgb(ui.h,ui.s,x*100.f/237);for(int y=235;y<253;y++)dst[y*512+x+18]=c;}
  int lx=18+int(ui.l*237/100);rect(dc,lx,234,1,20,0xffffff);
  wchar_t values[100];swprintf_s(values,L"H %03.0f\u00b0   S %03.0f%%   L %03.0f%%",ui.h,ui.s,ui.l);label(dc,18,266,values);
  auto c=hair::rgb(ui.h,ui.s,ui.l);rect(dc,18,286,28,14,c);swprintf_s(values,L"#%06X",c);label(dc,55,285,values,0xe7d5a9);
  rect(dc,18,306,238,24,0x333b3c);label(dc,101,311,L"Restablecer");label(dc,18,339,L"Se guarda al crear el personaje.",0xaaa89e);
 }
 auto src=static_cast<uint32_t*>(bits);for(int i=0;i<512*512;i++)src[i]|=0xff000000;
 uint32_t* out=dataOf(ui.tex);if(out){std::memcpy(out,src,512*512*4);dirty(ui.tex);}SelectObject(dc,oldFont);DeleteObject(font);SelectObject(dc,oldBmp);DeleteObject(bmp);DeleteDC(dc);ui.dirty=false;
}
static void preflightBody(){
 static bool checked=false;if(checked||!ready)return;checked=true;
 if(GetPrivateProfileIntW(L"Test",L"NativePreflight",0,(folder+L"NexusHairHslQA.ini").c_str())!=1)return;
 std::vector<std::vector<uint32_t>> variants;void* first=nullptr;int width=0,height=0;
 for(int i=0;i<4;i++){
  wchar_t name[160];swprintf_s(name,L"NexusHairT2M11.MElf_T2_1_Color%d_Mat0",i);
  void* mat=loadObject(materialClass,nullptr,name,nullptr,0x8000,nullptr);void* tex=bitmap(mat);std::vector<uint32_t> p;int w=0,h=0;
  if(!pixels(tex,p,w,h)){char report[220];sprintf_s(report,"QA load color=%d material=%p texture=%p w=%d h=%d format=%d mips=%d",i,mat,tex,w,h,tex?at<uint8_t>(tex,0x578):-1,tex?at<int>(tex,0x5f4):-1);log(report);throw 1;}if(!first){first=mat;width=w;height=h;}if(w!=width||h!=height)throw 2;variants.push_back(std::move(p));
 }
 auto mask=hair::differenceMask(variants);size_t hairPixels=0,protectedPixels=0;for(auto value:mask){if(value)++hairPixels;else++protectedPixels;}if(!hairPixels||!protectedPixels)throw 3;
 void* dynamic=newTexture(width,height,at<uint32_t>(bitmap(first),0x5c0));if(!dynamic||!dataOf(dynamic))throw 4;
 hair::tint(variants[0],mask,0x319bdb,dataOf(dynamic));dirty(dynamic);
 for(size_t i=0;i<mask.size();i++){auto output=dataOf(dynamic)[i];if((output&0xff000000)!=(variants[0][i]&0xff000000))throw 5;if(!mask[i]&&output!=variants[0][i])throw 6;}
 std::vector<void*> roots;void* composed=wrap(first,dynamic,roots);if(!composed||!bitmap(composed))throw 7;
 ui.free=true;ui.height=365;panelPixels();if(!ui.tex||!dataOf(ui.tex))throw 8;DWORD gdi=GetGuiResources(GetCurrentProcess(),GR_GDIOBJECTS);
 for(int i=0;i<10;i++){ui.dirty=true;panelPixels();}DWORD after=GetGuiResources(GetCurrentProcess(),GR_GDIOBJECTS);if(after!=gdi)throw 9;
 // A diagnostic bitmap of the exact native panel pixels, not an in-game screenshot.
 BITMAPFILEHEADER file{};BITMAPINFOHEADER info{};file.bfType=0x4d42;file.bfOffBits=sizeof(file)+sizeof(info);file.bfSize=file.bfOffBits+512*512*4;info.biSize=sizeof(info);info.biWidth=512;info.biHeight=-512;info.biPlanes=1;info.biBitCount=32;info.biCompression=BI_RGB;
 HANDLE f=CreateFileW((folder+L"HslNativePanelQA.bmp").c_str(),GENERIC_WRITE,FILE_SHARE_READ,nullptr,CREATE_ALWAYS,0,nullptr);if(f!=INVALID_HANDLE_VALUE){DWORD n;WriteFile(f,&file,sizeof(file),&n,nullptr);WriteFile(f,&info,sizeof(info),&n,nullptr);WriteFile(f,dataOf(ui.tex),512*512*4,&n,nullptr);CloseHandle(f);}
 ui.free=false;ui.height=94;ui.dirty=true;
 for(void* o:roots)removeRoot(o);removeRoot(dynamic);
 char report[240];sprintf_s(report,"PASS native preflight: RGBA texture=%dx%d; hair mask=%u protected=%u; alpha exact; wrapper clone; panel native UTexture; GDI handles stable=%lu.",width,height,unsigned(hairPixels),unsigned(protectedPixels),after);log(report);
}
static void preflightCpp(){try{preflightBody();}catch(int code){char report[100];sprintf_s(report,"FAIL native preflight: contract stage %d.",code);log(report);}catch(...){log("FAIL native preflight: C++ exception.");}}
static void preflightGuard(){
 __try{preflightCpp();}__except(EXCEPTION_EXECUTE_HANDLER){log("FAIL native preflight: native access violation.");}
}
static void preflight(){
 preflightGuard();
 if(ready&&GetPrivateProfileIntW(L"Test",L"QuitAfterPreflight",0,(folder+L"NexusHairHslQA.ini").c_str())==1){log("EXIT isolated native preflight process.");ExitProcess(0);}
}
static void drawBody(void* self,void* device){
 if(!initialize()||failed)return;std::lock_guard<std::recursive_mutex> lock(guard);
 if(ui.setup!=self){ui.setup=self;ui.free=false;ui.rebuild=false;ui.dirty=true;}
 if(at<int>(self,0x1f0)<0||at<int>(self,0x1fc)<0){if(ui.free){ui.free=false;ui.dirty=true;}return;}
 ui.lastDraw=GetTickCount64();attachWindow();int width=*screenX,height=*screenY;if(width<640||height<480)return;
 ui.x=width-ui.w-20;ui.y=36;int wanted=ui.free?365:94;if(wanted!=ui.height){ui.height=wanted;ui.dirty=true;}
 int legacy=at<int>(self,0x200);if(legacy>=0&&legacy<4)ui.legacy=legacy;
 if(ui.rebuild&&GetTickCount64()-ui.lastApply>40){ui.lastApply=GetTickCount64();ui.rebuild=false;using SetColor=void(__thiscall*)(void*,int);reinterpret_cast<SetColor>(nw+0x197e70)(self,ui.legacy);}
 void* combo=at<void*>(self,0x1dc);if(combo){using Enable=void(__thiscall*)(void*,int);auto fn=reinterpret_cast<Enable>(at<void**>(combo,0)[0x118/4]);fn(combo,ui.free?0:1);}
 if(ui.dirty)panelPixels();if(!ui.tex)return;
 using Clip=void(__thiscall*)(void*,int,int,int,int);using Origin=void(__thiscall*)(void*,int,int);using ResetClip=void(__thiscall*)(void*);
 reinterpret_cast<Clip>(nw+0x21df0)(device,0,0,width,height);reinterpret_cast<Origin>(nw+0x2f40)(device,0,0);
 originalTexture(device,ui.x,ui.y,ui.w,ui.height,0,0,ui.w,ui.height,ui.tex,255,1);reinterpret_cast<ResetClip>(nw+0x212e0)(device);
}
static void drawSafe(void* self,void* device){__try{drawBody(self,device);}__except(EXCEPTION_EXECUTE_HANDLER){failed=true;log("DISABLED creator panel: unexpected native layout. Classic remains available.");}}
extern "C" int __fastcall NexusHairDraw(void* self,void*,void* device){if(!nw)initialize();int result=originalDraw?originalDraw(self,device):0;if(!failed)drawSafe(self,device);return result;}
static void __cdecl packetBody(uint32_t* info){
 initialize();if(!failed&&ui.free&&ui.setup&&GetTickCount64()-ui.lastDraw<2000)info[22]=hair::encode(hair::rgb(ui.h,ui.s,ui.l),ui.legacy);
}
extern "C" __declspec(naked) void NexusHairPacket(){__asm{
 pushfd
 pushad
 lea eax,[esp+40]
 push eax
 call packetBody
 add esp,4
 popad
 popfd
 jmp dword ptr [packetTrampoline]
}}
BOOL WINAPI DllMain(HINSTANCE module,DWORD reason,LPVOID){if(reason==DLL_PROCESS_ATTACH)DisableThreadLibraryCalls(module);return TRUE;}
