from PIL import Image


def to_range(v):
    if v < 0:
        v += 16
    return v % 16


band_colors = (
    (203, 75, 255, 200),
    (172, 60, 244, 200),
    (158, 55, 233, 200),
    (133, 39, 217, 200))

width = 16
frames = 16 + len(band_colors) - 2

img = Image.new('RGBA', (width, frames * width), color=(55, 0, 157, 160))


def line_at(xy, color):
    for p in range(0, 16):
        img.putpixel((xy[0], xy[1] + p), color)


img_y = 0
for i in range(0, 16):
    img_y = i * width

    for b in range(0, min(i + 1, len(band_colors))):
        left = to_range(7 - i + b)
        right = to_range(8 + i - b)
        color = band_colors[b]
        line_at((left, img_y), color)
        line_at((right, img_y), color)

img_y += 16
line_at((7, img_y), band_colors[0])
line_at((8, img_y), band_colors[0])
line_at((6, img_y), band_colors[2])
line_at((9, img_y), band_colors[2])
line_at((5, img_y), band_colors[3])
line_at((10, img_y), band_colors[3])

img_y += 16
line_at((7, img_y), band_colors[0])
line_at((8, img_y), band_colors[0])
line_at((6, img_y), band_colors[3])
line_at((9, img_y), band_colors[3])

img.save("blocks/portal.png")
