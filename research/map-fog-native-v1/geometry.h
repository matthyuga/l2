#pragma once
#include <algorithm>
namespace fog {
struct Rect {int x,y,w,h;};
inline Rect visibleRect(int centerX,int centerY,int width,int height,int scrollX,int scrollY,int viewW,int viewH) {
    const int left=centerX-width/2-scrollX,top=centerY-height/2-scrollY;
    const int x=std::max(0,left),y=std::max(0,top);
    const int right=std::min(viewW,left+width),bottom=std::min(viewH,top+height);
    return {x,y,std::max(0,right-x),std::max(0,bottom-y)};
}
}
