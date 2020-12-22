import os, sys
from logging import getLogger, Formatter, handlers, ERROR, DEBUG, StreamHandler, WARNING
from additionals.settings import LOGGING_LEVEL, ENCODING

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, '..', 'log_files/', 'app.server.log')

# logger app init
logger = getLogger('app.server')
logger.setLevel(LOGGING_LEVEL)

# formatter
formatter = Formatter('%(asctime)-27s %(levelname)-12s %(filename)-20s %(lineno)-5s %(message)s')

# handlers
file_logger_handler = handlers.TimedRotatingFileHandler(PATH, encoding=ENCODING, interval=1, when='midnight')
file_logger_handler.setLevel(DEBUG)
file_logger_handler.setFormatter(formatter)

console_handler = StreamHandler()
console_handler.setLevel(WARNING)
console_handler.setFormatter(formatter)

# add handlers
logger.addHandler(file_logger_handler)
logger.addHandler(console_handler)


if __name__ == '__main__':

    logger.info('app started')
    logger.warning('attention!')
    logger.critical('critical error, shutdown the app')




