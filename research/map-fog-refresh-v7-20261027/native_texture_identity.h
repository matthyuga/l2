#pragma once
#include <d3d9.h>
namespace fogNative {
inline void* materialOf(void* source) {
    if(!source)return nullptr;
    using Getter=void*(__thiscall*)(void*);
    auto table=*reinterpret_cast<void***>(source);
    void* texture=reinterpret_cast<Getter>(table[0x14/4])(source);
    if(!texture)return nullptr;
    table=*reinterpret_cast<void***>(texture);
    return reinterpret_cast<Getter>(table[0x50/4])(texture);
}
inline IDirect3DTexture9* gpuOf(void* cache) {
    return *reinterpret_cast<IDirect3DTexture9**>(static_cast<unsigned char*>(cache)+0x38);
}
inline bool wireAtlas(void* cache,IDirect3DTexture9* atlas) {
    if(!atlas)return false;auto slot=reinterpret_cast<IDirect3DTexture9**>(static_cast<unsigned char*>(cache)+0x38);
    if(*slot==atlas)return false;auto old=*slot;atlas->AddRef();*slot=atlas;if(old)old->Release();return true;
}
}
