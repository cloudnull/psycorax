#!/usr/bin/env python
from __future__ import print_function
import sys

import traceback
from multiprocessing import freeze_support

# Local Modules
from psycorax import arguments
from psycorax import daemonizer, logger


def run_mon_psycorax():
    """
    Basic Method for starting the application from the launcher
    """
    # In place for OS's that do not support os.fork
    freeze_support()

    # Parse CLI Args
    p_args = arguments.args_and_values()

    # Sets an output style. Allows for Logging.
    output = logger.log_app(args=p_args)
    log = output[0]
    # Check to see if this application will be run as a Daemon
    try:
        daemonizer.daemon_args(p_args=p_args, output=output)
    except KeyboardInterrupt:
        sys.exit('AHH FAIL! You Killed me!')
    except Exception, exp:
        log.warn(exp)
        log.warn(traceback.format_exc())
        sys.exit('Major FAILURE...')


if __name__ == '__main__':
    # Run main if the application is executed from the CLI without the launcher
    run_mon_psycorax()
