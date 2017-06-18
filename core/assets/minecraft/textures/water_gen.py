from PIL import Image, ImageDraw
import math

alpha = int(0.6 * 255)
width = 16
frames = 32
radians_per_frame = 2 * math.pi / frames


class Square:
    next_direction = 1

    def __init__(self, pos, color, radius, size):
        (self.center_x, self.center_y) = pos
        self.color = color
        self.radius = radius / 2
        self.size = size
        self.direction = Square.next_direction
        Square.next_direction *= -1


def to_range(v):
    if v < 0:
        v += 16
    return v % 16


def iround(f):
    return int(round(f))


def adjust(color, steps, factor):
    for i in range(0, steps):
        color = (c * factor for c in color)
    return tuple(iround(c) for c in color)


def darker(steps):
    return adjust(bg_color, steps, 0.9)


def lighter(steps):
    return adjust(bg_color, steps, 1.15)


bg_color = (42, 63, 255)
squares = (
    Square((4, 5), lighter(1), 7, 5),
    # Square((12, 12), darker(2), 12, 6),
    Square((9, 10), lighter(1), 4, 7),
    # Square((12, 12), lighter(2), 6, 12),
)

bg_color += (alpha,)

img = Image.new('RGBA', (width, frames * width), color=bg_color)

frame_images = []

for i in range(0, frames):
    frame = Image.new('RGBA', (width, width), color=bg_color)
    draw = ImageDraw.Draw(frame)
    image_num = 1
    in_y = False
    for sq in squares:
        angle = radians_per_frame * i * sq.direction
        size_adjust = int(round(((sq.center_x + i) % frames )/ (frames / 2)))
        alpha_adjust = i % frames
        if alpha_adjust >= frames / 2:
            alpha_adjust = abs(frames - alpha_adjust)
        # if alpha_adjust >= 8:
        #     alpha_adjust -= alpha_adjust % 8
        x = math.sin(angle) * sq.radius
        y = math.cos(angle) * sq.radius
        in_y = not in_y
        if in_y:
            x = 0
        else:
            y = 0
            alpha_adjust = frames / 2 - alpha_adjust
        alpha_adjust += 2
        for x_pos in (-1, 0, 1):
            for y_pos in (-1, 0, 1):
                pos1 = (iround(sq.center_x + x + x_pos * width), iround(sq.center_y + y + y_pos * width))
                pos2 = (pos1[0] + sq.size + size_adjust, pos1[1] + sq.size + size_adjust)
                draw.rectangle(pos1 + pos2, outline=sq.color + (alpha + alpha_adjust,))
        # if i == 0:
        #     frame.show()
        image_num += 1
    img.paste(frame, (0, i * width))
    frame_images += [frame, ]

# img.show()
img.save("blocks/water_still.png")
#
# from moviepy.editor import VideoClip
#
#
# def make_frame(t):
#     """ returns an image of the frame at time t """
#     # ... create the frame with any library
#     return frame_images[t % len(frame_images)]  # (Height x Width x 3) Numpy array
#
#
# animation = VideoClip(make_frame, duration=3)  # 3-second clip
#
# # For the export, many options/formats/optimizations are supported
# animation.write_gif("/tmp/water.gif", fps=24)  # export as GIF (slow)
