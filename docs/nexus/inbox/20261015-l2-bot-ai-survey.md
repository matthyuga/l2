# Investigacion de IA de bots

Sesion salas15/10/2026. Referencias descargadas y analizadas estaticamente en E:/l2-local/research/bot-ai-survey; README documenta snapshots, evidencia y plan.

L2Autobots (Elfocrash, Kotlin/aCis382) es mejor referencia tactica por clase: skills condicionales, kite, defensas y summons. Requiere port selectivo; no aplicar patch completo ni importar MP magico/clan-party amistosos que contradicen salas. L2jRoboto Java/aCis372 archivado es referencia mas antigua. PlayerExplains/l2-smartbot C4 conecta Ollama para dialogos/conocimiento/comandos; combate sigue reglas fijas en SmartBotController, no LLM que aprende PvP.

No se ejecutaron builds/SQL/parches ni se modifico runtime. Propuesta: cerebro local por roles/arma/skills hibridas, soporte/controles/posicion, conservando instancias, RoomCombatRules, recursos y tandas actuales. Dos copias de perfil aun requieren identidades independientes, tarea distinta.
