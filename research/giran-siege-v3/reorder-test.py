from pathlib import Path
p=Path(__file__).parent/'GiranSiegeLab/GiranDefenseVerification.java'
s=p.read_text(encoding='utf-8')
start=s.index('  // All four rival leaders');end=s.index('\n }catch(Throwable e)',start)
block=s[start:end];s=s[:start]+s[end:];point=s.index('  // Real native bow')
s=s[:point]+block+'\n'+s[point:];p.write_text(s,encoding='utf-8')
print('Capture and guardian checks now precede bow/farm checks.')
