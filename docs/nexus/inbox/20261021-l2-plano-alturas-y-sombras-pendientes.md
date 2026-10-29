# L2 — plano de referencias y sombras pendientes

21/10/2026. Kevin pidió posponer las sombras y ver un plano matemático de altura/distancias entre suelo, muelle, naves y cielo.

- Sombras expresamente pendientes; anotado en `E:\l2-local\ANALISIS-CIELO-CICLO-Y-ALTURA.md`. No iniciar esa investigación hasta que Kevin la retome.
- Referencias del plano en `research\day-night-analysis\altitude-references.md`; visualización `alturas-muelle-aeronaves.html`.
- Cero local: suelo de regreso al Coliseo (148900,46100,-3403), región real de instalación del muelle denominado Gludio. No confundirlo con la ciudad geográfica de Gludio.
- Pisos nominales: muelleZ12016, naveZ12040, Aurelia terrazaZ12040/pisoBZ10792, Vigilia cubiertaZ12056/galeríaZ12760.
- Perfil vertical y planta X/Y con cuadrícula1000u; selector de dos referencias calcula ΔZ, distancia horizontal y recta3D. Unidades nativas, sin inventar conversión a metros.
- Skybox/sol/luna se muestran solo como posiciones técnicas separadas. No son techo ni altura atmosférica sobre el suelo local; se evita calcularles distancia de viaje.
- Validación Chrome: aritmética e interacción, anchos736/360/320 sin desbordes. Informe altitude-verification.json y capturas alturas-preview-*.png.
- Solo se crearon referencias/visualización y nota de pendiente. No se modificó juego, cliente ni Taller.
