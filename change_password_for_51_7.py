import requests
import csv
import urllib.parse
import urllib3
import logging

# Отключение предупреждения InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://arh.ertelecom.ru/system-api/EditCamera"
log = "grechushnikov.ir"
pas = "password"  # Пароль для аутентификации

headers = {'Content-Type': 'application/x-www-form-urlencoded'}

# Настройка логирования
logging.basicConfig(filename='edit_camera_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

with open('ID_cam_rf_51_7.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter=';')  # Указываем ; как разделитель
    header = next(reader, None)  # Получаем первую строку (заголовки столбцов) или None, если файл пуст
    if header is not None:
        for row in reader:
            if len(row) >= 3:  # Проверка, что в строке достаточно элементов
                IP = row[0].strip()  # Получаем IP из первого столбца
                ID = row[1].strip()  # Получаем ID из второго столбца
                password = row[2].strip()  # Получаем пароль из третьего столбца
                try:
                    body = {"AdminLogin": log, "AdminPassword": pas, "ID": ID, "Login": "admin", "Password": password}
                    encoded_body = urllib.parse.urlencode(body)

                    # Вывод информации о запросе перед отправкой
                    print(f'Sending request to URL: {url}')
                    print(f'Headers: {headers}')
                    print(f'Body: {encoded_body}')

                    r = requests.request("POST", url, data=encoded_body, headers=headers, verify=True)
                    response = r.json()

                    if response['success']:
                        logging.info('EditCamera request for IP %s was successful. Response:', IP, response)

                except Exception as e:
                    logging.error('Cannot edit camera with IP %s. Error: %s', IP, str(e))
            else:
                logging.error('Invalid row format in CSV file: %s', row)
    else:
        logging.error('CSV file is empty')
