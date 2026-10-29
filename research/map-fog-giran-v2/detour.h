#pragma once
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstring>
#include <cstdint>

// Restricted to the exact five-byte instruction sequence verified with REA.
// There are no relative instructions to relocate in this prologue.
struct EntryDetour {
    unsigned char* target=nullptr;
    unsigned char* trampoline=nullptr;
    bool install(void* function,void* replacement) {
        static const unsigned char expected[5]={0x55,0x8b,0xec,0x6a,0xff};
        auto p=static_cast<unsigned char*>(function);
        if(target||std::memcmp(p,expected,5))return false;
        auto t=static_cast<unsigned char*>(VirtualAlloc(nullptr,10,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
        if(!t)return false;
        std::memcpy(t,p,5);t[5]=0xe9;
        *reinterpret_cast<std::int32_t*>(t+6)=static_cast<std::int32_t>((p+5)-(t+10));
        DWORD old=0;
        if(!VirtualProtect(t,10,PAGE_EXECUTE_READ,&old)){VirtualFree(t,0,MEM_RELEASE);return false;}
        FlushInstructionCache(GetCurrentProcess(),t,10);
        if(!VirtualProtect(p,5,PAGE_EXECUTE_READWRITE,&old)){VirtualFree(t,0,MEM_RELEASE);return false;}
        unsigned char jump[5]={0xe9};
        *reinterpret_cast<std::int32_t*>(jump+1)=static_cast<std::int32_t>(static_cast<unsigned char*>(replacement)-(p+5));
        std::memcpy(p,jump,5);DWORD unused=0;VirtualProtect(p,5,old,&unused);
        FlushInstructionCache(GetCurrentProcess(),p,5);
        target=p;trampoline=t;return true;
    }
    bool restore() {
        if(!target)return true;
        DWORD old=0;if(!VirtualProtect(target,5,PAGE_EXECUTE_READWRITE,&old))return false;
        std::memcpy(target,trampoline,5);DWORD unused=0;VirtualProtect(target,5,old,&unused);
        FlushInstructionCache(GetCurrentProcess(),target,5);
        VirtualFree(trampoline,0,MEM_RELEASE);target=trampoline=nullptr;return true;
    }
};
