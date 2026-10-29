#pragma once
#include <d3d9.h>
namespace fogNative {
// The native material can treat its almost-opaque marker as an opaque draw.
// Apply the live atlas alpha for this draw only, restoring the caller's state.
struct FogDrawState {
    IDirect3DStateBlock9* saved=nullptr;
    DWORD priorBlend=0,priorAlphaOp=0;
    using BeforeDraw=void(*)(IDirect3DDevice9*,IDirect3DTexture9*);
    FogDrawState(IDirect3DDevice9* device,IDirect3DTexture9* atlas,BeforeDraw beforeDraw=nullptr) {
        if(!atlas)return;IDirect3DBaseTexture9* bound=nullptr;
        if(FAILED(device->GetTexture(0,&bound)))return;
        bool matches=bound==atlas;if(bound)bound->Release();if(!matches)return;
        if(beforeDraw)beforeDraw(device,atlas);
        device->GetRenderState(D3DRS_ALPHABLENDENABLE,&priorBlend);device->GetTextureStageState(0,D3DTSS_ALPHAOP,&priorAlphaOp);
        if(FAILED(device->CreateStateBlock(D3DSBT_ALL,&saved)))return;
        device->SetPixelShader(nullptr);
        device->SetRenderState(D3DRS_ALPHABLENDENABLE,TRUE);
        device->SetRenderState(D3DRS_SRCBLEND,D3DBLEND_SRCALPHA);
        device->SetRenderState(D3DRS_DESTBLEND,D3DBLEND_INVSRCALPHA);
        device->SetRenderState(D3DRS_BLENDOP,D3DBLENDOP_ADD);
        device->SetRenderState(D3DRS_ALPHATESTENABLE,FALSE);
        device->SetRenderState(D3DRS_SEPARATEALPHABLENDENABLE,FALSE);
        device->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE);
        device->SetTextureStageState(0,D3DTSS_COLORARG1,D3DTA_TEXTURE);
        device->SetTextureStageState(0,D3DTSS_COLORARG2,D3DTA_DIFFUSE);
        device->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_MODULATE);
        device->SetTextureStageState(0,D3DTSS_ALPHAARG1,D3DTA_TEXTURE);
        device->SetTextureStageState(0,D3DTSS_ALPHAARG2,D3DTA_DIFFUSE);
        device->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_DISABLE);
        device->SetSamplerState(0,D3DSAMP_ADDRESSU,D3DTADDRESS_CLAMP);
        device->SetSamplerState(0,D3DSAMP_ADDRESSV,D3DTADDRESS_CLAMP);
    }
    ~FogDrawState(){if(saved){saved->Apply();saved->Release();}}
};
}
