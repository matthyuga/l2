#!/usr/bin/env node

// Minimal Lineage2Ver413 L2.ini reader/writer.
// Algorithm reference: https://github.com/achrafsoltani/lineage2-linux/blob/main/l2ini.py

const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

const HEADER = Buffer.from('Lineage2Ver413', 'utf16le');
const MODULUS = BigInt(
  '0x75b4d6de5c016544068a1acf125869f43d2e09fc55b8b1e289556daf9b875763' +
  '5593446288b3653da1ce91c87bb1a5c18f16323495c55d7d72c0890a83f69bfd' +
  '1fd9434eb1c02f3e4679edfa43309319070129c267c85604d87bb65bae205de3' +
  '707af1d2108881abb567c3b3d069ae67c3a4c6a3aa93d26413d4c66094ae2039'
);
const PRIVATE_EXPONENT = 0x1dn;
const LEGACY_413_MODULUS = BigInt(
  '0x97df398472ddf737ef0a0cd17e8d172f0fef1661a38a8ae1d6e829bc1c6e4c3c' +
  'fc19292dda9ef90175e46e7394a18850b6417d03be6eea274d3ed1dde5b5d7bd' +
  'e72cc0a0b71d03608655633881793a02c9a67d9ef2b45eb7c08d4be329083ce4' +
  '50e68f7867b6749314d40511d09bc5744551baa86a89dc38123dc1668fd72d83'
);
const LEGACY_413_PRIVATE_EXPONENT = 0x35n;
const PUBLIC_EXPONENT = BigInt(
  '0x30b4c2d798d47086145c75063c8e841e719776e400291d7838d3e6c4405b504c' +
  '6a07f8fca27f32b86643d2649d1d5f124cdd0bf272f0909dd7352fe10a77b34d' +
  '831043d9ae541f8263c6fe3d1c14c2f04e43a7253a6dda9a8c1562cbd493c1b6' +
  '31a1957618ad5dfe5ca28553f746e2fc6f2db816c7db223ec91e955081c1de65'
);

function modPow(base, exponent, modulus) {
  let result = 1n;
  base %= modulus;
  while (exponent > 0n) {
    if (exponent & 1n) result = (result * base) % modulus;
    exponent >>= 1n;
    base = (base * base) % modulus;
  }
  return result;
}

function bufferToBigInt(buffer) {
  return BigInt(`0x${buffer.toString('hex') || '0'}`);
}

function bigIntToBuffer(value, size) {
  const hex = value.toString(16).padStart(size * 2, '0');
  return Buffer.from(hex, 'hex');
}

function align4(value) {
  return (value + 3) & ~3;
}

function crc32(buffer) {
  let crc = 0xffffffff;
  for (const byte of buffer) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit++) {
      crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
    }
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function decryptBody(body, modulus, exponent) {
  const payloads = [];
  for (let offset = 0; offset < body.length; offset += 128) {
    const encrypted = body.subarray(offset, offset + 128);
    const plain = bigIntToBuffer(modPow(bufferToBigInt(encrypted), exponent, modulus), 128);
    const size = plain[3];
    const start = 128 - align4(size);
    payloads.push(plain.subarray(start, start + size));
  }
  const payload = Buffer.concat(payloads);
  return zlib.inflateSync(payload.subarray(4));
}

function decrypt(filePath) {
  const data = fs.readFileSync(filePath);
  if (!data.subarray(0, HEADER.length).equals(HEADER)) {
    throw new Error('El archivo no tiene formato Lineage2Ver413.');
  }
  const body = data.subarray(HEADER.length, data.length - 20);
  if (body.length === 0 || body.length % 128 !== 0) {
    throw new Error('El cuerpo RSA del archivo no es válido.');
  }
  try {
    return decryptBody(body, MODULUS, PRIVATE_EXPONENT);
  } catch (modernError) {
    return decryptBody(body, LEGACY_413_MODULUS, LEGACY_413_PRIVATE_EXPONENT);
  }
}

function encrypt(plain, filePath) {
  const compressed = zlib.deflateSync(plain);
  const length = Buffer.alloc(4);
  length.writeUInt32LE(plain.length);
  const payload = Buffer.concat([length, compressed]);
  const blocks = [];
  for (let offset = 0; offset < payload.length; offset += 124) {
    const chunk = payload.subarray(offset, offset + 124);
    const block = Buffer.alloc(128);
    block[3] = chunk.length;
    chunk.copy(block, 128 - align4(chunk.length));
    blocks.push(bigIntToBuffer(modPow(bufferToBigInt(block), PUBLIC_EXPONENT, MODULUS), 128));
  }
  const body = Buffer.concat([HEADER, ...blocks]);
  const tail = Buffer.alloc(20);
  tail.writeUInt32LE(crc32(body), 12);
  fs.writeFileSync(filePath, Buffer.concat([body, tail]));
}

function encrypt111(plain, filePath) {
  const header = Buffer.from('Lineage2Ver111', 'utf16le');
  const encrypted = Buffer.alloc(plain.length);
  for (let index = 0; index < plain.length; index++) {
    encrypted[index] = plain[index] ^ 0xac;
  }
  const body = Buffer.concat([header, encrypted]);
  const tail = Buffer.alloc(20);
  tail.writeUInt32LE(crc32(body), 12);
  fs.writeFileSync(filePath, Buffer.concat([body, tail]));
}

function serverAddress(text) {
  const match = text.match(/^ServerAddr=(.+)$/m);
  return match ? match[1].trim() : null;
}

function usage() {
  console.error('Uso: node l2ini-local.js status|decrypt|set|set111|setplain <archivo l2.ini> [IP]');
  process.exit(1);
}

const [command, iniPath, address] = process.argv.slice(2);
if (!command || !iniPath) usage();

const plain = decrypt(path.resolve(iniPath));
const text = plain.toString('utf8');

if (command === 'status') {
  console.log(serverAddress(text) || 'ServerAddr no encontrado');
} else if (command === 'decrypt') {
  process.stdout.write(text);
} else if (command === 'set' || command === 'set111' || command === 'setplain') {
  if (!address) usage();
  if (!/^(?:\d{1,3}\.){3}\d{1,3}$/.test(address)) throw new Error('La dirección debe ser una IPv4.');
  if (!serverAddress(text)) throw new Error('ServerAddr no encontrado.');
  const backup = `${path.resolve(iniPath)}.original.bak`;
  if (!fs.existsSync(backup)) fs.copyFileSync(path.resolve(iniPath), backup);
  const updated = text.replace(/^ServerAddr=.*$/m, `ServerAddr=${address}`);
  if (command === 'setplain') {
    fs.writeFileSync(path.resolve(iniPath), Buffer.from(updated, 'utf8'));
  } else if (command === 'set111') {
    encrypt111(Buffer.from(updated, 'utf8'), path.resolve(iniPath));
  } else {
    encrypt(Buffer.from(updated, 'utf8'), path.resolve(iniPath));
    const verified = decrypt(path.resolve(iniPath)).toString('utf8');
    if (serverAddress(verified) !== address) throw new Error('La verificación posterior al cifrado falló.');
  }
  console.log(`ServerAddr=${address}`);
  console.log(`Copia original: ${backup}`);
} else {
  usage();
}
