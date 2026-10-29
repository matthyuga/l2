# Corrección acumulada del creador

Última versión instalada: v6. Pendiente confirmación visual del usuario.

- v4: etiquetas F/G tras E, o H/I tras G, mediante acceso directo sólo para las opciones nuevas. La tabla nativa de textos queda conservada.
- v4: 112 FinalBlend con la misma configuración de transparencia y doble cara que el cabello nativo. Materiales en SysTextures/NexusHairMaterialsV2.utx.
- v5: posiciones, rotaciones y escalas de los 28 cabellos coinciden con sus 14 modelos originales; geometría/texturas/esqueleto comprobados.
- v6: ambos paquetes usan envoltorio Lineage2Ver121 ligado al nombre exacto, con CRC32 y descifrado completo verificados. Reemplaza los envoltorios 111 anteriores, después del aviso de corrupción del paquete de materiales.

El paquete de materiales se cargó y exportó con UCC nativo: 112 materiales, 0 errores/advertencias. UModel carga los materiales y sus texturas. Eso no sustituye la aceptación y representación del cliente real.

Instalación actual: engine.dll y NWindow.dll de hair-material-v4 en ambos perfiles; NexusAppearanceV1.u de esta carpeta en ambos perfiles; NexusHairMaterialsV2.utx de esta carpeta en SysTextures. sysstring-e.dat restaurado al original. El diagnóstico v3 ya no está en el motor. Cada etapa tiene manifiesto y respaldo; no ejecutar el restaurador histórico v1 contra los archivos actuales sin revisar los hashes de las etapas posteriores.
