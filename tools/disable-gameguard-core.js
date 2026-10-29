const crypto = require('crypto');
const fs = require('fs');

const [source, destination] = process.argv.slice(2);
if (!source || !destination) {
  throw new Error('Usage: node disable-gameguard-core.js SOURCE DESTINATION');
}

const data = fs.readFileSync(source);
const actualHash = crypto.createHash('sha256').update(data).digest('hex');
const profiles = {
  d83449b1cdf0ac717a98be9289caab03cb507324a696ef449e31369e28416639: { offset: 0x1373b0, before: 1 }
};
const profile = profiles[actualHash];
if (!profile) {
  throw new Error(`Unexpected source SHA256: ${actualHash}`);
}

// PE export ?GL2UseGameGuard@@3HA (rabin2 physical offset).
const { offset } = profile;
const before = data.readInt32LE(offset);
if (before !== profile.before) {
  throw new Error(`Unexpected GL2UseGameGuard value at 0x${offset.toString(16)}: ${before}`);
}

data.writeInt32LE(0, offset);
fs.writeFileSync(destination, data, { flag: 'wx' });
const outputHash = crypto.createHash('sha256').update(data).digest('hex');
console.log(JSON.stringify({ source, destination, offset: `0x${offset.toString(16)}`, before, after: 0, sourceSha256: actualHash, outputSha256: outputHash }, null, 2));
