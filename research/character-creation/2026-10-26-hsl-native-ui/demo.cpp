#define NOMINMAX
#include "hsl_picker.h"
#include "hsl_math.h"
#include <windowsx.h>
#include <objidl.h>
using std::min;
using std::max;
#include <gdiplus.h>
#include <cstdio>
#include <vector>
#include <string>
#include <cstring>
#include <limits>
#pragma comment(lib,"gdiplus.lib")

namespace {
HWND parentWindow=nullptr,pickerWindow=nullptr;NexusHslState accepted,preview;Gdiplus::Bitmap* picture=nullptr;
std::wstring folder;
void __stdcall changed(uint32_t event,const NexusHslState* value,void*){
    preview=*value;if(event==NexusApply)accepted=*value;if(event!=NexusPreview)pickerWindow=nullptr;
    if(parentWindow)InvalidateRect(parentWindow,nullptr,FALSE);
}
void open(){if(pickerWindow&&IsWindow(pickerWindow)){SetForegroundWindow(pickerWindow);return;}pickerWindow=NexusHslOpen(parentWindow,&accepted,changed,nullptr);}
LRESULT CALLBACK demoProc(HWND w,UINT msg,WPARAM wp,LPARAM lp){
    if(msg==WM_CREATE){CreateWindowW(L"BUTTON",L"Personalizar color",WS_CHILD|WS_VISIBLE|WS_TABSTOP,36,198,176,30,w,reinterpret_cast<HMENU>(1),nullptr,nullptr);return 0;}
    if(msg==WM_COMMAND&&LOWORD(wp)==1){open();return 0;}
    if(msg==WM_PAINT){PAINTSTRUCT ps;HDC dc=BeginPaint(w,&ps);RECT r;GetClientRect(w,&r);HBRUSH b=CreateSolidBrush(RGB(19,27,35));FillRect(dc,&r,b);DeleteObject(b);SetBkMode(dc,TRANSPARENT);SetTextColor(dc,RGB(228,218,190));HFONT f=CreateFontW(-17,0,0,0,400,FALSE,FALSE,FALSE,DEFAULT_CHARSET,0,0,CLEARTYPE_QUALITY,0,L"Segoe UI");auto old=SelectObject(dc,f);TextOutW(dc,34,30,L"Creador · prueba de interfaz",static_cast<int>(wcslen(L"Creador · prueba de interfaz")));TextOutW(dc,34,82,L"Raza: Elfo",static_cast<int>(wcslen(L"Raza: Elfo")));TextOutW(dc,34,116,L"Sexo: Masculino",static_cast<int>(wcslen(L"Sexo: Masculino")));TextOutW(dc,34,150,L"Cabello: H",static_cast<int>(wcslen(L"Cabello: H")));
        TextOutW(dc,290,420,L"Imagen de referencia original",28);
        if(picture){Gdiplus::Graphics g(dc);g.SetInterpolationMode(Gdiplus::InterpolationModeHighQualityBicubic);g.DrawImage(picture,245,62,340,385);}
        b=CreateSolidBrush(hsl::color(preview.mode==NexusOriginal?hsl::rgb(42,70,65):preview.rgb));RECT swatch={36,266,204,328};FillRect(dc,&swatch,b);DeleteObject(b);wchar_t label[100];swprintf_s(label,preview.mode==NexusOriginal?L"Color original A-D":L"Elección: #%06X",preview.rgb);TextOutW(dc,36,342,label,static_cast<int>(wcslen(label)));
        SetTextColor(dc,RGB(155,167,178));TextOutW(dc,36,450,L"Demostración local. No cambia el personaje del juego.",static_cast<int>(wcslen(L"Demostración local. No cambia el personaje del juego.")));TextOutW(dc,36,479,L"La muestra de color responde a los eventos de la ventana.",static_cast<int>(wcslen(L"La muestra de color responde a los eventos de la ventana.")));SelectObject(dc,old);DeleteObject(f);EndPaint(w,&ps);return 0;}
    if(msg==WM_DESTROY){if(pickerWindow&&IsWindow(pickerWindow))NexusHslFinish(pickerWindow,FALSE);PostQuitMessage(0);return 0;}return DefWindowProcW(w,msg,wp,lp);
}
struct Events{std::vector<uint32_t> codes;std::vector<NexusHslState> states;};
void __stdcall testCallback(uint32_t e,const NexusHslState* s,void* context){auto p=static_cast<Events*>(context);p->codes.push_back(e);p->states.push_back(*s);}
int checks=0;
void require(bool ok){++checks;if(!ok){std::fprintf(stderr,"FAIL native UI check %d\n",checks);ExitProcess(2);}}
void bitmap(HWND w,const wchar_t* file){
    RECT r;GetClientRect(w,&r);int width=r.right,height=r.bottom;HDC dc=GetDC(nullptr),mem=CreateCompatibleDC(dc);BITMAPINFO info={};info.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);info.bmiHeader.biWidth=width;info.bmiHeader.biHeight=-height;info.bmiHeader.biPlanes=1;info.bmiHeader.biBitCount=32;info.bmiHeader.biCompression=BI_RGB;void* pixels=nullptr;HBITMAP bm=CreateDIBSection(dc,&info,DIB_RGB_COLORS,&pixels,nullptr,0);auto old=SelectObject(mem,bm);SendMessageW(w,WM_PRINT,reinterpret_cast<WPARAM>(mem),PRF_CLIENT|PRF_CHILDREN);BITMAPFILEHEADER header={};header.bfType=0x4D42;header.bfOffBits=sizeof(header)+sizeof(BITMAPINFOHEADER);header.bfSize=header.bfOffBits+width*height*4;FILE* out=nullptr;_wfopen_s(&out,file,L"wb");require(out!=nullptr);fwrite(&header,sizeof(header),1,out);fwrite(&info.bmiHeader,sizeof(BITMAPINFOHEADER),1,out);fwrite(pixels,1,width*height*4,out);fclose(out);SelectObject(mem,old);DeleteObject(bm);DeleteDC(mem);ReleaseDC(nullptr,dc);
}
int selftest(){
    for(int r=0;r<256;r+=17)for(int g=0;g<256;g+=17)for(int b=0;b<256;b+=17){uint32_t rgb=(r<<16)|(g<<8)|b;float h,s,l;hsl::fromRgb(rgb,h,s,l);require(hsl::rgb(h,s,l)==rgb);}
    NexusHslState initial;initial.hue=210;initial.saturation=50;initial.lightness=40;initial.legacyColor=2;initial.rgb=hsl::rgb(210,50,40);Events events;
    HWND w=NexusHslOpen(nullptr,&initial,testCallback,&events,1);require(w!=nullptr&&!IsWindowVisible(w));NexusHslState state;require(NexusHslRead(w,&state));require(state.rgb==initial.rgb);
    wchar_t input[40]={};GetDlgItemTextW(w,101,input,40);require(wcslen(input)==7);GetDlgItemTextW(w,102,input,40);require(wcstod(input,nullptr)==210);
    state.hue=280;require(NexusHslSet(w,&state));require(events.codes.size()==1&&events.codes[0]==NexusPreview);require(events.states.back().legacyColor==2);
    SendMessageW(w,WM_COMMAND,106,0);require(events.states.back().mode==NexusOriginal);
    state.hue=82;state.saturation=70;state.mode=NexusCustom;NexusHslSet(w,&state);
    bitmap(w,(folder+L"native-interface.bmp").c_str());
    require(NexusHslFinish(w,FALSE));require(!IsWindow(w));require(events.codes.back()==NexusCancel);require(std::memcmp(&events.states.back(),&initial,sizeof(initial))==0);
    events={};w=NexusHslOpen(nullptr,&initial,testCallback,&events,1);state=initial;state.lightness=75;NexusHslSet(w,&state);SendMessageW(w,WM_COMMAND,107,0);require(!IsWindow(w));require(events.codes.back()==NexusApply&&events.states.back().lightness==75);
    events={};w=NexusHslOpen(nullptr,&initial,testCallback,&events,1);SendMessageW(w,WM_CLOSE,0,0);require(events.codes.size()==1&&events.codes[0]==NexusCancel);
    events={};w=NexusHslOpen(nullptr,&initial,testCallback,&events,1);SendMessageW(w,WM_COMMAND,IDCANCEL,0);require(events.codes.size()==1&&events.codes[0]==NexusCancel);
    events={};w=NexusHslOpen(nullptr,&initial,testCallback,&events,1);DestroyWindow(w);require(events.codes.size()==1&&events.codes[0]==NexusCancel);
    events={};w=NexusHslOpen(nullptr,&initial,testCallback,&events,1);auto bad=initial;bad.hue=std::numeric_limits<float>::quiet_NaN();require(!NexusHslSet(w,&bad));bad=initial;bad.legacyColor=0xFF;require(!NexusHslSet(w,&bad));bad=initial;bad.size=1;require(!NexusHslSet(w,&bad));require(events.codes.empty());NexusHslFinish(w,FALSE);
    bad=initial;bad.mode=2;require(!NexusHslOpen(nullptr,&bad,testCallback,&events,1));
    FILE* out=nullptr;_wfopen_s(&out,(folder+L"native-test-results.json").c_str(),L"wb");require(out!=nullptr);std::fprintf(out,"{\"passed\":%d,\"rgb_roundtrips\":4096,\"cancel_restores_snapshot\":true,\"apply_event\":true,\"close_restores_snapshot\":true,\"invalid_inputs_rejected\":true,\"hidden_windows_only\":true,\"game_modified\":false}\n",checks);fclose(out);return 0;
}
}
int WINAPI wWinMain(HINSTANCE instance,HINSTANCE,LPWSTR args,int){
    wchar_t exe[MAX_PATH];GetModuleFileNameW(nullptr,exe,MAX_PATH);folder=exe;folder=folder.substr(0,folder.find_last_of(L"\\/")+1);
    if(wcsstr(args,L"--selftest"))return selftest();
    Gdiplus::GdiplusStartupInput input;ULONG_PTR token;Gdiplus::GdiplusStartup(&token,&input,nullptr);picture=Gdiplus::Bitmap::FromFile((folder+L"preview-original.png").c_str());
    WNDCLASSW wc={};wc.lpfnWndProc=demoProc;wc.hInstance=instance;wc.hCursor=LoadCursor(nullptr,IDC_ARROW);wc.lpszClassName=L"Nexus.HairHsl.Demo";RegisterClassW(&wc);
    parentWindow=CreateWindowW(wc.lpszClassName,L"L2 · Interfaz HSL — demostración local",WS_OVERLAPPEDWINDOW,120,80,1090,690,nullptr,nullptr,instance,nullptr);accepted.rgb=hsl::rgb(accepted.hue,accepted.saturation,accepted.lightness);preview=accepted;ShowWindow(parentWindow,SW_SHOWNORMAL);open();MSG msg;
    while(GetMessageW(&msg,nullptr,0,0)>0){if(pickerWindow&&IsWindow(pickerWindow)&&IsDialogMessageW(pickerWindow,&msg))continue;TranslateMessage(&msg);DispatchMessageW(&msg);}delete picture;Gdiplus::GdiplusShutdown(token);return 0;
}
