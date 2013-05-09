#!/usr/bin/env python
from __future__ import print_function
import sys

import traceback
from multiprocessing import freeze_support
import shelve
import prettytable

# Local Modules
from psycorax import arguments
from psycorax import daemonizer


def run_psycorax():
    """
    Basic Method for starting the application from the launcher
    """
    # In place for OS's that do not support os.fork
    freeze_support()

    # Parse CLI Args
    p_args = arguments.args_and_values()

    # Check to see if this application will be run as a Daemon
    try:
        if p_args['report']:
            _db = shelve.open(p_args['db_file'], flag='r')
            if p_args['date']:
                date = p_args['date']
                if date in _db:
                    print('REPORT FOR "%s"\t:' % date)
                    table = prettytable.PrettyTable(_db[date][0].keys())
                    for inst in _db[date]:
                        table.add_row(inst.values())
                    print(table)
                else:
                    print('%s not found in DB' % date)
            else:
                for day in _db.keys():
                    print('REPORT FOR "%s"\t:' % day)
                    table = prettytable.PrettyTable(_db[day][0].keys())
                    for inst in _db[day]:
                        table.add_row(inst.values())
                    print(table)
            _db.close()
            sys.exit()
        daemonizer.daemon_args(p_args=p_args)
    except KeyboardInterrupt:
        sys.exit('AHH FAIL! You Killed me!')
    except Exception:
        print(traceback.format_exc())
        sys.exit('Major FAILURE...')


if __name__ == '__main__':
    # Run main if the application is executed from the CLI without the launcher
    run_psycorax()
