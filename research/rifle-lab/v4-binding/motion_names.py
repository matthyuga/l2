import sys,json
from pathlib import Path
sys.path.insert(0,r'E:\l2-local\research\dust2-animation-study\native');from write_l2_animation import chunks
import struct
for p in Path(r'E:\l2-local\research\rifle-lab\v4-binding\trader-motion').rglob('*.psa'):
 c=chunks(p);size,n,d=c['ANIMINFO'];print(p)
 for i in range(n):
  q=struct.unpack_from('<64s64s4i3f3i',d,i*size);print(q[0].rstrip(b'\0').decode(),q[11],q[8])

