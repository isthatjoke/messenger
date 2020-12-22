"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
"""

from subprocess import Popen, PIPE
from ipaddress import ip_address
import socket


def host_ping(ip_lst):
    checked_ip = {'available ip': '', 'unavailable ip': ''}
    for ip in ip_lst:
        try:
            ip = socket.gethostbyname(ip)
        except socket.gaierror:
            print(f'typed ip {ip} is not correct')
            continue
        correct_ip = ip_address(ip)
        # try_to_check = Popen(f'ping {correct_ip} -n 1', stdout=PIPE, shell=True) #win
        try_to_check = Popen(f'ping -c 1 {correct_ip}', stdout=PIPE, shell=True) #mac
        try_to_check.wait()

        if try_to_check.returncode == 0:
            checked_ip['available ip'] += f'{str(correct_ip)}\n'
            print(f'available {correct_ip}')
        else:
            checked_ip['unavailable ip'] += f'{str(correct_ip)}\n'
            print(f'unavailable {correct_ip}')

    return checked_ip


if __name__ == '__main__':
    host_ping(['youtube.com', '1.1.1.1', 'google.com', 'geekbrains.com', '192.168.31.1', '0.2.330.1'])

