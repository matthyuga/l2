# L2: primer ensayo de exploración — 25/10/2026

Ruta real E:\l2-local\research\exploration-lab-v1. Fuentes Java preparadas en staging, adaptador compilado contra GameServer actual y 21 checks de estado PASS (python verify.py; PowerShell bloquea verify.ps1 por política local). No instalado/cargado: juego y servidor siguen intactos.

Una región anclable por GM; visita al entrar solicita título nativo una vez; baliza virtual por comando registra exploración personal; recuperación global independiente calcula TOTAL/PARTIAL/CLEAR. Todavía sin cristal físico ni cobertura gráfica. Persistencia global por archivo atómico y personal por PlayerVariables; runtime/DB/avisos nativos pendientes de validar en juego. Integración debe revisar whitelist WorldContent.ini y cargar una vez en arranque controlado, no hotreload. README conserva pasos y límites. No presentar como niebla implementada.

Actualizaci?n: Kevin pregunt? c?mo probarlo. Instaladas las dos fuentes y whitelist en runtime y fuente distribuible, con respaldo backups/exploration-lab-v1-20261025-204837 y manifiesto research/exploration-lab-v1/installation.json. Pendiente pr?ximo arranque controlado; no reiniciar mientras Kevin est? conectado. Sigue sin validaci?n visual ni niebla gr?fica.

Kevin cerr? el cliente y autoriz? continuar. Reiniciado solo GameServer; log confirma ExplorationLab V1 cargado y puerto7777 listo. Prueba visual y guardado real de personaje a?n pendientes. .explora ya disponible.

Kevin aport? dos capturas: t?tulo de descubrimiento visible; visita/baliza personales true con global=false da TOTAL; recuperar globalmente cambia a CLEAR. Activaci?n repetida reconocida. Falta reconexi?n/segundo personaje/entrada caminando y niebla gr?fica. Centro prueba -14570,-46575,-10847 (Pagan).

Validaci?n posterior de Kevin: tras la reconexi?n solicitada, captura muestra saludo de entrada, .explora iniciar y estado de la misma revisi?n con global=true, visita=true, baliza=true, CLEAR. No aparece repetido el t?tulo en la captura. Reconexi?n validada; reinicio completo de servidor y segundo personaje siguen pendientes.
