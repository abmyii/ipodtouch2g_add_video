#!/usr/bin/env python3
import dataset
import os
import shutil
import sys

location_db = dataset.connect('sqlite+pysqlite:///iTunes_Control/iTunes/iTunes Library.itlp/Locations.itdb')
library_db = dataset.connect('sqlite+pysqlite:///iTunes_Control/iTunes/iTunes Library.itlp/Library.itdb')

for video_path in sys.argv[1:]:
    video_filename = os.path.split(video_path)[1]

    # Copy video to necessary location
    video_location = 'iTunes_Control/Music/Videos/' + video_filename
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
    last['total_time_ms'] =

    # (library database) Add modified item
    library_db['item'].insert(last)

