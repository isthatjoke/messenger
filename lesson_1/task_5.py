"""
Задание 5.

Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.

Подсказки:
--- используйте модуль chardet, иначе задание не засчитается!!!
"""

import subprocess, chardet


def ping_and_decode(arr):
    ping_arr = subprocess.Popen(arr, stdout=subprocess.PIPE)
    for el in ping_arr.stdout:
        determine_encoding = chardet.detect(el)
        print(el.decode(determine_encoding['encoding']).encode('utf-8').decode('utf-8'))


arr_ydx = [
    'ping',
    'yandex.ru',
]

arr_ytb = [
    'ping',
    'youtube.com',
]

arr_gb = [
    'ping',
    'geekbrains.ru',
]

# ping_and_decode(arr_ydx)
# ping_and_decode(arr_ytb)
ping_and_decode(arr_gb)

