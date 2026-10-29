# REA instalado y verificado

15/10/2026, hora de Argentina. Instalación autorizada por el usuario: «quieres encargarte de todo?». Instalación local separada, sin sustituir Node antiguo ni alterar el servidor/cliente L2.

## Componentes

- Node.js portable24.22.0: `E:\l2-local\tools\node-v24.22.0-win-x64`.
- npm11.19.1 incluido en ese Node.
- REA6.5.0: `E:\l2-local\tools\rea-runtime\node_modules\rea-agents`.
- Ghidra12.1.4: `E:\l2-local\tools\ghidra_12.1.4_PUBLIC`.
- Java reutilizado: `E:\l2-local\tools\jdk-25.0.4.1+1`; doctor confirmó JDK64bits compatible.
- Source de referencia: `E:\l2-local\tools\rea`, HEAD f255899ee849aaef4a23fc385c62616ccf089e16.
- Lanzador CLI: `E:\l2-local\research\rea-setup\rea.cmd`.

Node y Ghidra se obtuvieron de nodejs.org y el release oficial NationalSecurityAgency/ghidra. SHA256 contrastado con SHASUMS256/metadata del release antes de extraer. REA se instaló desde el TGZ oficial6.5.0 ya verificado contra su SHA512 npm. URLs/hashes: dependencies.json y npm-package.json. Instalación npm con173 paquetes. No se habilitaron los scripts de instalación opcionales que npm dejó sin ejecutar; no hicieron falta para los análisis comprobados. No se verifican aquí Frida ni análisis dinámicos.

## Configuración

Plan revisado: setup-plan.json. Resultado: setup-result.json, status ready.

- Se añadió solo `[mcp_servers.rea]` a `C:\Users\KEVIN\.codex\config.toml`.
- Node y entrypoint del paquete registrados por ruta absoluta.
- Ghidra/Java registrados explícitamente en el entorno de ese MCP.
- Skill instalada en `C:\Users\KEVIN\.agents\skills\reverse-engineer-anything`.
- Backup creado por REA: `C:\Users\KEVIN\.codex\config.toml.rea.backup`.
- Copia adicional previa: `E:\l2-local\research\rea-setup\codex-config-before.toml` (configuración privada; no subir al repo).
- Comparación semántica de claves y conexiones previas: PASS, preservadas.
- No se cambió PATH global, Node portable13 antiguo, ni configuraciones de otros agentes.

## Verificaciones ejecutadas

1. CLI REA: versión6.5.0.
2. `doctor --client codex --provider ghidra --json`: healthy=true.
3. Proveedor Ghidra12.1.4 disponible; controles nativos Windows/NTFS/DACL/JobObject y JDK64bits PASS.
4. Sesión MCP real lanzada con el comando y entorno de config.toml: initialize + tools/list PASS,207 herramientas. Se comprobaron open_binary y procedure_pseudo_code.
5. Inspección por CLI de muestra EXE nativa x86: PE32, base0x400000,3 segmentos,4 procedimientos.
6. Sesión MCP real: abrir DLLx86 de muestra, descompilar0x401010 y observar la constante de retorno42, cerrar análisis: PASS.

Las muestras fueron generadas por `scripts/create-ghidra-windows-fixture.mjs` del repo oficial, en `tools/rea/build/fixtures`. Solo se analizaron estáticamente, no se ejecutaron. Evidencias: x86-inspection.json, mcp-verification.json, mcp-native-open_binary.json, mcp-native-procedure_pseudo_code.json, mcp-native-close_binary.json, doctor.json. El soporte Windows de REA/Ghidra continúa documentado como experimental; estas pruebas acreditan este entorno y las muestras, no todos los EXE/DLL de L2.

## Uso

Reiniciar completamente la app/agente y abrir una sesión nueva para cargar el MCP y la skill. La verificación directa de MCP no añade herramientas a la sesión de chat ya abierta.

Desde PowerShell, diagnóstico sin depender del PATH:

```powershell
& 'E:\l2-local\research\rea-setup\rea.cmd' doctor --client codex --provider ghidra --json
```

En una sesión nueva: «Comprueba las herramientas de REA y analiza estáticamente este archivo: [ruta]». Mantener el cliente/parche de L2Damage en carpeta separada cuando se descargue. Esta instalación no descargó ni examinó L2Damage.

Si se requiere desinstalar, usar el comando `uninstall --help` del lanzador para revisar su alcance y retirar solo la integración deseada. No sobrescribir toda config.toml desde el backup después de otros cambios sin comparar, porque podría borrar conexiones posteriores.

Fuentes: https://rea.tools/get-started/ ; https://github.com/morluto/rea ; https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build ; documentación MCP de OpenAI https://learn.chatgpt.com/docs/extend/mcp?surface=cli .
