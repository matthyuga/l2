#pragma once
#include <windows.h>
#include <wincrypt.h>
#include <array>
#include <string>
#include <vector>
#include <cmath>
#include <algorithm>
#include <cstdint>
#include <cstring>

namespace fog4 {
constexpr int Columns=100,Rows=150,Bytes=1875,Cell=4096;
constexpr int AtlasW=1024,AtlasH=2048;
constexpr double Scale=0.0050048828125;
using Bits=std::array<unsigned char,Bytes>;
struct Snapshot {Bits global{},personal{};unsigned player=0;};
inline bool decode(const std::wstring& text,Bits& result) {
    result.fill(0);if(text.empty())return true;
    if(text.size()>2500)return false;
    DWORD size=Bytes;
    return CryptStringToBinaryW(text.c_str(),static_cast<DWORD>(text.size()),CRYPT_STRING_BASE64|CRYPT_STRING_STRICT,result.data(),&size,nullptr,nullptr)!=FALSE;
}
inline bool parse(const wchar_t* text,size_t length,Snapshot& snapshot) {
    if(length>5500)return false;std::wstring input(text,length);
    std::vector<std::wstring> fields;size_t start=0;
    for(;;){size_t at=input.find(L'|',start);fields.push_back(input.substr(start,at==std::wstring::npos?at:at-start));if(at==std::wstring::npos)break;start=at+1;}
    if(fields.size()!=5||fields[0]!=L"#NXFOG4")return false;
    if(fields[1].empty()||fields[1].size()>10||fields[2].empty()||fields[2].size()>20)return false;
    for(wchar_t c:fields[1])if(c<L'0'||c>L'9')return false;
    for(wchar_t c:fields[2])if(c<L'0'||c>L'9')return false;
    unsigned long long id=0;for(wchar_t c:fields[1])id=id*10+c-L'0';
    if(!id||id>0x7fffffff)return false;
    Snapshot next;next.player=static_cast<unsigned>(id);
    if(!decode(fields[3],next.global)||!decode(fields[4],next.personal))return false;
    snapshot=next;return true;
}
inline double bit(const Bits& bits,int col,int row) {
    if(col<0||col>=Columns||row<0||row>=Rows)return 0;
    int index=row*Columns+col;return (bits[index/8]>>(index%8))&1;
}
inline double smooth(const Bits& bits,double x,double y) {
    int ix=static_cast<int>(std::floor(x)),iy=static_cast<int>(std::floor(y));double fx=x-ix,fy=y-iy;
    fx=fx*fx*(3-2*fx);fy=fy*fy*(3-2*fy);
    return (1-fy)*((1-fx)*bit(bits,ix,iy)+fx*bit(bits,ix+1,iy))+fy*((1-fx)*bit(bits,ix,iy+1)+fx*bit(bits,ix+1,iy+1));
}
inline unsigned char alpha(const Snapshot& s,double worldX,double worldY,double giranAlpha) {
    const double x=(worldX+131072)/Cell-.5,y=(worldY+262144)/Cell-.5;
    double personal=smooth(s.personal,x,y),global=smooth(s.global,x,y);
    double a=255*(1-personal)*(1-.45*global);
    return static_cast<unsigned char>(std::max(0.0,std::min(255.0,std::min(a,giranAlpha)))+.5);
}
}
