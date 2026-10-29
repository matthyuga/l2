'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert');
const source = fs.readFileSync(path.join(__dirname, 'import-web-assets.cjs'), 'utf8');
const start = source.indexOf('const sceneAssetIds =');
const end = source.indexOf('fs.writeFileSync(dataPath', start);
const map = {id: 'scene_giran_city', path: 'exports/scene-giran-city/scene.gltf'};
const data = {scenes: [{asset: map.id}], assets: [map, {id: 'old'}]};
const gallery = {models: [{key: 'plant', status: 'ready', gltf: 'plant.glb', title: 'Plant', native: true}]};
vm.runInNewContext(source.slice(start, end), {data, gallery, fs: {existsSync: () => true}, path, catalog: __dirname});
assert.deepEqual(data.assets.map(asset => asset.id), ['plant', 'scene_giran_city']);
assert.equal(data.assets[0].native, true);
const current = JSON.parse(fs.readFileSync(path.join(__dirname, 'data.json'), 'utf8'));
for (const scene of current.scenes) {
  const asset = current.assets.find(asset => asset.id === scene.asset);
  assert(asset, `Missing canvas: ${scene.id}`);
  assert(fs.existsSync(path.resolve(__dirname, '../model-catalog', asset.path)), `Missing map file: ${scene.id}`);
}
assert.equal(current.assets.filter(asset => asset.id.startsWith('web_kenney_nature_')).length, 329);
assert.equal(current.assets.filter(asset => asset.id.startsWith('web_3td_ruins_')).length, 12);
console.log('PASS: web imports preserve map canvases; four scenes and 341 web assets registered.');
