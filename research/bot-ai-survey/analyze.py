from pathlib import Path
import re,json,hashlib,subprocess,collections,csv,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parent
repos=['L2Autobots','L2jRoboto','l2-smartbot']
skills={}
for p in Path('E:/l2-local/server/game/data/stats/skills').rglob('*.xml'):
 for node in ET.parse(p).getroot().findall('skill'):
  sid=int(node.attrib['id']);skills[sid]={'name':node.attrib.get('name'),'target':node.findtext('targetType'),'operate':node.findtext('operateType'),'abnormal':node.findtext('abnormalType'),'source':str(p),'effects':[e.attrib.get('name') for e in node.findall('.//effect')]}
def group(path):
 text=str(path).replace('\\','/').lower()
 for key,category in [('preferences','preferences'),('/classes/','class_profiles'),('/ai/','combat'),('/attributes/','combat_attributes'),('/sequences/','world_sequences'),('/ui/','admin_ui'),('/dao/','persistence'),('/sql/','persistence'),('llm','social_llm'),('memory','social_llm'),('knowledge','social_llm'),('controller','combat'),('manager','lifecycle'),('scheduler','scheduler'),('/task/','scheduler'),('patch','core_hooks'),('/extensions/','core_adapter'),('/utils/','utilities')]:
  if key in text:return category
 return 'models_config_or_assets'
inventory=[];findings=[];profiles=[];counts={}
patterns={
 'resource_override':r'(?:currentMp\s*=|setCurrentMp\(|fullRestore\(|currentHp\s*=|setCurrentHp\()',
 'inventory_mutation':r'(?:addItem\(|destroyItem\(|equipItem\()',
 'relocation_revive':r'(?:teleportTo\(|teleToLocation\(|doRevive\()',
 'clan_party_assumption':r'(?:clanId\s*==|getClanId\(\)\s*==|party\s*==|getParty\(\)\s*==)',
 'http_or_external':r'(?:httpClient\.send|HttpRequest|https?://)',
 'todo_or_placeholder':r'(?:TODO|NotImplemented|UnsupportedOperationException)',
 'concurrent_execution':r'(?:GlobalScope|\.launch\s*\{|scheduleGeneral|scheduleAtFixedRate|ThreadPool\.execute)',
 'db_access':r'(?:prepareStatement|executeQuery|executeUpdate|getConnection\()',
}
for repo in repos:
 base=root/repo;commit=subprocess.check_output(['git','-C',str(base),'rev-parse','HEAD'],text=True).strip()
 tracked=subprocess.check_output(['git','-C',str(base),'ls-files'],text=True).splitlines()
 constants={}
 for name in tracked:
  p=base/name
  if p.suffix=='.kt':
   for symbol,value in re.findall(r'(?:const\s+)?val\s+(\w+)\s*(?::\s*Int)?\s*=\s*(\d+)\b',p.read_text(encoding='utf-8-sig')):constants[symbol]=int(value)
 for name in tracked:
  p=base/name;data=p.read_bytes();text=None
  try:text=data.decode('utf-8-sig')
  except UnicodeError:pass
  row={'repo':repo,'path':name,'category':group(name),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'text_scanned':text is not None,'lines':len(text.splitlines()) if text is not None else None,'imports':[]}
  if text is not None:
   row['imports']=re.findall(r'^import\s+([^;\n]+)',text,re.M)
   for lineno,line in enumerate(text.splitlines(),1):
    for category,pattern in patterns.items():
     if re.search(pattern,line):findings.append({'repo':repo,'path':name,'line':lineno,'kind':category,'evidence':line.strip()})
   if p.suffix in ['.kt','.java']:
    row['declared_types']=re.findall(r'\b(?:class|interface|enum(?:\s+class)?)\s+(\w+)',text)
   if repo=='L2Autobots' and '/classes/' in name and p.suffix=='.kt':
    refs=[]
    for lineno,line in enumerate(text.splitlines(),1):
     for symbol in re.findall(r'BotSkill\(\s*(\w+)',line):
      sid=int(symbol) if symbol.isdigit() else constants.get(symbol)
      refs.append({'symbol':symbol,'id':sid,'line':lineno,'expression':line.strip(),'local_skill':skills.get(sid),'exists_locally':sid in skills})
    profiles.append({'profile':p.stem,'path':name,'pre_class':'/pre/' in name,'skills':refs})
  inventory.append(row)
 counts[repo]={'commit':commit,'tracked_files':len(tracked),'text_files':sum(x['text_scanned'] for x in inventory if x['repo']==repo),'source_files':sum(Path(x['path']).suffix in ['.kt','.java'] for x in inventory if x['repo']==repo)}
for name,data in [('file-inventory.json',inventory),('static-findings.json',findings),('class-catalog.json',profiles),('analysis-summary.json',{'repositories':counts,'profiles':len(profiles),'skill_references':sum(len(p['skills']) for p in profiles),'unresolved_or_missing':[(p['profile'],s['symbol'],s['id']) for p in profiles for s in p['skills'] if not s['exists_locally']],'categories':dict(collections.Counter(x['category'] for x in inventory))})]:
 (root/name).write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
with (root/'file-inventory.csv').open('w',newline='',encoding='utf-8-sig') as out:
 fields=['repo','path','category','lines','sha256','text_scanned'];writer=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(inventory)
print((root/'analysis-summary.json').read_text(encoding='utf-8'))
