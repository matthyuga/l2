from pathlib import Path
p=Path(__file__).resolve().parents[1]/'model-catalog/render_gallery.py'
s=p.read_text(encoding='utf-8').replace("for m in report['models']:","for m in report['models']:\n    if not m['key'].startswith('airship_'):continue")
exec(compile(s,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
