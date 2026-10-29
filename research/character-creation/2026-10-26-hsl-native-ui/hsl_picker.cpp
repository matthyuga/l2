#define NEXUS_HSL_BUILD
#define NOMINMAX
#include "hsl_picker.h"
#include "hsl_math.h"
#include <windowsx.h>
#include <string>
#include <cwchar>
#include <new>

namespace {
const wchar_t* CLASS_NAME=L"Nexus.HairHsl.Picker.V1";
const COLORREF BG=RGB(23,29,35),INK=RGB(227,218,195),MUTED=RGB(159,166,169),GOLD=RGB(151,132,86),BORDER=RGB(89,91,79);
constexpr int W=426,H=602, ID_HEX=101,ID_H=102,ID_S=103,ID_L=104,ID_PROTECT=105,ID_ORIGINAL=106,ID_APPLY=107,ID_CANCEL=108;
const RECT PLANE={22,96,350,276},LIGHT={370,96,394,276};
const uint32_t PRESETS[12]={0x211D20,0x573B2B,0xAD7749,0xD5B97C,0xD7D9E0,0x707483,0x842C42,0xB46032,0x4C7770,0x476DA2,0x705392,0xAE668F};
struct Picker {
    HWND window=nullptr; NexusHslState initial,current; NexusHslCallback callback=nullptr;void* context=nullptr;
    HFONT font=nullptr,titleFont=nullptr;HBRUSH brush=nullptr;bool updating=false,done=false;int drag=0;
    ~Picker(){if(font)DeleteObject(font);if(titleFont)DeleteObject(titleFont);if(brush)DeleteObject(brush);}
};
HINSTANCE module(){HINSTANCE m=nullptr;GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,reinterpret_cast<LPCWSTR>(&module),&m);return m;}
Picker* get(HWND w){if(!w||!IsWindow(w))return nullptr;wchar_t name[96]={};GetClassNameW(w,name,96);return wcscmp(name,CLASS_NAME)?nullptr:reinterpret_cast<Picker*>(GetWindowLongPtrW(w,GWLP_USERDATA));}
bool validate(const NexusHslState* s){return s&&s->size==sizeof(NexusHslState)&&s->mode<=1&&s->legacyColor<=3&&s->protectOrnaments<=1&&hsl::valid(s->hue,s->saturation,s->lightness);}
void emit(Picker* p,uint32_t event,const NexusHslState& state){auto callback=p->callback;void* context=p->context;NexusHslState copy=state;if(callback)callback(event,&copy,context);}
void text(HDC dc,int x,int y,int w,int h,const wchar_t* value,COLORREF color,UINT flags=DT_LEFT|DT_VCENTER|DT_SINGLELINE){RECT r={x,y,x+w,y+h};SetTextColor(dc,color);SetBkMode(dc,TRANSPARENT);DrawTextW(dc,value,-1,&r,flags);}
void line(HDC dc,int x,int y,int x2,int y2,COLORREF color){HPEN pen=CreatePen(PS_SOLID,1,color);auto old=SelectObject(dc,pen);MoveToEx(dc,x,y,nullptr);LineTo(dc,x2,y2);SelectObject(dc,old);DeleteObject(pen);}
void fill(HDC dc,const RECT& r,COLORREF color){HBRUSH b=CreateSolidBrush(color);FillRect(dc,&r,b);DeleteObject(b);}
void border(HDC dc,const RECT& r,COLORREF color){HBRUSH b=CreateSolidBrush(color);FrameRect(dc,&r,b);DeleteObject(b);}
void controls(Picker* p){
    p->updating=true;wchar_t value[40];swprintf_s(value,L"#%06X",p->current.rgb);SetDlgItemTextW(p->window,ID_HEX,value);
    const float f[]={p->current.hue,p->current.saturation,p->current.lightness};for(int i=0;i<3;i++){swprintf_s(value,L"%.1f",f[i]);SetDlgItemTextW(p->window,ID_H+i,value);}
    SendDlgItemMessageW(p->window,ID_PROTECT,BM_SETCHECK,p->current.protectOrnaments?BST_CHECKED:BST_UNCHECKED,0);p->updating=false;
}
void refresh(Picker* p,bool preview){p->current.rgb=hsl::rgb(p->current.hue,p->current.saturation,p->current.lightness);controls(p);InvalidateRect(p->window,nullptr,FALSE);if(preview)emit(p,NexusPreview,p->current);}
void finish(Picker* p,bool accept){if(p->done)return;p->done=true;HWND w=p->window;NexusHslState result=accept?p->current:p->initial;emit(p,accept?NexusApply:NexusCancel,result);if(IsWindow(w))DestroyWindow(w);}
void updatePoint(Picker* p,int x,int y){
    if(p->drag==1){p->current.hue=hsl::clamp((x-PLANE.left)*359.9f/(PLANE.right-PLANE.left-1),0,359.9f);p->current.saturation=hsl::clamp((PLANE.bottom-1-y)*100.0f/(PLANE.bottom-PLANE.top-1),0,100);}
    else if(p->drag==2)p->current.lightness=hsl::clamp((LIGHT.bottom-1-y)*100.0f/(LIGHT.bottom-LIGHT.top-1),0,100);
    else if(p->drag>=3&&p->drag<=5){float v=hsl::clamp((x-112)/210.0f,0,1);if(p->drag==3)p->current.hue=v*359.9f;else if(p->drag==4)p->current.saturation=v*100;else p->current.lightness=v*100;}
    p->current.mode=NexusCustom;refresh(p,true);
}
void gradient(HDC dc,Picker* p){
    for(int y=PLANE.top;y<PLANE.bottom;y++)for(int x=PLANE.left;x<PLANE.right;x++)SetPixelV(dc,x,y,hsl::color(hsl::rgb((x-PLANE.left)*359.9f/(PLANE.right-PLANE.left-1),(PLANE.bottom-1-y)*100.0f/(PLANE.bottom-PLANE.top-1),50)));
    for(int y=LIGHT.top;y<LIGHT.bottom;y++){COLORREF c=hsl::color(hsl::rgb(p->current.hue,p->current.saturation,(LIGHT.bottom-1-y)*100.0f/(LIGHT.bottom-LIGHT.top-1)));fill(dc,RECT{LIGHT.left,y,LIGHT.right,y+1},c);}
    border(dc,PLANE,BORDER);border(dc,LIGHT,BORDER);int x=PLANE.left+static_cast<int>(p->current.hue/359.9f*(PLANE.right-PLANE.left-1)),y=PLANE.bottom-1-static_cast<int>(p->current.saturation/100*(PLANE.bottom-PLANE.top-1));
    HPEN white=CreatePen(PS_SOLID,2,RGB(255,255,255));auto old=SelectObject(dc,white);auto oldBrush=SelectObject(dc,GetStockObject(NULL_BRUSH));Ellipse(dc,x-5,y-5,x+6,y+6);SelectObject(dc,oldBrush);SelectObject(dc,old);DeleteObject(white);
    int ly=LIGHT.bottom-1-static_cast<int>(p->current.lightness/100*(LIGHT.bottom-LIGHT.top-1));border(dc,RECT{LIGHT.left-3,ly-2,LIGHT.right+3,ly+3},INK);
}
void paint(Picker* p,HDC target){
    HDC dc=CreateCompatibleDC(target);HBITMAP bitmap=CreateCompatibleBitmap(target,W,H);auto previous=SelectObject(dc,bitmap);fill(dc,RECT{0,0,W,H},BG);border(dc,RECT{0,0,W,H},GOLD);border(dc,RECT{3,3,W-3,H-3},BORDER);
    fill(dc,RECT{5,5,W-5,36},RGB(42,48,47));line(dc,6,36,W-6,36,GOLD);SelectObject(dc,p->titleFont);text(dc,18,7,340,25,L"Color del cabello",INK);SelectObject(dc,p->font);text(dc,W-31,7,20,25,L"×",INK,DT_CENTER|DT_SINGLELINE|DT_VCENTER);
    text(dc,22,49,365,20,L"Personalizar tono, saturación y luminosidad",MUTED);text(dc,22,74,328,18,L"Tono horizontal · saturación vertical",MUTED);gradient(dc,p);
    fill(dc,RECT{22,294,89,346},hsl::color(p->current.rgb));border(dc,RECT{22,294,89,346},GOLD);text(dc,102,289,150,18,L"Color elegido · HEX",MUTED);
    wchar_t value[80];swprintf_s(value,L"R %u     G %u     B %u",(p->current.rgb>>16)&255,(p->current.rgb>>8)&255,p->current.rgb&255);text(dc,102,337,260,18,value,MUTED);
    // Draw a backing value too: hidden-window PrintWindow does not paint the
    // Windows EDIT client area on every theme. Live EDIT controls overlay it.
    for(int id=ID_HEX;id<=ID_L;id++){RECT r=id==ID_HEX?RECT{102,310,250,335}:RECT{336,361+(id-ID_H)*34,394,386+(id-ID_H)*34};fill(dc,r,RGB(15,21,27));border(dc,r,BORDER);wchar_t content[40]={};GetDlgItemTextW(p->window,id,content,40);text(dc,r.left+5,r.top+1,r.right-r.left-10,r.bottom-r.top-2,content,INK);}
    const wchar_t* labels[]={L"Tono",L"Saturación",L"Luminosidad"};float values[]={p->current.hue/359.9f,p->current.saturation/100,p->current.lightness/100};
    for(int i=0;i<3;i++){int y=374+i*34;text(dc,22,y-10,88,25,labels[i],INK);fill(dc,RECT{112,y-3,322,y+3},RGB(65,73,78));border(dc,RECT{112,y-3,322,y+3},BORDER);int x=112+static_cast<int>(values[i]*210);fill(dc,RECT{x-4,y-8,x+5,y+9},GOLD);border(dc,RECT{x-4,y-8,x+5,y+9},INK);}
    line(dc,22,464,394,464,BORDER);text(dc,22,470,170,18,L"Tonos de partida",MUTED);for(int i=0;i<12;i++){int x=22+i*31;fill(dc,RECT{x,493,x+24,514},hsl::color(PRESETS[i]));border(dc,RECT{x,493,x+24,514},BORDER);}
    text(dc,22,574,372,17,p->current.mode==NexusOriginal?L"Se conservará el color original A–D.":L"Previsualización del color personalizado",MUTED);
    BitBlt(target,0,0,W,H,dc,0,0,SRCCOPY);SelectObject(dc,previous);DeleteObject(bitmap);DeleteDC(dc);
}
HWND child(Picker* p,LPCWSTR cl,LPCWSTR label,DWORD style,int id,int x,int y,int w,int h){HWND c=CreateWindowExW(cl==std::wstring(L"EDIT")?WS_EX_CLIENTEDGE:0,cl,label,WS_CHILD|WS_VISIBLE|style,x,y,w,h,p->window,reinterpret_cast<HMENU>(static_cast<INT_PTR>(id)),module(),nullptr);SendMessageW(c,WM_SETFONT,reinterpret_cast<WPARAM>(p->font),TRUE);return c;}
LRESULT CALLBACK proc(HWND w,UINT msg,WPARAM wp,LPARAM lp){
    Picker* p=reinterpret_cast<Picker*>(GetWindowLongPtrW(w,GWLP_USERDATA));
    if(msg==WM_NCCREATE){p=static_cast<Picker*>(reinterpret_cast<CREATESTRUCTW*>(lp)->lpCreateParams);p->window=w;SetWindowLongPtrW(w,GWLP_USERDATA,reinterpret_cast<LONG_PTR>(p));}
    if(!p)return DefWindowProcW(w,msg,wp,lp);
    switch(msg){
    case WM_CREATE:
        p->font=CreateFontW(-14,0,0,0,FW_NORMAL,FALSE,FALSE,FALSE,DEFAULT_CHARSET,OUT_DEFAULT_PRECIS,CLIP_DEFAULT_PRECIS,CLEARTYPE_QUALITY,DEFAULT_PITCH,L"Segoe UI");p->titleFont=CreateFontW(-15,0,0,0,FW_SEMIBOLD,FALSE,FALSE,FALSE,DEFAULT_CHARSET,OUT_DEFAULT_PRECIS,CLIP_DEFAULT_PRECIS,CLEARTYPE_QUALITY,DEFAULT_PITCH,L"Segoe UI");p->brush=CreateSolidBrush(RGB(15,21,27));
        child(p,L"EDIT",L"",WS_TABSTOP|ES_AUTOHSCROLL,ID_HEX,102,310,148,25);SendDlgItemMessageW(w,ID_HEX,EM_SETLIMITTEXT,7,0);
        for(int i=0;i<3;i++){child(p,L"EDIT",L"",WS_TABSTOP|ES_AUTOHSCROLL,ID_H+i,336,361+i*34,58,25);SendDlgItemMessageW(w,ID_H+i,EM_SETLIMITTEXT,6,0);}
        child(p,L"BUTTON",L"Conservar máscaras y adornos",WS_TABSTOP|BS_AUTOCHECKBOX,ID_PROTECT,22,524,280,22);
        child(p,L"BUTTON",L"Original",WS_TABSTOP|BS_OWNERDRAW,ID_ORIGINAL,22,550,105,26);child(p,L"BUTTON",L"Aceptar",WS_TABSTOP|BS_OWNERDRAW,ID_APPLY,181,550,100,26);child(p,L"BUTTON",L"Cancelar",WS_TABSTOP|BS_OWNERDRAW,ID_CANCEL,292,550,102,26);controls(p);return 0;
    case WM_PAINT:{PAINTSTRUCT ps;HDC dc=BeginPaint(w,&ps);paint(p,dc);EndPaint(w,&ps);return 0;}
    case WM_PRINTCLIENT:paint(p,reinterpret_cast<HDC>(wp));return 0;
    case WM_ERASEBKGND:return 1;
    case WM_CTLCOLORSTATIC:case WM_CTLCOLOREDIT:case WM_CTLCOLORBTN:{HDC dc=reinterpret_cast<HDC>(wp);SetTextColor(dc,INK);SetBkColor(dc,RGB(15,21,27));return reinterpret_cast<LRESULT>(p->brush);}
    case WM_DRAWITEM:{auto draw=reinterpret_cast<DRAWITEMSTRUCT*>(lp);bool down=(draw->itemState&ODS_SELECTED)!=0;fill(draw->hDC,draw->rcItem,down?RGB(70,67,48):RGB(44,51,52));border(draw->hDC,draw->rcItem,GOLD);wchar_t s[80];GetWindowTextW(draw->hwndItem,s,80);SelectObject(draw->hDC,p->font);text(draw->hDC,draw->rcItem.left,draw->rcItem.top,draw->rcItem.right-draw->rcItem.left,draw->rcItem.bottom-draw->rcItem.top,s,INK,DT_CENTER|DT_VCENTER|DT_SINGLELINE);if(draw->itemState&ODS_FOCUS){RECT r=draw->rcItem;InflateRect(&r,-3,-3);DrawFocusRect(draw->hDC,&r);}return TRUE;}
    case WM_COMMAND:{int id=LOWORD(wp),event=HIWORD(wp);if(p->updating)return 0;
        if(id==ID_APPLY||id==IDOK){finish(p,true);return 0;}if(id==ID_CANCEL||id==IDCANCEL){finish(p,false);return 0;}
        if(id==ID_ORIGINAL){p->current.mode=NexusOriginal;refresh(p,true);return 0;}
        if(id==ID_PROTECT){p->current.protectOrnaments=SendDlgItemMessageW(w,id,BM_GETCHECK,0,0)==BST_CHECKED;refresh(p,true);return 0;}
        if(event==EN_CHANGE){wchar_t buffer[40]={};GetDlgItemTextW(w,id,buffer,40);if(!buffer[0])return 0;
            if(id==ID_HEX){std::wstring s=buffer;if(s[0]==L'#')s.erase(0,1);if(s.size()!=6||s.find_first_not_of(L"0123456789ABCDEFabcdef")!=std::wstring::npos)return 0;auto rgb=wcstoul(s.c_str(),nullptr,16);hsl::fromRgb(rgb,p->current.hue,p->current.saturation,p->current.lightness);}
            else if(id>=ID_H&&id<=ID_L){wchar_t* end=nullptr;float value=wcstof(buffer,&end);if(!end||*end||!std::isfinite(value))return 0;value=hsl::clamp(value,0,id==ID_H?359.9f:100.0f);if(id==ID_H)p->current.hue=value;else if(id==ID_S)p->current.saturation=value;else p->current.lightness=value;}
            else return 0;
            p->current.mode=NexusCustom;p->current.rgb=hsl::rgb(p->current.hue,p->current.saturation,p->current.lightness);InvalidateRect(w,nullptr,FALSE);emit(p,NexusPreview,p->current);
        }
        if(event==EN_KILLFOCUS)controls(p);return 0;}
    case WM_LBUTTONDOWN:{int x=GET_X_LPARAM(lp),y=GET_Y_LPARAM(lp);POINT pt={x,y};if(y<36){if(x>W-38){finish(p,false);return 0;}ReleaseCapture();SendMessageW(w,WM_NCLBUTTONDOWN,HTCAPTION,lp);return 0;}
        p->drag=PtInRect(&PLANE,pt)?1:PtInRect(&LIGHT,pt)?2:0;for(int i=0;i<3;i++)if(x>=105&&x<=328&&y>=362+i*34&&y<=386+i*34)p->drag=3+i;
        if(p->drag){SetCapture(w);updatePoint(p,x,y);return 0;}
        if(y>=493&&y<=514){int i=(x-22)/31;if(x>=22&&i>=0&&i<12&&(x-22)%31<24){hsl::fromRgb(PRESETS[i],p->current.hue,p->current.saturation,p->current.lightness);p->current.mode=NexusCustom;refresh(p,true);}}return 0;}
    case WM_MOUSEMOVE:if(p->drag)updatePoint(p,GET_X_LPARAM(lp),GET_Y_LPARAM(lp));return 0;
    case WM_LBUTTONUP:p->drag=0;if(GetCapture()==w)ReleaseCapture();return 0;
    case WM_CAPTURECHANGED:p->drag=0;return 0;
    case WM_KEYDOWN:if(wp==VK_ESCAPE){finish(p,false);return 0;}if(wp==VK_RETURN){finish(p,true);return 0;}break;
    case WM_CLOSE:finish(p,false);return 0;
    case WM_NCDESTROY:if(!p->done){p->done=true;emit(p,NexusCancel,p->initial);}SetWindowLongPtrW(w,GWLP_USERDATA,0);delete p;return DefWindowProcW(w,msg,wp,lp);
    }
    return DefWindowProcW(w,msg,wp,lp);
}
}
HWND __stdcall NexusHslOpen(HWND owner,const NexusHslState* initial,NexusHslCallback callback,void* context,DWORD options){
    if(!validate(initial)){SetLastError(ERROR_INVALID_PARAMETER);return nullptr;}if(owner&&GetWindowThreadProcessId(owner,nullptr)!=GetCurrentThreadId()){SetLastError(ERROR_INVALID_THREAD_ID);return nullptr;}
    WNDCLASSEXW wc={sizeof(wc)};wc.lpfnWndProc=proc;wc.hInstance=module();wc.hCursor=LoadCursor(nullptr,IDC_ARROW);wc.lpszClassName=CLASS_NAME;wc.style=CS_HREDRAW|CS_VREDRAW;RegisterClassExW(&wc);
    auto p=new(std::nothrow) Picker;if(!p)return nullptr;p->initial=*initial;p->current=*initial;p->current.rgb=hsl::rgb(initial->hue,initial->saturation,initial->lightness);p->callback=callback;p->context=context;
    RECT r={0,0,1024,768};if(owner)GetWindowRect(owner,&r);else SystemParametersInfoW(SPI_GETWORKAREA,0,&r,0);int x=r.right-W-24,y=r.top+60;RECT desktop;SystemParametersInfoW(SPI_GETWORKAREA,0,&desktop,0);x=std::max(static_cast<int>(desktop.left),std::min(x,static_cast<int>(desktop.right)-W));y=std::max(static_cast<int>(desktop.top),std::min(y,static_cast<int>(desktop.bottom)-H));
    HWND w=CreateWindowExW(WS_EX_TOOLWINDOW,CLASS_NAME,L"Color del cabello",WS_POPUP|WS_CLIPCHILDREN,x,y,W,H,owner,nullptr,module(),p);if(!w)return nullptr;if(!(options&1)){ShowWindow(w,SW_SHOWNORMAL);UpdateWindow(w);}return w;
}
BOOL __stdcall NexusHslRead(HWND picker,NexusHslState* output){auto p=get(picker);if(!p||!output||output->size!=sizeof(NexusHslState))return FALSE;*output=p->current;return TRUE;}
BOOL __stdcall NexusHslSet(HWND picker,const NexusHslState* state){auto p=get(picker);if(!p||!validate(state))return FALSE;p->current=*state;refresh(p,true);return TRUE;}
BOOL __stdcall NexusHslFinish(HWND picker,BOOL accept){auto p=get(picker);if(!p)return FALSE;finish(p,accept!=FALSE);return TRUE;}
