import os, sys
from logging import Formatter, getLogger, DEBUG, ERROR, FileHandler, StreamHandler, WARNING
from additionals.settings import LOGGING_LEVEL, ENCODING

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, '..', 'log_files/', 'app.client.log')

# logger app init
logger = getLogger('app.client')
logger.setLevel(LOGGING_LEVEL)

# formatter
formatter = Formatter('%(asctime)-27s  %(levelname)-12s  %(message)s')

# handlers
file_logger_handler = FileHandler(PATH, encoding=ENCODING)
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
