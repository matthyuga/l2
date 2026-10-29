const crypto = require('crypto');
const fs = require('fs');

const [source, destination] = process.argv.slice(2);
if (!source || !destination) {
  throw new Error('Usage: node disable-gameguard-nwindow.js SOURCE DESTINATION');
}

const data = fs.readFileSync(source);
const expectedHash = 'cb85f7a5de375f1e9156ec6559aae2a0a809b3abac4150142aafb14bbf02b47b';
const actualHash = crypto.createHash('sha256').update(data).digest('hex');
if (actualHash !== expectedHash) {
  throw new Error(`Unexpected source SHA256: ${actualHash}`);
}

const patches = [
  {
    // NConsoleWnd::Initialize: do not invoke the obsolete GameGuard error
    // handler. NOP the argument setup as well, so the stack stays balanced.
    offset: 0x16a51e,
    before: Buffer.from('8b4508508bcee827d6fdff', 'hex'),
    after: Buffer.alloc(11, 0x90),
  },
  {
    // NConsoleWnd tick: skip the obsolete GameGuard process/error check.
    // Original: jne 0x1016a980. Patched: nop; jmp 0x1016a980.
    offset: 0x16a8e0,
    before: Buffer.from('0f859a000000', 'hex'),
    after: Buffer.from('90e99a000000', 'hex'),
  },
];

for (const patch of patches) {
  if (!data.subarray(patch.offset, patch.offset + patch.before.length).equals(patch.before)) {
    throw new Error(`Unexpected bytes at 0x${patch.offset.toString(16)}`);
  }
  patch.after.copy(data, patch.offset);
}

fs.writeFileSync(destination, data, { flag: 'wx' });
const outputHash = crypto.createHash('sha256').update(data).digest('hex');
console.log(JSON.stringify({
  source,
  destination,
  patches: patches.map(({ offset, before, after }) => ({
    offset: `0x${offset.toString(16)}`,
    before: before.toString('hex'),
    after: after.toString('hex'),
  })),
  sourceSha256: actualHash,
  outputSha256: outputHash,
}, null, 2));
