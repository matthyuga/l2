#pragma once
#include "fog_field.h"

namespace fog4 {
// Short messages stay below legacy screen-message string buffers. Apply only
// complete snapshots; a missing piece must never erase previously known land.
struct Assembly {
    std::wstring player,sequence;
    std::vector<std::wstring> parts;
    ULONGLONG started=0;
    int accept(const wchar_t* text,size_t length,std::wstring& completed) {
        completed.clear();if(length>230)return -1;
        std::wstring input(text,length);std::vector<std::wstring> header;size_t pos=0;
        for(int i=0;i<5;++i){size_t at=input.find(L'|',pos);if(at==std::wstring::npos)return -1;header.push_back(input.substr(pos,at-pos));pos=at+1;}
        if(header[0]!=L"#NXFC4")return -1;
        unsigned values[4]{};
        for(int i=1;i<5;++i){if(header[i].empty()||header[i].size()>10)return -1;unsigned long long v=0;for(wchar_t c:header[i]){if(c<L'0'||c>L'9')return -1;v=v*10+c-L'0';}if(v>0x7fffffff)return -1;values[i-1]=static_cast<unsigned>(v);}
        unsigned index=values[2],count=values[3];std::wstring payload=input.substr(pos);
        if(!values[0]||!count||count>86||index>=count||payload.empty()||payload.size()>64)return -1;
        ULONGLONG now=GetTickCount64();
        if(player!=header[1]||sequence!=header[2]||now-started>5000){player=header[1];sequence=header[2];parts.assign(count,L"");started=now;}
        if(parts.size()!=count)return -1;
        if(!parts[index].empty()&&parts[index]!=payload)return -1;
        parts[index]=payload;size_t size=0;
        for(const auto& p:parts){if(p.empty())return 0;size+=p.size();}
        if(size>5500)return -1;
        for(const auto& p:parts)completed+=p;
        Snapshot check;if(!parse(completed.c_str(),completed.size(),check)||check.player!=values[0]){completed.clear();return -1;}
        return 1;
    }
};
}
