import random
from PIL import Image, ImageDraw
from clip import *

DIM = 16
FRAMES = 32
RADIANS_PER_FRAME = 2 * math.pi / FRAMES

bg_color = (212, 90, 18)
squares = (
    Square((4, 5), lighter(bg_color, 2), 7, 5, FRAMES),
    Square((9, 10), lighter(bg_color, 1), 4, 7, FRAMES),
)

img = Image.new('RGB', (DIM, FRAMES * DIM), color=bg_color)

for frame_num in range(0, FRAMES):
    frame = Image.new('RGB', (DIM, DIM), color=bg_color)
    draw = ImageDraw.Draw(frame)
    for sq in squares:
        angle = RADIANS_PER_FRAME * frame_num * sq.direction
        size_adjust = int(round(((sq.center_x + frame_num) % FRAMES) / (FRAMES / 2)))
        if sq.direction > 0:
            x = 0
            y = math.cos(angle) * sq.radius
        else:
            x = math.sin(angle) * sq.radius
            y = 0
        for x_pos in (-1, 0, 1):
            for y_pos in (-1, 0, 1):
                pos1 = (iround(sq.center_x + x + x_pos * DIM), iround(sq.center_y + y + y_pos * DIM))
                pos2 = (pos1[0] + sq.size + size_adjust, pos1[1] + sq.size + size_adjust)
                draw.rectangle(pos1 + pos2, outline=sq.color)
    img.paste(frame, (0, frame_num * DIM))

img.save(directory('textures', 'block/lava_still.png'))

DIM *= 2

img = Image.new('RGB', (DIM, FRAMES * DIM), color=bg_color)
skitter = 13

random.seed(0)
stagger = []
for x in range(0, DIM):
    stagger += (random.randint(0, 7),)

color = lighter(bg_color, 1)
for frame_num in range(0, FRAMES):
    frame = Image.new('RGB', (DIM, DIM), color=bg_color)
    draw = ImageDraw.Draw(frame)
    for x_pos in (-1, 0, 1):
        for y_pos in (-1, 0, 1):
            for x in range(0, DIM, 4):
                for y in range(0, DIM, 10):
                    if (x / 4 + y / 10) % 2 == 1:
                        continue
                    pos1 = (iround(x + x_pos * DIM), iround(y + stagger[x] + frame_num + y_pos * DIM))
                    pos2 = (pos1[0] + 2, pos1[1] + 8)
                    draw.rectangle(pos1 + pos2, outline=color)
    img.paste(frame, (0, frame_num * DIM))

img.save(directory('textures', 'block/lava_flow.png'))
