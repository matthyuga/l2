const crypto = require('crypto');
const fs = require('fs');
const http = require('http');
const https = require('https');

function b64url(value) {
  const padding = '='.repeat((4 - value.length % 4) % 4);
  return Buffer.from(value.replace(/-/g, '+').replace(/_/g, '/') + padding, 'base64');
}

function requestJson(url, body) {
  return new Promise((resolve, reject) => {
    const req = https.request(url, { method: 'POST', headers: {
      'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body)
    }}, res => {
      let data = '';
      res.setEncoding('utf8');
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode < 200 || res.statusCode >= 300) return reject(new Error(`API HTTP ${res.statusCode}: ${data}`));
        try { resolve(JSON.parse(data)); } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.end(body);
  });
}

function download(url, destination, key, iv, total) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(destination, { flags: 'wx' });
    const decipher = crypto.createDecipheriv('aes-128-ctr', key, iv);
    let received = 0;
    const fail = err => { file.destroy(); fs.rm(destination, { force: true }, () => reject(err)); };
    const transport = new URL(url).protocol === 'http:' ? http : https;
    transport.get(url, res => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        file.close(); fs.rmSync(destination, { force: true });
        return download(res.headers.location, destination, key, iv, total).then(resolve, reject);
      }
      if (res.statusCode !== 200) return fail(new Error(`Download HTTP ${res.statusCode}`));
      res.on('data', chunk => {
        received += chunk.length;
        if (received === chunk.length || received - chunk.length < Math.floor(received / (64 * 1024 * 1024)) * (64 * 1024 * 1024)) {
          process.stderr.write(`\r${(received / 1048576).toFixed(1)} / ${(total / 1048576).toFixed(1)} MiB`);
        }
      });
      res.on('error', fail);
      decipher.on('error', fail);
      file.on('error', fail);
      file.on('finish', () => { process.stderr.write('\n'); file.close(resolve); });
      res.pipe(decipher).pipe(file);
    }).on('error', fail);
  });
}

(async () => {
  const [handle, encodedKey, destination] = process.argv.slice(2);
  if (!handle || !encodedKey || !destination) throw new Error('Usage: node mega-public-download.js HANDLE KEY DESTINATION');
  const raw = b64url(encodedKey);
  if (raw.length !== 32) throw new Error(`Unexpected MEGA key length: ${raw.length}`);
  const key = Buffer.alloc(16);
  for (let i = 0; i < 16; i++) key[i] = raw[i] ^ raw[i + 16];
  const iv = Buffer.concat([raw.subarray(16, 24), Buffer.alloc(8)]);
  const response = await requestJson(`https://g.api.mega.co.nz/cs?id=${Date.now()}`, JSON.stringify([{a:'g', g:1, p:handle}]));
  const info = response[0];
  if (typeof info === 'number') throw new Error(`MEGA API error ${info}`);
  if (!info.g || !Number.isFinite(info.s)) throw new Error(`Unexpected MEGA response: ${JSON.stringify(info)}`);
  console.log(`Downloading ${info.s} bytes from MEGA...`);
  await download(info.g, destination, key, iv, info.s);
  const size = fs.statSync(destination).size;
  if (size !== info.s) throw new Error(`Size mismatch: expected ${info.s}, got ${size}`);
  console.log(`Saved ${destination} (${size} bytes)`);
})().catch(err => { console.error(err.stack || err); process.exit(1); });
