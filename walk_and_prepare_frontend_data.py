#!/usr/bin/env python
"""
    <name>
        walk_repo

    <description>
        walks a target repository tree and gathers blob information to derive
        the average blob lifetime for to plot on the d3_barchart file.

    <usage>
        import as a module and call walk repository, or use as a standalone:
            ./walk_and_prepare_frontend_data.py [path/to/repo/.git]

        or
            ./walk_and_prepare_frontend_data.py [path/to/repo/bare/]

    <author>
        Santiago Torres-Arias

    <date>
        1448347063
"""
from pygit2 import Repository
from pygit2 import GIT_SORT_TIME, GIT_SORT_REVERSE
import numpy as np
import datetime, time

import sys
import json
import os

SECONDS_PER_DAY = 3600 * 24.0
COST_PER_DAY = 75000*365

"""
    <name>
        walk_repository

    <arguments>
        path (string): The path of the repository to parse

    <returns>
        a json file of the following fields:

            {
                COMMIT_ID: {"start_time": START_TIME,
                             "end_time": END_TIME,
                             "difference": END_TIME - START_TIME,
                             "filename": FILENAME
                             },
                OTHER_COMMIT_ID: {...}
            },
"""
def walk_repository(path):

    # load our requested repository
    repo = Repository(path)

    # walk the repository and check which authors are there
    blobs = {}
    old_blobs = set()
    old_date = -1

    for commit in repo.walk(repo.head.target, GIT_SORT_TIME | GIT_SORT_REVERSE):

        date = commit.commit_time
        root_tree = commit.tree

        these_blobs = load_blobs_for_root_tree(root_tree, repo)

        for blob, filename in these_blobs:
            if blob not in blobs:
                blobs[blob] = {}
                blobs[blob]["start"] = date
                blobs[blob]["start_commit"] = str(commit.id)
                blobs[blob]["filename"] = filename

        blob_diff = old_blobs - these_blobs
        for blob, filename in blob_diff:
            if blob not in blobs:
                print "wat"
            else:
                blobs[blob]['end'] = date
                blobs[blob]['end_commit'] = str(commit.id)
                blobs[blob]['difference'] = (date - blobs[blob]['start'])/SECONDS_PER_DAY

        old_date = date
        old_blobs = these_blobs

    # this sets so that blobs on the current worktree to "it's still here"
    for blob in blobs:
        if "end" not in blobs[blob]:

            blobs[blob]['end'] = time.mktime(datetime.datetime.now().timetuple())
            blobs[blob]['end_commit'] = str(commit.id)
            blobs[blob]['difference'] = (blobs[blob]['end'] - blobs[blob]['start'])/SECONDS_PER_DAY
            blobs[blob]['spicy'] = True

    return blobs 

def load_blobs_for_root_tree(tree, repo):

    return _get_blobs_for_tree(tree, repo, "./")

def _get_blobs_for_tree(tree, repo, prefix):
    blobs = set()
    for entry in tree:
        if entry.type == "tree":
            blobs |= _get_blobs_for_tree(repo[entry.id], repo, os.path.join(prefix, entry.name))
        else:
            blobs.add((str(entry.id), os.path.join(prefix,entry.name)))
    return blobs

def _bin_blobs(blobs):
    """ returns a binned version of the data in the following format:

    [
        {files: [file1, file2, ...], cost: COST, pos: position_in_hist},
        ...
    ]
    """

    # this will be our times
    dates = [blobs[blob]['difference'] for blob in blobs]

    # get bin edges
    hist, edges = np.histogram(dates, 500)

    bins = {}
    for blob in blobs:
        thisblob = blobs[blob]
        thisbin = np.digitize(thisblob['difference'], edges).tolist() - 1
        thisbin = edges[thisbin]

        if thisbin not in bins:
            bins[thisbin] = {'files':[thisblob['filename']], 'cost': COST_PER_DAY/(thisbin), "pos":thisbin}
            if thisblob['spicy']:
                bins[thisbin]['spicy'] = 1;

        else:
            if thisblob['spicy']:
                bins[thisbin]['spicy'] = 1;
            bins[thisbin]['files'].append(thisblob['filename'])

    return sorted([bins[thisbin] for thisbin in bins], key=lambda x: x['pos'])


"""main function, calls walk_repo on sys argument and dumps the result file """
if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage ./walk_repository [name] [output_file]")
        sys.exit(-1)

    repo_location = sys.argv[1]

    time_stats = walk_repository(repo_location)
    time_stats = _bin_blobs(time_stats)
    with open(sys.argv[2], "w") as fp:
        json.dump(time_stats, fp)
