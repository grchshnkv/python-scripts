import requests
import csv
import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor

# Настройка логирования
logging.basicConfig(filename='script_log_service_code_from_bd.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ping(ip):
    try:
        subprocess.check_output(['ping', '-c', '1', ip])
        return True
    except subprocess.CalledProcessError:
        return False

def check_system_info(ip, username, password):
    url = f"http://{ip}/cgi-bin/systeminfo_cgi?action=get"
    try:
        response = requests.get(url, auth=(username, password), timeout=10)  # Установка таймаута в 10 секунд
        if response.status_code == 200:
            logging.info(f"Код ответа 200 получен от {url}")
        else:
            logging.warning(f"Код ответа {response.status_code} получен от {url}")
    except requests.exceptions.RequestException as e:
        logging.warning(f"Ошибка при подключении к IP: {ip} - {e}")

def delete_service_codes(ip, username, password):
    url = f"http://{ip}/cgi-bin/srvcodes_cgi?action=set&RfidScanActive=close&NetInfoActive=close&NetResetActive=close&AdminResetActive=close&FullResetActive=close"
    response = requests.get(url, auth=(username, password))
    if response.status_code == 200:
        logging.info(f"Код добавления ключа успешно удален")
    else:
        logging.warning(f"Не удалить код добавления ключа")

def process_ip(row):
    ip = row['ip_address']
    password = row['password']
    username = 'admin'  # Предполагается, что имя пользователя всегда 'admin'

    logging.info(f"Начало проверки IP: {ip}")
    try:
        if not ping(ip):
            logging.warning(f"Не удалось подключиться к IP: {ip}. Переход к следующему IP.")
            return
        check_system_info(ip, username, password)
        delete_service_codes(ip, username, password)

        logging.info(f"Завершение проверки IP: {ip}")
    except requests.exceptions.RequestException as e:
        logging.warning(f"Ошибка при подключении к IP: {ip} - {e}")

# Чтение файла с учетными данными
with open('service_code_from_bd.csv', 'r') as file:
    reader = csv.DictReader(file, delimiter=';')
    with ThreadPoolExecutor() as executor:
        executor.map(process_ip, reader)
