import os
import sys
import time
import traceback
import logging

# For Daemon
import daemon
from daemon import pidfile
import signal
import grp
import errno
import random

# Local Imports
from psycorax import info, becrazy


class NoLogLevelSet(Exception):
    pass


class CloudNotStopSystem(Exception):
    pass


class DaemonDispatch(object):
    def __init__(self, p_args, output, handler):
        """
        The Daemon Processes the input from the application.
        """
        self.log = output
        self.p_args = p_args
        self.handler = handler
        self.log.info('Daemon Dispatch envoked')

    def pid_file(self):
        """
        Sets up the Pid files Location
        """
        # Determine the Pid location
        name = info.__appname__
        if os.path.isdir('/var/run/'):
            self.pid1 = '/var/run/%s.pid' % name
        else:
            import tempfile
            pid_loc = (tempfile.gettempdir(), os.sep, name)
            self.pid1 = '%s%s%s.pid' % pid_loc
        self.log.info('PID File is : %s' % (self.pid1))
        self.p_args['pid1'] = self.pid1
        return self.pid1

    def gracful_exit(self, signum=None, frame=None):
        """
        Exit the system
        """
        self.log.info('Exiting The Daemon Process for %s. '
                      'Signal recieved was %s on %s'
                      % (info.__appname__, signum, frame))
        self.system.stop()

    def context(self, pid_file):
        """
        pid_file='The full path to the PID'
        The pid name assumes that you are making an appropriate use of locks.

        Example :

        from daemon import pidfile
        pidfile.PIDLockFile(path='/tmp/pidfile.pid', threaded=True)

        Context Creation for the python-daemon module. Default values are for
        Python-daemon > 1.6 This is for Python-Daemon PEP 3143.
        """
        if self.p_args['debug']:
            context = daemon.DaemonContext(
                stderr=sys.stderr,
                stdout=sys.stdout,
                working_directory=os.sep,
                umask=0,
                pidfile=pidfile.PIDLockFile(path=pid_file),
                )
        else:
            context = daemon.DaemonContext(
                working_directory=os.sep,
                umask=0,
                pidfile=pidfile.PIDLockFile(path=pid_file),
                )

        context.signal_map = {
            signal.SIGTERM: 'terminate',
            signal.SIGHUP: 'terminate',
            signal.SIGUSR1: 'terminate'}

        _gid = grp.getgrnam('nogroup').gr_gid
        context.gid = _gid
        context.files_preserve = [self.handler.stream]
        return context

    def daemon_main(self):
        # Set the start time of the Application
        self.log.info('%s is Entering Daemon Mode' % info.__appname__)
        try:
            # Run the PsycoRAX Application
            self.psyco = becrazy.Crazyness(m_args=self.p_args,
                                           output=self.log)
            self.system = True
            me_sleep = self.p_args['time']
            interval = int(me_sleep * .25)
            if interval < 1:
                interval = 1
            while self.system:
                if me_sleep < 1:
                    sleeper = 1 * 60 * 60
                else:
                    sleeper = random.randrange(1, (me_sleep * 60), interval)
                self.log.info('NOTICE:\tNext Attack in "%s" Seconds' % sleeper)
                time.sleep(sleeper)
                self.psyco.authenticate()
                self.psyco.crazy_man()

        except Exception, exp:
            self.log.critical(traceback.format_exc())
            self.log.critical(exp)


class DaemonINIT(object):
    def __init__(self, p_args, output, handler):
        # Bless the daemon dispatch class
        self.d_m = DaemonDispatch(p_args=p_args,
                                  output=output,
                                  handler=handler)
        self.log = output
        self.p_args = p_args
        self.pid_file = self.d_m.pid_file()
        self.status = self.daemon_status()

    def is_pidfile_stale(self, pid):
        """
        Determine whether a PID file is stale.
        Return 'True' if the contents of the PID file are
        valid but do not match the PID of a currently-running process;
        otherwise return 'False'.
        """
        # Method has been inspired fromthe PEP-3143 v1.6 Daemon Library.
        if os.path.isfile(pid):
            with open(pid, 'r') as pid_file_loc:
                proc_id = pid_file_loc.read()
            if proc_id:
                try:
                    os.kill(int(proc_id), signal.SIG_DFL)
                except OSError, exc:
                    if exc.errno == errno.ESRCH:
                        # The specified PID does not exist
                        try:
                            os.remove(pid)
                            print('Found a stale PID file, and I killed it.')
                        except Exception:
                            msg = ('You have a stale PID and I cant break it. '
                                   'So I have quit.  Start Trouble Shooting.'
                                   'The PID file is %s' % pid)
                            self.log.critical(traceback.format_exc())
                            sys.exit(msg)
                except Exception, exp:
                    self.log.critical(traceback.format_exc())
                    sys.exit(exp)
            else:
                os.remove(pid)
                print('Found a stale PID file, but it was empty.'
                      ' so I removed it.')

    def daemon_status(self):
        self.pid = None
        stop_arg_list = (self.p_args['stop'],
                          self.p_args['status'])
        msg_list = []
        pid = self.pid_file
        self.is_pidfile_stale(pid)
        if os.path.isfile(pid):
            with open(pid, 'rb') as f_pid:
                p_id = int(f_pid.read())
            self.pid = True
            msg = ('PID "%s" exists - Process ( %d )' % (pid, p_id))
            msg_list.append(msg)

        elif any(stop_arg_list):
            msg = ('No PID File has been found for "%s".'
                  ' %s is not running.' % (pid, info.__appname__))
            msg_list.append(msg)

        pid_msg = tuple(msg_list)
        return pid_msg

    def daemon_run(self):
        if not self.pid:
            # Start the Daemon with the new Context
            self.log.info('Starting up the listener Daemon')
            with self.d_m.context(self.pid_file):
                try:
                    self.d_m.daemon_main()
                except Exception, exp:
                    self.log.critical(traceback.format_exc())
                    self.log.critical(exp)
            print('\n'.join(self.daemon_status()))
        else:
            sys.exit('\n'.join(self.daemon_status()))

    def daemon_stop(self):
        # Get PID Name and Location
        pid = self.pid_file
        if os.path.isfile(pid):
            with open(pid, 'r') as pid_file_loc:
                proc_id = pid_file_loc.read()
            p_id = int(proc_id)
            self.log.info('Attempting Stop Action. PID File = %s - PID: %s'
                          % (pid, p_id))
            try:
                print('Stopping the %s Application' % info.__appname__)
                os.kill(p_id, signal.SIGKILL)
                time.sleep(1)
                print('Confirming the %s has been stopped' % info.__appname__)
                os.kill(p_id, signal.SIG_DFL)
            except OSError, exp:
                if exp.errno == errno.ESRCH:
                    print('Application has been stopped')
                    if os.path.isfile(pid):
                        print('Removing PID File %s' % pid)
                        os.remove(pid)
            except Exception, exp:
                self.log.critical(exp)
                self.log.critical(traceback.format_exc())
                sys.exit('Something bad happened, begin the '
                         'troubleshooting process.')
            except Exception:
                self.log.critical(traceback.format_exc())
        else:
            print('\n'.join(self.daemon_status()))


def logger_setup(log_level='info'):
    """
    Setup logging for your application
    """
    logger = logging.getLogger("%s Logging" % info.__appname__)

    # Log Level Arguments
    if log_level.upper() == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif log_level.upper() == 'INFO':
        logger.setLevel(logging.INFO)
    elif log_level.upper() == 'WARN':
        logger.setLevel(logging.WARN)
    elif log_level.upper() == 'ERROR':
        logger.setLevel(logging.ERROR)
    else:
        raise NoLogLevelSet('I died because you did not set the log level in'
                            ' your arguments. Heres what was set %s'
                            % log_level)

    # Set Formatting
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s"
                                  " - %(message)s")

    # Create the Log File
    # ==========================================================================
    # IF "/var/log/" does not exist, or you dont have write permissions to
    # "/var/log/" the log file will be in your working directory
    # Check for ROOT user if not log to working directory
    filename = '%s_daemonizer.log' % info.__appname__
    if os.path.isfile(filename):
        logfile = filename
    else:
        user = os.getuid()
        logname = ('%s' % filename)
        if not user == 0:
            logfile = logname
        else:
            if os.path.isdir('/var/log'):
                log_loc = '/var/log'
                logfile = '%s/%s' % (log_loc, logname)
            else:
                try:
                    os.mkdir('%s' % log_loc)
                    logfile = '%s/%s' % (log_loc, logname)
                except Exception:
                    logfile = '%s' % logname

    # Building Handeler
    handler = logging.FileHandler(logfile)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info('Logger Online')
    return logger, handler


def daemon_args(p_args):
    """
    Loads the arguments required to leverage the Daemon

    Arguments to run the daemon need to look something like this :

    p_args = {'start': None,
              'stop': None,
              'status': None,
              'restart': None}

    Notes for "p_args" :
    * "start, stop, status, restart" uses True, False, or None for its values.
    * "debug, info, warn, error" are the Valid log levels are.
    * "debug_mode" sets the daemon into debug mode which uses stdout / stderror.
    * "debug_mode" SHOULD NOT BE USED FOR NORMAL OPERATION! and can cause
      "error 5" over time
    """
    logger, handler = logger_setup(log_level=p_args['log_level'])

    # Bless the Daemon Setup / INIT class
    d_i = DaemonINIT(p_args=p_args,
                     output=logger,
                     handler=handler)

    if p_args['start']:
        logger.info('starting %s' % info.__appname__)
        d_i.daemon_run()

    elif p_args['stop']:
        logger.info('stopping %s' % info.__appname__)
        d_i.daemon_stop()

    elif p_args['status']:
        pid = d_i.daemon_status()
        print('%s ==> %s' % (info.__appname__, pid[0]))

    elif p_args['restart']:
        logger.info('%s is Restarting' % info.__appname__)
        print('%s is Restarting' % info.__appname__)

        # Check the status
        d_i.daemon_status()

        # Stop Daemon
        d_i.daemon_stop()
        time.sleep(2)

        # ReBless the class to start the app post stop
        d_r = DaemonINIT(p_args=p_args,
                         output=logger,
                         handler=handler)
        d_r.daemon_run()
