# TVT manual run 2 analizado

Proyecto real E:\l2-local, 10/10/2026. Usuario confirmó victoria y diversión;
se analizó la telemetría existente SIN reinicios ni cambios de combate/IA/DB.

Hellsing 3–0–0, rondas contra Holly/Sacred/Holly de 39,242/47,191/86,155 segundos.
Run2 MANUAL WINNER_Hellsing; EVENT_END dropped=0; 654 impactos reales del registro
de grupo separados de solicitudes de skills. Evidencia TSV/JSON/manifest en
reports/group-agite-run-2. Informe portable ANALISIS-TVT-2026-10-10-RUN2.md,
copia CONTINUIDAD-W10/ANALISIS-TVT-RUN2.md y cloud-repo/docs (sin commit/push).

Daño Hellsing registrado313932,98: Hellkevin propio167509; Selene67866;
Vaelkor57796,87; Noctis+Nightshades10682,11; Amber10079. Crítico mayor del usuario
6644 Ice Vortex; Arcana Mace Acumen+16 frente a armas+4 en perfiles capturados.
Vaelkor recibió142799 directos y murió dos veces en ronda3; ambas resurrecciones
confirmadas. Noctis/Selene muy protegidos, con71 solicitudes aceptadas MajorHeal
y70CPclan entre ambos; no se infiere HP curado efectivo de solicitudes.

Amber18disparos:5 a Zhurak (886),13 a Nightshade de Myrentha (9193). Sin impactos
en ronda1; sin lluvia registrada dentro del TVT. Último hit a Nightshade fue699
de Amber; próxima muestra lo mostró muerto. No hay DEATH global para asegurar
formalmente último golpe. LabTelemetry filtra summon-vs-summon y por eso omite
esos13impactos; usar GroupAgite para analizar summons. Queda además un hit de
Hellkevin soloGroup y unoSelene soloLab; expuesto como limitación en informe.

Hallazgos para eventual mejora, TODAVÍA NO CORREGIDOS:
- GroupAgite detecta skill278 como cubic3 pero XMLes4; skill1281 busca1 peroes8.
  Noctis43invocacionescubics, Myrentha18Spark; revisar también capacidad máxima.
- Rivales presionaronfrente y dejaronapoyos libres. Revisarfoco/táctica.
- Selene/Noctis pidieron res del mismo cadáver concurrentemente; coordinar.
- Vaelkor resucitado quedó sin buffs yHPmax3213vs5374 inicial; revisar rebuff.
- Probar Amber fuego/lluvia/retarget antes de alterar daño por esta sola partida.

Daño es registro del motor, no HP neto: CP/TransferPain/overkill; estadoscada2s.
Partida valida manualmente equipos y res individuales; no demuestra balance
con equipoigualado, eficacia de todas las skills ni resurrección masiva.
