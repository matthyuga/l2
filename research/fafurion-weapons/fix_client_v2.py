"""Prepare/apply compatible display aliases and terminated Fafurion descriptions."""
from pathlib import Path
import hashlib,json,struct,subprocess,sys,datetime,shutil,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
CLIENT=PROJECT.parent/'l2/system-hud'
OUT=ROOT/'client-fix-v2';OUT.mkdir(exist_ok=True)
CODEC=PROJECT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
ASM=PROJECT/'tools-src/L2FileEdit/data/l2asm-disasm'
FOOT=b'\x0cSafePackage\0'
IDS=set(range(54130,54137));ALIASES=dict(zip(range(54130,54137),range(24130,24137)))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(args):
    p=subprocess.run([str(a) for a in args],capture_output=True,check=True)
    return p.stdout.decode(errors='replace')
def spans(data):
    """Read exact Interlude itemname record boundaries, including ASCF payloads."""
    pos=4;rows=[]
    def asc():
        nonlocal pos
        b=data[pos];pos+=1;v=b&63;neg=b&128;more=b&64;shift=6
        while more:
            b=data[pos];pos+=1;v|=(b&127)<<shift;more=b&128;shift+=7
        size=v*(2 if neg else 1);payload=data[pos:pos+size];pos+=size
        return payload
    for _ in range(struct.unpack_from('<I',data)[0]):
        start=pos;iid=struct.unpack_from('<I',data,pos)[0];pos+=4
        for _ in range(2):
            size=struct.unpack_from('<I',data,pos)[0];pos+=4+size
        desc=asc();pos+=4
        for _ in range(4):asc()
        pos+=2+4;asc()
        rows.append((iid,start,pos,desc))
    assert data[pos:]==FOOT,(pos,len(data),data[pos:pos+20])
    return rows
def prepare():
    manifest={'aliases':ALIASES,'catalogs':{},'xml':{},'status':'prepared'}
    for file in (PROJECT/'server/game/data/stats/items').rglob('*.xml'):
        assert not any(int(i.get('id')) in ALIASES.values() for i in ET.parse(file).getroot().findall('item')),'Display aliases collide with server items'
    for name,idcol in [('weapongrp',1),('itemname-e',0)]:
        original=OUT/(name+'.before.raw');run([CODEC,'-o',original,CLIENT/(name+'.dat')])
        ddf=OUT/(name+'.ddf');text=OUT/(name+'.before.txt')
        run([ASM/'l2disasm.exe','-d',ASM/f'DAT_defs/Interlude/{name}.ddf','-e',ddf,'-o','e',original,text])
        lines=text.read_text(encoding='utf-8').splitlines();columns=lines[0];parsed=[line.split('\t') for line in lines[1:] if line.strip()]
        assert not any(int(r[idcol]) in ALIASES.values() for r in parsed),'Client alias collision'
        selected=[r for r in parsed if int(r[idcol]) in IDS];assert len(selected)==7
        if name=='itemname-e':
            for row in selected:row[3]='a,Arma de grado S.\\0'
        extra=[]
        for row in selected:
            alias=row.copy();alias[idcol]=str(ALIASES[int(row[idcol])]);extra.append(alias)
        additions=selected+extra if name=='itemname-e' else extra
        additiontxt=OUT/(name+'.add.txt');additiontxt.write_text(columns+'\n'+'\n'.join('\t'.join(r) for r in additions)+'\n',encoding='utf-8')
        additionraw=OUT/(name+'.add.raw');run([ASM/'l2asm.exe','-d',ddf,additiontxt,additionraw])
        before=original.read_bytes();added=additionraw.read_bytes();assert before.endswith(FOOT) and added.endswith(FOOT)
        count=struct.unpack_from('<I',before)[0]
        if name=='weapongrp':
            after=struct.pack('<I',count+7)+before[4:-len(FOOT)]+added[4:-len(FOOT)]+FOOT
            assert after[4:len(before)-len(FOOT)]==before[4:-len(FOOT)]
        else:
            oldspans=spans(before);newspans=spans(added)
            replacements={iid:added[a:b] for iid,a,b,desc in newspans}
            chunks=[]
            for iid,a,b,desc in oldspans:
                chunks.append(replacements[iid] if iid in IDS else before[a:b])
            chunks.extend(replacements[iid] for iid in ALIASES.values())
            after=struct.pack('<I',count+7)+b''.join(chunks)+FOOT
            for iid,a,b,desc in spans(after):
                if iid in IDS or iid in ALIASES.values():assert desc==b'Arma de grado S.\0',(iid,desc)
            # Preserve every unrelated original record, including encoding and terminators.
            lookup={iid:after[a:b] for iid,a,b,desc in spans(after)}
            for iid,a,b,desc in oldspans:
                if iid not in IDS:assert lookup[iid]==before[a:b]
        raw=OUT/(name+'.raw');raw.write_bytes(after)
        verifytxt=OUT/(name+'.verified.txt');run([ASM/'l2disasm.exe','-d',ddf,'-o','e',raw,verifytxt])
        verified=verifytxt.read_text(encoding='utf-8').splitlines();assert len(verified)==len(lines)+7
        output=OUT/(name+'.dat');run([CODEC,'-c','encode','-p','413','-o',output,raw])
        check=OUT/(name+'.roundtrip.raw');run([CODEC,'-o',check,output]);assert check.read_bytes()==after
        manifest['catalogs'][name]={'target':str(CLIENT/(name+'.dat')),'before_encoded_sha256':sha(CLIENT/(name+'.dat')),
            'after_encoded_sha256':sha(output),'after_raw_sha256':sha(raw),'added_aliases':7,'modified_existing_ids':sorted(IDS) if name=='itemname-e' else []}
    ET.register_namespace('xsi','http://www.w3.org/2001/XMLSchema-instance')
    for prefix in ['server','source/L2J_Mobius_CT_0_Interlude/dist','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist']:
        target=PROJECT/prefix/'game/data/stats/items/54100-54199.xml'
        tree=ET.parse(target);root=tree.getroot()
        for item in root.findall('item'):
            iid=int(item.get('id'));assert item.find("set[@name='displayId']") is None
            item.insert(1,ET.Element('set',{'name':'displayId','val':str(ALIASES[iid])}))
        ET.indent(root,space='\t');stage=OUT/(str(len(manifest['xml']))+'-54100-54199.xml');tree.write(stage,encoding='utf-8',xml_declaration=True)
        manifest['xml'][str(target)]={'stage':str(stage),'before':sha(target),'after':sha(stage)}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('PREPARED: seven display aliases <32768, fourteen terminated descriptions, all unrelated record bytes preserved')
def install():
    closed=subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process L2 -ErrorAction SilentlyContinue){exit 5}'],capture_output=True)
    assert closed.returncode==0,'L2 is running: close the client before installing'
    manifest=json.loads((OUT/'manifest.json').read_text());assert manifest['status']=='prepared'
    changes=[]
    for name,entry in manifest['catalogs'].items():changes.append((OUT/(name+'.dat'),Path(entry['target']),entry['before_encoded_sha256']))
    for target,entry in manifest['xml'].items():changes.append((Path(entry['stage']),Path(target),entry['before']))
    for stage,target,before in changes:assert sha(target)==before,'Concurrent change: '+str(target)
    backup=PROJECT/'backups'/('fafurion-client-fix-v2-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
    records=[]
    for i,(stage,target,before) in enumerate(changes):
        saved=backup/(str(i)+'-'+target.name);shutil.copy2(target,saved)
        records.append({'target':str(target),'backup':str(saved),'before':before,'after':sha(stage)})
    (backup/'files.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    try:
        for stage,target,before in changes:shutil.copy2(stage,target)
        for row in records:assert sha(row['target'])==row['after']
    except Exception:
        for row in records:
            if sha(row['target'])==row['after']:shutil.copy2(row['backup'],row['target'])
        raise
    manifest.update(status='installed',backup=str(backup),files=records)
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    # Refresh current verification hashes; retain the initial manifest in the backup.
    for name in ['manifest.json','installation.json']:shutil.copy2(ROOT/name,backup/('initial-'+name))
    active=json.loads((ROOT/'manifest.json').read_text());installed=json.loads((ROOT/'installation.json').read_text())
    for name,entry in manifest['catalogs'].items():
        active['catalogs'][name].update(after_encoded_sha256=entry['after_encoded_sha256'],after_raw_sha256=entry['after_raw_sha256'],added=14)
    for item in active['items']:item['display_id']=ALIASES[item['id']]
    hashes={r['target']:r['after'] for r in records}
    for row in installed['files']:
        if row['target'] in hashes:row['after_sha256']=hashes[row['target']]
    installed['client_fix_v2_backup']=str(backup)
    (ROOT/'manifest.json').write_text(json.dumps(active,indent=2),encoding='utf-8')
    (ROOT/'installation.json').write_text(json.dumps(installed,indent=2),encoding='utf-8')
    print('INSTALLED '+str(backup))
if __name__=='__main__':install() if '--install' in sys.argv else prepare()
