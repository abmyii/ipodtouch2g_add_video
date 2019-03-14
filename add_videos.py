#!/usr/bin/env python3
import dataset
import os
import sys

from moviepy.video.io.VideoFileClip import VideoFileClip

# Add a cropbox if specified
cropbox = ''
if '-crop' in sys.argv:
    index = sys.argv.index('-crop')
    cropbox = ',crop=' + sys.argv[index+1]  # Set cropbox

    # Remove args from sys.argv
    sys.argv.pop(index+1)
    sys.argv.pop(index)

# Taken and modified from https://stackoverflow.com/a/23274686
ffmpeg_opts = '-c:v libx264 -crf 23 -preset fast -profile:v baseline -level 3 \
-refs 6 -vf "scale=480:240,setdar=2:1,format=yuv420p{cropbox}" -c:a copy'


# https://www.reddit.com/r/moviepy/comments/2bsnrq/is_it_possible_to_get_the_length_of_a_video/
def getVideoLength(filename):
    return VideoFileClip(filename).duration * 1000  # Seconds to milliseconds


def convertVideo(video, output):
    return os.system(
        f'ffmpeg -i {video} {ffmpeg_opts} {output}'
    )


# Mount IPod
mounted = False  # Stores wether program mount the IPod or not
ipod_mount_path = '/tmp/IPod'
if not os.path.exists(ipod_mount_path):
    os.mkdir(ipod_mount_path)
if not os.listdir(ipod_mount_path):
    out = os.system('ifuse ' + ipod_mount_path)
    mounted = True

# Make "Videos" Folder if necessary
itunes_path = f'{ipod_mount_path}/iTunes_Control/Music/Videos/'
if not os.path.isdir(itunes_path):
    os.mkdir(itunes_path)

itunes_db_path = f'{ipod_mount_path}/iTunes_Control/iTunes/iTunes Library.itlp'
location_db = dataset.connect(
    f'sqlite+pysqlite:///{itunes_db_path}/Locations.itdb'
)
library_db = dataset.connect(
    f'sqlite+pysqlite:///{itunes_db_path}/Library.itdb'
)

for video_path in sys.argv[1:]:
    video_filename = os.path.split(video_path)[1]

    # Copy video to necessary location
    print(f'Copying and converting {video_filename}')
    video_location = itunes_path + video_filename
    if os.path.exists(video_location):
        print('Video already exists. Skipping.')
    else:
        convertVideo(video_path, video_location)

    print(f'Adding {video_filename} to database')

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
    last['total_time_ms'] = getVideoLength(video_path)

    # (library database) Add modified item
    library_db['item'].insert(last)

# Unmount IPod if the program mounted it
if mounted:
    out = os.system('fusermount -u /tmp/IPod')
