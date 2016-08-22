#!/usr/bin/env python

###
#   Imports
#
import sys
import os
import urllib2


###
#   class iCalDict
#
#   Convert a .ics file into a Dictionary object.
#
class iCalDict():

    ###
    #   __init__
    #
    #   Create a new iCalDict instance with a string representing a .ics file
    #   (referenced by a string as a file path or URL) and an optional mapping
    #   between .ics file keys and returned keys in the Dictionary.
    #
    def __init__(self, ics_file, mapping = {}):
        self.__ics_file = ics_file
        self.__mapping = mapping
        self.content = self.__file_get_contents()
        self.data = self.__sanitize_data()

    ###
    #   convert
    #
    #   Convert the .ics file into a Dictionary.
    #
    def convert(self):

        # Confirm that all incoming data is valid, namely the file itself.
        self.__validate()

        if "BEGIN:VEVENT" not in self.data: raise Exception(self.__error_messages("no_events"))

        # Filter data by eliminating metadata and extraneous lines.
        self.data = self.data[ self.data.index("BEGIN:VEVENT") : len(self.data) -  self.data[::-1].index("END:VEVENT") ]

        output = []

        # Continue to iterate over the events and convert each event block to a Dictionary.
        # Filter this data out of data and continue. 
        while len(self.data) > 0:
            output.append(self.__array_to_dict(self.data[ 0 : self.data.index("END:VEVENT") + 1 ]))
            self.data = [value for key, value in enumerate(self.data) if key > self.data.index("END:VEVENT")]

        return output

    ###
    #   array_to_dict
    #
    #   Given a list of .ics lines, return the list as a Dictionary object.
    #
    def __array_to_dict(self, data):

        if not isinstance(data, list): raise Exception("An array is required to convert data to JSON. A non-array parameter has been provided.")

        output = {}

        for line in data:

            elements = line.split(':')

            if not isinstance(elements, list) and len(elements) is not 2: raise Exception("The following line does not follow expected convention: %s" % line)

            if elements[0] in output:
                # TODO: A key already exists in the output, this would overwrite. Handle.
                pass

            output[elements[0]] = elements[1]

        return output

    ###
    #   __file_get_contents
    #
    #   Retrieve the contents of the .ics file as an array,
    #   separated by line.
    #
    def __file_get_contents(self):

        content = None

        if os.path.isfile(self.__ics_file):
            content = open(self.__ics_file, 'r').read()
        else:
            content = urllib2.urlopen(self.__ics_file).read()

        return [line for line in content.split("\r\n")]

    ###
    #   __sanitize_data
    #
    #   Sanitize the class variable such that wrapped lines are
    #   appended to the array elements they belong with.
    #
    def __sanitize_data(self):
        
        output = []

        for line in self.content:

            if len(line) == 0: continue

            if line[0] == ' ':
                output[len(output) - 1] += line
            else:
                output.append(line.rstrip(" ").lstrip(" "))

        return output

    ###
    #   __validate
    #
    #   Validate the .ics file's data and raise exceptions where needed.
    #
    def __validate(self):

        # If the file does not start with "BEGIN:VCALENDAR".
        if "BEGIN:VCALENDAR" not in self.data[0]:
            raise Exception(self.__error_messages("invalid_file"))

    ###
    #   __error_messages
    #
    #   Return an error message given an identifying key.
    #
    def __error_messages(self, key):

        messages = {
            "invalid_file": "This file is invalid. A .ics file is identified as a file in which the first line is \"BEGIN:VCALENDAR\".",
            "no_events":    "No Events, identified by the \"BEGIN:VEVENT\" line, have been found."
        }

        if key not in messages: return "An unknown error has occured."

        return messages[key]

###
#   Testing the above.
#
if __name__ == '__main__':
    # converter = iCalDict('http://25livepub.collegenet.com/calendars/NJIT_EVENTS.ics')
    converter = iCalDict('events.ics')
    print converter.convert()
