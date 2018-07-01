# !/usr/bin/env python3

''" A class to handle SubRip (.srt) files. ''"

# Imports
import os # Miscellaneous operating system interfaces
import re # Regular expression operations
import sys # System-specific parameters and functions


# A class to handle SubRip files
class SubRip(object):

  # Initialization
  def __init__(self):

    # Declare class variables
    self.filepath = '' # Currently open file path
    self.subtitles = [] # A list for subtitles

    # Compiled regular expression objects
    self.timecode = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3} --> ' +
      '\d{2}:\d{2}:\d{2},\d{3}\Z')


  # Close SubRip-file
  def close_file(self):
    self.filepath = ''
    self.subtitles = []


  # Delete subtile
  def delete(self, key):
    del self.subtitles[key]


  # Open SubRip-file
  def open_file(self, filepath, enc='utf_8_sig', strip=True):

    # Close any previous file
    self.close_file()

    # Check file path
    if filepath == '':
      return False, 'File not specified.'

    # Retrieve basename for file
    basename = os.path.basename(filepath)

    # Check if file exists
    if not os.path.exists(filepath):
      return False, 'File does not exist: "{0}".'.format(basename)

    # File path should be an existing regular file
    if not os.path.isfile(filepath):
      return False, 'Not a file: "{0}".'.format(basename)

    # File should not be empty
    if not os.path.getsize(filepath) > 0:
      return False, 'File is empty: "{0}".'.format(basename)

    # Check file extension
    ext = os.path.splitext(filepath)[1][1:].lower()
    if ext != 'srt':
      return False, 'File type is not valid: "{0}".'.format(basename)

    # Loop through file and parse contents into a list
    key = ''
    timecode = ''
    lines = ''
    with open(filepath, 'r', encoding=enc) as filehandle:
      for line in iter(filehandle):

        # Trim line
        line = line.strip()

        # Strip unwanted characters
        if strip:
          line = re.sub(u'[\u0000-\u001f]', '', line) # ASCII control characters
          line = line.replace(u'\ufeff', '') # Unicode byte order mark (BOM)

        # First we find out the subtitle key
        if key == '':
          if strip:
            line = re.sub('[^\d]', '', line) # Strip everything but numbers
          if re.match(r"^[\d]+\Z", line):
            key = line
            continue
          else:
            return False, 'Numbering error. Line="{0}".'.format(line)

        # After subtitle key, next thing should be the timestamps
        if key != '' and timecode == '':
          if strip:
            line = re.sub('[^:,\- >\d]+', '', line) # Strip unnecessary chars
          if self.timecode.match(line):
            timecode = line
            continue
          else:
            return False, 'Timecode error. Line="{0}".'.format(line)

        # The rest of the lines are the actual subtitle lines
        if key != '' and timecode != '' and line != '':
          if lines != '':
            lines += '<br />'
          lines += line
          continue

        # When we have everything, we append it to our subtitles list
        if key != '' and timecode != '' and lines != '':
          self.subtitles.append([key, timecode, lines])
          key = ''
          timecode = ''
          lines = ''
        else:
          return False, 'Subtitle parsing error. Key="{0}", ' + \
            'timecode="{1}", lines="{2}".'.format(key, timecode, lines)

    # The loop doesn't always catch the last line if the file has only one
    # empty line at EOF
    if key != '' and timecode != '' and lines != '':
      self.subtitles.append([key, timecode, lines])
      key = ''
      timecode = ''
      lines = ''

    # Final check so variables are completely empty
    if key == '' and timecode == '' and lines == '':
      self.filepath = filepath
      return True, 'File opened successfully.'
    else:
      return False, 'Subtitle parsing error. Key="{0}", ' + \
        'timecode="{1}", lines="{2}".'.format(key, timecode, lines)


  # Save SubRip-file
  def save_file(self, enc='utf_8_sig'):

    # Check for file
    if not self.filepath:
      return False, 'No file open.'

    # Remove empty lines from the end of the file
    length = int(len(self.subtitles))
    while length > 1 and self.subtitles[length - 1] == '':
      del self.subtitles[length - 1]
      length = int(len(self.subtitles))

    # Loop file data and save to file
    try:
      filehandle = open(self.filepath, 'w', encoding=enc)
      for key, subtitle in enumerate(self.subtitles):
        if key > 0:
          filehandle.write('\n')
        filehandle.write(subtitle[0] + '\n')
        filehandle.write(subtitle[1] + '\n')
        filehandle.write(subtitle[2].replace('<br />', '\n') + '\n')
      filehandle.close()
    except IOError as e:
      return False, 'I/O error({0}): "{1}".'.format(e.errno, e.strerror)
    except UnicodeDecodeError:
      return False, 'Unicode Decode Error: "{0}".'.format(filepath)
    except UnicodeEncodeError:
      return False, 'Unicode Encode Error: "{0}".'.format(filepath)
    except:
      return False, 'Unexpected error: "{0}".'.format(sys.exc_info()[1])
    else:
      return True, 'File saved successfully.'
