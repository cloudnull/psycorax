import argparse
import sys
import os

from psycorax import info


def args_and_values():
    """
    Look for flags, these are all of the available options for Turbolift.
    """
    parser = argparse.ArgumentParser(formatter_class=lambda prog:
        argparse.HelpFormatter(prog,
                               max_help_position=50),
        usage='%(prog)s',
        description=('PsycoRAX The Automation and'
                     ' Infrastructure Stress Tester'),
        epilog=info.VINFO)

    # Setup for the positional Arguments
    authgroup = parser.add_argument_group('Authentication', 'Authentication'
                                          ' against the OpenStack API')
    optionals = parser.add_argument_group('Additional Options', 'Things you'
                                          ' might want to add to your'
                                          ' operation')

    # Base Authentication Argument Set
    authgroup.add_argument('-u',
                           '--os-user',
                           metavar='[USERNAME]',
                           help='Defaults to env[OS_USERNAME]',
                           default=os.environ.get('OS_USERNAME', None))
    authgroup.add_argument('-a',
                           '--os-apikey',
                           metavar='[API_KEY]',
                           help='Defaults to env[OS_API_KEY]',
                           default=os.environ.get('OS_API_KEY', None))
    authgroup.add_argument('-p',
                           '--os-password',
                           metavar='[PASSWORD]',
                           help='Defaults to env[OS_PASSWORD]',
                           default=os.environ.get('OS_PASSWORD', None))
    authgroup.add_argument('-r',
                           '--os-region',
                           metavar='[REGION]',
                           help='Defaults to env[OS_REGION_NAME]',
                           default=os.environ.get('OS_REGION_NAME', None))
    authgroup.add_argument('--os-auth-url',
                           metavar='[AUTH_URL]',
                           help='Defaults to env[OS_AUTH_URL]',
                           default=os.environ.get('OS_AUTH_URL', None))
    authgroup.add_argument('--os-rax-auth',
                           choices=['dfw', 'ord', 'lon'],
                           help='Rackspace Cloud Authentication',
                           default=None)
    authgroup.add_argument('--os-version',
                           metavar='[VERSION_NUM]',
                           default=os.getenv('OS_VERSION', 'v2.0'),
                           help='env[OS_VERSION]')
    authgroup.add_argument('--use-http',
                            action='store_true',
                            default=None,
                            help=('Forces the NOVA API to Use HTTP instead'
                                  ' of HTTPS'))
    authgroup.add_argument('--os-verbose',
                            action='store_true',
                            default=None,
                            help=('Make the OpenStack Authentication'
                                  ' Verbose'))

    # Optional Aguments
    optionals.add_argument('--test',
                            action='store_true',
                            default=None,
                            help=('Does Nothing to anything, just performs a'
                                  ' simple run test as if we were going to'
                                  ' attack our environment'))
    optionals.add_argument('--ssh-port',
                           metavar='[PORT_NUMBER]',
                           default=22,
                           type=int,
                           help=('If using SSH, you can specify an SSH Port'
                                 ' By Default this is "22"'))
    optionals.add_argument('--ssh-user',
                           metavar='[USER_NAME]',
                           default='root',
                           help=('If using SSH, you can specify an SSH User'
                                 ' By Default this is "root"'))
    optionals.add_argument('--ssh-key',
                           metavar='[PATH_TO_PRIVATE_KEY]',
                           default=None,
                           help=('If you want me to monkey with instances from'
                                 ' within the instances, I will need an SSH'
                                 ' key. This is the path to the key file that'
                                 ' you would like to use.'))
    optionals.add_argument('--error-retry',
                           metavar='[ATTEMPTS]',
                           type=int,
                           default=5,
                           help=('This option sets the number of attempts'
                                 ' %(prog)s will attempt an operation'
                                 ' before quiting. The default is 5. This'
                                 ' is useful if you have a spotty network'
                                 ' or ISP.'))
    optionals.add_argument('--time',
                           metavar='[time]',
                           type=int,
                           default=60,
                           help=('Time is expressed in minutes. As Such provide'
                                 ' A Time that you would like the system to run'
                                 ' between. Note that the time is a range, and'
                                 ' A Random time will be used from the integer'
                                 ' you choose. The default is 60 Minutes.'))
    optionals.add_argument('--cc-attack',
                           metavar='[ATTACKS]',
                           type=int,
                           default=1,
                           help=('This operations makes the system attack'
                                 ' a range between 1 and X number of instances'
                                 ' simultaniously Default is 1. If you use 0,'
                                 ' I pick a random number of instances and'
                                 ' attack them'))
    optionals.add_argument('--log-level',
                           metavar='[LOG_LEVEL]',
                           choices=['critical', 'warn', 'info', 'debug'],
                           default='info',
                           help=('Set the Log Level'))
    optionals.add_argument('--system-config',
                           metavar='[CONFIG-FILE]',
                           type=str,
                           default=None,
                           help=('Path to your Configuration file. This is '
                                 'an optional argument used to spec '
                                 'credentials. File MUST use permissions'))
    optionals.add_argument('--start',
                           action='store_true',
                           help='Start The PsycoRax')
    optionals.add_argument('--restart',
                           action='store_true',
                           help='Restart The PsycoRax')
    optionals.add_argument('--stop',
                           action='store_true',
                           help='Stop The PsycoRax')
    optionals.add_argument('--status',
                           action='store_true',
                           help='Get the Status of The PsycoRax')
    optionals.add_argument('--quiet',
                           action='store_true',
                           help='Make %(prog)s Shut the hell up')
    optionals.add_argument('--verbose',
                           action='store_true',
                           help='Be verbose While Uploading')
    optionals.add_argument('--debug',
                           action='store_true',
                           help='Turn up verbosity to over 9000')
    optionals.add_argument('--version',
                           action='version',
                           version=info.V_N)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit('Give me something to do and I will do it')

    # Parse the arguments
    args = parser.parse_args()
    set_args = vars(args)
    set_args = check_parsed(set_args)
    if set_args:
        return set_args
    else:
        sys.exit(parser.print_help())


def check_parsed(set_args):
    # Parse Config File
    #if set_args['system_config']:
    #    from turbolift.operations import systemconfig
    #    set_args = systemconfig.ConfigureationSetup(set_args).config_args()

    # Interperate the Parsed Arguments
    if set_args['os_region']:
        set_args['os_region'] = set_args['os_region'].upper()

    if set_args['os_rax_auth']:
        set_args['os_rax_auth'] = set_args['os_rax_auth'].upper()

    if not set_args['os_user']:
        print('\nNo Username was provided, use [--os-user]\n')
        return False

    if not (set_args['os_apikey'] or set_args['os_password']):
        parser.print_help()
        print('\nNo API Key or Password was provided, use [--os-apikey]\n')
        return False

    if set_args['os_apikey']:
        set_args['os_password'] = set_args['os_apikey']

    if set_args['os_rax_auth'] and set_args['os_region']:
        parser.print_help()
        print('You can\'t use both [--os-rax-auth] and'
              ' [--os-region] in the same command, so I quit...\n')
        return False

    if set_args['debug']:
        set_args['os_verbose'] = True
        set_args['verbose'] = True
        print('DEFAULT ARGUMENTS : %s\n' % (set_args))

    return set_args
