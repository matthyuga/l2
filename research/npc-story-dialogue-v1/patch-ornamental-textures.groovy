import acmi.l2.clientmod.io.*
import java.security.MessageDigest

def s=new File(args[0]),mode=args[1]
def names=['BackgroundOpaque','BackgroundSemi']
def sha={byte[] b->MessageDigest.getInstance('SHA-256').digest(b).encodeHex().toString()}
if(mode=='dump'){
 new File(s,'native-exports').mkdirs()
 new UnrealPackage(new File(s,'original.raw.u'),true).withCloseable{up->
  def inventory=[]
  up.exportTable.each{e->
   def data=e.objectRawData
   inventory<<[e.objectInnerFullName,e.fullClassName,sha(data),data.length].join('\t')
   if(names.contains(e.objectInnerFullName))new File(s,'native-exports/'+e.objectInnerFullName+'.bin').bytes=data
  }
  new File(s,'native-inventory-before.tsv').text=inventory.join('\n')
 }
 println 'PASS: native background exports dumped from decoded current package.'
}else{
 assert mode=='patch'
 def output=new File(s,'patched.raw.u');output.bytes=new File(s,'original.raw.u').bytes
 new UnrealPackage(output,false).withCloseable{up->
  names.each{n->
   def e=up.exportTable.find{it.objectInnerFullName==n};assert e && e.fullClassName=='Engine.Texture'
   def b=new File(s,'native-exports/'+n+'.new.bin').bytes
   assert b.length==e.objectRawData.length
   e.setObjectRawData(b)
  }
 }
 new UnrealPackage(new File(s,'original.raw.u'),true).withCloseable{old->
  new UnrealPackage(output,true).withCloseable{up->
   assert old.exportTable.size()==up.exportTable.size()
   assert old.importTable*.objectFullName==up.importTable*.objectFullName
   assert old.nameTable*.name==up.nameTable*.name
   int preserved=0
   old.exportTable.each{e->
    def after=up.exportTable.find{it.objectInnerFullName==e.objectInnerFullName};assert after
    if(names.contains(e.objectInnerFullName))assert Arrays.equals(after.objectRawData,new File(s,'native-exports/'+e.objectInnerFullName+'.new.bin').bytes)
    else{assert Arrays.equals(e.objectRawData,after.objectRawData):e.objectInnerFullName;preserved++}
   }
   assert up.exportTable.count{it.fullClassName=='Engine.Texture'}==35
   println 'PASS: exact new background bytes; '+preserved+' other exports byte identical; imports, names and 35-texture inventory preserved.'
  }
 }
}
