from pathlib import Path
import hashlib,json,subprocess,zipfile
S=Path(__file__).resolve().parent;R=S.parents[1]
relative=Path('org/l2jmobius/gameserver/network/serverpackets/SkillCatalogView.java')
original=R/'source/L2J_Mobius_CT_0_Interlude/java'/relative
text=original.read_text();start=text.index('    public static boolean nativeWindowAction(String action)');end=text.index('    private static final Map',start)
old=text[start:end];assert 'voice .amber toggle' in old and 'voice .sticker ' not in old
actions=['voice .habilidades','voice .habilidades next',*[f'voice .habilidades quick {i}' for i in range(-1,6)],'voice .amber toggle',*[f'voice .sticker {i}' for i in range(1,20)]]
method='    public static boolean nativeWindowAction(String action)\n    {\n        return action!=null&&Set.of(\n            '+',\n            '.join(json.dumps(a) for a in actions)+'\n        ).contains(action);\n    }\n'
patched=text[:start]+method+text[end:]
target=S/'source'/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(patched)
java=R/'tools/jdk-25.0.4.1+1/bin'
p=subprocess.run([str(java/'javac.exe'),'-encoding','UTF-8','-cp',str(R/'server/libs/*'),'-d',str(S/'compiled'),str(target)],capture_output=True,text=True)
(S/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
sources=[original,R/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/java'/relative]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(S/'input-hashes.json').write_text(json.dumps({str(p):sha(p) for p in sources if p.exists()},indent=2))
(S/'actions.json').write_text(json.dumps(actions,indent=2))
print('Compiled exact native-action whitelist: existing actions plus sticker numbers 1..19.')
