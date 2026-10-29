# Amber: asistencia activable — 10/10/2026

Origen: sesión Amber. Proyecto real E:\l2-local, cliente E:\l2\system-hud.

Usuario pidió que la asistencia fuera una skill activable que pueda apagar. Implementada quinta habilidad temporal19014 **Asistencia de Amber**, toggle nativo T/SELF, icono provisional icon.skill0337, coste cero, sin funciones de estadísticas. Nueva invocación comienza manual. Alt+K/barra: clic ON/OFF. `.amber auto/manual` y órdenes nativas Seguir/Detener sincronizan el mismo estado e indicador. Puede apagarse durante una lluvia comprometida sin cancelar el lanzamiento. Morir, retirar, logout o ruptura limpian el estado; ruptura revoca cinco skills. Sin summon/contrato no queda toggle activo.

123 checks PASS con probes de ambercontracttest en instancia privada, incluyendo clics Player.useMagic, muerte, contrato sin summon, limpieza y regresión de IA/arco/fuego/lluvia. Core conservado SHA256 2E35D88F6050EB22619ADF00EE0070494126AE0ED535DC33B0E4C1E18BC99349. Solo scripts Amber/XML y registro del efecto nuevo; otros módulos preservados.

Cliente: una fila nueva en cada DAT actual skillgrp/skillname-e; 29839 previas byte idénticas, nuevo total29840. Protocolo413 roundtrip PASS, preservadas revisiones visuales existentes. Builder research/amber-l2/scripts/build_amber_assist_toggle_client.py prepara sin instalar ni reiniciar y rechaza IDs duplicados. No ejecutar el constructor antiguo sobre respaldos históricos.

Docs AMBER-ASISTENCIA-ACTIVABLE.md y CONTINUIDAD-W10/17_AMBER_ASISTENCIA_ACTIVABLE_2026-10-10.md. Prueba backups/amber-assist-toggle-2026-10-10/verification-123-checks.log; reporte reports/amber-assist-toggle-verification.json. Runtime/source/dist/overlay propios sincronizados localmente, sin commit/push. Falta revisión visual del usuario en cliente. Arranque normal lab.amber.verify=false después de la prueba, con L2 cerrado y cero conexiones comprobados.
