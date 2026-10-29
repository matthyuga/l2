from package_tools import *
import json,subprocess,hashlib,zlib
D=pathlib.Path(__file__).resolve().parent;stage=D/'stage';client=D/'client';codec=ROOT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe';proof=[]
for folder in ['Maps','StaticMeshes','Textures']:
    for p in (stage/folder).glob('*'):
        target=client/folder/p.name;target.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run([str(codec),'-c','encode','-p','121','-f',p.name,'-o',str(target),str(p)],check=True,capture_output=True)
        raw=p.read_bytes();enc=target.read_bytes();key=sum(map(ord,p.name.lower()))&255
        assert enc[:28].decode('utf-16le')=='Lineage2Ver121' and len(enc)==len(raw)+48
        assert enc[28:28+len(raw)].translate(bytes(x^key for x in range(256)))==raw
        # Independent CRC check avoids the old CLI's hanging -v parser. Native
        # format: 20-byte footer, CRC32 at footer byte 12, over header+ciphertext.
        assert struct.unpack_from('<I',enc,len(enc)-8)[0]==zlib.crc32(enc[:-20]),p.name
        proof.append(dict(relative=folder+'/'+p.name,sha256=hashlib.sha256(enc).hexdigest(),bytes=len(enc),roundtrip=True,crc_verified=True))
(D/'wrapper-proof.json').write_text(json.dumps(proof,indent=2));print('PASS:',len(proof),'client packages, filename-bound 121 wrappers and checksum-verified full round trips.')
