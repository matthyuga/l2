/*
 * Actualizador web del cliente (Downloads).
 *
 * El jugador elige la carpeta del juego; se compara cada archivo con
 * /updater/manifest.json (tamano y SHA-256) y se baja solo lo que falta o
 * cambio, comprobando el hash antes de escribirlo. Los hashes ya calculados se
 * guardan en IndexedDB: la segunda vez solo se releen los archivos tocados.
 *
 * Usa la File System Access API, que solo tienen Chrome y Edge de escritorio.
 * Hace lo mismo que el launcher (L2Pride.exe), sin instalar nada.
 */
(function () {
    'use strict';

    var raiz = document.querySelector('[data-l2-actualizador]');
    if (!raiz) {
        return;
    }

    var T = {};
    try { T = JSON.parse(raiz.getAttribute('data-textos') || '{}'); } catch (e) { T = {}; }

    var URL_MANIFIESTO = raiz.getAttribute('data-manifiesto');
    var GRANDE = 48 * 1024 * 1024; // los mayores, de uno en uno (se tienen enteros en memoria)
    var A_LA_VEZ = 4;

    var bElegir = raiz.querySelector('[data-act-elegir]');
    var bCambiar = raiz.querySelector('[data-act-cambiar]');
    var aviso = raiz.querySelector('[data-act-aviso]');
    var nCarpeta = raiz.querySelector('[data-act-carpeta]');
    var panel = document.querySelector('[data-act-panel]');
    var nEstado = panel.querySelector('[data-act-estado]');
    var nDetalle = panel.querySelector('[data-act-detalle]');
    var nPc = panel.querySelector('[data-act-pc]');
    var nBarra = panel.querySelector('[data-act-barra]');
    var bParar = panel.querySelector('[data-act-cancelar]');

    function t(clave, vars) {
        // Con n = 1, la frase en singular si existe (clave + "1").
        if (vars && Number(String(vars.n).replace(/\D/g, '')) === 1 && T[clave + '1']) { clave += '1'; }
        var s = T[clave] || clave;
        Object.keys(vars || {}).forEach(function (k) { s = s.split(':' + k).join(vars[k]); });
        return s;
    }

    var soportado = 'showDirectoryPicker' in window && window.isSecureContext &&
        'DecompressionStream' in window && window.crypto && crypto.subtle && 'indexedDB' in window;

    if (!soportado) {
        bElegir.disabled = true;
        aviso.textContent = t('sinSoporte');
        aviso.hidden = false;
        return;
    }

    // ------------------------------------------------------------------
    // IndexedDB: la carpeta elegida y los hashes ya calculados
    // ------------------------------------------------------------------
    var db = null;

    function abrirDb() {
        return new Promise(function (ok) {
            try {
                var r = indexedDB.open('l2pride-actualizador', 1);
                r.onupgradeneeded = function () {
                    r.result.createObjectStore('kv');
                    r.result.createObjectStore('hashes');
                };
                r.onsuccess = function () { db = r.result; ok(); };
                r.onerror = function () { ok(); };
            } catch (e) { ok(); }
        });
    }

    function dbGet(almacen, clave) {
        return new Promise(function (ok) {
            if (!db) { ok(undefined); return; }
            try {
                var r = db.transaction(almacen).objectStore(almacen).get(clave);
                r.onsuccess = function () { ok(r.result); };
                r.onerror = function () { ok(undefined); };
            } catch (e) { ok(undefined); }
        });
    }

    function dbPut(almacen, clave, valor) {
        return new Promise(function (ok) {
            if (!db) { ok(); return; }
            try {
                var tx = db.transaction(almacen, 'readwrite');
                tx.objectStore(almacen).put(valor, clave);
                tx.oncomplete = function () { ok(); };
                tx.onerror = function () { ok(); };
            } catch (e) { ok(); }
        });
    }

    // ------------------------------------------------------------------
    // Pantalla
    // ------------------------------------------------------------------
    function bytes(n) {
        if (n >= 1073741824) { return (n / 1073741824).toFixed(2) + ' GB'; }
        if (n >= 1048576) { return (n / 1048576).toFixed(1) + ' MB'; }
        return Math.max(1, Math.round(n / 1024)) + ' KB';
    }

    // Lo que falta, ya con su frase: "less than a minute left", "about 12 min left".
    function tiempo(s) {
        if (s < 60) { return t('casiListo'); }
        if (s < 3600) { return t('quedan', { t: t('minutos', { m: Math.round(s / 60) }) }); }
        return t('quedan', { t: t('horas', { h: Math.floor(s / 3600), m: Math.round((s % 3600) / 60) }) });
    }

    function poner(estado, detalle, fraccion, tono) {
        panel.hidden = false;
        panel.classList.toggle('is-ok', tono === 'ok');
        panel.classList.toggle('is-mal', tono === 'mal');
        nEstado.textContent = estado;
        nDetalle.textContent = detalle || '';
        var barra = nBarra.firstElementChild;
        nBarra.classList.toggle('is-indeterminada', fraccion < 0);
        if (fraccion >= 0) {
            barra.style.width = (Math.min(1, fraccion) * 100).toFixed(1) + '%';
            nPc.textContent = tono ? '' : Math.floor(fraccion * 100) + '%';
        } else {
            barra.style.width = '';
            nPc.textContent = '';
        }
    }

    function mostrarCarpeta(h) {
        if (h) {
            nCarpeta.textContent = t('carpeta', { nombre: h.name });
            bElegir.textContent = t('actualizar');
            bCambiar.hidden = false;
        }
    }

    // ------------------------------------------------------------------
    // Archivos de la carpeta
    // ------------------------------------------------------------------
    function Carpeta(h) {
        this.h = h;
        this.dirs = {};
    }

    Carpeta.prototype.dir = async function (partes, crear) {
        var d = this.h;
        var ruta = '';
        for (var i = 0; i < partes.length; i++) {
            ruta += partes[i].toLowerCase() + '/';
            if (this.dirs[ruta]) { d = this.dirs[ruta]; continue; }
            d = await d.getDirectoryHandle(partes[i], { create: crear });
            this.dirs[ruta] = d;
        }
        return d;
    };

    Carpeta.prototype.archivo = async function (ruta, crear) {
        var p = ruta.split('/');
        var nombre = p.pop();
        var d = await this.dir(p, crear);
        return d.getFileHandle(nombre, { create: crear });
    };

    // null si no existe
    Carpeta.prototype.leer = async function (ruta) {
        try {
            var fh = await this.archivo(ruta, false);
            return await fh.getFile();
        } catch (e) {
            if (e && (e.name === 'NotFoundError' || e.name === 'TypeMismatchError')) { return null; }
            throw e;
        }
    };

    async function estaVacia(h) {
        // eslint-disable-next-line no-unused-vars
        for await (var _ of h.values()) { return false; }
        return true;
    }

    async function sha256(buf) {
        var d = new Uint8Array(await crypto.subtle.digest('SHA-256', buf));
        var s = '';
        for (var i = 0; i < d.length; i++) { s += (d[i] < 16 ? '0' : '') + d[i].toString(16); }
        return s;
    }

    function error(nombre, mensaje) {
        var e = new Error(mensaje);
        e.l2 = nombre;
        return e;
    }

    function explicar(e) {
        var n = e && e.name;
        if (e && e.l2) { return e.message; }
        if (n === 'NotAllowedError' || n === 'SecurityError') { return t('sinPermiso'); }
        if (n === 'NoModificationAllowedError' || n === 'InvalidModificationError') { return t('enUso'); }
        if (n === 'TypeError' || n === 'NetworkError') { return t('red'); }
        return (e && e.message) || String(e);
    }

    // ------------------------------------------------------------------
    // El trabajo
    // ------------------------------------------------------------------
    var carpetaGuardada = null;
    var trabajando = false;
    var control = null;

    async function permiso(h) {
        try {
            if ((await h.queryPermission({ mode: 'readwrite' })) === 'granted') { return true; }
            return (await h.requestPermission({ mode: 'readwrite' })) === 'granted';
        } catch (e) {
            return false;
        }
    }

    async function elegir() {
        try {
            var h = await window.showDirectoryPicker({ id: 'l2pride', mode: 'readwrite' });
            carpetaGuardada = h;
            await dbPut('kv', 'carpeta', h);
            mostrarCarpeta(h);
            return h;
        } catch (e) {
            if (e && e.name === 'AbortError') { return null; }
            throw e;
        }
    }

    async function actualizar(h) {
        trabajando = true;
        bElegir.disabled = true;
        bCambiar.disabled = true;
        bParar.hidden = false;
        control = new AbortController();
        var senal = control.signal;

        try {
            poner(t('conectando'), '', -1);
            var r = await fetch(URL_MANIFIESTO + '?t=' + Date.now(), { cache: 'no-store', signal: senal });
            if (r.status === 404) { throw error('publicar', t('noPublicado')); }
            if (!r.ok) { throw error('red', t('red')); }
            var m = await r.json();
            var carpeta = new Carpeta(h);

            // Es la carpeta del juego, o una vacia donde instalarlo.
            var instalar = false;
            if (!(await carpeta.leer('system/L2.exe'))) {
                if (!(await estaVacia(h))) { throw error('carpeta', t('noEsJuego')); }
                if (!window.confirm(t('instalarAqui', { tam: bytes(m.total || 0) }))) {
                    panel.hidden = true;
                    return;
                }
                instalar = true;
            }

            // ---- Revisar ----
            var pendientes = [];
            var total = m.archivos.length;
            poner(t('revisando'), '', 0);
            for (var i = 0; i < total; i++) {
                if (senal.aborted) { throw error('parado', t('detenido')); }
                var a = m.archivos[i];
                var e = { r: a[0], t: a[1], h: a[2], z: a[3], m: a[4] === 1 };
                var f = instalar ? null : await carpeta.leer(e.r);
                if (!f) {
                    pendientes.push(e);
                } else if (!e.m) {
                    if (f.size !== e.t) {
                        pendientes.push(e);
                    } else {
                        var clave = h.name + '|' + e.r;
                        var c = await dbGet('hashes', clave);
                        var hash = c && c.t === f.size && c.m === f.lastModified ? c.h : null;
                        if (!hash) {
                            nDetalle.textContent = e.r.replace(/\//g, '\\');
                            hash = await sha256(await f.arrayBuffer());
                            await dbPut('hashes', clave, { t: f.size, m: f.lastModified, h: hash });
                        }
                        if (hash !== e.h) { pendientes.push(e); }
                    }
                }
                if (i % 20 === 0) { poner(t('revisando'), nDetalle.textContent, (i + 1) / total); }
            }

            var borrar = [];
            for (var b = 0; b < (m.borrar || []).length; b++) {
                if (await carpeta.leer(m.borrar[b])) { borrar.push(m.borrar[b]); }
            }

            if (!pendientes.length && !borrar.length) {
                poner(t('listo'), t('listoVersion', { v: m.version }), 1, 'ok');
                return;
            }

            // ---- Bajar ----
            // Los archivos con el mismo contenido (hay .int identicos) se bajan una vez.
            var grupos = {};
            var unicos = [];
            pendientes.forEach(function (x) {
                if (!grupos[x.h]) { grupos[x.h] = []; unicos.push(x); }
                grupos[x.h].push(x);
            });
            var totalBytes = 0;
            unicos.forEach(function (x) { totalBytes += x.z || x.t; });
            var hecho = 0;
            var fallos = [];
            var titulo = instalar ? t('instalando') : t('bajando', { n: pendientes.length.toLocaleString() });
            var inicio = Date.now();
            var ultimo = { b: 0, t: inicio, v: 0 };

            var refresco = setInterval(function () {
                var ahora = Date.now();
                var s = (ahora - ultimo.t) / 1000;
                if (s >= 0.5) {
                    var v = (hecho - ultimo.b) / s;
                    ultimo.v = ultimo.v ? ultimo.v * 0.7 + v * 0.3 : v;
                    ultimo.b = hecho;
                    ultimo.t = ahora;
                }
                var d = t('de', { a: bytes(hecho), b: bytes(totalBytes) });
                if (ultimo.v > 0) {
                    d += ' · ' + bytes(ultimo.v) + '/s · ' + tiempo((totalBytes - hecho) / ultimo.v);
                }
                poner(titulo, d, totalBytes ? hecho / totalBytes : 0);
            }, 500);

            async function bajarUno(e) {
                var sumado = 0;
                for (var intento = 1; intento <= 3; intento++) {
                    try {
                        var url = m.base + e.h.slice(0, 2) + '/' + e.h + (e.z ? '.gz' : '.bin');
                        var resp = await fetch(url, { signal: senal });
                        if (!resp.ok) { throw error('red', 'HTTP ' + resp.status); }
                        var lector = resp.body.getReader();
                        var cuerpo = new ReadableStream({
                            pull: async function (c) {
                                var x = await lector.read();
                                if (x.done) { c.close(); return; }
                                hecho += x.value.byteLength;
                                sumado += x.value.byteLength;
                                c.enqueue(x.value);
                            },
                            cancel: function (motivo) { return lector.cancel(motivo); }
                        });
                        var flujo = e.z ? cuerpo.pipeThrough(new DecompressionStream('gzip')) : cuerpo;
                        var buf = await new Response(flujo).arrayBuffer();
                        if (buf.byteLength !== e.t || (await sha256(buf)) !== e.h) { throw error('danado', t('danado')); }

                        var grupo = grupos[e.h];
                        for (var j = 0; j < grupo.length; j++) {
                            var fh = await carpeta.archivo(grupo[j].r, true);
                            var w = await fh.createWritable({ keepExistingData: false });
                            await w.write(buf);
                            await w.close();
                            var f = await fh.getFile();
                            await dbPut('hashes', h.name + '|' + grupo[j].r, { t: f.size, m: f.lastModified, h: e.h });
                        }
                        return;
                    } catch (err) {
                        hecho -= sumado;
                        sumado = 0;
                        if (senal.aborted) { throw error('parado', t('detenido')); }
                        var n = err && err.name;
                        // Sin permiso o archivo en uso: repetir no sirve.
                        if (intento === 3 || n === 'NotAllowedError' || n === 'NoModificationAllowedError' || n === 'InvalidModificationError' || n === 'SecurityError') {
                            grupos[e.h].forEach(function (x) { fallos.push({ ruta: x.r, error: err }); });
                            return;
                        }
                        await new Promise(function (ok) { setTimeout(ok, 1200 * intento); });
                    }
                }
            }

            try {
                var grandes = unicos.filter(function (x) { return x.t >= GRANDE; });
                var chicos = unicos.filter(function (x) { return x.t < GRANDE; });

                for (var g = 0; g < grandes.length; g++) { await bajarUno(grandes[g]); }

                var cola = chicos.slice();
                var obreros = [];
                for (var k = 0; k < A_LA_VEZ; k++) {
                    obreros.push((async function () {
                        while (cola.length) { await bajarUno(cola.shift()); }
                    })());
                }
                await Promise.all(obreros);
            } finally {
                clearInterval(refresco);
            }

            for (var x = 0; x < borrar.length; x++) {
                try {
                    var p = borrar[x].split('/');
                    var nombre = p.pop();
                    await (await carpeta.dir(p, false)).removeEntry(nombre);
                } catch (e2) { /* si ya no esta, mejor */ }
            }

            if (fallos.length) {
                var primero = fallos[0];
                poner(t('fallaron', { n: fallos.length.toLocaleString() }),
                    primero.ruta.replace(/\//g, '\\') + ': ' + explicar(primero.error), 0, 'mal');
                return;
            }

            poner(t('listo'), t('listoArchivos', { v: m.version, n: pendientes.length.toLocaleString() }), 1, 'ok');
        } catch (e) {
            if (e && e.l2 === 'parado') {
                poner(t('detenido'), '', 0, 'mal');
            } else if (e && e.name === 'AbortError') {
                poner(t('detenido'), '', 0, 'mal');
            } else {
                poner(explicar(e), '', 0, 'mal');
            }
        } finally {
            trabajando = false;
            control = null;
            bElegir.disabled = false;
            bCambiar.disabled = false;
            bParar.hidden = true;
        }
    }

    bElegir.addEventListener('click', async function () {
        if (trabajando) { return; }
        try {
            var h = carpetaGuardada;
            if (h && !(await permiso(h))) { h = null; }
            if (!h) { h = await elegir(); }
            if (h) { await actualizar(h); }
        } catch (e) {
            poner(explicar(e), '', 0, 'mal');
        }
    });

    bCambiar.addEventListener('click', async function () {
        if (trabajando) { return; }
        try {
            var h = await elegir();
            if (h) { await actualizar(h); }
        } catch (e) {
            poner(explicar(e), '', 0, 'mal');
        }
    });

    bParar.addEventListener('click', function () {
        if (control) { control.abort(); }
    });

    window.addEventListener('beforeunload', function (ev) {
        if (trabajando) { ev.preventDefault(); ev.returnValue = ''; }
    });

    abrirDb().then(function () { return dbGet('kv', 'carpeta'); }).then(function (h) {
        if (h && typeof h.queryPermission === 'function') {
            carpetaGuardada = h;
            mostrarCarpeta(h);
        }
    });
})();
