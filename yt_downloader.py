from pytubefix import YouTube, exceptions
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.ttk import *
from PIL import Image, ImageTk
import requests
from io import BytesIO
from moviepy import VideoFileClip, AudioFileClip
import subprocess
import sys
import threading
import os
# install library ffmpeg for media processing (for moviepy and pydub)

root=tk.Tk()
root.title("YouTube-Video Downloader")

ent_label=tk.Label(root, text="Enter your YouTube link: ", font=("Times New Roman", 14, "bold"))
ent_label.pack(padx=10, pady=5)

link=tk.StringVar()
link_entry=tk.Entry(root, textvariable=link, font=("Times New Roman", 12), width=50)
link_entry.pack(padx=10, pady=5)

def set_resolutions(*args):
    yt=YouTube(link.get())
    video_stream=yt.streams.filter(file_extension="mp4", only_video=True).order_by("resolution").desc()  # only_video -> audio version available
    resolutions=[stream.resolution for stream in video_stream[::2]]
    resolution_combo["values"]=tuple(resolutions)

link.trace_add("write", set_resolutions)

col_frame=tk.Frame(root)
col_frame.pack()

res_str=tk.StringVar()
resolution_combo=Combobox(col_frame, textvariable=res_str, font=("Times New Roman", 12))

resolution_combo.pack(padx=5, pady=5, side=tk.LEFT)

type_str=tk.StringVar()
filetype_combo=Combobox(col_frame, textvariable=type_str, font=("Times New Roman", 12))
filetype_combo["values"]=("mp3", "mp4")
filetype_combo.pack(padx=5, pady=5, side=tk.RIGHT)

def disable_resolutions(*args):
    if type_str.get()=="mp3":
        resolution_combo.config(state="disabled")
    elif type_str.get()=="mp4":
        resolution_combo.config(state="normal")    

type_str.trace_add("write", disable_resolutions)

def download_conf(*args):
    if (type_str.get())=="":         #    if (res_str.get() or type_str.get())==None:      ->trace_add
        messagebox.showinfo("Information", "You have to select a file type!")
        return
    if (type_str.get()=="mp4" and res_str.get()==""):
        messagebox.showinfo("Information", "You have to choose a resolution!")
        return
    resolution_combo.config(state="disabled")
    filetype_combo.config(state="disabled")
    download_button.destroy()
    global progress, task
    progress=Progressbar(root, orient="horizontal", length=100, mode="determinate")
    progress.pack(padx=10, pady=10, fill=tk.X)
    #progress["value"]=20
    #progress.update_idletasks()
    task=threading.Thread(target=yt_download)
    task.start()
    progressbar_update()
    
def progressbar_update():        
    if task.is_alive(): # run multiple prompts at once
        if progress["value"]==100:
            progress["value"]=0
        else:
            progress["value"]+=1
        root.after(50, progressbar_update)
    else:
        messagebox.showinfo("Information","Your file has been downloaded!")
        root.destroy()
        return subprocess.Popen([sys.executable]+sys.argv)

def yt_download():
    try:
        yt=YouTube(link.get())
    except:
        messagebox.showinfo("Information","Video unavailable!")
        return
    
    load_preview(yt)
    tit_label=tk.Label(root, text=yt.title, font=("Times New Roman", 10))
    tit_label.pack(padx=10, pady=5)
    if (type_str.get())=="mp4":
        vid_download(yt)
    else:
        audio_download(yt) 
    print("readx")

def vid_download(yt):
    video=yt.streams.filter(res=res_str.get(), only_video=True).first()
    video_file=video.download(filename="video.mp4")

    audio_stream=yt.streams.filter(only_audio=True).first()
    audio_file=audio_stream.download(filename="audio.mp4")

    final_vid=VideoFileClip(video_file)
    final_audio=AudioFileClip(audio_file)
    final_vid=final_vid.with_audio(final_audio)

    default_filename=yt.title.replace(" ", "_") + ".mp4"
    file_path=filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")], initialfile=default_filename)   
    final_vid.write_videofile(file_path)
    os.remove(video_file)
    os.remove(audio_file)
    
# https://www.youtube.com/watch?v=hcm55lU9knw
def audio_download(yt):
    audio_stream=yt.streams.filter(only_audio=True).first()
    audio_file=audio_stream.download(filename="audio.mp4")
    audio=AudioFileClip(audio_file)
    default_filename=yt.title.replace(" ", "_") + ".mp3"
    file_path=filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3")], initialfile=default_filename)
    audio.write_audiofile(file_path)
    os.remove(audio_file)

def load_preview(yt):    
    response=requests.get(yt.thumbnail_url)
    img_data=BytesIO(response.content)
    img=Image.open(img_data)
    img=img.resize((240, 180), Image.LANCZOS)
    img=ImageTk.PhotoImage(img)
    preview_label=tk.Label(root, image=img)
    preview_label.image=img
    preview_label.pack(padx=10, pady=5)

download_button=tk.Button(root, text="Download", font=("Times New Roman", 12), width=30, command=download_conf)
download_button.pack(padx=10, pady=5)
root.mainloop()