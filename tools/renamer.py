import os
from os import listdir
from os.path import isfile, join

path = "../sprites/intro/"
files = [f for f in listdir(path) if isfile(join(path, f))]

for f in files:
    if "frame" not in f:
        continue
    old_path = os.path.join(path, f)
    filename = f.replace("_", ".")[0:len("frame_000")] + ".png"
    filename = filename.replace("frame", "science")
    new_path = os.path.join(path, filename)
    os.rename(old_path, new_path)
