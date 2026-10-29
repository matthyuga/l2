# Composición del mapa — análisis nativo REA, 25/10/2026

## Alcance y resultado

Análisis estático realizado efectivamente con REA/Ghidra12.1.4 sobre E:\l2\system-hud\NWindow.dll, PE x86, SHA256 a8bda77a97cd3e8583ce61e227380303212dbfc25ae10f8907106379fec3f292. La DLL se abrió, se completó el análisis de Ghidra y se inspeccionaron funciones y referencias. No hubo instrumentación en vivo, cambios de binario ni pruebas de dibujo. La evidencia completa está en rea-map-composition-evidence.json (31 registros antes del cierre). Los exports Unreal y el layout XDAT proceden de la lectura local previa, no de Ghidra.

La idea del contenedor compartido es correcta como arquitectura. En este cliente, sin embargo, el contenido desplazable del mapa no es una imagen hija que podamos agrupar directamente mediante XDAT: su dibujo y desplazamiento ocurren dentro del control nativo NCMinimapWnd. Los hijos/siblings anclados a la ventana no heredan esos desplazamientos internos por el mero parentesco.

## Composición observada

```text
MinimapWnd / MinimapWnd_Expand           [ventanas y botones de interfaz]
  Minimap                              [control nativo NCMinimapWnd]
    OnPaint                            [rutina nativa, no nodos XDAT debajo]
      origen de dibujo y límites del visor
      DrawWorldMap o DrawTownMap
      iconos de cuadrícula y cuadrícula cuando corresponde
      ubicaciones de party / propio jugador / objetivos
      finalización del dibujo
  texturas UI de sombra y botones       [layout de la ventana]
```

Los nombres de las funciones locales FUN_* se asocian a nombres NCMinimapWnd mediante referencias de las rutinas de excepción contiguas y corroboración por llamadas/operaciones. Son identificaciones analíticas: no símbolos originales recuperados en todos los casos. Los tipos y convenciones inferidos por el decompilador no son aún una firma lista para hooks.

## Evidencias principales

| Hallazgo | Dirección / evidencia REA |
|---|---|
| OnPaint establece origen, pasa límites al backend y elige mapa global o urbano | 0x101895c0; ev_d783af944f8bfbd68c5e7b4438d746e6437602d0815f219ca08dd629c5593585 |
| Origen de render guardado explícitamente y sumado al dibujar texturas | 0x10002f40, ev_f7be6bb4a91fe29d26988f711926d98aac306ebf1ca48462981208cc1bf74bf7; 0x10021a00, ev_799ddb1fe48d5083efbc521e9c817af3ee93bb27e3dd45ed9892756e5f05465b |
| Mapa continental: doble bucle2x3, seis referencias de material desde objeto+0x1cc; pasa offsets internos a rutina de recorte | 0x10187910; ev_7142a8fbbc047f745043faef6adf4988622464ab78d0b8a72404ff20c8a6e82c |
| Recorte de cada bloque usa tamaño0x400=1024 y calcula destino/origen UV | 0x10187760; ev_bef1afc39b9a732ee89f41c246c7da74fe0aa04e6e5441e7ddeb291ecd6165ba |
| Mapa urbano sigue otra ruta, usa material local y los mismos offsets del objeto | 0x10189130; ev_66f1c64b3118cf0507508a69df8f4d42f9bafa885c9f3361aff4f8020f63921f |
| Arrastre modifica campos+0x25c/+0x260 y limita desplazamiento según dimensiones | 0x1018b5d0; ev_62fc27f990187765e172759753639930f7ffbeeff03082a5e3ac4e26b408bc38 |
| Centrado también modifica esos campos; modo/identificador de mapa en+0x250 | 0x1018a680; ev_a88f0c27706cc13d2946362732bdd6f135012f867675c4b35a56e24e034f1a82 |
| Iconos nativos ya restan esos offsets a sus posiciones, mostrando cómo mantenerse alineados | 0x10187d60; ev_a20820739302e6deeb1b094ee9209b5650bc3c222b7600192d54b96f3bbe7ea0 |
| DrawGridIcon construye registros de cuadrícula61x61; aparece solo en rama global del pintado | 0x10188d90 y0x101895c0; ev_0b823d0d61ad418479f228cf66149d05835f54ccd460b2b5c28179e12c9ab5f9 |

Los offsets son relativos al objeto de esta DLL exacta, no direcciones estables de memoria en ejecución. No trasladarlos a otra crónica o DLL sin verificar identidad. La fórmula aritmética completa mundo→mapa no quedó recuperada: el decompilador pierde parte de la semántica FPU alrededor de FUN_101c19e0. No inventar escalas ni usar coordenadas de ciudad como si fueran continentales.

## Decisión de implementación propuesta

Conservar las ventanas compacta/ampliada y NCMinimapWnd. Añadir una etapa PaintFog vinculada al dibujo nativo del mapa, aprovechando su origen, desplazamientos y recorte, en lugar de confiar solo en un padre común en XDAT.

Puntos candidatos: inmediatamente después de dibujar el fondo continental y el fondo urbano, dentro de OnPaint antes de finalizar el contexto de render. Se debe decidir el orden respecto a cuadrícula y marcadores. Un hook al retorno de DrawWorldMap/DrawTownMap es una hipótesis técnica para prototipo, no código verificado.

La niebla emplearía polígonos o máscaras por región cartográfica, convertidos a la proyección activa. El estado global/personal permanece en el servidor. La interfaz necesita un canal de sincronización aún no implementado entre ExplorationLab y cliente; el éxito de los títulos de descubrimiento NO acredita ese canal.

## Primera prueba que corresponde construir

1. En staging y contra esta identidad exacta, confirmar convención de llamada/contexto del dispositivo y el campo del mapa activo mediante ensamblado antes de escribir el hook.
2. Dibujar un rectángulo semitransparente de diagnóstico en una coordenada cartográfica fija, usando la transformación de este control.
3. Comprobar arrastre, recorte en los cuatro bordes, mapa compacto/ampliado, resolución y transición continental/ciudad. Diferenciar ampliar ventana de cambiar proyección o zoom urbano.
4. Solo después introducir cobertura por regiones y conectar TOTAL/PARTIAL/CLEAR. No crear miles de controles XDAT sin medición ni prometer una textura dinámica compatible por la existencia de SetTexture.
5. Revisar visibilidad de iconos y objetivos bajo niebla: dibujar una capa sobre el fondo no oculta automáticamente marcadores dibujados después. El marcador del jugador puede permanecer arriba, los demás requieren una política explícita.

Alternativas: un overlay exterior sincronizado leyendo estas transformaciones añade dependencia de estado interno y orden de dibujo. Una ventana cartográfica propia daría control completo, a coste de reconstruir proyección, interacción y marcadores. No parece necesario elegirla antes de probar el punto nativo localizado.

## Límites

El análisis responde dónde ocurre el desplazamiento y cómo se compone el mapa; no demuestra que el hook funcione ni que una máscara se pueda añadir sin problemas de rendimiento/compatibilidad. Tampoco se validó el recorte gráfico en ejecución: se identificó su ruta y cálculo en código. No se cambiaron cliente ni servidor durante esta investigación.
