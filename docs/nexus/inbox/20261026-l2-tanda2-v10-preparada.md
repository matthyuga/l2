# L2: reparaci?n de Tanda 2 preparada, pendiente instalar

El usuario confirm? fallo visual en los siete estilos v9. Se comprob? que TextureIndex no se renumer? al quitar material vac?o: mallas importadas tienen referencias a skins 1/2 en lugar de 0/1. V10 lo corrige y a?ade GetPcTexNum para cargar todos los materiales. Pasa pruebas de enlaces nativos, 112 replays del bucle real y regresiones.

Trabajo real E:/l2-local/research/character-creation/2026-10-26-tanda2-v10. install.py listo y bloquea si L2 est? abierto. Se pidi? al usuario cerrar el cliente (PID 8712 al revisar); todav?a no confirm?. No se instal? v10. No afirmar corregido visualmente hasta nueva prueba. Bit?cora BITACORA-TANDA2-PEINADOS-20261026.md.


## Reparaci?n v10 instalada

El usuario confirm? el cierre del cliente. Se instal? v10 en ambos perfiles, con paquetes nuevos y correcci?n de GetPcTexNum. Verificados los hashes y backups de los ocho archivos de instalaci?n; el manifiesto de reversi?n global de Tanda 2 est? actualizado y consistente. No se modific? servidor, selector, originales, Tanda 1 ni caras. Backup: E:\l2-local\backups\tanda2-v10-20261026-193622. La comprobaci?n visual de los siete estilos sigue pendiente.
