#!/usr/bin/env python3

from PIL import Image, ExifTags, ImageOps
import tkinter as tk
from tkinter import filedialog
import os


def stretch_images_in_dir(s=1.33):
    """
    Stretch all jpg files in a folder
    """
    root = tk.Tk()
    root.withdraw()
    new_dir = "stretched"

    dir = filedialog.askdirectory()
    images_fp = os.path.join(dir, new_dir)
    if not os.path.exists(images_fp):
        os.makedirs(images_fp)
    os.chdir(dir)

    file_list = os.listdir()
    file_list.sort()

    x = [a for a in file_list if a.upper().endswith(".JPG")]
    for file_ in x:
        with open(file_, "r+b") as f:
            with Image.open(f) as image:
                image.load()
                exif = image.info['exif']
                width = int(float(image.size[0]) * float(s))
                height = image.size[1]
                image = image.resize((width, height), Image.ANTIALIAS)
                image = ImageOps.exif_transpose(
                    image
                )  # make sure rotation matches exif settings
                print('Done: ', file_)
                image.save(os.path.join(images_fp, file_), image.format, exif=exif)


if __name__ == "__main__":
    stretch_images_in_dir()

