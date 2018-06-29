# bwsrt

A tool to fix common errors from SubRip files.


## Caution!
If you are not 100% certain of what you are about to do or if you don't even
know what this application does then please do yourself a favor and don't even
download it. You can ruin all your files with simply running it. This
application does not create any backup files before running. You have been
warned.


## Getting started
This application lists all SubRip files (files with the extension "srt") from
the current working directory. When the files are listed, bwsrt will try to
parse all those files one by one, reporting any errors found while parsing.

If the "fix" option is enabled, bwsrt will also fix all errors that have been
reported during parsing and checking.

For more information about SubRip files, you can read about them from this
[Wikipedia page](https://en.wikipedia.org/wiki/SubRip)


### Strip unwanted characters from file
Enabled by default. In some cases subtitle files contain invalid characters.
For instance, sometimes there are ASCII control characters like the NULL
character or a duplicate unicode byte order mark (BOM). Usually media players
ignore these errors but in some cases this will result in broken subtitles.

When enabled, bwsrt will strip all ASCII characters between decimals 0-31.
There is no use for these kind of characters in SubRip files so these are safe
to remove. For more information, you can read about ASCII control characters
from this [Wikipedia page](https://en.wikipedia.org/wiki/Control_character)


### Check blacklisted words
Enabled by default. This option will check if the spoken subtitle lines contain
blacklisted words that are set in the configuration file.

If fixing is enabled, the subtitles that contain any of these blacklisted words
in the spoken subtitle lines are removed.


### Check duplicate lines
Not enabled by default. This option will combine duplicate subtitles when they
occur consecutively. In some cases there are subtitle files that have the same
spoken lines and/or same timestamps multiple times.

This option will enable bwsrt to loop the file backwards and compare each
spoken subtitle lines against each other. If the spoken subtitle lines are the
same, those will be combined to a single subtitle and the duplicate subtitle is
removed.

This option is not enabled by default because there are cases where the same
subtitle might be a duplicate intentionally. For instance, a character in a
movie might ask "hello?" or "is there someone there?" twice with a pause in
between. In this case the duplicate subtitle is intentional and removing the
duplicate would result in a combined subtitle which would be wrong.


### Check subtitle numbering
Enabled by default. This option will reset the subtitle numbering in SubRip
files. These kind of errors are very common and most media players ignore the
subtitle numbering anyway so these errors are in no way critical. This is also
the easiest to check and fix.


### Check subtitle overlapping
Enabled by default. This option will compare the subtitle timestamps against
each other and if the timestamps overlap, bwsrt will report these as errors.

As of writing this, there are two possible ways the subtitle timestamps can
overlap. The first check will see if the timestamp to show a subtitle occurs
before the timestamp to hide it. The second check will see if the timestamp to
show a subtitle occurs before the timestamp to hide the previous subtitle.


## Running on Linux

### Installing dependencies (Debian-based systems)
Open your terminal application and type:
`sudo apt-get install python3`

Hit enter. Enter your password when prompted. Answer yes to the question about
using additional disk space.

### Downloading the source
git clone https://github.com/bulkware/bwsrt.git

### Running the application
You can run the application from the source code using this command:
`python3 bwsrt.py`
