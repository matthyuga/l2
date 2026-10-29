// Apply observer-only input bindings before launch. Keep network/login settings intact.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '../..');
const target = path.resolve(root, '../l2/system-camera-online/user.ini');
const functions = fs.readFileSync(path.join(root, 'l2ini-local.js'), 'utf8').split('const [command, iniPath, address]')[0];
const codec = vm.runInNewContext(functions + '\n({decrypt,encrypt})', {require,Buffer,console,process});
const original = codec.decrypt(target).toString('utf8');
if (!original.includes('[Engine.Input]')) throw new Error('Missing Engine.Input section');
let updated = original;
const bindings = {F9:'camerawalking mode=on', F10:'camerawalking mode=off'};
for (const [key, command] of Object.entries(bindings)) {
    const pattern = new RegExp('^' + key + '=.*$', 'gm');
    updated = pattern.test(updated)
        ? updated.replace(pattern, key + '=' + command)
        : updated.replace('[Engine.Input]', '[Engine.Input]\r\n' + key + '=' + command);
}
if (updated !== original) {
    const backup = path.join(__dirname, 'online-user-before-camera-keys.ini.bak');
    if (!fs.existsSync(backup)) fs.copyFileSync(target, backup);
    codec.encrypt(Buffer.from(updated, 'utf8'), target);
    if (codec.decrypt(target).toString('utf8') !== updated) throw new Error('Input verification failed');
}
console.log('Observer bindings ready: F9 camera on; F10 camera off. Online runtime test pending.');
