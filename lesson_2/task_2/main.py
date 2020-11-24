"""
2. Задание на закрепление знаний по модулю json. Есть файл orders
в формате JSON с информацией о заказах. Написать скрипт, автоматизирующий
его заполнение данными.

Для этого:
Создать функцию write_order_to_json(), в которую передается
5 параметров — товар (item), количество (quantity), цена (price),
покупатель (buyer), дата (date). Функция должна предусматривать запись
данных в виде словаря в файл orders.json. При записи данных указать
величину отступа в 4 пробельных символа;
Проверить работу программы через вызов функции write_order_to_json()
с передачей в нее значений каждого параметра.

ПРОШУ ВАС НЕ УДАЛЯТЬ ИСХОДНЫЙ JSON-ФАЙЛ
ПРИМЕР ТОГО, ЧТО ДОЛЖНО ПОЛУЧИТЬСЯ

{
    "orders": [
        {
            "item": "printer",
            "quantity": "10",
            "price": "6700",
            "buyer": "Ivanov I.I.",
            "date": "24.09.2017"
        },
        {
            "item": "scaner",
            "quantity": "20",
            "price": "10000",
            "buyer": "Petrov P.P.",
            "date": "11.01.2018"
        }
    ]
}

вам нужно подгрузить JSON-объект
и достучаться до списка, который и нужно пополнять
а потом сохранять все в файл
"""

import json


def make_file(file):
    with open(file, 'w', encoding='utf-8') as new_file:
        dict_to_file = {'orders': []}
        json.dump(dict_to_file, new_file, indent=4)


def write_order_to_json(item, quantity, price, buyer, date):
    dict_to_upload = {
        'item': item,
        'quantity': quantity,
        'price': price,
        'buyer': buyer,
        'date': date,
    }
    with open('orders_new.json') as js_file:
        opened_file = json.load(js_file)
        orders = opened_file['orders']

    orders.append(dict_to_upload)
    opened_file['orders'] = orders

    with open('orders_new.json', 'w', encoding='utf-8') as js_file:
        json.dump(opened_file, js_file, indent=4)


# make_file('orders_new.json')
# write_order_to_json(item='phone', quantity='3', price='1000', buyer='timur z.', date='23.11.2020')
write_order_to_json(item='ipad', quantity='15', price='1200', buyer='Ivan G.', date='01.06.2021')



