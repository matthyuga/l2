const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const code=fs.readFileSync('E:/l2-local/l2ini-local.js','utf8').split('const [command, iniPath, address]')[0];
const codec=vm.runInNewContext(code+'\n({decrypt,encrypt})',{require,Buffer,console,process});
for(const folder of process.argv.slice(2)){
 const file=path.join(folder,'l2.ini');let text=codec.decrypt(file).toString('utf8');
 if(!/^IsL2NetLogin=True\s*$/m.test(text)||!/^ServerAddr=127\.0\.0\.1\s*$/m.test(text))throw Error('Expected local online client');
 if(!text.includes('Paths=../nexus-tv/*.u')){
  if(!text.includes('[Core.System]'))throw Error('Missing resource path section');
  text=text.replace('[Core.System]','[Core.System]\r\nPaths=../nexus-tv/*.u');
  codec.encrypt(Buffer.from(text,'utf8'),file);
  if(codec.decrypt(file).toString('utf8')!==text)throw Error('INI roundtrip failed');
 }
 console.log('Online configuration and NexusTV resource path verified: '+folder);
}
