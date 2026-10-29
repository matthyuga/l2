#pragma once
#define WIN32_LEAN_AND_MEAN
#include <windows.h>

namespace fog {
// REA verified NCGDevice::GetFinalAlpha: argument255 inherits byte+74,
// halved when dword+70 is nonzero. Change that context only for our drawing.
// SEH finally restores the previous state even if drawing raises an exception.
inline void withFullWindowAlpha(void* device,void(*draw)(void*),void* context) {
    auto bytes=static_cast<unsigned char*>(device);
    auto flags=reinterpret_cast<int*>(bytes+0x70);
    auto alpha=bytes+0x74;
    const int savedFlags=*flags;
    const unsigned char savedAlpha=*alpha;
    *flags=0;*alpha=255;
    __try {draw(context);}
    __finally {*flags=savedFlags;*alpha=savedAlpha;}
}
}
