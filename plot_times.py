#!/usr/bin/env python
"""
    <name>
        plot_times

    <description>
        Provided a file with stats obtained from walk_repo. Plot a histogram
        containing the lifetime of each blob object in a target repository

    <usage>
            ./plot_times.py [path_to_stats_file]

    <author>
        Santiago Torres-Arias

    <date>
        1448347063
"""
import matplotlib.pyplot as plt
import json
import sys

SECONDS_PER_DAY = 3600 * 24

def create_time_differences(blob_times):
    blob_differences = []

    for blob in blob_times:
        this_blob = blob_times[blob]
        if "difference" in this_blob:
            this_time = (this_blob['difference'])/SECONDS_PER_DAY
            blob_differences.append(this_time)
        else:
            print("Skipped {}".format(blob))

    return blob_differences

def load_information(filename):
    with open(filename) as fp:
        blob_times  = json.load(fp)

    return blob_times

def plot_histogram(time_differences):
    plt.hist(time_differences, bins=500, normed=True)
    plt.show()

def plot_costs(bins):
    pass
    #line = 
    #for thisbin in plt.xticks:

    

if __name__ == "__main__":
   
    blob_times = load_information(sys.argv[1])
    time_differences = create_time_differences(blob_times)
    plot_histogram(time_differences)
