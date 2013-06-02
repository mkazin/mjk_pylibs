"""
fileParser.py - Version 0.3 , by Michael Kazin (https://github.com/mkazin)

  A collection of functions to make it easy to parse content from a file.

Requires:
  * re for searchAndParse()

Changelog:
 * v 0.1 -    Initial version
 * v 0.2 -    Added set_verbose().  Fixed debug statement
 * v 0.3 -    Initial public release on GitHub
 
Notes:
 * The latest version of this library should be available on GitHub:
   https://github.com/mkazin/mjk_pylibs
 * Please see the same location for additional information
"""

import re

STATUS_ERROR = -1
STATUS_NOT_OPEN = 0
STATUS_FILE_OPEN = 1
STATUS_FINISHED = 2


class FileParser:

    verbose = 0
    status = STATUS_NOT_OPEN
    filename = ""
    filecontents = ""
    lines = []
    currline = -1
    linecount = -1

    def __init__(self):
        self.data = []

    ###########################################################################
    #
    # set_file(filepath) - initialization function to provide the filename
    #
    # Usage:
    #     status = set_file(filepath)
    #
    # Inputs:
    #     filepath        - full path the the file.  Does not support URLs
    #
    # Returns:
    #     The content of the file or ERROR_MESSAGE
    #
    ###########################################################################
    def set_file(self, filepath):
        self.filename = filepath

        if self.verbose:
            print "set_file called on file: " + self.filename

        # Let's try to open the file
        infile = open(self.filename, 'r')
        self.lines = infile.readlines()
        infile.close()

        self.linecount = len(self.lines)
        if self.linecount > 0:
            self.status = STATUS_FILE_OPEN
            self.currline = 0
        else:
            self.status = STATUS_ERROR

        if self.verbose:
            print "\tlinecount: " + str(self.linecount)

        return self.status

    ###########################################################################
    # current_line() - returns the content of the currently set line
    #
    # Usage:
    #     line = object.current_line()
    # Returns:
    #     The content of the currently set line
    ###########################################################################
    def current_line(self):
        if self.currline < 0:
            return ""

        if self.currline >= len(self.lines):
            return "Error!  Index out of bounds in self.lines[]"

        return self.lines[self.currline]

    ###########################################################################
    # skip_line() - increments the currently set line by one
    #
    # Usage:
    #     status = object.skip_line()
    # Returns:
    #     The status of the object after skipping.  Can be used to determine
    #  if the last line was reached.
    ###########################################################################
    def skip_line(self):
        self.currline += 1

        # Check to see if this is the last line and the status needs updating
        if self.currline >= self.linecount:
            self.status = STATUS_FINISHED

        return self.status

    def reset_line_number(self):
        # Ensure we're not in an error state
        if (self.status == STATUS_FILE_OPEN or self.status == STATUS_FINISHED):
            self.currline = 0
            self.status = STATUS_FILE_OPEN
        return self.status

    def skip_to_string(self, searchterm):

#        if self.verbose:
#          print "Entered skipToString().  Searching for |" + searchterm +
#            "|\n\tSearching lines:\n"

        found = False
        # Loop until we either find the search term, or get to EOF
        while (not found) and (self.status < STATUS_FINISHED):
            # Look for the search term in the current line
#            if self.verbose:  print str(self.currline) + "\t|" + "|"
            found = searchterm in self.current_line()
            if not found:
                # if not found, advance to the next line
                self.skip_line()

        return self.status

    # searchex is a regular expression as can be passed to re.search(),
    # complete with parenthases indicating result groups.
    # The returned value will be that result group
    def search_and_parse(self, searchex):

        if self.verbose:
            print "Entered search_and_parse().  Searching for |" + searchex + \
                "|\n\tSearching lines:\n"
        found = False
        # Loop until we either find the search term, or get to EOF
        while (not found) and (self.status < STATUS_FINISHED):
            # Look for the search term in the current line
            rawline = self.current_line()

            if self.verbose:
                print str(self.currline) + "\t|" + rawline + "|"

            result = re.search(searchex, rawline)

            if (result == None):
                found = False
                # if not found, advance to the next line
                self.skip_line()
            else:
                return result

    # Allows a calling application to control verbosity
    # Pass in 1 to enable verbose statements, or 0 to disable them.
    # Defaults to 0.
    def set_verbose(self, val):
        self.verbose = val
