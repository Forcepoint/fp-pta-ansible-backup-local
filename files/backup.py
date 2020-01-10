#!/usr/local/bin/python2.7

"""
Author: Jeremy Cornett
Date: 2018-01-02
Purpose: Create a tar of the specified folder and store it in the specified location. Retain the specified number of
records.
"""

import argparse
import datetime
import glob
import os
import tarfile


if __name__ == "__main__":
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description="Create a tar of the specified folder and store it in the specified "
                                                 "location. Retain the specified number of records.")
    parser.add_argument("name", help="The name to give the tar.")
    parser.add_argument("target", help="The file or directory to tar up.")
    parser.add_argument("destination", help="The directory to place the tar.")
    parser.add_argument("retention", help="The number of tars to retain. Zero means infinite (i.e. don't delete "
                                          "anything).")
    args = parser.parse_args()

    # Give the log file some space between runs.
    print
    print

    path_target = os.path.abspath(os.path.normpath(args.target))
    path_destination = os.path.abspath(os.path.normpath(args.destination))

    # Ensure the target and destination exist.
    if not os.path.exists(path_target):
        raise ValueError("The target path must exist.")
    else:
        print "TARGET: {}".format(path_target)
    if not os.path.exists(path_destination):
        raise ValueError("The destination path must exist.")
    else:
        print "DESTINATION: {}".format(path_destination)

    # Ensure retention is a positive number.
    count_retain = int(float(args.retention))
    if count_retain < 0:
        raise ValueError("The retention number ({}) must greater than or equal to zero.".format(args.retention))

    # Construct the tar file name from the current date and time.
    path_tar = os.path.join(path_destination, "{}_{}.tar".format(args.name,
                                                                 datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")))

    # By virtue of using a timestamp as part of the name, a collision shouldn't occur, but it's good to check anyways.
    if os.path.exists(path_tar):
        raise ValueError("COLLISION - The calculated path for the tar already exists - {}".format(path_tar))

    # Tar up the target to the destination folder.
    print "TAR: {}".format(path_tar)
    with tarfile.open(path_tar, "w") as file_tar:
        file_tar.add(path_target)

    # Check how many tars there are. If there's more than the retention value, delete the older ones. Ensure
    # that the timestamp for each tar is taken from the filename, not the file attributes.
    list_tars = glob.glob(os.path.join(path_destination, "{}_*.tar".format(args.name)))

    if len(list_tars) > count_retain:
        # The files are named in such a way that a lexicographical sort will sort them chronologically as well.
        list_tars.sort()
        # The more recent ones we want to retain.
        for i in range(0, count_retain):
            list_tars.pop()

        for path_tar_delete in list_tars:
            print "DELETE: {}".format(path_tar_delete)
            os.remove(path_tar_delete)
