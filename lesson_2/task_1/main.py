"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт,
осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt,
info_3.txt и формирующий новый «отчетный» файл в формате CSV.

Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов
с данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список. Должно
получиться четыре списка — например, os_prod_list, os_name_list,
os_code_list, os_type_list. В этой же функции создать главный список
для хранения данных отчета — например, main_data — и поместить в него
названия столбцов отчета в виде списка: «Изготовитель системы»,
«Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data
(также для каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл;

Пример того, что должно получиться:

Изготовитель системы,Название ОС,Код продукта,Тип системы

1,LENOVO,Windows 7,00971-OEM-1982661-00231,x64-based

2,ACER,Windows 10,00971-OEM-1982661-00231,x64-based

3,DELL,Windows 8.1,00971-OEM-1982661-00231,x86-based

Обязательно проверьте, что у вас получается примерно то же самое.

ПРОШУ ВАС НЕ УДАЛЯТЬ СЛУЖЕБНЫЕ ФАЙЛЫ TXT И ИТОГОВЫЙ ФАЙЛ CSV!!!
"""


import csv, chardet, re


def get_data(*args):
    main_data = []
    os_vendor_list = []
    os_name_list = []
    sys_code_list = []
    sys_type_list = []
    header_list = []

    def add_to_tmp_lst(search_list):
        if search_list:
            tmp_list.append(search_list)

    for element in args:
        with open(element, 'rb') as file:
            read_file = file.read()
            determine_enc = chardet.detect(read_file)
            encoding = determine_enc['encoding']

        if not encoding == 'utf-8':
            file_data = read_file.decode(encoding).encode('utf-8').decode('utf-8')
            with open(element, 'w', encoding='utf-8') as file:
                file.write(file_data)

        with open(element, encoding='utf-8') as file:
            file_read = file.read()
            tmp_list = []
            add_to_tmp_lst(re.findall(r'(Изготовитель системы.*)', file_read))
            add_to_tmp_lst(re.findall(r'(Название ОС.*)', file_read))
            add_to_tmp_lst(re.findall(r'(Код продукта.*)', file_read))
            add_to_tmp_lst(re.findall(r'(Тип системы.*)', file_read))
            for lst in tmp_list:
                separator = re.search(r':', lst[0]).end()
                header = lst[0][:separator - 1]
                if header and header not in header_list:
                    header_list.append(header)
                data = lst[0][separator + 1:]
                data = ' '.join(data.split())
                if 'Изготовитель системы' in lst[0]:
                    os_vendor_list.append(data)
                elif 'Название ОС' in lst[0]:
                    os_name_list.append(data)
                elif 'Код продукта' in lst[0]:
                    sys_code_list.append(data)
                else:
                    sys_type_list.append(data)
    main_data.append(header_list)
    for i in range(0, len(os_name_list)):
        tmp = []
        tmp.append(i + 1)
        tmp.append(os_vendor_list[i])
        tmp.append(os_name_list[i])
        tmp.append(sys_code_list[i])
        tmp.append(sys_type_list[i])
        main_data.append(tmp)
    return main_data


def write_to_csv(filename):

    data = get_data('info_1.txt', 'info_2.txt', 'info_3.txt')
    with open(filename, 'w') as csv_file:
        write_to_file = csv.writer(csv_file)
        for row in data:
            write_to_file.writerow(row)


write_to_csv('data.csv')

with open('data.csv') as file:
    print(file.read())