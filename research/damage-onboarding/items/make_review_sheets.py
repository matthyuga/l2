"""Create labeled inspection crops of saved screenshots; originals unchanged."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path('E:/l2-damage/client/Lineage II/system')
out = Path(__file__).resolve().parent / 'review'
out.mkdir(exist_ok=True)
files = [root / f'Shot{n:05}.jpg' for n in range(32, 114)]
for start in range(0, len(files), 12):
    batch = files[start:start + 12]
    sheet = Image.new('RGB', (1000, 1400), '#eeeeee')
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(batch):
        x, y = (i % 4) * 250, (i // 4) * 350
        draw.text((x + 4, y + 4), path.name, fill='black')
        with Image.open(path) as im:
            sheet.paste(im.crop((482, 213, 728, 537)), (x, y + 22))
    target = out / f'sheet-{start//12+1:02}.png'
    sheet.save(target)
    print(target)
