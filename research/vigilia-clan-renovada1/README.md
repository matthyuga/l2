# Vigilia renovada1

Encargo: remodelar y decorar la aeronave de cabeza de dragón como nave de clan, conservando el mobiliario ya reducido y corrigiendo escaleras y timón respecto de los personajes.

Fuente efectiva: `../vigilia-clan-v3/Vigilia-clan-v3.blend`. Original y V3 instalada conservados. Diseño separado: `Vigilia-renovada1.blend`. Uso, enlaces y límites documentados en `../../mapas editados/vigiliarenovada1/README.md`.

Reproducción: Blender 5.0.1 con `build_renovation.py`, después `polish_export.py`; optimizar únicamente las dos copias de textura exportadas con Pillow a un máximo de 1024 px preservando proporción; Node24 con `register-project.cjs`. Si existen proyectos, el registro se detiene salvo `--rebuild`: conservar primero cualquier edición posterior del usuario. Reiniciar únicamente el servidor local del taller si cambia data.json.

`audit_geometry.py` lee el master y comprueba apoyos, altura libre y recorridos contra los triángulos con una envolvente de referencia de 24u de ancho y 46u de alto. `design-manifest.json` documenta dimensiones y conservación de los 22 componentes reducidos del dormitorio. `verify-renovation.cjs` renderiza las diez cámaras del editor real, revisa cuatro vistas con maniquíes, exporta, guarda por API y recarga. `render_presentation.py` crea las imágenes de presentación desde Blender.

Catálogo `custom_vigilia_renovada1`, escena `vigilia_clan`, proyectos `vigiliarenovada1` y `vigiliarenovada1-escala`. El segundo es una copia de revisión, no una vista sincronizada. No ejecutar instaladores históricos para instalar esta revisión sobre el mapa actual.
