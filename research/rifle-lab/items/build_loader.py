"""Compile a transient item-registration agent. Never attaches or installs it."""
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[2]
JDK = PROJECT / 'tools/jdk-25.0.4.1+1/bin'
out = ROOT / 'loader-build'
out.mkdir(exist_ok=True)
subprocess.run([str(JDK / 'javac.exe'), '-encoding', 'UTF-8', '-cp', str(PROJECT / 'server/libs/*'),
                '-d', str(out), str(ROOT / 'RiflePrototypeItems.java')], check=True)
manifest = out / 'agent.mf'
manifest.write_text('Manifest-Version: 1.0\nAgent-Class: RiflePrototypeItems\n\n', encoding='utf-8')
subprocess.run([str(JDK / 'jar.exe'), 'cfm', str(out / 'rifle-items-agent.jar'), str(manifest),
                '-C', str(out), 'RiflePrototypeItems.class'], check=True)
print('Compiled staged loader only. Nothing attached or installed.')
