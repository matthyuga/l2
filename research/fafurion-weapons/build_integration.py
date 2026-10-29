"""Stage Fafurion additions, preserving existing DAT record bytes exactly."""
from pathlib import Path
import copy, hashlib, json, re, struct, subprocess, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
STAGE = ROOT / 'stage'
CLIENT = PROJECT.parent / 'l2/system-hud'
CODEC = PROJECT / 'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
ASM = PROJECT / 'tools-src/L2FileEdit/data/l2asm-disasm'
PACK = ROOT / 'System_Fafurion_Weapons'
IDS = list(range(54130, 54137))
BASE_IDS = [6365, 6364, 6371, 6366, 6367, 6370, 6580]

def run(args):
    p = subprocess.run([str(a) for a in args], capture_output=True)
    if p.returncode: raise RuntimeError(p.stdout.decode(errors='replace') + p.stderr.decode(errors='replace'))
    return p.stdout.decode(errors='replace')

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    vendor = (PACK/'System_dat_IL.txt').read_text(encoding='utf-8-sig').splitlines()
    names = [s.split('\t') for s in vendor if re.match(r'^5413[0-6]\t',s)]
    weapons = [s.split('\t') for s in vendor if re.match(r'^0\t5413[0-6]\t',s)]
    assert len(names)==len(weapons)==7
    all_items={}
    for path in (PROJECT/'server/game/data/stats/items').rglob('*.xml'):
        for item in ET.parse(path).getroot().findall('item'):
            iid=int(item.get('id'))
            if iid not in all_items or path.parent.name!='custom': all_items[iid]=item
    assert not (set(IDS)&all_items.keys()), 'Fafurion IDs already installed: do not rebuild against installed files'
    root=ET.Element('list', {'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance', 'xsi:noNamespaceSchemaLocation':'../../xsd/items.xsd'})
    report=[]
    for fields, weapon, base in zip(names,weapons,BASE_IDS):
        iid=int(fields[0]); item=copy.deepcopy(all_items[base]);item.set('id',str(iid));item.set('name',fields[1])
        for node in list(item):
            if node.tag=='skills': item.remove(node)
        if base==6370:
            skills=ET.SubElement(item,'skills');ET.SubElement(skills,'skill',{'id':'3599','level':'1'})
        item.find("set[@name='icon']").set('val',weapon[13])
        stats={s.get('type'):s.text for s in item.find('stats')}
        # Fixed columns before the variable weapon/effect arrays match this vendor layout.
        assert len(weapon)==92, (iid,len(weapon))
        assert int(weapon[41])==int(stats['pAtk'])
        weapon[42]=stats['mAtk']
        weapon[20]='8' # ADAMANTAITE material in this client, not vendor material 47.
        weapon[56]='-1' # Regular weapon, not a hero item.
        fields[3]='a,Arma de grado S.\\0'
        root.append(item)
        report.append({'id':iid,'name':fields[1],'base_id':base,'stats':stats,
                       'type':item.find("set[@name='weapon_type']").get('val'),
                       'magic':base==6366,'skills':[dict(s.attrib) for s in item.findall('skills/skill')], 'icon':weapon[13]})
    ET.indent(root,space='\t')
    ET.ElementTree(root).write(STAGE/'54100-54199.xml',encoding='utf-8',xml_declaration=True)
    manifest={'pack_sha256':sha(PROJECT/'descarga de assets/Fafurion_Weapons_H5_IL.rar'),'items':report,'catalogs':{}}
    for name,rows,idcol in [('weapongrp',weapons,1),('itemname-e',names,0)]:
        before=STAGE/(name+'.before.raw')
        # Re-read current catalogs: staging must never rely on stale backups.
        run([CODEC,'-o',before,CLIENT/(name+'.dat')])
        original=before.read_bytes()
        run([ASM/'l2disasm.exe','-d',ASM/f'DAT_defs/Interlude/{name}.ddf','-e',STAGE/(name+'.ddf'),'-o','e',before,STAGE/(name+'.before.txt')])
        text=(STAGE/(name+'.before.txt')).read_text(encoding='utf-8').splitlines()
        existing={int(s.split('\t')[idcol]) for s in text[1:] if s.strip()}
        assert not set(IDS)&existing
        (STAGE/(name+'.add.txt')).write_text(text[0]+'\n'+'\n'.join('\t'.join(r) for r in rows)+'\n',encoding='utf-8')
        run([ASM/'l2asm.exe','-d',STAGE/(name+'.ddf'),STAGE/(name+'.add.txt'),STAGE/(name+'.add.raw')])
        extra=(STAGE/(name+'.add.raw')).read_bytes()
        assert struct.unpack_from('<I',extra)[0]==7
        # Disassembler/assembler footer is an identical SafePackage marker.
        footer=b'\x0cSafePackage\0'
        assert original.endswith(footer) and extra.endswith(footer), (name,original[-24:],extra[-24:])
        count=struct.unpack_from('<I',original)[0]
        final=struct.pack('<I',count+7)+original[4:-len(footer)]+extra[4:-len(footer)]+footer
        assert final[4:len(original)-len(footer)]==original[4:-len(footer)]
        raw=STAGE/(name+'.raw');raw.write_bytes(final)
        run([ASM/'l2disasm.exe','-d',STAGE/(name+'.ddf'),'-o','e',raw,STAGE/(name+'.verified.txt')])
        verified=(STAGE/(name+'.verified.txt')).read_text(encoding='utf-8').splitlines()
        assert len(verified)==len(text)+7
        assert verified[1:len(text)]==text[1:]
        for line,row in zip(verified[-7:],rows):
            assert int(line.split('\t')[idcol])==int(row[idcol])
        out=STAGE/(name+'.dat')
        run([CODEC,'-c','encode','-p','413','-o',out,raw])
        check=STAGE/(name+'.roundtrip.raw');run([CODEC,'-o',check,out]);assert check.read_bytes()==final
        manifest['catalogs'][name]={'existing_records_preserved':count,'added':7,'before_encoded_sha256':sha(CLIENT/(name+'.dat')),'before_raw_sha256':sha(before),'after_encoded_sha256':sha(out),'after_raw_sha256':sha(raw)}
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(manifest,indent=2))

if __name__=='__main__': main()
