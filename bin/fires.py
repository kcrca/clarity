import clip
import json

from PIL import Image

src_dir = clip.directory('defaults', 'textures', 'block')
dst_dir = clip.directory('textures', 'block')

for prefix in ('', 'soul_', 'campfire_', 'soul_campfire_'):
    for suffix in ('', '_0', '_1'):
        file = "%sfire%s.png" % (prefix, suffix)
        try:
            src = Image.open("%s/%s" % (src_dir, file)).convert("RGBA")
            dst = Image.new("RGBA", src.size)
            size = src.size[0]
            half = int(size / 2)
            for frame_y in range(0, src.size[1], size):
                frame = src.crop((0, frame_y, size, frame_y + size))
                new_height = int(2 * size / 3)
                reduced = frame.resize((size, new_height))
                dst.paste(reduced, (0, frame_y + size - new_height))
            dst.save("%s/%s" % (dst_dir, file), optimize=True)

            mcmeta = json.load(open("%s/%s.mcmeta" % (src_dir, file)))
            mcmeta['animation']['frametime'] = 3
            json.dump(mcmeta, open("%s/%s.mcmeta" % (dst_dir, file), 'w'))
        except FileNotFoundError:
            print("skipping %s" % file)
