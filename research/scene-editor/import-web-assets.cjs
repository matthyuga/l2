'use strict';

const fs = require('fs');
const path = require('path');

const lab = path.resolve(__dirname, '../..');
const catalog = path.join(lab, 'research/model-catalog');
const webRoot = path.join(lab, 'research/web-assets');
const galleryPath = path.join(catalog, 'gallery.json');
const gallery = JSON.parse(fs.readFileSync(galleryPath, 'utf8'));

function ensure(dir) { fs.mkdirSync(dir, { recursive: true }); }
function copy(source, target) { ensure(path.dirname(target)); fs.copyFileSync(source, target); }
function words(name) {
  return name.replace(/([a-z])([A-Z])/g, '$1 $2').replace(/[_-]+/g, ' ').replace(/\s+/g, ' ').trim();
}
function category(name) {
  const n = name.toLowerCase();
  if (/tree|plant|flower|grass|bush|mushroom|cactus|crop|reed|lily|log/.test(n)) return 'Web CC0 · Vegetación';
  if (/rock|stone|boulder|cliff|pebble/.test(n)) return 'Web CC0 · Rocas y naturaleza';
  if (/bridge|wall|fence|gate|tower|ruin|temple|cathedral|pillar|column|foundation|rail/.test(n)) return 'Web CC0 · Estructuras';
  return 'Web CC0 · Decoración natural';
}

function replaceBatch(batch, models) {
  gallery.models = gallery.models.filter(model => model.batch !== batch);
  gallery.models.push(...models);
}

const kenneySource = path.join(webRoot, 'sources/kenney_nature-kit');
const kenneyModels = path.join(kenneySource, 'Models/GLTF format');
const kenneySides = path.join(kenneySource, 'Side');
const kenneyExport = path.join(catalog, 'exports/web-kenney-nature');
const kenneyThumbs = path.join(catalog, 'thumbs/web-kenney-nature');
ensure(kenneyExport); ensure(kenneyThumbs);

const kenneyEntries = fs.readdirSync(kenneyModels).filter(file => file.toLowerCase().endsWith('.glb')).sort().map(file => {
  const stem = path.basename(file, '.glb');
  const thumb = path.join(kenneySides, stem + '.png');
  const renderedThumb = path.join(kenneyThumbs, stem + '.png');
  copy(path.join(kenneyModels, file), path.join(kenneyExport, file));
  if (fs.existsSync(thumb)) copy(thumb, path.join(kenneyThumbs, stem + '.png'));
  return {
    mesh: file,
    package: 'Kenney Nature Kit',
    key: 'web_kenney_nature_' + stem.toLowerCase().replace(/[^a-z0-9]+/g, '_'),
    category: category(stem),
    names: [words(stem)],
    title: words(stem),
    types: ['StaticMesh', 'Web', 'CC0'],
    gltf: 'exports/web-kenney-nature/' + file,
    thumbnail: (fs.existsSync(thumb) || fs.existsSync(renderedThumb)) ? 'thumbs/web-kenney-nature/' + stem + '.png' : null,
    status: 'ready',
    material_count: 1,
    batch: 'Web CC0 · Kenney Nature Kit',
    source_url: 'https://kenney.nl/assets/nature-kit',
    license: 'CC0-1.0'
  };
});
replaceBatch('Web CC0 · Kenney Nature Kit', kenneyEntries);

const ruinsExport = path.join(catalog, 'exports/web-3td-fantasy-ruins');
const ruinsThumbs = path.join(catalog, 'thumbs/web-3td-fantasy-ruins');
const ruinsEntries = [];
if (fs.existsSync(ruinsExport)) {
  ensure(ruinsThumbs);
  for (const file of fs.readdirSync(ruinsExport).filter(file => file.toLowerCase().endsWith('.glb')).sort()) {
    const stem = path.basename(file, '.glb');
    const preview = path.join(webRoot, 'sources/3td_fantasy-ruins/FantasyRuins_Ready', stem + '.jpg');
    const renderedPreview = path.join(ruinsThumbs, stem + '.png');
    if (fs.existsSync(preview)) copy(preview, path.join(ruinsThumbs, stem + '.jpg'));
    ruinsEntries.push({
      mesh: file,
      package: '3TD Fantasy Ruins',
      key: 'web_3td_ruins_' + stem.toLowerCase().replace(/[^a-z0-9]+/g, '_'),
      category: 'Web CC0 · Ruinas y estructuras',
      names: [words(stem)], title: words(stem),
      types: ['StaticMesh', 'Web', 'CC0'],
      gltf: 'exports/web-3td-fantasy-ruins/' + file,
      thumbnail: fs.existsSync(preview) ? 'thumbs/web-3td-fantasy-ruins/' + stem + '.jpg' : (fs.existsSync(renderedPreview) ? 'thumbs/web-3td-fantasy-ruins/' + stem + '.png' : null),
      status: 'ready', material_count: 1,
      batch: 'Web CC0 · 3TD Fantasy Ruins',
      source_url: 'https://opengameart.org/content/3td-fantasy-ruins-pack',
      license: 'CC0-1.0'
    });
  }
}
replaceBatch('Web CC0 · 3TD Fantasy Ruins', ruinsEntries);

gallery.models.sort((a, b) => (a.key || '').localeCompare(b.key || ''));
fs.writeFileSync(galleryPath, JSON.stringify(gallery, null, 2) + '\n');
const dataPath = path.join(__dirname, 'data.json');
const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
// Native map canvases are registered outside gallery.models. Keep their
// references when refreshing the placeable asset library.
const sceneAssetIds = new Set(data.scenes.map(scene => scene.asset));
const sceneAssets = data.assets.filter(asset => sceneAssetIds.has(asset.id));
data.assets = gallery.models.filter(model =>
  model.status === 'ready' && model.gltf && fs.existsSync(path.join(catalog, model.gltf))
).map(model => ({
  id: model.key,
  title: model.title,
  path: model.gltf,
  thumbnail: model.thumbnail || null,
  mesh: model.mesh || '',
  category: model.category || '',
  batch: model.batch,
  native: model.native === true,
  sourcePackage: model.sourcePackage
}));
for (const asset of sceneAssets) {
  if (!data.assets.some(candidate => candidate.id === asset.id)) data.assets.push(asset);
}
fs.writeFileSync(dataPath, JSON.stringify(data, null, 2) + '\n');
fs.writeFileSync(path.join(webRoot, 'import-manifest.json'), JSON.stringify({
  generated_at: new Date().toISOString(),
  packs: [
    { name: 'Kenney Nature Kit', license: 'CC0-1.0', source: 'https://kenney.nl/assets/nature-kit', imported: kenneyEntries.length },
    { name: '3TD Fantasy Ruins', license: 'CC0-1.0', source: 'https://opengameart.org/content/3td-fantasy-ruins-pack', imported: ruinsEntries.length }
  ]
}, null, 2) + '\n');
console.log(JSON.stringify({ kenney: kenneyEntries.length, ruins: ruinsEntries.length }));
