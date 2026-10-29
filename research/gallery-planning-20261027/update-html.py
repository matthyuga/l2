from pathlib import Path
p=Path(r'E:\l2-local\research\model-catalog\gallery.html')
text=p.read_text(encoding='utf-8')
def replace(old,new):
 global text
 assert text.count(old)==1,old
 text=text.replace(old,new)
replace('gallery.css?v=20261023-items','gallery.css?v=20261027-planning')
replace('gallery.js?v=20261023-items','gallery.js?v=20261027-planning')
replace('Buscar nombre, ID o modelo','Buscar nombre, ID, idea o etiqueta')
replace('placeholder="Amber, Baium, Ketra, comerciante, 29020…"','placeholder="Raoul, capitán, Aden, 400k, 29020…"')
replace('<p id="locationNote"', '''<section class="planningFilters" aria-label="Filtrar mis propuestas"><label>Territorio propuesto<select id="plannedRegion"><option value="">Todos los territorios propuestos</option></select></label><label>Etiqueta provisional<select id="plannedTag"><option value="">Todas las etiquetas</option></select></label><p class="small">Organizá tus ideas con nombres y etiquetas propios desde la ficha de cada modelo.</p></section><p id="locationNote"''')
replace('<h2 id="detailTitle"></h2>','<h2 id="detailTitle"></h2><p id="detailOriginalName" class="small"></p>')
replace('<label>¿Para qué lo usarías?', '''<section class="planningEditor" aria-labelledby="planningHeading"><h3 id="planningHeading">Tu personaje provisional</h3><p class="small">Datos para tu historia. El nombre y las referencias del modelo original se conservan.</p><label>Nombre elegido o sugerido<input id="planningName" type="text" placeholder="Raoul, capitán del paso, nombre pendiente…"></label><div class="planningFields"><label>Territorio propuesto<input id="planningTerritory" type="text" list="planningTerritories" placeholder="Aden, Rune, Gludio…"></label><label>Facción o bando<input id="planningFaction" type="text" placeholder="Aden, Elmore, independiente…"></label><label>Nivel propuesto<input id="planningLevel" type="text" placeholder="70, 75-80, por definir…"></label><label>IP propuesto<input id="planningPower" type="text" placeholder="400k, 850k máximo…"></label></div><datalist id="planningTerritories"></datalist><label for="planningTagInput">Etiquetas provisionales</label><div id="draftTags" class="planningTags" aria-label="Etiquetas del personaje"></div><div class="planningTagEntry"><input id="planningTagInput" type="text" placeholder="capitán, prólogo, aliado…" aria-describedby="planningTagHelp"><button id="addPlanningTag" type="button">Añadir</button></div><p id="planningTagHelp" class="small">Enter, coma o «Añadir» para crear etiquetas. Podés escribir varias separadas por comas; × las quita.</p></section><label>¿Para qué lo usarías?''')
replace('<button id="saveFavorite"','<p id="planningSaveStatus" class="small planningSaveStatus" role="status"></p><button id="saveFavorite"')
p.write_text(text,encoding='utf-8')
print('Ficha y filtros añadidos; versiones de caché actualizadas.')
