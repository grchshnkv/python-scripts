import requests
import json
import csv
import urllib.parse
import urllib3
import logging

# Отключение предупреждения InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://vs-mmk.domru.ru/system-api/FindCameras"
log = "grechushnikov.ir"
pas = "password"

headers = {'Content-Type': 'application/x-www-form-urlencoded'}

# Настройка логирования
logging.basicConfig(filename='ip_51_7.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

with open('ip_51_7.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)  # Пропуск первой строки с заголовками столбцов
    with open('ID_cam_mmk_51_7.csv', 'w', newline='') as id_file:
        writer = csv.writer(id_file)
        for row in reader:
            IP = row[0].strip()
            try:
                body = {"AdminLogin": log, "AdminPassword": pas, "IP": IP}
                encoded_body = urllib.parse.urlencode(body)

                # Вывод информации о запросе перед отправкой
                print(f'Sending request to URL: {url}')
                print(f'Headers: {headers}')
                print(f'Body: {encoded_body}')

                r = requests.request("POST", url, data=encoded_body, headers=headers, verify=True)
                text = json.loads(r.text)
                cam_found = False  # Флаг для отслеживания, была ли найдена камера
                for cam in text:
                    if 'ID' in cam:
                        cam_id = cam['ID']
                        writer.writerow([IP, cam_id])
                        cam_found = True  # Установить флаг, что камера была найдена
                if not cam_found:
                    logging.info('Not ID Cam: %s', IP)
                    writer.writerow(['Not ID', IP])

                # Добавление информации о запросе в файл логов
                logging.info('Request for IP %s was successful', IP)

            except Exception as e:
                logging.error('Cannot find camera %s. Error: %s', IP, str(e))

