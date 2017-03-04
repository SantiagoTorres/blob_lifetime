#!/usr/bin/env python
"""
    <name>
        plot_times

    <description>
        Provided a file with stats obtained from walk_repo. Dump a txt file
        containing the computed lifetimes for each blob.

    <usage>
            ./dump_blob_differences.py [path_to_stats_file]

    <author>
        Santiago Torres-Arias

    <date>
        1448347063
"""
import json
import sys
import datetime, time

SECONDS_PER_DAY = 3600 * 24

with open(sys.argv[1]) as fp:
    blob_info = json.load(fp)

now = time.mktime(datetime.datetime.now().timetuple())
for blob in blob_info: 
    # compute the time to "today" if there is no end time
    this_blob = blob_info[blob]
    if this_blob['end'] == -1:
        this_blob["difference"] = now - this_blob['start']
    
    print("{} {} {} {}".format(blob_info[blob]['difference'],
        blob_info[blob]['filename'], this_blob['start_commit'], blob_info[blob]['end_commit']))
