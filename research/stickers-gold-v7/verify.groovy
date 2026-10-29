import acmi.l2.clientmod.io.*
def s=new File(args[0])
new UnrealPackage(new File(s,'NexusStickerGoldV7.u'),true).withCloseable{up->
 def textures=up.exportTable.findAll{it.fullClassName=='Engine.Texture'}
 def expected=['Wheel','Title','HintPlate']
 (0..<8).each{i->['Up','Over','Down'].each{state->expected<<'S'+i+state}}
 ['Center','Open'].each{n->['Up','Over','Down'].each{state->expected<<n+state}}
 assert textures.size()==33
 assert textures.collect{it.objectInnerFullName.toLowerCase()}.toSet()==expected.collect{it.toLowerCase()}.toSet()
 assert !up.exportTable.any{it.fullClassName in ['Core.Function','Engine.Emitter','Engine.SpriteEmitter']}
 println 'PASS: exact 33-texture UI-only inventory, no functions or world emitters.'
}
