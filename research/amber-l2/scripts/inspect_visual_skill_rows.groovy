def root=new File(args[0]),schemas=new File(root,'tools/L2ClientDat/dist/data/structure/dats')
def c=new AmberCatalog(new File(root,'exports/contract/combat-vfx-v4/skillgrp.raw'),schemas,'skillgrp.xml','ScionsOfDestiny')
for(int id:[2033,1059,19006,19007,19009,19013])println c.rows.find{it.skill_id==id&&it.skill_level==1}.findAll{k,v->!k.startsWith('_')}
