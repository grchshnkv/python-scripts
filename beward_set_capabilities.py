import requests
import subprocess
import json
import logging
from datetime import datetime

# Ping
def ping(ip):
    try:
        subprocess.check_output(['ping', '-c', '1', ip])
        return True
    except subprocess.CalledProcessError:
        return False

# Отправка update
def send_update_request(ip, username, password, capabilities):
    url = f"http://{ip}/cgi-bin/pwdgrp_cgi?action=update&username=user1&capabilities=1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,1,0,0,0,0,0"
    response = requests.get(url, auth=(username, password))
    return response.text

# Чтение файла с IP-адресами
with open('ip_addresses.txt', 'r') as ip_file:
    ip_addresses = [line.strip() for line in ip_file]

# Чтение файла с данными для авторизации
with open('accounts.txt', 'r') as accounts_file:
    accounts = json.load(accounts_file)
    for account in accounts:
        username = account["admin"]
        password = account["password"]
        capabilities = "1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,1,0,0,0,0,0"

        # Подключение к каждому домофону
        for ip in ip_addresses:
            if ping(ip):
                logging.info(f"Успешное подключение к домофону с IP-адресом {ip}")
                response = send_update_request(ip, username, password, capabilities)
                logging.info(f"Ответ на запрос UPDATE для домофона с IP-адресом {ip}: {response}")
            else:
                logging.info(f"Не удалось подключиться к домофону с IP-адресом {ip}")