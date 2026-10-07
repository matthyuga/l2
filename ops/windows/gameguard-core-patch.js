#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const corePath = 'D:\\l2\\system\\Core.dll';
const backupPath = 'D:\\l2-local\\backups\\Core.dll.before-gameguard-disable.bak';
const exportName = '?GL2UseGameGuard@@3HA';

function parsePe(buffer) {
  if (buffer.toString('ascii', 0, 2) !== 'MZ') throw new Error('Core.dll no tiene cabecera MZ.');
  const pe = buffer.readUInt32LE(0x3c);
  if (buffer.toString('ascii', pe, pe + 4) !== 'PE\0\0') throw new Error('Core.dll no tiene cabecera PE.');
  const fileHeader = pe + 4;
  const sectionCount = buffer.readUInt16LE(fileHeader + 2);
  const optionalSize = buffer.readUInt16LE(fileHeader + 16);
  const optional = fileHeader + 20;
  if (buffer.readUInt16LE(optional) !== 0x10b) throw new Error('Se esperaba un DLL PE32.');
  const exportRva = buffer.readUInt32LE(optional + 96);
  const sections = [];
  const sectionTable = optional + optionalSize;
  for (let index = 0; index < sectionCount; index++) {
    const entry = sectionTable + (index * 40);
    sections.push({
      name: buffer.toString('ascii', entry, entry + 8).replace(/\0.*$/, ''),
      virtualSize: buffer.readUInt32LE(entry + 8),
      virtualAddress: buffer.readUInt32LE(entry + 12),
      rawSize: buffer.readUInt32LE(entry + 16),
      rawOffset: buffer.readUInt32LE(entry + 20),
    });
  }
  function rvaToOffset(rva) {
    const section = sections.find((item) => rva >= item.virtualAddress && rva < item.virtualAddress + Math.max(item.virtualSize, item.rawSize));
    if (!section) throw new Error(`RVA 0x${rva.toString(16)} fuera de las secciones PE.`);
    return section.rawOffset + (rva - section.virtualAddress);
  }
  const exports = rvaToOffset(exportRva);
  const functionCount = buffer.readUInt32LE(exports + 20);
  const nameCount = buffer.readUInt32LE(exports + 24);
  const functions = rvaToOffset(buffer.readUInt32LE(exports + 28));
  const names = rvaToOffset(buffer.readUInt32LE(exports + 32));
  const ordinals = rvaToOffset(buffer.readUInt32LE(exports + 36));
  for (let index = 0; index < nameCount; index++) {
    const nameOffset = rvaToOffset(buffer.readUInt32LE(names + (index * 4)));
    let end = nameOffset;
    while (buffer[end] !== 0) end++;
    const name = buffer.toString('ascii', nameOffset, end);
    if (name === exportName) {
      const ordinal = buffer.readUInt16LE(ordinals + (index * 2));
      if (ordinal >= functionCount) throw new Error('Ordinal exportado fuera de rango.');
      const dataRva = buffer.readUInt32LE(functions + (ordinal * 4));
      return { dataRva, dataOffset: rvaToOffset(dataRva), sections };
    }
  }
  throw new Error(`No se encontro el simbolo ${exportName}.`);
}

function inspect(filePath) {
  const buffer = fs.readFileSync(filePath);
  const pe = parsePe(buffer);
  return { buffer, ...pe, value: buffer.readUInt32LE(pe.dataOffset) };
}

const command = process.argv[2] || 'status';
if (!['status', 'disable', 'restore'].includes(command)) {
  throw new Error('Uso: node gameguard-core-patch.js status|disable|restore');
}

if (command === 'restore') {
  if (!fs.existsSync(backupPath)) throw new Error(`No existe la copia ${backupPath}`);
  fs.copyFileSync(backupPath, corePath);
}

let info = inspect(corePath);
if (command === 'disable' && info.value !== 0) {
  if (info.value !== 1) throw new Error(`Valor inesperado ${info.value}; no se modificara el DLL.`);
  fs.mkdirSync(path.dirname(backupPath), { recursive: true });
  if (!fs.existsSync(backupPath)) fs.copyFileSync(corePath, backupPath);
  info.buffer.writeUInt32LE(0, info.dataOffset);
  fs.writeFileSync(corePath, info.buffer);
  info = inspect(corePath);
  if (info.value !== 0) throw new Error('La verificacion posterior al parche fallo.');
}

console.log(`Symbol=${exportName}`);
console.log(`RVA=0x${info.dataRva.toString(16)}`);
console.log(`FileOffset=0x${info.dataOffset.toString(16)}`);
console.log(`Value=${info.value}`);
console.log(`Backup=${backupPath}`);
