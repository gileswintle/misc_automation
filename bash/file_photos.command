#!/usr/bin/env python3

from PIL import Image, ExifTags, ImageOps
import tkinter as tk
from tkinter import filedialog
import os, datetime, time, shutil



def find_img_date(full_filename):
    date_ = time.ctime(os.path.getmtime(full_filename))
    mod_date = datetime.datetime.strptime(date_, "%a %b %d %H:%M:%S %Y")

    with open(full_filename, "r+b") as f:
        try:
            with Image.open(f) as image:
                exif = image.getexif()
                creation_time = exif.get(36867)
                try:  # try to get exif date and if exists else use mod date
                    exif_dt = datetime.datetime.strptime(
                        creation_time, "%Y:%m:%d %H:%M:%S"
                    )
                except TypeError:
                    exif_dt = mod_date
        except:  # if corrupted then use mod date
            exif_dt = mod_date
    return exif_dt

def img_file_by_year_month(recursive=True, delete_empty=True, preserve_old=False):
    """Search folder and all sub folders (if recursive == True) and place all jpg and movie files
    in folders by year and month, delete empty folders (if delete_empty == True
    exclude directories that have _ in them and place them in the year root
    """
    root = tk.Tk()
    root.withdraw()
    target_dir = filedialog.askdirectory()
    file_types = (".JPG", ".JPEG", ".PNG", ".NEF", ".RAF", ".MOV", ".MP4")

    if recursive:
        files_to_be_treated = [
            (root, name)
            for root, dirs, files in os.walk(target_dir)
            for name in files
            if name.upper().endswith(file_types) and '_' not in os.path.basename(os.path.normpath(root))
        ]
        directories_to_move = [root for root, dirs, files in os.walk(target_dir) if  '_' in os.path.basename(os.path.normpath(root))]
        print('Event directories: ', [os.path.basename(d) for d in directories_to_move])
    else:
        file_list = os.listdir(target_dir)
        file_list.sort()
        files_to_be_treated = [
            (target_dir, a)
            for a in file_list
            if a.upper().endswith(file_types)
        ]
    # print('target: ',files_to_be_treated)

    # move event directories
    for d in directories_to_move:
        yr = os.path.basename(d)[0:4]
        if yr.isnumeric():
            yr_dir = os.path.join(target_dir, yr)
            if not os.path.exists(yr_dir):
                os.makedirs(yr_dir)
            if not os.path.exists(os.path.join(yr_dir, os.path.basename(d))):
                try:
                    shutil.move(d, yr_dir)
                except:
                    pass

    for dir_, file_ in files_to_be_treated:
        full_filename = os.path.join(dir_, file_)
        exif_dt = find_img_date(full_filename)
        year = exif_dt.year
        month = exif_dt.month
        yr_dir = os.path.join(target_dir, str(year))
        if not os.path.exists(yr_dir):
            os.makedirs(yr_dir)
        mnth_str = str(month)
        if len(mnth_str) == 1:
            mnth_str = f"0{mnth_str}"
        mnth_dir = os.path.join(yr_dir, mnth_str)
        if not os.path.exists(mnth_dir):
            os.makedirs(mnth_dir)
        new_file = os.path.join(mnth_dir, file_)
        if full_filename != new_file:
            if os.path.exists(new_file) and preserve_old:
                os.rename(new_file, os.path.join(mnth_dir, "old_" + file_))
            os.rename(full_filename, new_file)
            print('Moving: ', new_file)

    # Delete empty directories
    if recursive and delete_empty:
        repeat = True
        while repeat:
            dirs = [root for root, dirs, files in os.walk(target_dir)]
            for dir_ in dirs:
                list_dir = [f for f in os.listdir(dir_) if not f.startswith(".")]
                if len(list_dir) == 0:
                    print('Removing: ', dir_)
                    shutil.rmtree(dir_)
                    repeat = True
                else:
                    repeat = False


if __name__ == "__main__":
    img_file_by_year_month()
