import acmi.l2.clientmod.io.UnrealPackage
import java.security.MessageDigest

def root=new File(args[0]),client=new File(root.parentFile.parentFile.parentFile,'l2')
def stage=new File(root,'exports/surface-v1')
def compact={int v->boolean neg=v<0;v=Math.abs(v);def a=[(byte)((v&63)|(neg?128:0)|(v>63?64:0))];v>>>=6;while(v){a<<(byte)((v&127)|(v>127?128:0));v>>>=7};a as byte[]}
def hash={byte[] bytes->MessageDigest.getInstance('SHA-256').digest(bytes).encodeHex().toString()}
def reports=[]
new UnrealPackage(new File(client,'systextures/FFighter.utx'),true).withCloseable {up->
    assert up.exportTable.any{it.objectInnerFullName=='LowBody.TexEnvMap0' && it.fullClassName=='Engine.TexEnvMap'}
}
for(String name:['L2AmberNPCv5','L2AmberArcherV2']){
    def input=new File(client,'animations/'+name+'.ukx'),output=new File(stage,name+'.ukx')
    output.bytes=input.bytes
    new UnrealPackage(output,false).withCloseable {up->
        up.addNameEntries(['Diffuse','SelfIllumination','SelfIlluminationMask','Specular','SpecularityMask','Opacity','TwoSided','ZWrite','AlphaTest','AlphaRef','OutputBlending','FallbackMaterial','None'].collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
        up.addImportEntries(['FFighter.LowBody.TexEnvMap0':'Engine.TexEnvMap']+
            ['AmberBody','AmberOutfit'].collectMany{atlas->[atlas+'LightMask',atlas+'SpecMask']}.collectEntries{[('AmberSurfaceV1.'+it):'Engine.Texture']})
        for(String atlas:['AmberBody','AmberOutfit']){
            def texture=up.exportTable.find{it.objectInnerFullName==atlas}
            def stream=new ByteArrayOutputStream()
            def objectProperty={String property,int reference->
                byte[] bytes=compact(reference);assert bytes.length<=2
                stream.write(compact(up.nameReference(property)))
                // UE2 property size code 0=1 byte, 1=2 bytes. Import refs may be compact 2-byte values.
                stream.write(5|((bytes.length==2?1:0)<<4));stream.write(bytes)
            }
            ['Diffuse','SelfIllumination','Opacity','FallbackMaterial'].each{objectProperty(it,texture.objectReference)}
            ['SelfIlluminationMask':atlas+'LightMask','SpecularityMask':atlas+'SpecMask'].each{prop,obj->
                objectProperty(prop,up.importTable.find{it.objectFullName=='AmberSurfaceV1.'+obj}.objectReference)
            }
            objectProperty('Specular',up.importTable.find{it.objectFullName=='FFighter.LowBody.TexEnvMap0'}.objectReference)
            for(String prop:['TwoSided','ZWrite','AlphaTest']){
                stream.write(compact(up.nameReference(prop)));stream.write(0xD3);stream.write(0)
            }
            stream.write(compact(up.nameReference('AlphaRef')));stream.write(1);stream.write(128)
            stream.write(compact(up.nameReference('OutputBlending')));stream.write(1);stream.write(1)
            stream.write(compact(up.nameReference('None')))
            up.exportTable.find{it.objectInnerFullName==atlas+'Shader'}.setObjectRawData(stream.toByteArray())
        }
    }
    new UnrealPackage(input,true).withCloseable {before->new UnrealPackage(output,true).withCloseable {after->
        assert before.exportTable.size()==after.exportTable.size()
        assert before.importTable.every{old->after.importTable.any{it.objectFullName==old.objectFullName&&it.fullClassName==old.fullClassName}}
        int preserved=0
        for(def old:before.exportTable){
            def fresh=after.exportTable.find{it.objectInnerFullName==old.objectInnerFullName}
            assert fresh!=null && old.fullClassName==fresh.fullClassName
            if(!old.objectInnerFullName.endsWith('Shader')){assert Arrays.equals(old.objectRawData,fresh.objectRawData):old.objectInnerFullName;preserved++}
        }
        reports<<[package:name,preserved_exports:preserved,changed_exports:['AmberBodyShader','AmberOutfitShader'],
                  source_sha256:hash(input.bytes),staged_sha256:hash(output.bytes),geometry_and_texture_payloads_preserved:true]
    }}
}
new File(stage,'package-proof.tsv').text='package\tpreserved_exports\tsource_sha256\tstaged_sha256\n'+reports.collect{[it.package,it.preserved_exports,it.source_sha256,it.staged_sha256].join('\t')}.join('\n')+'\n'
println 'PASS: only the two shader exports changed in each Amber package; native mesh, skeleton, transforms, texture payloads and animation dependencies preserved.'
