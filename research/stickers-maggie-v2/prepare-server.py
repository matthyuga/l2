from pathlib import Path
import json
S=Path(__file__).resolve().parent;R=S.parents[1];old=R/'research/stickers-radial-v1'
names=json.loads((S/'cutouts.json').read_text())['stickers'];names=[r['name'] for r in names]
text=(old/'StickerEmotes.java').read_text()
start=text.index('static final String[] NAMES = ');end=text.index(';',start)
text=text[:start]+'static final String[] NAMES = {'+', '.join(json.dumps(n) for n in names)+'}'+text[end:]
text=text.replace('8 reactions, 3s visual, 5s server cooldown; .sticker 1..8','19 Maggie Fess stickers, 3s visual, 5s server cooldown; .sticker 1..19')
text=text.replace('Stickers: Alt+E o boton de carita. .sticker 1..8: Risa, GG, Corazon, Enojo, Llanto, Sorpresa, Duda, Saludo.','Stickers: boton junto al minimapa. .sticker 1..19: '+', '.join(names)+'. Alt+E desactivado temporalmente.')
text=text.replace('public final class StickerEmotes','public final class MaggieStickerEmotes').replace('public StickerEmotes()','public MaggieStickerEmotes()').replace('new StickerEmotes()','new MaggieStickerEmotes()')
(S/'MaggieStickerEmotes.java').write_text(text)
(S/'StickerEmotes.java').write_text('package custom.StickerEmotes;\n/** Compatibility entry: the catalog is now loaded by MaggieStickerEmotes. */\npublic final class StickerEmotes { public static void main(String[] args) {} }\n')
verify=(old/'verify-client.groovy').read_text().replace('NexusStickersV1','NexusStickersV2').replace('NexusStickerEffectsV1','NexusStickerEffectsV2').replace('0..<8','0..<19').replace('8 finite one-shot','19 finite one-shot')
(S/'verify-client.groovy').write_text(verify)
print('Prepared 19 selections, corrected help and fresh native package verifier.')
