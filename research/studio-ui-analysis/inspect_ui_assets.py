"""Read-only CharaStudio Unity scene UI layout inventory (not runtime state)."""
from pathlib import Path
import UnityPy,json,re,hashlib
OUT=Path(__file__).resolve().parent
ROOT=Path('K:/JUEGOS/KOIKATSU 22/CharaStudio_Data')
src=ROOT/'level1'
env=UnityPy.load(str(src),str(ROOT/'sharedassets1.assets'))
objects=[o for o in env.objects if o.assets_file.name==src.name]
gos={};rects={};transforms={};errors=[]
for obj in objects:
 try:
  if obj.type.name=='GameObject':gos[obj.path_id]=obj.read_typetree()
  elif obj.type.name in ('Transform','RectTransform'):
   d=obj.read_typetree();transforms[obj.path_id]=d
   if obj.type.name=='RectTransform':rects[d['m_GameObject']['m_PathID']]=d
 except Exception as e:errors.append({'id':obj.path_id,'type':obj.type.name,'error':str(e)})
go_transform={t['m_GameObject']['m_PathID']:i for i,t in transforms.items()}
def hierarchy(gid,seen=None):
 seen=set() if seen is None else seen
 if gid in seen:return '<cycle>'
 seen.add(gid);g=gos.get(gid,{})
 t=transforms.get(go_transform.get(gid),{})
 father=transforms.get(t.get('m_Father',{}).get('m_PathID',0),{})
 parent=father.get('m_GameObject',{}).get('m_PathID',0)
 return (hierarchy(parent,seen)+'/' if parent else '')+g.get('m_Name',str(gid))
rows=[]
for gid,g in gos.items():
 p=hierarchy(gid);r=rects.get(gid,{})
 rows.append({'game_object_id':gid,'name':g['m_Name'],'path':p,'active_self':bool(g.get('m_IsActive')),'rect':{k:r.get(k) for k in ('m_AnchorMin','m_AnchorMax','m_AnchoredPosition','m_SizeDelta','m_Pivot') if k in r},'components':g.get('m_Component',[])})
controllers=[]
wanted={'RootButtonCtrl','AddButtonCtrl','WorkspaceCtrl','TreeNodeCtrl','ManipulatePanelCtrl','CameraControl','CameraSelector','GuideInput','GuideObjectManager','SystemButtonCtrl','Studio','MPItemCtrl','MPCameraCtrl'}
for obj in objects:
 if obj.type.name!='MonoBehaviour':continue
 try:
  d=obj.read_typetree(check_read=False);reader=obj.read(check_read=False);script=reader.m_Script.read();cls=script.m_ClassName
  if cls not in wanted:continue
  gid=d.get('m_GameObject',{}).get('m_PathID');controllers.append({'class':script.m_Namespace+'.'+cls,'game_object_path':hierarchy(gid),'component_id':obj.path_id,'serialized':d})
 except Exception as e:
  if len(errors)<30:errors.append({'id':obj.path_id,'type':'MonoBehaviour','error':str(e)[:200]})
report={'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'authority':'shipped Unity scene assets; not a live capture','controller_payload_coverage':'MonoBehaviour base headers and MonoScript identities only. check_read=False permits unread script-specific fields; those fields are not decoded or claimed complete.','counts':{'game_objects':len(gos),'rect_transforms':len(rects),'selected_controllers':len(controllers)},'layout':rows,'controllers':controllers,'errors':errors}
(OUT/'unity-ui-layout.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
selected=[r for r in rows if r['path'].count('/')<2 or re.search(r'work(space|place)|manipulate|rootbutton|camera.*save|camera.*select|button.*root|add.*button',r['name'],re.I)]
print(json.dumps({'counts':report['counts'],'selected_layout':[{'path':r['path'],'rect':r['rect']} for r in selected if 'Workspace' in r['path'] or r['name']=='00_Command'],'controllers':[{'class':c['class'],'path':c['game_object_path'],'fields':list(c['serialized'])} for c in controllers],'error_sample':errors[:2]},ensure_ascii=False,indent=2))
