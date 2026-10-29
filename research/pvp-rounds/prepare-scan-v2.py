from pathlib import Path
s=Path(__file__).resolve().parent
t=(s/'ScanPvpTerrain.java').read_text().replace('ScanPvpTerrain','ScanPvpTerrainV2').replace('6000,18000,-30000,-16000','0,18000,-30000,-1000')
(s/'ScanPvpTerrainV2.java').write_text(t)
(s/'scan-v2.mf').write_text('Manifest-Version: 1.0\nAgent-Class: ScanPvpTerrainV2\n\n')
