from pathlib import Path
import subprocess

lab = Path(__file__).resolve().parent
root = lab.parent.parent
java = root / 'tools/jdk-25.0.4.1+1/bin'
sources = list((lab / 'src/custom/ExplorationLab').glob('*.java'))
sources.append(lab / 'tests/ExplorationStateTest.java')
subprocess.run([str(java / 'javac.exe'), '-encoding', 'UTF-8', '-cp', str(root / 'server/libs/*'),
                '-d', str(lab / 'build'), *map(str, sources)], check=True)
subprocess.run([str(java / 'java.exe'), '-cp', str(lab / 'build'),
                'custom.ExplorationLab.ExplorationStateTest'], check=True)
