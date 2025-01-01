import colorsys
import csv
import sys

from PIL import Image, ImageColor, ImageDraw

if len(sys.argv) == 1:
    sys.exit(0)
print('argv: %s' % sys.argv)
biomes = {}
all = []
for f in sys.argv[1:]:
    with open(f) as csv_file:
        r = csv.reader(csv_file)
        things = None
        for row in r:
            if not things and not row[0]:
                color = row[1]
                things = row[2:]
            elif things:
                color = row[1]
                for biome in row[0].split('\n'):
                    try:
                        in_biome = biomes[biome]
                    except KeyError:
                        in_biome = []
                    biomes[biome] = color

order = sorted(biomes.items(),
               key=lambda x: (colorsys.rgb_to_hsv(*ImageColor.getrgb(x[1]))[2], x[0]))
prev = ''
colors = []
n = 1
for b in order:
    if b[1] == prev:
        c = '       '
        n += 1
    else:
        c = b[1]
        colors.append(b[1])
        n = 1
    print(c, b[0], "(%d)" % n)
    prev = b[1]

color_img = Image.new('RGB', (16 * len(colors), 16))
color_draw = ImageDraw.Draw(color_img)
for i, c in enumerate(colors):
    color_draw.rectangle((i * 16, 0, (i + 1) * 16, 16), fill=ImageColor.getrgb(c))
color_img.show()
