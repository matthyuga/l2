# Audio de Nexus TV: resultado de la investigacion

16/10/2026. El sonido actual sigue perteneciendo al reproductor dedicado de Chrome en Windows. Esta actualizacion NO lo convierte en sonido del juego.

## Evidencia del cliente

Se abrio `E:\l2\system-screen-lab\ALAudio.dll` con REA. SHA256: `7e0c506bd1200c6eb681096a2db22dc134e78c2d64b06a4e69da0dc0e0db3881`. La vista general de REA no termino; se continuo la inspeccion PE con pefile, sin cambiar el binario.

ALAudio carga OpenAL dinamicamente: contiene los nombres `OpenAL32.dll`, `DefOpenAL32.dll`, `alcGetCurrentContext`, `alBufferData` y las funciones de fuentes. El cliente trae ambas bibliotecas OpenAL. Sus exportaciones incluyen `UALAudioSubsystem::PlayMusic`, `StopMusic`, `GetSoundVolume` y `GetMusicVolume`. Engine exporta la variable estatica `USound::Audio`. Los imports PE completos quedaron en `audio-imports.json`.

Esto permite plantear un puente PCM hacia el contexto OpenAL del cliente, con buffers en cola y volumen tomado del subsistema de L2. No se llamaron estas funciones ni se verifico aun la mezcla dentro de una sesion real del juego. La existencia de los simbolos no prueba por si sola compatibilidad con todos los clientes.

## Implementacion siguiente

1. Archivo local: decodificar su audio a PCM con FFmpeg y compartir un buffer circular con el receptor. Reiniciar el buffer en cada seek/cambio de fuente y seguir el reloj de video.
2. Cliente: consumir PCM desde el contexto OpenAL existente; parar al cerrar/apagar la TV, respetar volumen del juego y evitar audio duplicado del navegador.
3. YouTube: obtener audio exclusivamente del reproductor dedicado, mediante captura autorizada de su propia pestana o una salida virtual dedicada. El IFrame oficial no entrega PCM a la pagina anfitriona. No basta con el canal de imagen CDP.
4. Despues: atenuacion por distancia a la pantalla, orientacion y sincronizacion entre espectadores. La prueba actual sigue siendo local a una PC.

Windows instalado: 10.0.19042. La API de captura por proceso que Microsoft documenta requiere build20348 o posterior; no es una solucion directamente disponible aqui. Capturar toda la salida de Windows mezclaria tambien el sonido de L2 y otras aplicaciones, por lo que no se implemento ese atajo.

Referencias primarias: [captura por proceso, Microsoft](https://learn.microsoft.com/en-us/samples/microsoft/windows-classic-samples/applicationloopbackaudio-sample/), [IFrame de YouTube](https://developers.google.com/youtube/iframe_api_reference).

No se cambio el dispositivo de sonido, no se instalo OBS ni un driver virtual y no se modificaron ALAudio/Engine/OpenAL.
