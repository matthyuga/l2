'use strict';
const fs=require('fs'),path=require('path');
const source=fs.readFileSync(path.join(__dirname,'server.js'),'utf8')
  .replace('port=32290','port=32291')
  .replace("if(name==='/')name='/index.html';","if(name==='/')name='/giran-index.html';")
  .replace('index\\.html|app\\.js','giran-index\\.html|index\\.html|app-giran\\.js|app\\.js');
new Function('require','__dirname','__filename',source)(require,__dirname,__filename);
