import sys
import os
import ConfigParser
import codecs
import stat


class ConfigureationSetup(object):
    def __init__(self, args):
        """
        Parse arguments from a Configuration file.  Note that anything can be
        set as a "Section" in the argument file.
        """
        self.args = args
        self.config_file = args['system_config']
        self.check_perms()

    def check_perms(self):
        """
        Check the permissions of the config file prior to performing any actions
        """
        # If config file is specified, confim proper permissions
        if self.config_file:
            confpath = self.config_file
            if os.path.isfile(os.path.realpath(confpath)):
                mode = oct(stat.S_IMODE(os.stat(confpath).st_mode))
                modes = (mode == '0600', mode == '0400')
                if not any(modes):
                    sys.exit('To use a configuration file the permissions'
                             ' need to be "0600" or "0400"')

    def config_args(self):
        """
        Loop through the configuration file and set all of our values.
        """
        # setup the parser to for safe config parsing with a no value argument
        # Added per - https://github.com/cloudnull/turbolift/issues/2
        if sys.version_info >= (2, 7, 0):
            parser = ConfigParser.SafeConfigParser(allow_no_value=True)
        else:
            parser = ConfigParser.SafeConfigParser()

        # Load the configuration file for parsing
        with codecs.open(self.config_file, 'r', encoding='utf-8') as f:
            parser.readfp(f)

        # Ensure that there is atleast one section in the configuration file
        if len(parser.sections()) < 1:
            sys.exit('No sections were placed into the configuration file as'
                     ' such I have quit.')
        else:
            # Parse all sections for the configuration file
            for section_name in parser.sections():
                for name, value in parser.items(section_name):
                    name = name.encode('utf8')
                    value = value.encode('utf8')
                    self.args.update({name: value})
        return self.args
