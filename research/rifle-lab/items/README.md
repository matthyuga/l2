# Rifle item staging

No se modificaron clientes, servidor, base de datos ni personajes desde esta carpeta.

`stage_items.py` genera XML servidor y agrega filas a `weapongrp.dat` y `itemname-e.dat` dentro de esta carpeta. Se clona Short Bow **13** (BOW, sin grado, pAtk 16/mAtk 6, rango 500, velocidad 293). ID propuesto **32580**, libre en los XML y los catálogos del laboratorio al preparar el staging. Se vuelve a comprobar en cada ejecución. No se usa un tipo de arma nuevo: por ahora conserva mecánicas de arco, incluidas flechas, MP, ataques y animaciones existentes.

Entrada: JSON como `assets.example.json`; reemplazar `mesh`, `textures` en orden de materiales y `icon` por las referencias compiladas reales. El icono de arco es un sustituto válido mientras no haya icono propio.

```powershell
python E:\l2-local\research\rifle-lab\items\stage_items.py --assets E:\l2-local\research\rifle-lab\items\assets.json --output E:\l2-local\research\rifle-lab\items\stage
```

Opciones `--client-system` y `--server-items` permiten leer otra copia. Las salidas están limitadas a esta carpeta. No instala. El manifiesto registra SHA256 de entrada/salida, número de registros, conservación exacta de todos los registros antiguos y verificación de cifrado 413 por descifrado posterior. Se conservan también los bytes del pie original del catálogo.

`schema-smoke` es una prueba de estructura con referencias **provisionales**. Pasó con 1621 filas antiguas de armas y 9765 nombres preservados; no instalar esas salidas.

`catalog_weapon.py` extiende localmente el lector existente `research/amber-l2/scripts/contract_dat.py`: wrappers, condicionales, INT y UBYTE necesarios para estos dos catálogos. No cambia el lector compartido.

## Registro de servidor

El XML final puede instalarse en `game/data/stats/items` para el siguiente arranque; `ItemData` enumera sus archivos al construirse. Un simple reload **no descubre archivos nuevos** porque reutiliza `_itemFiles`.

Para una demostración temporal sin reiniciar hay un agente opcional compilado con `build_loader.py`: `loader-build/rifle-items-agent.jar`, Agent-Class `RiflePrototypeItems`. No se adjuntó. Recibe como argumento el directorio de staging absoluto, lee `32580-rifle-prototypes.xml` y registra únicamente IDs entre 32580 y 32589, rechazando colisiones. No da ítems, no toca personajes y no escribe archivos del servidor ni DB; sólo deja `registration.log` en staging. Un reinicio o recarga ItemData borra los registros transitorios. Debe coordinarse cualquier recarga posterior mientras existan objetos de prueba en inventarios.

Verificado: compilación del agente contra los JAR del servidor, estructura y roundtrip de los dos catálogos. Pendiente: referencias compiladas reales, carga dentro del juego, orientación en mano y ataques propios de rifle.
