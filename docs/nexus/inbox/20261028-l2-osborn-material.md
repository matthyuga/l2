# Osborn corregido — 28/10/2026

Ficha m0527, LineageNPCs.e_patriarch_MOrc_m00 (12 NPC asociados). El cuerpo se recortaba por usar la alfa de Diffuse como opacidad. El Shader original declara Opacity=e_patriarch_MOrc_m00_t00_b01_or, distinto de Diffuse=e_patriarch_MOrcc_t00_b01_sp. Se compuso RGB del diffuse + alfa de Opacity y se aplicó AlphaRef=160/255 del FinalBlend original. Miniatura regenerada y material verificado en Three.js.

Informe y evidencia: E:\l2-local\research\osborn-material-fix-20261028\REVISION.md.

No se cambió geometría, huesos, animaciones, paquetes originales ni otras fichas. Caché actualizada y build_gallery.py respeta alpha_cutoff específico al reconstruir materiales.
