from PIL import Image
import sys

for f in sys.argv[1:]:
    img = Image.open(f)
    img.save(f)