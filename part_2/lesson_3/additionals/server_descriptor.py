from log.config import server_log_config
from decos import Log
import logging, socket
from .check_ip import check_first_octet, check_two_three_octets, check_forth_octet, check_ip


logger = logging.getLogger('app.server')


@Log()
class PortVerifier:

    def __set__(self, instance, value):
        if value < 1024 or value > 65535:
            logger.error(f'invalid port number {value}')
            raise ValueError(f'port is out off range 1024 - 65535, u typed {value}')
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


@Log()
class HostVerifier:
    def __set__(self, instance, value):
        if not check_ip(value):
            try:
                ip = socket.gethostbyname(value)
                sliced_ip = ip.split('.')
            except ValueError:
                logger.error(f'ip address is incorrect {value}')

        else:
            sliced_ip = value.split('.')

        if len(sliced_ip) == 4:
            for el in range(0, 4):
                if el == 0 and check_first_octet(sliced_ip[el]) \
                        or 0 < el < 3 and check_two_three_octets(sliced_ip[el]) \
                        or el == 3 and check_forth_octet(sliced_ip[el]):
                    pass
                else:
                    logger.error(f'ip is incorrect {value}')
                    raise ValueError('ip is incorrect')
        else:
            logger.error(f'ip is incorrect {value}')
            raise ValueError('ip is incorrect')

        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name



