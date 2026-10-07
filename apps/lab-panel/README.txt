LABORATORIO L2
===============

Abrir:
  ..\7-ABRIR-PANEL-L2.cmd

Cerrar:
  ..\8-CERRAR-PANEL-L2.cmd

Dirección local:
  http://127.0.0.1:3210

El panel no usa Internet y sólo escucha en esta PC.

Modo oficina portátil:
  Doble clic en ..\11-ABRIR-LAB-L2-OFICINA.cmd

  Este modo usa Node y MariaDB incluidos en el disco, funciona aunque cambie la
  letra de unidad y no inicia Lineage II. Para cerrarlo correctamente antes de
  retirar el disco usa ..\12-CERRAR-LAB-L2-OFICINA.cmd.

Secciones:
  - Personajes: ficha, build, recursos, inventario y valores seguros.
  - Razas y clases: atributos base y progresión al nivel 80.
  - Skills: potencia por nivel, coste, casteo, rango y reutilización.
  - Telemetría: DPS, daño recibido, recursos, rotación y diagnóstico.

Los cambios de XML se replican en servidor y código fuente. Antes de cada
guardado se crea una copia dentro de ..\backups\lab-panel.

Los cambios de clase o skill requieren reiniciar el Game Server. El botón
"Aplicar y reiniciar" respeta el protector existente y no expulsa al cliente:
si detecta una conexión activa, cancela el reinicio.
