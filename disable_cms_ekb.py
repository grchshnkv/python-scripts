import csv
import requests
import logging

# Настройка логирования
logging.basicConfig(filename='ip_ekb.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Путь к файлу
csv_file = 'ip_ekb.csv'

# Проход по каждой строке файла
with open(csv_file, 'r') as file:
    csv_reader = csv.DictReader(file, delimiter=';')
    for row in csv_reader:
        ip = row['ip']
        password = row['password']

        # Авторизация на IP-адресе с паролем из столбца 'password'
        session = requests.Session()
        login_response = session.get(f'http://{ip}', auth=('admin', password))

        if login_response.status_code == 200:
            logging.info(f'Авторизация на {ip} прошла успешно')

            # Выполнение запроса для каждой квартиры с авторизацией
            for apartment_number in range(1, 10000):
                response = session.get(
                    f'http://{ip}/cgi-bin/apartment_cgi?action=set&Number={apartment_number}&BlockCMS=on',
                    auth=('admin', password))

                if response.status_code == 200:
                    logging.info(f'Успешно выполнен запрос для квартиры {apartment_number}')
                else:
                    logging.error(f'Ошибка при выполнении запроса для квартиры {apartment_number}')
        else:
            logging.error(f'Ошибка авторизации на {ip}')
