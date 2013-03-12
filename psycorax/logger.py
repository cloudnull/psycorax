import logging
import os


def log_app(args):
    """
    Default Logging information and Handler
    """
    logger = logging.getLogger("PsycoRax Logging")
    if args['log_level'] == 'debug':
        logger.setLevel(logging.DEBUG)
    elif args['log_level'] == 'info':
        logger.setLevel(logging.INFO)
    elif args['log_level'] == 'warn':
        logger.setLevel(logging.WARN)
    elif args['log_level'] == 'error':
        logger.setLevel(logging.ERROR)

    formatter = logging.Formatter("%(asctime)s - %(name)s -"
                                  " %(levelname)s - %(message)s")

    # Create the Log File
    logfile = 'ameba-monitoring.log'
    if os.path.isdir('/var/log/'):
        if not os.path.isdir('/var/log/psycorax'):
            try:
                os.mkdir('/var/log/psycorax')
                logfile = '/var/log/psycorax/psycorax-server.log'
            except Exception:
                try:
                    logfile = '/var/log/psycorax-server.log'
                    pass
                except Exception:
                    logfile = 'psycorax-server.log'
        else:
            logfile = '/var/log/psycorax/psycorax-server.log'

    # Building Handeler
    handler = logging.FileHandler(logfile)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info('Logger Online')
    log_data = (logger, handler)

    return log_data
