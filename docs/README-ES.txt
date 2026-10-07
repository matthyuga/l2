LINEAGE II INTERLUDE LOCAL
==========================

YA ESTA CONFIGURADO
  El servidor y el cliente quedaron listos para jugar solo en este PC.
  Todo el servidor escucha unicamente en 127.0.0.1.
  Los accesos detectan automaticamente la letra actual del disco portatil.

INICIAR
  Haz doble clic en 2-JUGAR.cmd dentro de esta carpeta.
  Ese acceso inicia el servidor si hace falta, espera hasta que este listo y abre el juego.
  La primera carga del servidor puede tardar unos dos minutos.

PRIMERA CUENTA
  En la pantalla de login escribe cualquier usuario y contrasena nuevos.
  La cuenta se crea automaticamente.
  Tambien hay una cuenta local preparada para probar:
  Usuario: solo
  Contrasena: solo123

HACER UN PERSONAJE GM
  1. Crea el personaje y sal del juego.
  2. Haz doble clic en 4-HACER-GM.cmd dentro de esta carpeta.
  3. Escribe el nombre exacto del personaje.
  4. Entra de nuevo y usa //admin para abrir el panel.

SUBCLASES ACUMULATIVAS
  Usa //buildlab con un personaje GM. Solo la clase principal define la raza y la
  apariencia. La principal puede cambiar de raza, reiniciarse y evolucionar paso a
  paso desde clase inicial hasta tercera profesion. Las tres Sub no eligen raza:
  cada una guarda directamente una profesion de segunda clase y puede evolucionar
  opcionalmente a tercera. Hay botones para vaciar una Sub, las tres Sub o reiniciar
  todas las clases. Las ramas repetidas se bloquean y los skills se acumulan.

PANEL LABORATORIO L2
  Haz doble clic en 7-ABRIR-PANEL-L2.cmd dentro de esta carpeta.
  Se abre una interfaz local para revisar personajes e inventario, ajustar atributos
  de clases, editar potencia/coste/reutilizacion de skills y analizar combates.
  No necesita Internet ni Codex y solo escucha en http://127.0.0.1:3210.
  Cada cambio de XML crea una copia en D:\l2-local\backups\lab-panel.
  Para cerrar solamente el panel usa D:\l2-local\8-CERRAR-PANEL-L2.cmd.

LABORATORIO DE IDEAS PORTATIL
  Usa 9-ABRIR-LAB-IDEAS.cmd para trabajar en ideas, pendientes,
  decisiones y sesiones sin iniciar el Game Server ni MariaDB. Todo se guarda
  dentro de D:\l2-local\idea-lab\data y funciona sin instalar dependencias.
  Las conversaciones de docs chatsgpt se pueden consultar en modo lectura.
  Para cerrar su servidor local usa D:\l2-local\10-CERRAR-LAB-IDEAS.cmd.

LABORATORIO L2 EN MODO OFICINA
  Usa 11-ABRIR-LAB-L2-OFICINA.cmd desde el disco portatil. Inicia solamente
  MariaDB y el panel usando herramientas incluidas en el disco; no inicia Login,
  Game Server ni el cliente. Permite consultar y editar personajes, Ares/Nyx,
  clases, skills y telemetria existente. El reinicio queda bloqueado: los cambios
  se aplican al volver a la PC principal. Cierra todo con
  12-CERRAR-LAB-L2-OFICINA.cmd antes de desconectar el disco.

TELEMETRIA DE COMBATE
  El servidor registra golpes, skills lanzados, fallos, criticos, CP/HP/MP y muertes.
  El panel agrupa esos eventos por enfrentamiento y calcula DPS, dano recibido,
  distribucion por skill y recomendaciones. Tras instalar una actualizacion del
  capturador, usa el boton "Aplicar y reiniciar" con el cliente desconectado.

CATALOGO DE RAZAS, CLASES Y SUBCLASES
  La seccion Telemetria conserva perfiles separados para Principal, Sub 1, Sub 2
  y Sub 3. Cada perfil identifica la raza de la principal, las cuatro clases de
  la build, la clase activa, nivel, equipo, cantidad de efectos y stats finales.
  Se captura al entrar, al cambiar de clase y durante las pruebas de combate.
  Para una medicion base comparable usa nivel 80, el mismo equipo y cero efectos.

RAZA PERMANENTE
  Cambiar entre Principal y Sub conserva la raza, cuerpo y apariencia definidos
  por la clase principal. La raza solo cambia mediante el boton separado
  "Cambiar raza" de //buildlab. En laboratorio este boton es administrativo; para
  un servidor publico debe conectarse a un permiso o credito de servicio pagado.

GM SHOP
  Mirellas aparece junto al buffer del Coliseo. Vende armas, sets, joyas,
  consumibles y libros. Desde //buildlab puedes recibir 1.000.000.000 Adena.

VER ESTADO
  Haz doble clic en 3-ESTADO.cmd dentro de esta carpeta.

DETENER
  Sal del personaje y haz doble clic en:
  5-DETENER-SERVIDOR.cmd dentro de esta carpeta.

CONFIGURACION DEL CLIENTE
  El acceso 2-JUGAR.cmd usa la carpeta hermana l2\system-hud\L2.exe,
  sin depender de que el disco sea D:, E: u otra letra.
  Es una copia de pruebas con el HUD grafico de CP/HP para Ares.
  La base limpia y recuperable permanece en D:\l2\system-clean.
  D:\l2\system\l2.ini conserva intacto el cifrado original de 2007.
  Windows redirige L2authd.Lineage2.com a 127.0.0.1 mediante el archivo hosts.
  Para volver a aplicar esa entrada usa 0-CONFIGURAR-CLIENTE.cmd.
  La copia anterior de hosts esta en:
  D:\l2-local\backups\hosts-before-lineage2-local.txt

GAMEGUARD
  El GameGuard de 2007 intentaba conectarse a su actualizador antiguo y mostraba
  los errores de actualizacion, 610 y 153. El acceso local deriva de D:\l2\system-clean:
  conserva la pareja limpia Core.dll + NWindow.dll. En esta compilacion concreta,
  GL2UseGameGuard=1 hace que NWindow omita las comprobaciones antiguas; ponerlo en
  cero muestra el login pero impide autenticar. GameGuard.des se conserva con el
  nombre GameGuard.des.disabled-local.
  Windows puede pedir confirmacion de administrador al iniciar este cliente antiguo.
  Copia original: D:\l2-local\backups\GameGuard.des.original.bak
  Core limpio verificado: D:\l2-local\quarantine\lin2-il-w10-system\system\Core.dll
  NWindow original: D:\l2-local\backups\NWindow.dll.before-gameguard-disable.bak
  Archivo desactivado: D:\l2\system-hud\GameGuard.des.disabled-local

ARCHIVOS IMPORTANTES
  Configuracion del juego: D:\l2-local\server\game\config
  Tasas de EXP y drops:    D:\l2-local\server\game\config\Rates.ini
  Scripts y datos:         D:\l2-local\server\game\data
  Registros:               D:\l2-local\logs
  Cliente original:        D:\l2\system\l2.ini.original.bak

ARENA DE PRUEBAS
  La configuracion de Ares, la maga Nyx y el Build Lab estan en:
  D:\l2-local\ARENA-DE-PRUEBAS.txt

RED
  MariaDB:       127.0.0.1:3307
  Login Server:  127.0.0.1:2106
  Game Server:   127.0.0.1:7777
  Enlace interno 127.0.0.1:19014
  No se abrieron puertos del router ni reglas del firewall.
