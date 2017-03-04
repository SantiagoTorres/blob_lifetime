#!/usr/bin/env python
"""
    <name>
        walk_repo

    <description>
        walks a target repository tree and gathers blob information to derive
        the average blob lifetime

    <usage>
        import as a module and call walk repository, or use as a standalone:
            ./walk_repo.py [path/to/repo/.git]

        or
            ./walk_repo.py [path/to/repo/bare/]

    <author>
        Santiago Torres-Arias

    <date>
        1448347063
"""
from pygit2 import Repository
from pygit2 import GIT_SORT_TIME, GIT_SORT_REVERSE

import sys
import json
import os

"""
    <name>
        walk_repository

    <arguments>
        path (string): The path of the repository to parse

    <returns>
        a dictionary, keyed by commit author containing:
            author:{
                signed: n,   # number of signed commits
                unsigned: m, # number of unsigned commits
                emails: k,   # The author's email
            }
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
                blobs[blob]['difference'] = date - blobs[blob]['start']

        old_date = date
        old_blobs = these_blobs

    # this sets so that blobs on the current worktree to "it's still here"
    for blob in blobs:
        if "end" not in blobs[blob]:
            blobs[blob]['end'] = -1
            blobs[blob]['end_commit'] = str(commit.id)
            blobs[blob]['difference'] = -1

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


"""main function, calls walk_repo on sys argument and prints a summary"""
if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage ./walk_repository [name] [output_file]")
        sys.exit(-1)

    repo_location = sys.argv[1]

    time_stats = walk_repository(repo_location)
    with open(sys.argv[2], "w") as fp:
        json.dump(time_stats, fp)
