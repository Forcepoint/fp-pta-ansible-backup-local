#!/usr/bin/python

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
import pathlib
import pwd
import subprocess


def log(path_log, message):
    """Output the given message to the log file.
    :param path_log: The path to the log file to append the message to.
    :type path_log: str
    :param message: The message to add to the log file.
    :type message: str
    :return: None
    """
    with open(path_log, 'a') as file_log:
        message_lines = message.split('\n')
        if len(message_lines) <= 1:
            file_log.write("{} {}\n".format(datetime.datetime.now(), message))
        else:
            # Make the log easier to read for multiline output.
            file_log.write("{} {}\n".format(datetime.datetime.now(), message_lines[0]))
            for line in message_lines[1:]:
                file_log.write("\t{}\n".format(line))


def setup_logging(log_folder, prefix='', retain=10):
    """Determine the intended log file path and cleanup old logs.
    :param log_folder: The folder to add the log file to.
    :type log_folder: str
    :param prefix: The prefix to give the log files.
    :type prefix: str
    :param retain: The number of log files to retain.
    :type retain: int
    :return: The path of the log file.
    :rtype: str
    """
    assert os.path.exists(log_folder), "The log folder must already exist."

    # Calculate the intended log path.
    if len(prefix) == 0:
        log_file_path = os.path.join(log_folder, "{}.log".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")))
    else:
        log_file_path = os.path.join(log_folder, "{}_{}.log".format(
            prefix, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")))
    assert not os.path.exists(log_file_path), "A log file already exists with that name - {}".format(log_file_path)
    log(log_file_path, "SCRIPT START")

    # Get all log files in the directory that's not cron.log.
    list_log_files = glob.glob(os.path.join(log_folder, "{}*.log".format(prefix)))
    if 'cron.log' in list_log_files:
        list_log_files.remove('cron.log')
    # The log files should sort chronologically when sorted lexically.
    list_log_files.sort()

    # Delete old logs to keep a maximum.
    if len(list_log_files) > retain:
        for path_log_file_to_delete in list_log_files[:-1*(retain+1)]:
            os.remove(path_log_file_to_delete)

    return log_file_path


if __name__ == "__main__":
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description="Create a tar of the specified folder and store it in the specified "
                                                 "location. Retain the specified number of records.")
    parser.add_argument("name", help="The name to give the tar.")
    parser.add_argument("target", help="The file or directory to tar up.")
    parser.add_argument("destination", help="The directory to place the tar.")
    parser.add_argument("retention", help="The number of tars to retain. Zero means infinite (i.e. don't delete "
                                          "anything).")
    parser.add_argument("--what-if", action='store_true', help="Do not perform any deletions, encryptions, "
                                                               "or transfers.")
    args = parser.parse_args()

    # Get a log file setup in the same directory as this script.
    path_log_file = setup_logging(pathlib.Path(__file__).parent.resolve(), prefix=args.name)

    # Initialize
    path_target = os.path.abspath(os.path.normpath(args.target))
    path_destination = os.path.abspath(os.path.normpath(args.destination))
    count_retain = int(float(args.retention))
    path_tar = os.path.join(path_destination, "{}_{}.tar".format(
        args.name, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")))

    # Assumptions
    assert os.path.exists(path_target), "The target path must exist."
    assert os.path.exists(path_destination), "The destination path must exist."
    assert count_retain >= 0, "The retention number ({}) must greater than or equal to zero.".format(args.retention)
    assert not os.path.exists(path_tar), \
        "COLLISION - The calculated path for the tar already exists - {}".format(path_tar)

    # Log some basic information.
    log(path_log_file, "WHAT-IF: {}".format(args.what_if))
    log(path_log_file, "TARGET: {}".format(path_target))
    log(path_log_file, "DESTINATION: {}".format(path_destination))
    log(path_log_file, "TAR: {}".format(path_tar))

    # Tar up the target to the destination folder.
    if not args.what_if:
        # Create the tar with sudo so that any files not owned by the current user are captured.
        command_tar = ['sudo', 'tar', '-cvf', path_tar, path_target]
        list_tar_output = subprocess.check_output(command_tar, text=True).split()
        log(path_log_file, 'TAR OUTPUT...\n{}'.format('\n'.join(list_tar_output)))
        log(path_log_file, 'OWN TAR')
        subprocess.check_call(['sudo', 'chown', "{0}:{0}".format(pwd.getpwuid(os.getuid()).pw_name), path_tar])

    if count_retain != 0:
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
                log(path_log_file, "DELETE: {}".format(path_tar_delete))
                if not args.what_if:
                    os.remove(path_tar_delete)
