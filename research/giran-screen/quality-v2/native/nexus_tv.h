#pragma once
#include <windows.h>
#include <stdint.h>
namespace nxtv {
constexpr DWORD Magic=0x3156544e;
constexpr UINT Width=512,Height=384,TextureSize=512;
constexpr wchar_t Channel[]=L"Local\\NexusGiranTV_v1";
constexpr DWORD Marker[8]={0xff1234e0,0xffda7142,0xff28c56a,0xffa531c8,0xffe8b927,0xff347ad1,0xffcf4265,0xff71d8ac};
struct Frame { volatile LONG sequence; DWORD magic,width,height; ULONGLONG tick; DWORD pixels[Width*Height]; };
}
