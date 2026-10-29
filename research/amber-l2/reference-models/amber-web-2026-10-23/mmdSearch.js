/**
 * mmdSearch.js — Composant de recherche de personnages MMD
 * Stylisé avec Tailwind CSS / DaisyUI 
 * (c) 2026 MMDfr.fr
 */

const DEFAULT_OPTIONS = {
    spritesheetUrl: 'https://api.mmdfr.fr/static/gs/spritesheet.webp',
    apiBaseUrl: 'https://api.mmdfr.fr',
    placeholder: 'Search a character ...',
    maxResults: 10,
    spriteSizeFactor: 0.5,
    spriteSize: (typeof GS_CELL_SIZE !== 'undefined' ? Math.round(GS_CELL_SIZE * 0.5) : 50),
    spriteCols: (typeof GS_COLS !== 'undefined' ? GS_COLS : 10),
    spriteRows: (typeof GS_ROWS !== 'undefined' ? GS_ROWS : 13),
    debounceMs: 300,
    onSelect: null,
    nameSearch: null,
    numName: null,
};

/**
 * Initialise le composant de recherche dans un conteneur existant.
 * @param {string|HTMLElement} container - ID ou élément conteneur
 * @param {object} options - Options de configuration
 * @returns {object} Contrôle du composant (methodes destroy, setResult, etc.)
 */
export function initSearch(container, options = {}) {
    const opts = { ...DEFAULT_OPTIONS, ...options };

    // Résoudre le conteneur
    const el = typeof container === 'string'
        ? document.getElementById(container)
        : container;
    if (!el) {
        console.error(`mmdSearch: conteneur introuvable (${container})`);
        return null;
    }

    // Récupérer les données de recherche : options > globales
    const nameSearchData = opts.nameSearch || (typeof nameSearch !== 'undefined' ? nameSearch : null);
    const numNameData = opts.numName || (typeof numName !== 'undefined' ? numName : null);

    if (!nameSearchData || !numNameData) {
        el.innerHTML = '<div class="alert alert-error">Error: search data not found. Load searchDB.js or pass nameSearch/numName in options.</div>';
        return null;
    }

    // Variables internes
    let currentAbortController = null;
    let debounceTimer = null;

    // --- Construction du DOM (Tailwind / DaisyUI) ---
    el.innerHTML = `
        <div>
            <input type="text" id="${el.id}-input" name="character-search" class="input input-bordered w-full text-lg" placeholder="${escapeHtml(opts.placeholder)}" autocomplete="off">
            <div class="suggestions-dropdown w-full mt-1 shadow-xl rounded-box bg-base-100 border border-base-300 hidden"></div>
        </div>
        <div class="result-card mt-4 hidden"></div>
    `;

    // Préchargement du spritesheet dès le chargement de la page
    const preloadImg = new Image();
    preloadImg.src = opts.spritesheetUrl;
    preloadImg.style.display = 'none';
    document.body.appendChild(preloadImg);

    const inputEl = el.querySelector('input');
    const suggestionsEl = el.querySelector('.suggestions-dropdown');
    const resultEl = el.querySelector('.result-card');

    // --- Fonctions de recherche ---

    /**
     * Normalise une chaîne (enlève accents, met en minuscule)
     */
    function normalize(str) {
        return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    }

    /**
     * Cherche les personnages correspondant à la requête
     * @param {string} query - Texte saisi
     * @returns {Array} Liste de { nom, num, urlName }
     */
    function getSuggestions(query) {
        if (!query) return [];
        const q = normalize(query);
        const alreadyFound = {};
        const results = [];
        let p = nameSearchData.indexOf(q, 0);

        while (p > 0) {
            const nd = nameSearchData.indexOf('=', p) + 1;
            const nf = nameSearchData.indexOf(',', nd);
            const numS = nameSearchData.substring(nd, nf);
            const numN = parseInt(numS, 10);

            if (!(numN in alreadyFound)) {
                const dispName = numNameData[numN];
                let ssd = nd - 18;
                if (ssd < 0) ssd = 0;
                const ssdSearch = nameSearchData.substring(ssd, nd - 1);
                const lastComma = ssdSearch.lastIndexOf(',');
                const kSearch = ssdSearch.substring(lastComma + 1);
                const urlName = dispName.split(',')[0];

                results.push({ nom: dispName, num: numS, urlName });
                alreadyFound[numN] = true;
            }

            p = nameSearchData.indexOf(q, nf);
        }

        results.sort((a, b) => a.nom.localeCompare(b.nom));
        return results.slice(0, opts.maxResults);
    }

    /**
     * Affiche les suggestions dans une liste DaisyUI
     */
    function showSuggestions(list) {
        suggestionsEl.innerHTML = '';
        if (list.length === 0) {
            suggestionsEl.classList.add('hidden');
            return;
        }
        suggestionsEl.classList.remove('hidden');

        const spriteSize = opts.spriteSize;
        const bgW = spriteSize * opts.spriteCols;
        const bgH = spriteSize * opts.spriteRows;

        for (const item of list) {
            const num = parseInt(item.num, 10);
            const col = num % opts.spriteCols;
            const row = Math.floor(num / opts.spriteCols);

            const div = document.createElement('div');
            div.className = 'flex items-center gap-3 px-3 py-2 cursor-pointer hover:bg-base-200 border-b border-base-200 last:border-b-0 transition-colors duration-150';

            // Sprite
            const sprite = document.createElement('span');
            sprite.className = 'block flex-shrink-0 rounded-lg bg-base-200';
            sprite.style.backgroundImage = `url(${opts.spritesheetUrl})`;
            sprite.style.backgroundPosition = `-${col * spriteSize}px -${row * spriteSize}px`;
            sprite.style.backgroundSize = `${bgW}px ${bgH}px`;
            sprite.style.width = `${spriteSize}px`;
            sprite.style.height = `${spriteSize}px`;
            div.appendChild(sprite);

            // Nom
            const nameSpan = document.createElement('span');
            nameSpan.className = 'text-base-content flex-1 min-w-0';
            const parts = item.nom.split(',');
            nameSpan.textContent = parts[0];
            if (parts.length > 1) {
                nameSpan.textContent += ', ' + parts.slice(1).join(', ');
            }
            div.appendChild(nameSpan);

            // Numéro (badge)
            const numSpan = document.createElement('span');
            numSpan.className = 'badge badge-ghost badge-sm ml-auto flex-shrink-0';
            numSpan.textContent = `#${item.num}`;
            div.appendChild(numSpan);

            // Événement clic
            div.addEventListener('click', () => {
                inputEl.value = item.urlName;
                suggestionsEl.classList.add('hidden');
                fetchCharacterInfo(item.urlName, item.num, item.nom);
                if (typeof opts.onSelect === 'function') {
                    opts.onSelect({ ...item });
                }
            });

            suggestionsEl.appendChild(div);
        }
    }

    // --- Appel API FastAPI ---

    /**
     * Récupère les infos d'un personnage via l'API
     */
    async function fetchCharacterInfo(name, spriteNum, allNames) {
        if (currentAbortController) {
            currentAbortController.abort();
        }
        currentAbortController = new AbortController();
        const { signal } = currentAbortController;

        resultEl.classList.remove('hidden');
        resultEl.innerHTML = '<div class="flex justify-center items-center p-8"><span class="loading loading-spinner loading-md text-primary"></span><span class="ml-2 text-base-content/70">Loading character...</span></div>';

        try {
            const rname = name.toLowerCase().replace(' ', '')
            const url = `${opts.apiBaseUrl.replace(/\/+$/, '')}/api/character/${encodeURIComponent(rname)}`;
            const response = await fetch(url, { signal });

            if (!response.ok) {
                if (response.status === 404) {
                    showResultError(`Character "${escapeHtml(name)}" not found in database.`);
                } else {
                    showResultError(`Server error (${response.status})`);
                }
                return;
            }

            const data = await response.json();
            showResult(data, spriteNum, allNames);
        } catch (err) {
            if (err.name === 'AbortError') return;
            showResultError(`Unable to reach server: ${err.message}`);
        } finally {
            currentAbortController = null;
        }
    }

    /**
     * Affiche le résultat détaillé (infos du personnage) en DaisyUI card
     */
    function showResult(data, spriteNum, allNames) {
        if (!data || !data.versions || data.versions.length === 0) {
            resultEl.innerHTML = '<div class="p-8 text-center text-base-content/50 italic">No Pmx version available for this character.</div>';
            return;
        }

        let namesHtml = '';
        let name = escapeHtml(data.name);
        if (allNames) {
            const names = allNames.split(',').map(n => n.trim()).filter(n => n);
            if (names.length > 1) {
                namesHtml = '<div class="text-sm text-base-content/60 mt-1">' + names.slice(1).map(n => escapeHtml(n)).join(' · ') + '</div>';
                name = escapeHtml(names[0]);
            }
        }

        const numSprite = parseInt(spriteNum, 10) || 0;
        const col = numSprite % opts.spriteCols;
        const row = Math.floor(numSprite / opts.spriteCols);
        const spriteSize = 100;

        let html = `
        <div class="card bg-base-100 border border-base-300 shadow-lg">
            <div class="card-body">
                <div class="flex items-center gap-4 pb-4 border-b-2 border-primary mb-6">
                    <div class="flex-shrink-0 rounded-xl border-2 border-base-300 bg-base-200" style="
                        background-image: url(${opts.spritesheetUrl});
                        background-position: -${col * spriteSize}px -${row * spriteSize}px;
                        background-size: ${spriteSize * opts.spriteCols}px ${spriteSize * opts.spriteRows}px;
                        width: ${spriteSize}px;
                        height: ${spriteSize}px;
                    "></div>
                    <div>
                        <h2 class="card-title text-2xl">${name}</h2>
                        ${namesHtml}
                    </div>
                </div>

                <h3 class="text-lg font-semibold text-base-content mb-4 pb-2 border-b-2 border-primary inline-block">Versions</h3>

                <div class="overflow-x-auto">
                    <table class="table table-zebra table-lg w-full">
                        <tbody>`;

        for (const v of data.versions) {
            const versionStr = v.ver.slice(0, -1) + '.' + v.ver.slice(-1);
            const sizeStr = v.sd;
            const altStr = v.alt;
            const href = escapeHtml(v.url);
            const rem = escapeHtml(v.r);
            let fileName = v.url.split('/').pop() || v.url;
            try { fileName = decodeURIComponent(fileName); } catch (e) { /* nom déjà décodé ou invalide */ }
            fileName = escapeHtml(fileName);
            html += `<tr>
                <td>
                    <a class="btn btn-primary" href="${href}" target="_blank" rel="noreferrer">
                    <div>Download  <strong>v${versionStr} - ${altStr}</strong></div>
                    <div> ${fileName}  :  ${sizeStr}</div>
                    ${rem ? `<div class="text-xs text-base-content/40">${rem}</div>` : ''}
                    </a>
                </td>
            </tr>`;
        }

        html += `</tbody></table></div></div></div>`;
        resultEl.innerHTML = html;
    }

    function showResultError(msg) {
        resultEl.innerHTML = `<div class="alert alert-error">${msg}</div>`;
    }

    // --- Gestion des événements ---

    function onInput() {
        clearTimeout(debounceTimer);
        resultEl.classList.add('hidden');
        const val = inputEl.value.trim();
        if (!val) {
            suggestionsEl.classList.add('hidden');
            return;
        }
        debounceTimer = setTimeout(() => {
            const list = getSuggestions(val);
            showSuggestions(list);
        }, opts.debounceMs);
    }

    inputEl.addEventListener('input', onInput);

    // Cacher les suggestions au clic ailleurs
    document.addEventListener('click', (e) => {
        if (!el.contains(e.target)) {
            suggestionsEl.classList.add('hidden');
        }
    });

    // --- API publique ---

    /**
     * Charge manuellement le résultat pour un personnage donné
     */
    function loadCharacter(name, spriteNum, allNames) {
        inputEl.value = name;
        suggestionsEl.classList.add('hidden');
        fetchCharacterInfo(name, spriteNum, allNames);
    }

    /**
     * Nettoie le composant
     */
    function destroy() {
        clearTimeout(debounceTimer);
        if (currentAbortController) {
            currentAbortController.abort();
        }
        // Supprimer l'image de préchargement du DOM
        if (preloadImg.parentNode) {
            preloadImg.parentNode.removeChild(preloadImg);
        }
        el.innerHTML = '';
    }

    return { loadCharacter, destroy };
}

// --- Utilitaires ---

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}