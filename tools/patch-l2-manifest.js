const crypto = require('crypto');
const fs = require('fs');

const [source, destination] = process.argv.slice(2);
if (!source || !destination) {
  throw new Error('Usage: node patch-l2-manifest.js SOURCE DESTINATION');
}

const input = fs.readFileSync(source);
const actualHash = crypto.createHash('sha256').update(input).digest('hex');
const supportedHashes = new Set([
  'cbec5e7f97dfc29b72232f39f08502e106b0af8862b5cb4e3afc0d64637ea591',
  '790d9068796714389d82a400d14d26dcb9e6ecdfc6c2b5eba92ebd1a441b10ee'
]);
if (!supportedHashes.has(actualHash)) {
  throw new Error(`Unexpected source SHA256: ${actualHash}`);
}

const before = Buffer.from('level="requireAdministrator" uiAccess="false"></requestedExecutionLevel>', 'ascii');
const after = Buffer.from('level="asInvoker" uiAccess="false">           </requestedExecutionLevel>', 'ascii');
if (before.length !== after.length) {
  throw new Error('Internal replacement length mismatch');
}

const offset = input.indexOf(before);
if (offset < 0 || input.indexOf(before, offset + 1) >= 0) {
  throw new Error('Expected exactly one requireAdministrator manifest entry');
}

after.copy(input, offset);
fs.writeFileSync(destination, input, { flag: 'wx' });
const outputHash = crypto.createHash('sha256').update(input).digest('hex');
console.log(JSON.stringify({ source, destination, offset, sourceSha256: actualHash, outputSha256: outputHash }, null, 2));
