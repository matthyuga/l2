"""Record visually reviewed offers; do not infer hidden prices or item IDs."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
SHOTS = Path('E:/l2-damage/client/Lineage II/system')
# screenshot | displayed product/variant | output quantity | currency cost | note
DATA = '''32|Hero Crown|1|20|
33|Hero Crown|1|20|Repite la captura 32
34|Crystal Scroll: Enchant Armor S [100% +20]|1|1|Tipo/grado según descripción visible
35|Crystal Scroll: Enchant Weapon S [100% +20]|1|2|Tipo/grado según descripción visible
36|Secret Book of Giants|8|1|
37|Top-Grade Life Stone [15%]|10|3|Nivel exacto truncado; descripción menciona personajes 76+
38|High-Grade Life Stone [10%]|10|2|Nivel exacto truncado; descripción menciona personajes 76+
39|Mid-Grade Life Stone [5%]|10|1|Nivel exacto truncado; descripción menciona personajes 76+
40|Ring of Baium|1|10|
41|Necklace of Valakas|1|10|
42|Earring of Antharas|1|10|
43|Zaken's Earring|1|10|
44|Frintezza's Necklace|1|10|
45|Ring of Queen Ant|1|10|
46|Dragon Bugle of Star|1|20|
47|Monster Only (Shield of Imperial ...)|1|5|Nombre truncado; no se completa por inferencia
48|Nephilim Lord (shield)|1|5|
49|Tattoo of Damage — Unique|1|20|
50|Adena|10000|1|
51|Blessed Scroll of Escape|2|1|
52|Noblesse Letter|1|10|
53|Staff of Evil Spirits — Bodily Blessing|1|10|
54|Staff of Evil Spirits — Magic Focus|1|10|
55|Blessed Scroll of Escape|2|1|Repite la captura 51
56|Blessed Scroll of Escape: Clan Hall|2|1|
57|Blessed Scroll of Escape: Castle|2|1|
58|Special Christmas Tree|1|5|
59|Straw Hat|1|?|Cantidad de moneda tapada por tooltip
60|Cap Adidas|1|10|
61|Hair Style Change Potion — E|1|3|
62|Santa's Antlers|1|5|
63|Pirate Hat|1|5|
64|Demon Horns|1|5|
65|Ring of Core|1|1000|
66|Earring of Orfen|1|2000|
67|Ring of Queen Ant|1|5000|
68|Zaken's Earring|1|5000|
69|Ring of Baium|1|5000|
70|Earring of Antharas|1|8000|
71|Necklace of Valakas|1|12000|
72|Frintezza's Necklace|1|15000|
73|Crystal Scroll: Enchant Weapon A [100% +20]|1|500|Tipo/grado según descripción visible
74|Crystal Scroll: Enchant Armor A [100% +20]|1|200|Tipo/grado según descripción visible
75|Tattoo of Damage — Legend|1|30000|Además requiere Tattoo of Damage Unique x1
76|Crystal Scroll: Enchant Weapon S [100% +20]|1|40|Tipo/grado según descripción visible
77|Crystal Scroll: Enchant Armor S [100% +20]|1|20|Tipo/grado según descripción visible
78|Mid-Grade Life Stone [5%]|1|3|Nivel exacto truncado; descripción menciona personajes 76+
79|High-Grade Life Stone [10%]|1|5|Nivel exacto truncado; descripción menciona personajes 76+
80|Top-Grade Life Stone [15%]|1|10|Nivel exacto truncado; descripción menciona personajes 76+
81|Secret Book of Giants|1|10|
82|Greater CP Potion|300|10|
83|Nephilim Lord (shield)|1|100|
84|Monster Only (Shield of Imperial ...)|1|100|Nombre truncado
85|Dragon Bugle of Star|1|200|
86|Mystery Potion|1|10|
87|Blessed Scroll of Escape: Castle|1|10|
88|Hair Style Change Potion — A|1|100|
89|Alien Mask|1|500|
90|Lord Mask [3]|1|?|Cantidad de moneda tapada por tooltip
91|Terminator Mask|1|500|
92|Angel Halo|1|100|
93|Santa's Antlers|1|100|
94|Special Christmas Tree|1|5000|
95|Firework|1|50|
96|Alien Mask|1|5000|
97|Pirate Hat|1|1000|
98|Crystal Scroll: Enchant Weapon S [100% +20]|1|3|Tipo/grado según descripción visible
99|Crystal Scroll: Enchant Armor S [100% +20]|1|1|Tipo/grado según descripción visible
100|Mid-Grade Life Stone [5%]|5|1|Nivel exacto truncado; descripción menciona personajes 76+
101|High-Grade Life Stone [10%]|5|2|Nivel exacto truncado; descripción menciona personajes 76+
102|Top-Grade Life Stone [15%]|5|3|Nivel exacto truncado; descripción menciona personajes 76+
103|Secret Book of Giants|2|1|
104|Greater CP Potion|300|1|
105|Quick Healing Potion|2|1|
106|Nephilim Lord (shield)|1|5|
107|Dragon Bugle of Star|1|50|
108|Monster Only (Shield of Imperial ...)|1|5|Nombre truncado
109|Hero Crown|1|30|
110|Adena|5000|1|
111|Noblesse Letter|1|20|
112|Hunter Cap|1|20|
113|Santa's Antlers|1|10|'''

def main():
    rows = []
    for line in DATA.splitlines():
        n, product, amount, cost, note = line.split('|')
        n = int(n)
        currency = ('Donator Coin' if n <= 64 else 'Damage Coin' if n <= 75
                    else 'Voter Coin' if n <= 93 else 'PC Bang Points' if n <= 97 else 'Festival Adena')
        source = SHOTS / f'Shot{n:05}.jpg'
        rows.append(dict(screenshot=source.name, product=product, output_quantity=int(amount),
                         currency=currency, cost=None if cost == '?' else int(cost),
                         extra_required='Tattoo of Damage Unique x1' if n == 75 else '',
                         note=note, source=str(source), sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
    assert len(rows) == 82 and len({r['screenshot'] for r in rows}) == 82
    (ROOT / 'shop-observations.json').write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding='utf8')
    lines = ['# Catálogo observado de Special Unique Shop', '',
             '17/10/2026. Revisión visual de 82 capturas, Shot00032 a Shot00113. Incluye dos repeticiones (33 y 55). '
             'No se afirma que estas imágenes agoten todas las listas de la tienda. Dos costes están tapados por tooltips.', '',
             'Las cantidades de producto son las del lote mostrado. Los costes son requisitos visibles; no se efectuaron compras. '
             'Los efectos y porcentajes son anuncios del cliente, no mediciones. La moneda agrupa las observaciones; no se deduce el nombre del submenú solo por ella.', '']
    for currency in dict.fromkeys(r['currency'] for r in rows):
        lines += ['## ' + currency, '', '| Producto | Lote | Coste | Evidencia | Nota |', '|---|---:|---:|---|---|']
        for r in rows:
            if r['currency'] != currency:
                continue
            link = '[%s](<%s>)' % (r['screenshot'], Path(r['source']).as_posix())
            lines.append('| %s | %s | %s | %s | %s |' % (r['product'], r['output_quantity'],
                         r['cost'] if r['cost'] is not None else 'No legible', link, r['note']))
        lines += ['']
    lines += ['## Lectura para el diseño', '',
              '- Hay artículos de progresión/poder y cosméticos, no solamente accesorios visuales.',
              '- Algunos productos aparecen con varias monedas. Hero Crown figura por 20 Donator Coin y por 30 Festival Adena; Noblesse Letter por 10 Donator Coin y por 20 Festival Adena.',
              '- Tattoo Legend exige 30.000 Damage Coin y un Tattoo Unique: es una mejora con objeto previo, según los requisitos visibles.',
              '- Los lotes importan: Secret Book of Giants aparece x8 por 1 Donator Coin, x1 por 10 Voter Coin y x2 por 1 Festival Adena.',
              '- Las joyas vistas por Donator Coin cuestan 10 cada una; por Damage Coin sus precios varían. No se deduce equivalencia económica sin conocer cómo se gana cada moneda.',
              '- La oferta de Hero Crown o tattoos no demuestra cómo se implementan o aplican sus efectos. No se midió balance, disponibilidad real al canjear ni obtención de monedas.',
              '- Estos datos documentan Damage. No son decisiones de implementación para nuestro servidor.', '']
    (ROOT / 'CATALOGO-TIENDA-OBSERVADO.md').write_text('\n'.join(lines), encoding='utf8')
    print('82 observaciones registradas; 2 costes no legibles; 2 capturas repetidas.')

if __name__ == '__main__':
    main()
