#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstring>
#include <cstddef>
struct Frame { volatile LONG sequence; DWORD magic,width,height; ULONGLONG tick; DWORD pixels[512*384]; };
static_assert(offsetof(Frame,pixels)==24,"Relay ABI mismatch");
extern "C" __declspec(dllexport) int PublishFrame(Frame* frame,const void* pixels,UINT length){
 if(!frame||!pixels||length!=512*384*4)return 0;
 if(frame->sequence&1)InterlockedIncrement(&frame->sequence);
 InterlockedIncrement(&frame->sequence);MemoryBarrier();
 frame->magic=0x3156544e;frame->width=512;frame->height=384;frame->tick=GetTickCount64();
 memcpy(frame->pixels,pixels,length);MemoryBarrier();InterlockedIncrement(&frame->sequence);return 1;
}
struct HDFrame { volatile LONG sequence; DWORD magic,width,height; ULONGLONG tick; DWORD pixels[1280*960]; };
static_assert(offsetof(HDFrame,pixels)==24,"HD relay ABI mismatch");
extern "C" __declspec(dllexport) int PublishFrameHD(HDFrame* frame,const void* pixels,UINT length){
 if(!frame||!pixels||length!=1280*960*4)return 0;
 if(frame->sequence&1)InterlockedIncrement(&frame->sequence);
 InterlockedIncrement(&frame->sequence);MemoryBarrier();
 frame->magic=0x3256544e;frame->width=1280;frame->height=960;frame->tick=GetTickCount64();
 memcpy(frame->pixels,pixels,length);MemoryBarrier();InterlockedIncrement(&frame->sequence);return 1;
}
