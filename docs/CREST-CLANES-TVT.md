# Crest y alianzas del TvT — 2026-10-10

Aplicadas a los tres clanes existentes. Las imágenes originales de crest son 24x12: alianza a la izquierda (8x12), clan a la derecha (16x12). Separadas y convertidas a DDS DXT1 mediante DDSConverter del servidor: 176 bytes por ally y 224 por clan.

| Clan | Alianza | Líder | Integrantes restantes |
|---|---|---|---|
| Hellsing | Hell | Hellkevin | Vaelkor, Noctis, Selene |
| Holly | Holly | Kaelis | Gorvak, Myrentha, Ignara |
| Sacred | Sacred | Caelan | Arden, Zhurak, Morvain |

Cada alianza tiene como fundador su propio clan. Clan nivel 5 para alianza; no se añadieron habilidades de clan. Membresías existentes preservadas: 4 por clan, 12 en total. Los bots conservan sus nombres persistidos ArenaNombre y sus nombres visibles del evento.

Backup anterior y resultado: backups/clan-crests-2026-10-10/before.json y after.json.
Artefactos: crest/prepared/*.png y *.dds. apply-crests.js tiene controles para impedir repetición accidental y valida líderes/miembros antes de modificar.

GameServer reiniciado sin jugadores conectados; carga 3 clanes y 6 crests, PID 20696. Panel iniciado para verificación. verify-arena-roster.js SUCCESS 19/19 y copias 7/7. Visualización en cliente pendiente; no se abrió cliente ni se inició un combate.

## Correccion posterior de compatibilidad

El cliente rechazo DDS16x12/8x12: el dibujo visible sigue asi, pero la textura necesita altura16. Instalados DDS16x16/8x16, IDs7–12, sin cambiar clanes/alianzas/miembros. Ver `CREST-CORRECCION-DIMENSIONES.md`. Carga6crests y roster19/19 comprobados; confirmacion visual pendiente.
