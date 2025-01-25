import requests
import subprocess
import csv
import logging
import datetime

# Установка настроек логирования
logging.basicConfig(filename='log_reboot.txt', level=logging.INFO)

# Ping
def ping(ip):
    try:
        subprocess.check_output(['ping', '-c', '1', ip])
        return True
    except subprocess.CalledProcessError:
        return False

# Отправка update
def send_update_request(ip, password):
    url = f"http://{ip}/cgi-bin/restart.cgi?user=admin&pwd={password}"
    try:
        response = requests.get(url, auth=("admin", password))
        response.raise_for_status()  # Проверка на ошибки HTTP
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при отправке запроса UPDATE для домофона с IP-адресом {ip}: {e}")
        return None

# Путь к файлу CSV
csv_file = 'credentials_reboot.csv'

# Чтение CSV файла
ip_addresses = []
passwords = []

with open(csv_file, 'r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter=';')  # Использование ; в качестве разделителя
    next(reader)  # Пропуск первой строки с названиями столбцов
    for row in reader:
        if len(row) >= 2:  # Проверка, что в строке есть два значения
            ip_addresses.append(row[0])
            passwords.append(row[1].strip())
        else:
            logging.warning(f"Некорректная строка в файле CSV: {row}")

# Подключение к каждому домофону
for ip, password in zip(ip_addresses, passwords):
    if ping(ip):
        logging.info(f"Успешное подключение к домофону с IP-адресом {ip}")
        response = send_update_request(ip, password)
        if response is not None:
            logging.info(f"Время отправки запроса UPDATE для домофона с IP-адресом {ip}: {datetime.datetime.now()}")
            logging.info(f"Ответ на запрос UPDATE для домофона с IP-адресом {ip}: {response}")
    else:
        logging.info(f"Не удалось подключиться к домофону с IP-адресом {ip}")
