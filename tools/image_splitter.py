import os
from pathlib import Path

from PIL import Image


def crop(path, input, filename, height, width, skip=0, k=0, max_k=1000, area=None):
    im = Image.open(input)
    imgwidth, imgheight = im.size
    for i in range(0, imgheight, height):
        for j in range(0, imgwidth, width):
            if skip > 0:
                skip = skip - 1
                continue
            box = (j, i, j + width, i + height)
            a = im.crop(box)
            try:
                if area:
                    tmp = Image.new(a.mode, (area[2],area[3]))
                    tmp.paste(a, (area[2]-width, area[3]-height))
                else:
                    tmp = a

                if max_k:
                    tmp.save(os.path.join(path, filename + ".00" + str(k) + ".png", ))
                else:
                    tmp.save(os.path.join(path, filename + ".png", ))
            except:
                print(":(")
                pass
            k += 1
            if k >= max_k:
                return


if __name__ == "__main__":
    path = Path("../assets/sprites/ant/")
    input = Path("../assets/sprites/ant/ant_big.png")
    print(input.absolute())
    w = 32
    h = 32

    # crop(path, input, "plum_back_walk", h, w, skip=12, max_k=4)

    files = ["_big"]
    area = [0, 0, 32, 32]
    for i, x in enumerate(files):
        x = "ant" + x
        crop(path, input, x, h, w, skip=i * 4, max_k=8, area=area)
        crop(path, input, "_".join(x.split("_")[:-1]), h, w, skip=i * 4, max_k=0, area=area)
