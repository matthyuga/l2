def root=new File(args[0]),schemas=new File(root,'tools/L2ClientDat/dist/data/structure/dats')
for(def spec:[['skillgrp','skillgrp.xml'],['skillname','skillname.xml']]){
 def c=new AmberCatalog(new File(root,'exports/contract/combat-vfx-v6/'+spec[0]+'.before.raw'),schemas,spec[1],'ScionsOfDestiny')
 c.rows.findAll{it.skill_id>=19011&&it.skill_id<=19030||it.skill_id>=19200&&it.skill_id<=19610}.each{println it.findAll{k,v->k in ['skill_id','skill_level','description','name','desc']}}
}
