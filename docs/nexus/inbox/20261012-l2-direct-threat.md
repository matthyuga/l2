# L2: macro de amenaza directa

- Proyecto: `E:\l2-local`.
- Implementado y activo el 12 de octubre de 2026: `.amenaza` / `.agresor` selecciona
  al responsable del último daño directo dirigido al jugador; summons/pets remiten
  al dueño. `.amenaza macro` crea un macro nativo sin duplicar ni pisar existentes.
- Excluye afectados secundarios de áreas/lanzas, auras sin objetivo individual,
  ticks periódicos, reflejos y daño transferido. Conserva el objetivo original al
  comenzar el cast. Caducidad 30 s; selección con controles de visibilidad, instancia,
  alcance, muerte y bloqueo de target. No ataca automáticamente.
- Núcleo y script compilados, JAR desplegado y servidor reiniciado sin clientes.
  26 comprobaciones de integración PASS con probes temporales en instancia privada.
- Documentación: `E:\l2-local\AUTOTARGET-AMENAZA.md`.
- Evidencia: `E:\l2-local\reports\direct-threat-2026-10-12\verification.txt`.
- Backup: `E:\l2-local\backups\direct-threat-2026-10-12`.
- Overlay preservado en la jerarquía existente del proyecto. No se hizo commit/push.
