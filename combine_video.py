
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
from moviepy.video.fx.resize import resize
import tkinter as tk
from tkinter import filedialog
import os, copy, datetime

'''
titles need imagemagick: mac - brew install imagemagick
'''

def stretch_video_in_dir(s=1.33, concat=True, same_dir=True, del_orig=False, title='Test title', 
    subtitle='date', trim_end=True):
    """Stretch all video files in a folder
    then concatenate
    do not stretch if '_i' in file name
    Title and subtitle blank to not add any title

    """
    yr = datetime.datetime.now().year
    m = datetime.datetime.now().month
    combined_file = f"{yr}_{m}_{title.lower().replace(' ', '_')}.mp4"
    title = f'       {title}\n       {subtitle}'

    root = tk.Tk()
    root.withdraw()
    new_dir = "stretched"
    file_types = ('.MOV', '.MP4')

    dir = filedialog.askdirectory()
    if same_dir:
        images_fp = dir
    else:
        images_fp = os.path.join(dir, new_dir)
    if not os.path.exists(images_fp):
        os.makedirs(images_fp)
    os.chdir(dir)

    file_list = os.listdir()
    file_list.sort()


    x = [a for a in file_list if a.upper().endswith(file_types)]
    print(len(x), ' files to process')
    clips_resized = []
    for cntr, file_ in enumerate(x):
        file_name_only = os.path.splitext(file_)[0]
        new_file = file_name_only + '_e.mp4'
        # with VideoFileClip(file_) as clip:  does not allow concatonate
        clip = VideoFileClip(file_)
        if trim_end:
            clip = clip.subclip(0,-0.5)
        width = clip.w
        height = clip.h
        if '_i' not in file_name_only and s != 1:
            width = int(width * s)
            clip_s = clip.resize((width, height))
        else:
            clip_s = clip
        if title and cntr == 0:
            # Generate a text clip
            txt_clip = TextClip(title, size=(width,100), fontsize=20, font="Arial", align='West', color='white', bg_color='black', kerning=3, interline=10)
            txt_clip = txt_clip.set_position((0.0,0.8), relative=True).set_duration(3)
            # Overlay the text clip above the first clip
            clip_s = CompositeVideoClip([clip_s, txt_clip])
        clips_resized.append(clip_s)
        # if sep_files:
        #     clips_resized[cntr].write_videofile(os.path.join(images_fp, new_file), codec="libx264")
        # print('Done: ', file_)
        if not concat:
            clips_resized[cntr].write_videofile(os.path.join(images_fp, new_file), codec="libx264")
        print('Done: ', file_)

    if concat:
        combined_vid = concatenate_videoclips(clips_resized, method="compose")
        combined_vid.write_videofile(os.path.join(images_fp, combined_file), codec="libx264", fps=24, threads=4)

        

    for clip in clips_resized:
        clip.close()
    if del_orig:
        for file_ in x:
            os.remove(file_)

def get_meta(files):
    from exif_tool.exiftool import ExifTool
    with ExifTool() as et:
        metadata = et.get_metadata_batch(files)
    for d in metadata:
        for k in d:
            print(k, d[k])


def cl_combine():
    '''
    CLI with options to:
    1. Combine video files
    2. Stretch (is an anamorphic lens has been used)
    3. Delete last 0.5 seconds of each clip
    4. Add a title
    Output is in 24fps mp4
    '''
    title = input("Title: ")
    subtitle = input("Subtitle: ")
    st = input("Stretch video 33%?  y/n: ")
    if st == 'y':
        s = 1.33
    else:
        s = 1
    combine = input("Combine to one file? y/n: ")
    if combine == 'y':
        concat = True
    else:
        concat = False
    trim_end = input("trim end of each video file by 0.5 seconds?  y/n:")
    print(f'Combine videos and add title : {title} and subtitle : {subtitle} with a stretch of {s}.')
    print('Please select directory when dialog appears.')
    stretch_video_in_dir(s=s, concat=concat, title=title, subtitle=subtitle, trim_end=trim_end)


if __name__ == "__main__":
    cl_combine()
    




    