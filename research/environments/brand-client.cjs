// Label the isolated client's server ID 1 without changing Lab/Damage files.
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('E:/l2-local/l2ini-local.js','utf8').split('const [command, iniPath, address]')[0];
const file = process.argv[2], label = process.argv[3];
if (!file || !['L2 Hellgames','L2 Academy'].includes(label)) throw new Error('Explicit environment label required');
const codec = vm.runInNewContext(source+'\n({decrypt,encrypt})', {require,Buffer,console,process});
const data = codec.decrypt(file);
let pos = 4;
function compact() {
 let b=data[pos++], n=b&63, neg=b&128, more=b&64, shift=6;
 while(more) { b=data[pos++]; n|=(b&127)<<shift; shift+=7; more=b&128; if(shift>34)throw new Error('Invalid compact integer'); }
 return neg ? -n : n;
}
function readString() {
 const n=compact(), size=Math.abs(n)*(n<0?2:1);
 if(size>100000 || pos+size>data.length) throw new Error('Invalid string length');
 const value=data.subarray(pos,pos+size).toString(n<0?'utf16le':'latin1').replace(/\0+$/,''); pos+=size; return value;
}
function writeString(value) {
 const raw=Buffer.from(value+'\0','latin1'); let n=raw.length;
 const bytes=[n&63]; n>>>=6; if(n)bytes[0]|=64;
 while(n){let b=n&127; n>>>=7; if(n)b|=128; bytes.push(b);}
 return Buffer.concat([Buffer.from(bytes),raw]);
}
const count=data.readUInt32LE(0), rows=[]; let found=0;
for(let i=0;i<count;i++) {
 const start=pos;
 const id=data.readUInt32LE(pos), tag=data.readUInt32LE(pos+4); pos+=8;
 let name=readString(), desc=readString();
 if(id===1){name=label; desc=label+' - entorno independiente'; found++;}
 const head=Buffer.alloc(8); head.writeUInt32LE(id,0);head.writeUInt32LE(tag,4);
 if(id===1) rows.push(head,writeString(name),writeString(desc));
 else rows.push(data.subarray(start,pos));
}
// The Lab table has an opaque extension after the declared row count.
// Preserve that suffix byte-for-byte rather than treating it as parsed rows.
if(found!==1 || !data.subarray(-13).equals(Buffer.from('\x0cSafePackage\0','latin1'))) throw new Error('Server table framing check failed');
const header=Buffer.alloc(4);header.writeUInt32LE(count);
const updated=Buffer.concat([header,...rows,data.subarray(pos)]);
codec.encrypt(updated,file);
if(!codec.decrypt(file).equals(updated))throw new Error('Server label roundtrip failed');
console.log(label+': client server label verified; opaque suffix preserved ('+(data.length-pos)+' bytes)');
