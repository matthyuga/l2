# Reparaci?n Tanda 2 v10 ? instalada; comprobaci?n visual pendiente

El usuario comprob? que v9 se ve mal en los siete casos. No atribuirlo a un archivo original corrupto: se verific? un error de la adaptaci?n de materiales.

Causa: se compactaron ?ndices de caras/materiales, pero no VMaterial.TextureIndex en MATT0000. Ejemplo v9: MElf H entra con ?ndices internos 1/2 y UModel exporta Tex1/material_1; MElf I s?lo exporta material_0 sin textura. Esto explica la textura desplazada y superficies grises. En v10 se renumeran tambi?n esos ?ndices y se exige que la exportaci?n de UCC tenga exactamente Tex0/Tex1 (o Tex0) en su orden correcto.

El bucle nativo de engine.dll, 10487a65..10487aa9, consulta GetPcTexNum antes de pedir GetPcTexName. Se a?adi? un hook a GetPcTexNum (entrada 10484240, export 1030a047) s?lo para los siete estilos nuevos: material count 1/2 en AH, 0 en BH desactivado. Los dem?s casos, incluidos Original y Tanda 1, siguen el c?digo nativo sin cambios.

Pruebas: siete geometr?as orientadas/esqueletos, enlaces de materiales correctos, doce texturas RGBA id?nticas y doce FinalBlend exportados por UCC nativo con cero errores/advertencias. 5824 casos de conteo/ABI y 112 ejecuciones del bucle nativo real, verificando que cada ?ndice activo recibe su FinalBlend. Pasan adem?s los 2303 casos anteriores y los 15486 casos Tanda 2. Los paquetes usan formato 121, CRC independiente y descifrado exacto. Las letras, selector, caras, servidor y personajes no cambian.

Instalar con python research/character-creation/2026-10-26-tanda2-v10/install.py cuando Lineage II est? cerrado. El script lo comprueba, crea backups, instala ambos perfiles y mantiene la reversi?n global de Tanda 2 apuntando a los archivos previos a v9. Instalada tras el usuario confirmar el cierre del cliente. Ambos perfiles y sus hashes verificados. La comprobaci?n visual dentro del juego sigue pendiente; no afirmar que la apariencia ya est? confirmada.
