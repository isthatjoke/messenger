"""
Задание 4.

Преобразовать слова «разработка», «администрирование», «protocol»,
«standard» из строкового представления в байтовое и выполнить
обратное преобразование (используя методы encode и decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
"""


def arr_encode(arr):
    for i in range(len(arr)):
        arr[i] = arr[i].encode('utf-8')
    print(arr)
    return words_list


def arr_decode(arr):
    for i in range(len(arr)):
        arr[i] = arr[i].decode('utf-8')
    print(arr)
    return words_list


words_list = [
    'разработка',
    'администрирование',
    'protocol',
    'standard',
]

arr_encode(words_list)
arr_decode(words_list)

