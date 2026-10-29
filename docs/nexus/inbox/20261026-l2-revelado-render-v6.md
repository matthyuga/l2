# L2 — revelado gráfico V6 pendiente de prueba real

Usuario reportó mapa opaco tras V5. Servidor sigue registrando posiciones y lugares,
cliente recibe snapshots completos, pero la última sesión no tenía MATCHED V4.
No atribuir a V5 ni borrar progreso: falla enlace de textura dinámica.

En E:\l2-local\research\map-fog-render-v6 se preparó/instaló DLLV6 con L2 cerrado,
sin reinicio servidor. Backup backups\map-fog-render-v6-20261026-005508. REA confirmó
FD3DTexture::Cache D3DDrv RVA32ac0 (RET8, prólogo55 8d6c2490), getters14/50 para
UTexture y GPUcache+38. Hook por identidad del material evita depender de firma
leída del GPU. Refresh en Present cubre bindings retenidos. También UpdateTexture
para staging: pruebaHAL V4 falla12, V6 pasa, pero no es prueba de ruta real L2.
30476checks con Javafixture y HALmanaged/staged. Falta validación REAL del hook.

Se preguntó al usuario que abra L2/mapa para revisar logs. Buscar INSTALLED V6
native texture identity hook y MATCHED V6 native UTexture identity. Si faltaMATCHED,
investigar UI2Dmapping/atlasing. No afirmar solucionado sin observación.
Servidor V5 y datos FOG4 conservados. Documentación README/evidencia/manifiesto en
research\map-fog-render-v6. ManifiestoV4actualizado para restauración a V3.
