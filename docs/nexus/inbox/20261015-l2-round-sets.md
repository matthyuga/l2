# Salas: tandas por ronda y equipos aleatorios

Sesion salas15/10/2026, real E:/l2-local/research/pvp-round-sets. Aplicado en caliente PID27412 y fuentes runtime/source/overlay. Parties de jugadores se conservan por instruccion explicita; bots disuelven/rearman parties. Orden conjunto de jugadores/bots sorteado para repartir colores equilibrados en cantidad.

Proxima tanda nativa distinta preparada antes del limite; libera/restaura anterior y activa siguiente. Fallback conserva tanda actual y mezcla si no hay suficientes perfiles. Parar bots cancela tambien reservas preparadas. Seis activos +seis preparados auditados; transicion real probada en fixture aislado (no forzada en ronda de usuario), marcador/equipos/cleanup/party e instancia de Hellkevin verificados. README/verification.txt/installation.json documentan.

Instancias por modo ya existen. Dos copias de un perfil Noctis precisan identidades independientes: NO se implementaron clones ni nombres duplicados. Roster prestado y reservas siguen sin recuperacion persistente ante crash; detener bots antes de apagar o usar siege. Ultimo verificador de cadena ahora pvp-round-sets/verify-installation.py.
