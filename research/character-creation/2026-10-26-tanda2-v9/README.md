# Tanda 2 v9 ? instalada el 26/10/2026

Siete peinados a?adidos, sin sustituir Original, Tanda 1 ni caras. Elfa clara femenina fuera de esta ampliaci?n por pedido del usuario.

| Modelo | Opci?n de origen | Letra nueva |
|---|---|---|
| MElf | D | H |
| MElf | E | I |
| MDarkElf | D | H |
| FOrc | C | J |
| MOrc | B | H |
| MShaman | D | H |
| FDwarf | D | J |

Nuevos paquetes: NexusHairT2V9.u en system-hud y system-camera-online; NexusHairT2M9.utx en SysTextures. Cada uno usa formato 121 ligado a su nombre, con CRC y descifrado id?ntico al original compilado. Los siete dise?os conservan sus texturas de origen. A/B/C/D de Hair Color apuntan a los mismos materiales para estos siete estilos en esta primera versi?n; los anteriores conservan sus colores.

Las mallas de esta tanda incluyen los adornos de las capturas (gafas, m?scaras y otros elementos). Sus materiales se compactaron de los ?ndices usados a 0/1, manteniendo geometr?a y texturas; las piezas originales con ?ndice 0 sin tri?ngulos se quitaron. Se adapt? el esqueleto al nativo. La malla MElf I tiene una variaci?n de UV inferior a 0.0001 por la uni?n de cu?as casi iguales que hace UCC; el informe num?rico est? en asset-test-results.json.

Verificaci?n: 2303 casos de regresi?n de hooks anteriores; 15486 casos nuevos de recursos, materiales, selector y ABI, con engine/UI reubicados; 15876 casos sobre el bytecode Java real; siete geometr?as orientadas y esqueletos; doce texturas RGBA id?nticas tras recompilar; doce materiales FinalBlend cargados/exportados por UCC nativo con cero errores/advertencias. La comprobaci?n visual en el cliente, movimiento, cascos y persistencia de un personaje real queda para la revisi?n del usuario. No se crearon ni modificaron personajes de usuario.

Se actualizaron fuentes locales y overlay, y ?nicamente las dos entradas de CharacterCreate en ambos JAR, preservando las dem?s. Clase principal redefinida en GameServer vivo con agente que comprueba que no haya clientes conectados. No se reinici? el servidor. Se actualizaron las bases de reversi?n del m?dulo corporal para que una reversi?n de ese m?dulo conserve esta ampliaci?n.

Preparaci?n: se corrigieron antes de instalar las banderas de los objetos FinalBlend, su paquete separado y la condici?n que evita duplicar opciones al reconstruir el selector. El modo -v del decodificador qued? esperando y se sustituy? por CRC independiente y descifrado comparado byte a byte. Ninguno de esos paquetes intermedios se instal?.

Reversi?n: python research/character-creation/2026-10-26-tanda2-v9/rollback.py, cliente cerrado y GameServer vivo. El script comprueba hashes, restaura la clase viva y archivos previos. No toca personajes: si ya se guardaron personajes con ?ndices de Tanda 2, revisar sus apariencias antes de revertir para no dejarlos con ?ndices sin modelo. No se ejecut? la reversi?n sobre la instalaci?n exitosa.

Copias y manifiestos: installation.json y su carpeta backup. Final: final-verification.json. Evidencia de REA del selector nativo: ev_b678f28a6d92239aa3a62b8a76b7b8f280f5e44a8ea16f4aafc31d462006eeb2; offsets UI raza 0x1f0, arquetipo 0x1f4, sexo 0x1f8 confirmados con el binario nativo.
