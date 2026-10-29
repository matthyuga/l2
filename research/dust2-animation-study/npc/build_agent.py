import pathlib,subprocess
R=pathlib.Path(__file__).parent;J=pathlib.Path(r'E:\l2-local\tools\jdk-25.0.4.1+1\bin');out=R/'classes';out.mkdir(exist_ok=True)
# javac UTF8 source without BOM.
p=R/'Dust2AnimationNpc.java';p.write_text(p.read_text(encoding='utf-8-sig'),encoding='utf8')
p=R/'AttachElven.java';p.write_text(p.read_text(encoding='utf-8-sig'),encoding='utf8')
cmd=[str(J/'javac.exe'),'-encoding','UTF-8','-cp',r'E:\l2-local\server\libs\*','-d',str(out),str(R/'Dust2AnimationNpc.java'),str(R/'AttachElven.java')]
p=subprocess.run(cmd,capture_output=True,text=True);print(p.stdout,p.stderr);assert p.returncode==0
(R/'npc.mf').write_text('Manifest-Version: 1.0\nAgent-Class: Dust2AnimationNpc\n\n')
subprocess.run([str(J/'jar.exe'),'cfm',str(R/'npc-agent.jar'),str(R/'npc.mf'),'-C',str(out),'Dust2AnimationNpc.class'],check=True)
print('NPC agent compiled. Not yet attached.')
