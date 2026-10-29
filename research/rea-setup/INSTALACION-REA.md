> Actualizaci?n: instalaci?n completada y verificada. Ver REA-INSTALADO.md para el estado vigente.

# REA — descarga e instalación en Windows

Preparado el 15/10/2026. Se descargaron fuentes y paquete oficial; NO se ejecutó setup, no se instaló la skill de REA ni se modificó la configuración de agentes. No se conectó un MCP ni se analizó L2Damage.

## Descargas

- Repositorio oficial: https://github.com/morluto/rea
- Copia local: E:\l2-local\tools\rea
- npm oficial: rea-agents, versión descargada 6.5.0.
- Paquete local: E:\l2-local\research\rea-setup\rea-agents-6.5.0.tgz
- Integridad SHA-512 contrastada con el registro npm: PASS; URL y hashes en npm-package.json.
- El source main también declara 6.5.0, pero source y paquete publicado no se asumen idénticos.

## 1. Node.js y npm

REA requiere Node 22.19+ dentro de la rama22, 24.11+ dentro de la rama24, o26+. La copia portable del proyecto es Node13.14.0 y no sirve para REA. En el PATH de esta sesión no se encontraron node/npm/npx; esto no descarta otras instalaciones fuera del PATH.

La guía oficial propone Node24 LTS. Instalar desde https://nodejs.org/ o en PowerShell:

```powershell
winget install --exact --id OpenJS.NodeJS.LTS
```

Cerrar y abrir PowerShell; comprobar la versión efectiva antes de continuar:

```powershell
node --version
npm.cmd --version
```

No sustituir el node.exe portable antiguo: puede ser una dependencia de otros proyectos. Una instalación portable moderna separada también es posible.

## 2. Ver el plan de configuración

Con Node compatible y npm disponibles:

```powershell
npx.cmd -y rea-agents@6.5.0 setup --client codex --dry-run --json
```

Esto descarga/ejecuta la herramienta para preparar un plan, pero --dry-run no aplica la configuración del agente. Revisar rutas y cambios de MCP/skill que propone. No elegir todos los clientes si solo se busca uno.

Para aplicar después:

```powershell
npx.cmd rea-agents@6.5.0 setup --client codex
```

El instalador de REA muestra su plan y pide aceptación. Registra el MCP e instala sus instrucciones de trabajo, con backups de la configuración. El comando usa la versión fijada que descargamos; @latest puede cambiar.

No hace falta compilar el repositorio para esta vía. El repositorio sirve para inspección y desarrollo; el paquete npm incluye los archivos distribuidos. Conservar el TGZ como copia local.

## 3. Motor de análisis para EXE/DLL de L2

REA es el enlace; el análisis nativo necesita un proveedor. En Windows, la vía gratuita documentada es Ghidra, y REA la marca experimental. No recomendar Hopper para Windows: su documentación lo indica no disponible.

- Ghidra oficial: https://github.com/NationalSecurityAgency/ghidra/releases
- La documentación del source descargado declara Ghidra12.1.x, verificado con12.1.4, y JDK64 bits dentro del rango admitido por Ghidra (21+ en esa documentación).
- Nuestro proyecto tiene un JDK25 en E:\l2-local\tools\jdk-25.0.4.1+1; todavía no se probó con Ghidra.
- Para L2 importa el soporte PE x86/32bits. El source actual lo documenta; verificarlo mediante doctor y una muestra al configurar, sin asumir que toda función nativa funciona en Windows.

Tras descargar/descomprimir Ghidra y seleccionar las rutas REALES:

```powershell
$env:GHIDRA_INSTALL_DIR = 'E:\ruta-real\ghidra_12.1.4_PUBLIC'
$env:JAVA_HOME = 'E:\l2-local\tools\jdk-25.0.4.1+1'
npx.cmd -y rea-agents@6.5.0 doctor --provider ghidra --json
```

Esas variables son del PowerShell actual. El setup de REA puede guardar rutas verificadas del proveedor para el agente; no asumir que una app ya abierta recibe variables definidas después en otra terminal.

## 4. Verificación de conexión

Reiniciar el cliente/agente que indique el instalador y ejecutar:

```powershell
npx.cmd -y rea-agents@6.5.0 doctor --client codex --json
```

Luego comprobar desde una sesión nueva que aparecen las herramientas de REA. El diagnóstico del cliente y el diagnóstico de Ghidra son distintos: uno no garantiza el otro.

## Fuentes

- https://rea.tools/get-started/
- E:\l2-local\tools\rea\docs\installation.md
- E:\l2-local\tools\rea\docs\windows-ghidra-p0.md

Estado: descargas preparadas; instalación y conexión pendientes. No se modificó servidor o cliente L2.
