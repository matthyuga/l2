import pathlib,json,subprocess,rarfile
from inventory import OUT,MODELS,TEXTURES

data=json.loads((OUT/'inventory.json').read_text('utf-8'))
for r in data['records']:
    if r['status']!='no_supported_model':continue
    root=pathlib.Path(r['root'])
    for archive in root.rglob('*.rar'):
        dest=archive.parent/('unpacked_'+archive.stem);dest.mkdir(exist_ok=True)
        with rarfile.RarFile(archive) as z:
            for info in z.infolist():
                name=info.filename.replace('\\','/')
                if not (dest/name).resolve().is_relative_to(dest.resolve()):raise ValueError('Unsafe RAR path')
                if info.is_symlink():raise ValueError('Unexpected symlink')
        unrar=pathlib.Path(r'C:\Program Files\WinRAR\UnRAR.exe')
        command=[str(unrar),'x','-o+','-idq',str(archive),str(dest)+'\\'] if unrar.exists() else ['tar','-xf',str(archive),'-C',str(dest)]
        result=subprocess.run(command,capture_output=True,text=True)
        if result.returncode:
            r['error']=result.stderr or result.stdout
            r['extraction_failed']=True
        else:
            r.pop('error',None);r.pop('extraction_failed',None)
    files=[p for p in root.rglob('*') if p.is_file()]
    r['models']=[str(p.relative_to(root)) for p in files if p.suffix.lower() in MODELS]
    r['textures']=sum(p.suffix.lower() in TEXTURES for p in files)
    if r['models'] and not r.get('extraction_failed'):r['status']='source_ready'
(OUT/'inventory.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('Source-ready packages:',sum(r['status']=='source_ready' for r in data['records']))
