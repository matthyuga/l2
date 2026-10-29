# Memoria de Lineage2 preparada para Windows 11

El usuario llevará físicamente el Seagate USB que hoy es E:. Se confirmó BusType
USB y que proyecto E:\l2-local, cliente E:\l2, herramientas y database\data están
en esa unidad. No hace falta copiar esos datos a otro disco para trasladarlos.

Se preparó E:\l2-local\CONTINUIDAD-W11\LEER-PRIMERO.md y copia de README/proyectos,
resumen Lineage2, notas de inbox y enlaces relevantes de Nexus en subcarpeta
Nexus. Copias verificadas por hash. La nueva sesión puede usar esa memoria si
K:\_CodexNexus no existe en Windows 11. Las letras históricas no son rutas nuevas.

Incluye estado final GroupAgite v1.1 PASS y pendientes manuales de Amber/4vs4,
core hash, cambios locales sin push y pasos antes de retirar/primer arranque.
Se anotaron dos MySqlBinLocation heredados a D:/l2-local/tools/... para revisar.

No se detuvo ni modificó el servidor/cliente/base. Antes de retirar: salir del
personaje, cerrar L2, ejecutar 5-DETENER-SERVIDOR.cmd, cerrar paneles/herramientas
que usen el disco y expulsar correctamente. El script solicita cierre limpio
de MariaDB. La ejecución en Windows 11 todavía debe verificarse.
