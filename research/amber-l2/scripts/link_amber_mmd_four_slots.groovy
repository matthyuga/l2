import acmi.l2.clientmod.io.UnrealPackage
import java.nio.ByteBuffer
import java.nio.ByteOrder
def root=new File(args[0]),stage=new File(root,'exports/mmd-variants-fix4-20261023')
def compact=AmberCatalog.&compact
def decode={byte[] d,int p->int b=d[p++]&255;boolean neg=(b&128)!=0;int v=b&63;boolean more=(b&64)!=0;int shift=6;while(more){b=d[p++]&255;v|=(b&127)<<shift;more=(b&128)!=0;shift+=7};[neg?-v:v,p]}
def expected=new File(root,'reports/expected-bones.txt').readLines()
for(String label:['v10','v14']){
 String pkg=label=='v10'?'AmberMMD10':'AmberMMD14'
 def materials=new File(stage,label+'/materials.tsv').readLines().collect{def v=it.split('\t');[name:v[0],texture:v[1]]}
 def output=new File(stage,pkg+'.ukx');output.bytes=new File(root,'tools/l2editor/L2Editor/'+pkg+'.u').bytes
 new UnrealPackage(output,false).withCloseable{up->
  up.setUUID(UUID.randomUUID());up.addImportEntries(['L2AmberArcherMotion.FFighter_anim':'Engine.MeshAnimation'])
  def mesh=up.exportTable.find{it.objectInnerFullName=='AmberNPC'};assert mesh
  byte[] raw=mesh.objectRawData;def matches=[]
  for(int offset=0;offset<raw.length-5000;offset++){
   if((raw[offset]&255)!=76)continue
   try{
    def count=decode(raw,offset);if(count[0]!=76)continue
    int at=count[1];boolean ok=true
    for(String name:expected){def bone=decode(raw,at);if(bone[0]!=up.nameReference(name)){ok=false;break};at=bone[1]+56}
    if(ok&&decode(raw,at)[0]==0)matches<<at
   }catch(Exception ignored){}
  }
  assert matches.size()==1:'reference skeleton ambiguity '+matches
  int position=matches[0],end=decode(raw,position)[1]
  def stream=new ByteArrayOutputStream();stream.write(raw,0,position);stream.write(compact(up.importTable.find{it.objectFullName=='L2AmberArcherMotion.FFighter_anim'}.objectReference));stream.write(raw,end,raw.length-end);raw=stream.toByteArray()
  // Match the already verified native female origin/rotation, without editing old packages.
  def bb=ByteBuffer.wrap(raw).order(ByteOrder.LITTLE_ENDIAN);def scaleOffsets=[]
  for(int i=0;i<110;i++)if(bb.getFloat(i)==1f&&bb.getFloat(i+4)==1f&&bb.getFloat(i+8)==1f)scaleOffsets<<i
  assert scaleOffsets.size()==1:'mesh scale layout '+scaleOffsets
  int origin=scaleOffsets[0]+12;assert (0..<6).every{bb.getInt(origin+it*4)==0}
  bb.putFloat(origin+8,26.5f);bb.putInt(origin+16,49152);mesh.setObjectRawData(raw)
  up.addNameEntries(['Diffuse','SelfIllumination','Opacity','TwoSided','ZWrite','AlphaTest','AlphaRef','OutputBlending','FallbackMaterial','None'].collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
  for(def material:materials){
   def texture=up.exportTable.find{it.objectInnerFullName==material.texture};assert texture
   def props=new ByteArrayOutputStream()
   for(String property:['Diffuse','SelfIllumination','Opacity','FallbackMaterial']){
    byte[] value=compact(texture.objectReference);assert value.length<=2
    props.write(compact(up.nameReference(property)));props.write(5|((value.length==2?1:0)<<4));props.write(value)
   }
   for(String property:['TwoSided','ZWrite','AlphaTest']){props.write(compact(up.nameReference(property)));props.write(0xD3);props.write(0)}
   props.write(compact(up.nameReference('AlphaRef')));props.write(1);props.write(128)
   props.write(compact(up.nameReference('OutputBlending')));props.write(1);props.write(1)
   props.write(compact(up.nameReference('None')))
   up.addExportEntry(material.name+'Shader','Engine.Shader',null,props.toByteArray(),UnrealPackage.DEFAULT_OBJECT_FLAGS)
  }
  println 'PASS '+pkg+': exact76-bone animation binding, origin='+origin+', four client-safe masked/self-lit shaders.'
 }
}
