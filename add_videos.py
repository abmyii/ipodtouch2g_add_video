#!/usr/bin/env python3
import dataset
import os
import shutil
import sys

from moviepy.video.io.VideoFileClip import VideoFileClip


# https://www.reddit.com/r/moviepy/comments/2bsnrq/is_it_possible_to_get_the_length_of_a_video/
def getVideoLength(filename):
    return VideoFileClip(filename).duration * 60  # Seconds to milliseconds


# Mount IPod
ipod_mount_path = '/tmp/IPod'
if not os.path.exists(ipod_mount_path):
    os.mkdir(ipod_mount_path)
if not os.listdir(ipod_mount_path):
    out = os.system('ifuse ' + ipod_mount_path)

# Make "Videos" Folder if necessary
itunes_path = f'{ipod_mount_path}/iTunes_Control/Music/Videos/'
if not os.path.isdir(itunes_path):
    os.mkdir(itunes_path)

itunes_db_path = '{ipod_mount_path}/iTunes_Control/iTunes/iTunes Library.itlp'
location_db = dataset.connect(
    f'sqlite+pysqlite://{itunes_db_path}/Locations.itdb'
)
library_db = dataset.connect(
    f'sqlite+pysqlite://{itunes_db_path}/Library.itdb'
)

for video_path in sys.argv[1:]:
    video_filename = os.path.split(video_path)[1]

    # Copy video to necessary location
    video_location = itunes_path + video_filename
    shutil.copyfile(video_path, video_location)

    print(f'Adding {video_filename}')

    # (location database) Use last row but change necessary fields
    last = location_db['location'].find_one(order_by=['-item_pid'])

    last['item_pid'] += 1
    last['location'] = 'Videos/' + video_filename

    # (location database) Add modified item
    location_db['location'].insert(last)

    # (library database) Use last row but change necessary fields
    last = library_db['item'].find_one(order_by=['-pid'])

    last['pid'] += 1
    last['title'] = os.path.splitext(video_filename)[0]
    last['total_time_ms'] = getVideoLength(video_filename)

    # (library database) Add modified item
    library_db['item'].insert(last)

# Unmount IPod
out = os.system('fusermount -u /tmp/IPod')
