#pragma once
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdint>

// Call on the owning UI thread, which must keep pumping Windows messages.
// These events are not game packets and do not modify a Player or account.
enum NexusHslEvent : uint32_t { NexusPreview=1, NexusApply=2, NexusCancel=3 };
enum NexusHslMode : uint32_t { NexusOriginal=0, NexusCustom=1 };
struct NexusHslState {
    uint32_t size=sizeof(NexusHslState);
    uint32_t mode=NexusCustom;
    float hue=25.0f, saturation=50.0f, lightness=42.0f;
    uint32_t rgb=0; // 0x00RRGGBB, recomputed for custom mode.
    uint32_t legacyColor=0; // Existing A-D index; never overwritten by RGB.
    uint32_t protectOrnaments=1;
};
using NexusHslCallback=void(__stdcall*)(uint32_t event,const NexusHslState* state,void* context);
#ifdef NEXUS_HSL_BUILD
#define NEXUS_HSL_API extern "C" __declspec(dllexport)
#else
#define NEXUS_HSL_API extern "C"
#endif
// options bit 0 creates an initially hidden window for automated tests.
NEXUS_HSL_API HWND __stdcall NexusHslOpen(HWND owner,const NexusHslState* initial,NexusHslCallback callback,void* context,DWORD options=0);
NEXUS_HSL_API BOOL __stdcall NexusHslRead(HWND picker,NexusHslState* output);
NEXUS_HSL_API BOOL __stdcall NexusHslSet(HWND picker,const NexusHslState* state);
NEXUS_HSL_API BOOL __stdcall NexusHslFinish(HWND picker,BOOL accept);
