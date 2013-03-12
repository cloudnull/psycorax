import traceback
import os
import sys
import time
import tempfile
import random

# For Daemon
import daemon
from daemon import pidfile
import signal
import grp
import errno

# Local Modules
from psycorax import info
from psycorax import becrazy


class DaemonDispatch(object):
    def __init__(self, p_args, output):
        """
        The Daemon Processes the input from the application.
        """
        self.p_args = p_args
        self.handler = output[1]
        self.log = output[0]
        self.log.info('Daemon Dispatch envoked')
        self.psyco = becrazy.Crazyness(m_args=self.p_args,
                                       output=self.log)

    def pid_file(self):
        """
        Sets up the Pid files Location
        """
        # Determine the Pid location 
        name = info.__appname__
        if os.path.isdir('/var/run/'):
            self.pid1 = '/var/run/%s.pid' % name
        else:
            pid_loc = (tempfile.gettempdir(), os.sep, name)
            self.pid1 = '%s%s%s.pid' % pid_loc
        self.log.info('PID File is : %s' % (self.pid1))
        self.p_args['pid1'] = self.pid1
        print(self.pid1)
        return self.pid1

    def gracful_exit(self, signum=None, frame=None):
        """
        Exit the system
        """
        self.log.info('Exiting The Daemon Process for %s. '
                      'Signal recieved was %s on %s'
                      % (info.__appname__, signum, frame))
        self.system = False

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
        if self.p_args['os_verbose']:
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
            signal.SIGHUP: self.gracful_exit,
            signal.SIGUSR1: self.gracful_exit}

        ameba_gid = grp.getgrnam('nogroup').gr_gid
        context.gid = ameba_gid
        context.files_preserve = [self.handler.stream]
        return context

    def daemon_main(self):
        # Set the start time of the Application
        self.log.info('%s is Entering Daemon Mode' % info.__appname__)
        try:
            if self.p_args['time'] <= 0:
                self.p_args['time'] = 1
            sleepy = random.randrange(0, self.p_args['time']) + 1
            sleeper = sleepy * 60
            # Run the PsycoRAX Application
            self.psyco = becrazy.Crazyness(m_args=self.p_args,
                                           output=self.log)
            self.system = True
            while self.system:
                self.psyco.authenticate()
                self.psyco.crazy_man()
                time.sleep(sleeper)
        except Exception, exp:
            self.log.critical(traceback.format_exc())
            self.log.critical(exp)


class DaemonINIT(object):
    def __init__(self, p_args, output):
        # Bless the daemon dispatch class
        self.d_m = DaemonDispatch(p_args=p_args,
                                  output=output)
        self.log = output[0]
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
        start_arg_list = (self.p_args['stop'],
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

        elif any(start_arg_list):
            msg = ('No PID File has been found for "%s". '
                  '%s is not running.' % (pid, info.__appname__))
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
        else:
            sys.exit('\n'.join(self.status))

    def daemon_stop(self):
        # Get PID Name and Location
        pid = self.pid_file
        if os.path.isfile(pid):
            with open(pid, 'r') as f_pid:
                p_id = f_pid.read()
            p_id = int(p_id)
            try:
                self.d_m.gracful_exit()
                print('Stopping the %s Application' % info.__appname__)
                os.kill(p_id, signal.SIGTERM)
                if os.path.isfile(pid):
                    os.remove(pid)
            except OSError, exp:
                self.log.critical(exp)
                self.log.critical(traceback.format_exc())
                sys.exit('Something bad happened, begin the '
                         'troubleshooting process.')
            except Exception:
                self.log.critical(traceback.format_exc())
        print('\n'.join(self.status))


def daemon_args(p_args, output):
    """
    Loads the arguments required to leverage the Ameba Server
    """

    # Bless the Daemon Setup / INIT class
    d_i = DaemonINIT(p_args=p_args, output=output)

    if p_args['start']:
        d_i.daemon_run()

    elif p_args['stop']:
        d_i.daemon_stop()

    elif p_args['status']:
        pid = d_i.daemon_status()
        output[0].info(pid)

    elif p_args['restart']:
        output[0].info('%s is Restarting' % info.__appname__)

        # Check the status
        d_i.daemon_status()

        # Stop Ameba Server
        d_i.daemon_stop()
        time.sleep(2)

        # ReBless the class to start the app post stop
        d_r = DaemonINIT(p_args=p_args, output=output)
        d_r.daemon_run()
