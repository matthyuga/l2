import pathlib
root=pathlib.Path(__file__).resolve().parents[1]/'model-catalog'
source=(root/'render_gallery.py').read_text(encoding='utf-8')
source=source.replace("if m.get('status')!='ready':continue", "if m.get('status')!='ready' or not (m['key'].startswith('superion_') or m['key'].startswith('airship_scene_')):continue")
exec(compile(source,str(root/'render_gallery.py'),'exec'),{'__file__':str(root/'render_gallery.py'),'__name__':'__main__'})
