import sys, inspect, traceback
from logging import getLogger
from log.config import server_log_config, client_log_config

if 'server' in sys.argv[0]:
    logger = getLogger('app.server')
else:
    logger = getLogger('app.client')


def log(func):
    def save_to_log(self, *args, **kwargs):
        ordered_function = func(self, *args, **kwargs)

        logger.debug(f'the function "{func.__name__}" with params "{args}", "{kwargs}"'
                     f' has been ordered from module "{func.__module__}", called from "{inspect.stack()[1][3]}"'
                     f'', stacklevel=3)

        return ordered_function

    return save_to_log


class Log:

    def __init__(self):
        pass

    def __call__(self, func):

        def save_to_log(*args, **kwargs):
            ordered_function = func(*args, **kwargs)

            logger.debug(f'''(from class) the function "{''.join(inspect.stack()[1][4][0].split())}"''' 
                         f''' with params {args}, {kwargs}'''
                         f''' has been ordered from module {inspect.getmodule((inspect.stack()[1])[0])}, called from "{inspect.stack()[1][3]}"''',
                         stacklevel=2)

            return ordered_function

        return save_to_log
