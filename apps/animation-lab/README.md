# Nexus L2 Animation Lab — primera versión

Abrir desde E:/l2-local/EDITOR-ANIMACIONES-L2.cmd. Es un editor especializado dentro de Blender3.5.1, con panel lateral Nexus L2; no es una web ni requiere instalar un addon global. Lanzador usa --factory-startup y registra addon únicamente en ese proceso. Guardar el .blend conserva acciones, resultados y recetas. Volver a abrir con el lanzador para cargar también el panel.

## Uso
1. En la vista3D pulsar N si no aparece panel lateral; pestaña Nexus L2.
2. Elegir Base (Wyvern/Strider/caminar/etc.) y Capa superior (casteo/arco/gesto).
3. Peso0 mantiene la base; peso1 toma la capa. Torso y cabeza permiten mezcla intermedia. Brazos separados.
4. Conservar pelvis y piernas evita reemplazarlas con la capa. Fijar raíz elimina desplazamiento global de la base, usando su primer fotograma. No fija al mundo cada articulación: sigue siendo una postura animada y requiere anclaje a montura real aparte.
5. Opcional: modoPose y seleccionar huesos, activar máscara Solo seleccionados para limitar aún más la capa.
6. Ajustar fotogramas, velocidades y desfases; Generar mezcla y previsualizar crea acción nueva, no destruye fuentes. Reproducir/Pausar o barraespaciadora muestra resultado. Cambiar un control requiere generar otra mezcla, no actualización automática continua.
7. Resultado + Cargar receta recupera configuración y selección de huesos de una mezcla anterior. Nombre nuevo para mantener versiones.
8. Exportar guarda PSA, UKX, recipe.json y log bajo animation-lab/exports/<acción>. No sobrescribe carpeta existente. Guardar .blend aparte para conservar edición completa.

## Biblioteca incluida
29acciones nativas reales de Fighter mujer: Wyvern,Strider,CastShort/Mid/Long/End,arco,run/walk ysociales. Además postura de agacharse y mezcla de manos de Studio previamente retargeteadas. No incluye todas las animaciones de Koikatsu ni montura/armas como mallas de vista previa. Para incorporar más clips hay que extraer/adaptar al mismo esqueleto y cargarlos como acciones de Blender. Primera versión restringida a76huesos Fighter mujer; no convertir cuerpos distintos por nombres parecidos. Compatibilidad de bones verificada antes de mezclar. Exportador nativo verifica orden con PSK original.

La biblioteca de movimiento original y la configuración del panel se guardan en Nexus-L2-Animation-Lab.blend. Acciones de ejemplo generadas sin instalar en juego: Wyvern_Conjuro_Prueba. Ejemplo sin geometría del dragón, por lo que la postura sentada queda flotando o por debajo del suelo si se agrega una plancha arbitraria. Editor no contiene suelo de colisión ni representa altura de la montura. Para vista3D se retiraron piso/luces de QA. No entregar render de QA con suelo como muestra final de encaje.

## Verificación
prepare_lab.py arma biblioteca y verifica numéricamente el mezclador: piernas/pelvis coinciden con base hasta1.2e-7, brazos peso1 con cuaterniones de capa,raízfija. Exportación real por operadorUI completada. UModel recargaUKX y roundtripPSA preserva120frames76huesos30fps, posición/rotación error0.0 (export-validation.json). No reproducción de esta mezcla en clienteL2 aún. Aviso de lectura SCALEKEYS del PSA nativo indica extensión no reconocida por importer; no asumir que escalas nativas se recuperan (movimiento de muestra sin escala especial). El mezclador nuevo sí exporta escala .blend, pero PSA/UKX estándar usado guarda posición/rotación, no escala animada.

## Límites de primera versión
No IK de contacto configurable, vista de montura, ajuste de empuñaduras, timeline con varias capas/entradas/salidas ni asociación automática a skills. Mezcla interpolada de transformaciones locales; requiere revisión de hombros/torso/pies y posibles colisiones con dragón/arco/Arcana. Casteo montado real depende del servidor y del binding cliente. No instala automáticamente ni modifica runtime/core/DB/salasPvP. No declarar combate montado implementado por ver una animación.

## Archivos
nexus_animation_lab.py addon local, open_lab.py arranque, prepare_lab.py generador, Abrir-Editor.ps1 launcher. Blender3.5.1 en D:/BlenderVersions y herramientas/extractos/PSK en E:/l2-local. Rutas adaptables si cambiaPC. No reejecutar prepare_lab.py sobre trabajo editado: genera escena base y prueba exportación con carpeta ya existente que rechazará sobrescritura. Hacer copia .blend de usuario antes de reconstruir biblioteca.

## Interfaz simplificada V0.2 — 15/10/2026
Actualizada y abierta nueva instancia desde lanzador. No se cerraron ni guardaron ventanas previas del usuario.
Panel dividido1Modelo/2Animaciones/3Partes/4Vista previa. Cargar modelo admitePSK,FBX,GLB/GLTF,BLEND con exactamente1rig y jerarquía exacta Fighter mujer76huesos; oculta modelo anterior, no borra. Es importador compatible, NO retarget universal ni cambia cliente. Cargar objeto/montura de referencia admiteOBJ,FBX,GLB/GLTF,BLEND sin reemplazar rig de mezcla. Referencias se colocan manualmente.
Cargar animaciones admitePSA(conjunto de nombres76huesos igual) oacciones deBLEND(contracks para rig). PSA/BLEND puede traer variosclips y se eligen enBase/Capa. Clips crudos Unity/Koikatsu no se cargan directamente; extraer/adaptar antes. Importa animaciones y deja acción activa anterior. Modelo nuevo obtiene animation_data almezclar (corregido fallo detectado prueba).
Selecciones rápidas Solo brazos/Torso y brazos/Cuerpo completo/Solo piernas, sliders regionales0base/1capa; bloqueo pelvis/piernas de base. Ver base/Ver capa/Ver resultado cambian acción mostrada; Reproducir anima; Centrar encuadra; Generar mezcla hace resultado nuevo. Cambiar pesos requiere Generar de nuevo. Máscara de huesos,root,velocidades/desfases pasan aAjustes avanzados. Cargar receta devuelveconfiguración.
Prueba significativa verify_interface_v2.py: todospresets,importPSA,importmodeloPSK,modelo anterioroculto,mezcla sobrerigcargado,restauraciónrecetaPASS(interface-v2-validation.json). Nuevos botones preview implementados; UI nativa no capturada automáticamente. Test de panel no sustituye inspección humana. Backup addon v01 conserva versiónanterior. Scene principal no sobrescrita paraevitar cambiosdeusuario.
