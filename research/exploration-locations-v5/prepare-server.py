from pathlib import Path
base=Path(__file__).resolve().parent
source=base.parent/'exploration-walking-v4/server/custom/ExplorationWalking/ExplorationWalking.java'
s=source.read_text(encoding='utf8')
changes=[
('private final ExplorationPlaces places;', 'private final ExplorationPlaces places;\n    private final NativeExplorationZones nativeZones;'),
('places=new ExplorationPlaces(Path.of("data/scripts/custom/ExplorationWalking/places.xml"));','places=new ExplorationPlaces(Path.of("data/scripts/custom/ExplorationWalking/places.xml"));\n        nativeZones=new NativeExplorationZones(Path.of("data/scripts/custom/ExplorationWalking"));'),
('ExplorationWalking V4.2 ready: "+places.size()+" named exploration places plus TownZones;', 'ExplorationWalking V5 ready: "+nativeZones.size()+" native records, "+nativeZones.maskCount()+" original zone masks;'),
('var place=town==null?places.find(p.getX(),p.getY(),p.getZ()):null;', 'var nativeZone=town==null?nativeZones.find(p.getX(),p.getY(),p.getZ()):null;\n            var place=town==null && nativeZone==null?places.find(p.getX(),p.getY(),p.getZ()):null;'),
('town!=null?"FOG4_TOWN_"+town.getTownId():place!=null?', 'town!=null?"FOG4_TOWN_"+town.getTownId():nativeZone!=null?"FOG4_PLACE_"+nativeZone.id:place!=null?'),
('town!=null?town.getName():place.name', 'town!=null?town.getName():nativeZone!=null?nativeZone.name:place.name')]
for before,after in changes:
    assert s.count(before)==1,before;s=s.replace(before,after)
(base/'server/custom/ExplorationWalking/ExplorationWalking.java').write_text(s,encoding='utf8')
print('Prepared native-first server recognition, original TownZones and old fallback preserved.')
