import glob
import os

os.chdir('subtitles')
filelist = glob.glob("*.nfo")
for f in filelist:
    os.remove(f)
