 ['A','B','C','D'].each{style->
  make('UseStyle'+style,null){emit,guard,api,p,buttonApi->
   pages.eachWithIndex{win,i->
    def controls=['Close','Original','Compensate','Opaque','Semi','Clear']+(i==0?['Explore','Greet']:[i==3?'Restart':'Next'])
    controls.each{n->emit(buttonApi(win+'.'+n,['Up','Down','Over'].collect{'NexusAmberButtonsV5.'+style+n+it}))}
    emit(api('SetTexture',[new StringConst(win+'.StyleBadge'),new StringConst('NexusAmberButtonsV5.Current'+style)],0,'NWindow.UIAPI_TEXTURECTRL'))
   }
  }
 }
