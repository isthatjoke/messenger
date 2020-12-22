"""
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
"""

from ipaddress import ip_address
import socket, sys
from task_1 import host_ping


def host_range_ping():
    tested_ips = []
    try:
        ip = input('type ip address or host name: ')
        inc_numb = int(input('type increase number: '))
    except ValueError:
        print('increase number must be integer')
        return

    if not check_ip(ip):
        ip = socket.gethostbyname(ip)
        sliced_ip = ip.split('.')

    else:
        sliced_ip = ip.split('.')

    if len(sliced_ip) == 4:
        while inc_numb != 0:
            ip = '.'.join(sliced_ip)
            correct_ip = ip_address(ip)
            tested_ips.append(str(correct_ip))
            sliced_ip[-1] = str(int(sliced_ip[-1]) + 1)

            if int(sliced_ip[-1]) > 254:
                print('too much for ip octet')
                break
            inc_numb -= 1
    else:
        print('ip typed incorrectly')
        return

    return host_ping(tested_ips)


def check_ip(ip):
    for el in ip:
        if el.isdigit() or el == '.':
            pass
        else:
            return False
    return True


if __name__ == '__main__':

    host_range_ping()

