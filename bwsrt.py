# !/usr/bin/env python3

""" A tool to fix common errors from SubRip files. """


#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# Python imports, application classes, etc.
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

import argparse # Parser for command-line options, arguments and sub-commands
import configparser # Configuration file parser
import datetime # Basic date and time types
import os # Miscellaneous operating system interfaces
import re # Regular expression operations
import sys # System-specific parameters and functions

from class_subrip import SubRip


#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# Declare variables, read configuration, check command line arguments, etc.
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

debug = False
fix = False
scriptspath = os.path.dirname(os.path.realpath(__file__)) # Scripts path
configfile = os.path.join(scriptspath, "bwsrt.cfg") # Configuration file
timeformat = '%H:%M:%S,%f' # Time format for parsing SubRip timecodes
workingpath = os.getcwd() # Working path
zerostamp = '00:00:00,000' # Zero time stamp

# Read configuration file
config = configparser.RawConfigParser()
config.read(configfile)
blacklist = str(config.get("Configuration", "BlackList"))
blacklist_regex = re.compile(blacklist)
check_blacklist = config.getboolean("Configuration", "CheckBlackList")
check_numbering = config.getboolean("Configuration", "CheckNumbering")
check_overlapping = config.getboolean("Configuration", "CheckOverlapping")

# Read command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d", action="store_true", dest="debug",
    required=False, help="Print debugging information.")
parser.add_argument("-f", action="store_true", dest="fix",
    required=False, help="Fix file.")
args = parser.parse_args() # Returns data from the options specified

# Command line arguments override default and config settings
if args.debug:
    debug = True
if args.fix:
    fix = True


#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# Loop files from working dir
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# List files from working path
for filename in os.listdir(workingpath):

    ext = os.path.splitext(filename)[1][1:].lower()
    filepath = os.path.join(workingpath, filename)

    # Check file extension
    if ext != 'srt':
        continue

    # Read SubRip file
    print('Processing file: "{0}".'.format(filename))
    print()
    srt = SubRip()
    ok, message = srt.open_file(filepath)
    if not ok:
        print('Error while opening file: "{0}"'.format(filename))
        print(message)
        sys.exit()

    # Print subtitle data for debugging purposes
    if debug:
        for subtitle in srt.subtitles:
            print(subtitle)
        print()


    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # Check blacklisted words
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    if check_blacklist:
        for key, subtitle in enumerate(srt.subtitles):
            r = blacklist_regex.search(subtitle[2])
            if r is not None:
                print('Blacklisted word found from line:')
                print('Line number..........: {0}'.format(key))
                print('Word.................: {0}'.format(r.group(0)))
                print('Subtitles............: {0}.'.format(subtitle[2]))
                print()
                srt.delete(key)


    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # Check subtitle numbering
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    if check_numbering:
        counter = 1
        for key, subtitle in enumerate(srt.subtitles):
            subtitle_number = int(subtitle[0])
            if counter != subtitle_number:
                print('Subtitle numbering error in file: "{0}".'.format(
                    filename))
                print('Expected number {0}, got {1}.'.format(
                    counter, subtitle_number))
                if fix:
                    srt.subtitles[key][0] = str(counter)
                    print('Fixed numbering. Line="{0}".'.format(
                        srt.subtitles[key]))
                print()
            counter += 1


    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # Check subtitle numbering
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    if check_overlapping:

        # Reset variables
        datetime3 = datetime.datetime.strptime(zerostamp, timeformat)
        datetime4 = datetime.datetime.strptime(zerostamp, timeformat)
        prevkey = -1
        timecode = re.compile(r'^(\d{2}:\d{2}:\d{2},\d{3}) --> ' +
            '(\d{2}:\d{2}:\d{2},\d{3})\Z')

        for key, subtitle in enumerate(srt.subtitles):

            datetime1 = datetime.datetime.strptime(zerostamp, timeformat)
            datetime2 = datetime.datetime.strptime(zerostamp, timeformat)
            linenumber = key + 1

            # Parse timecodes into datetime objects
            r = timecode.search(subtitle[1])
            if r is not None:
                datetime1 = datetime.datetime.strptime(r.group(1), timeformat)
                datetime2 = datetime.datetime.strptime(r.group(2), timeformat)
                timestr1=datetime1.strftime(timeformat)[:-3]
                timestr2=datetime2.strftime(timeformat)[:-3]

                # Check if subtitle show/hide-timecodes are ok
                if datetime1 >= datetime2:
                    datetime5 = datetime1 + datetime.timedelta(milliseconds=300)
                    timestr5=datetime5.strftime(timeformat)[:-3]
                    print('Show/hide subtitle overlapping detected.')
                    print('Linenumber...........: {0}, line: {1}'.format(
                        linenumber, subtitle[1]))
                    print('Fixed timestamp......: {0}, line: {1} --> {2}'
                        .format(linenumber, timestr1, timestr5))
                    print()
                    if fix:
                        srt.subtitles[key][1] = timestr1 + ' --> ' + timestr5

                # Check if previous subtitle hide-timecode is ok
                elif datetime1 <= datetime4:
                    datetime5 = datetime1 - datetime.timedelta(milliseconds=1)
                    timestr5=datetime5.strftime(timeformat)[:-3]
                    print('Subtitle overlapping detected between previous',
                        'subtitle.')
                    print('Previous timestamp...: {0}, line: {1}'
                        .format(prevkey, srt.subtitles[prevkey][1]))
                    print('Current timestamp....: {0}, line: {1}'.format(
                        linenumber, subtitle[1]))
                    print('Fixed timestamp......: {0}, line: {1} --> {2}'
                        .format(prevkey, timestr3, timestr5))
                    print()
                    if fix:
                        srt.subtitles[prevkey][1] = timestr3 + ' --> ' + timestr5

                # Save previous line data for later checks
                datetime3 = datetime.datetime.strptime(r.group(1), timeformat)
                datetime4 = datetime.datetime.strptime(r.group(2), timeformat)
                timestr3=datetime3.strftime(timeformat)[:-3]
                timestr4=datetime4.strftime(timeformat)[:-3]
                prevkey = key

            else:
                print('Unable to extract timecodes from file: "{0}".'.format(
                    filename))
                continue


    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    # File processing complete. Save file if option is enabled.
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    if fix:
        print("File saved with fixes.")
        srt.save_file()

    print('Processing complete.')
    print()
