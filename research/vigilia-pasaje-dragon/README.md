# Pasaje y mirador del dragón

build_passage.py parte del máster de vigilia-ajustes-estructura. Abre una bóveda real por diferencia booleana en el cuello y un hueco en la parte superior del cráneo. Añade grupos independientes de pasaje, mirador y figuras de referencia. Conserva las firmas de las mallas fuera del mascarón.

El máster mantiene las piezas por separado. La exportación pasaje.gltf compacta cuatro raíces, dejando intactos los recursos del resto de la aeronave. register-project.cjs genera vigiliaturbinas3 y -escala, y registra custom_vigilia_pasaje en los catálogos persistentes. --rebuild solo durante iteración previa a la entrega; preservar futuras ediciones del usuario.

design-audit.json documenta capacidad y puntos previstos para NPC/teleport. La auditoría geométrica comprueba el espacio vertical de .46 sobre cinco puntos de cada una de tres huellas en el mirador, contra la geometría real del mascarón. verify-passage.cjs verifica conservación de las otras 18 zonas, carga, exportación, guardado y recarga, y produce capturas incluyendo el interior y la variante con tres referencias.

Ver mapas editados/vigiliaturbinas3/README.md para instrucciones y créditos. No hay NPCs reales, teletransporte de servidor, geodata o instalación nativa.
