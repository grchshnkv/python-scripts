import requests
import json
import csv
import urllib.parse
import urllib3
import re
import datetime

# Отключение предупреждения InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url_find_cameras = "https://vs-spb.domru.ru/system-api/FindCameras"
url_find_accounts = "https://vs-spb.domru.ru/system-api/FindAccounts"
url_get_cameras = "https://vs-spb.domru.ru/system-api/GetCameras"
url_add_account = "https://vs-spb.domru.ru/system-api/AddAccount"
url_add_camera = "https://vs-spb.domru.ru/system-api/AddCamera"
log = "grechushnikov.ir"
pas = "pas"

headers = {'Content-Type': 'application/x-www-form-urlencoded'}

def log_message(message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{current_time}] {message}"
    with open("log.txt", "a") as log_file:
        log_file.write(log_entry + "\n")

def log_request(url, method, body):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{current_time}] {method} request to {url} with body: {body}"
    with open("log_spb_forpost.txt", "a") as log_file:
        log_file.write(log_entry + "\n")

with open('spb_deleted_forpost_test.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter=';')
    next(reader)  # Пропуск первой строки с названиями столбцов
    with open('ID_cam_spb_forpost.csv', 'w', newline='') as id_file:
        writer = csv.writer(id_file)
        for row in reader:
            name = row[0].strip()
            ip = row[1].strip()
            password = row[2].strip()  # Получение пароля из столбца "password"
            try:
                # Поиск камеры по IP
                find_body = {"AdminLogin": log, "AdminPassword": pas, "IP": ip}
                encoded_find_body = urllib.parse.urlencode(find_body)
                log_request(url_find_cameras, "POST", encoded_find_body)
                r_find = requests.request("POST", url_find_cameras, data=encoded_find_body, headers=headers, verify=True)
                find_text = json.loads(r_find.text)
                if len(find_text) > 0 and 'Name' in find_text[0] and 'AccountID' in find_text[0]:
                    camera_name = find_text[0]['Name']
                    account_id = find_text[0]['AccountID']
                    # Получение информации о камере
                    get_body = {"AdminLogin": log, "AdminPassword": pas, "AccountID": account_id}
                    encoded_get_body = urllib.parse.urlencode(get_body)
                    log_request(url_get_cameras, "POST", encoded_get_body)
                    r_get = requests.request("POST", url_get_cameras, data=encoded_get_body, headers=headers, verify=True)
                    get_text = json.loads(r_get.text)
                    groups = get_text[0]['Groups']
                    writer.writerow([name, ip, camera_name, groups])
                else:
                    # Поиск аккаунта по имени
                    find_account_body = {"AdminLogin": log, "AdminPassword": pas, "Name": name}
                    encoded_find_account_body = urllib.parse.urlencode(find_account_body)
                    log_request(url_find_accounts, "POST", encoded_find_account_body)
                    r_find_account = requests.request("POST", url_find_accounts, data=encoded_find_account_body, headers=headers, verify=True)
                    find_account_text = json.loads(r_find_account.text)
                    if len(find_account_text) > 0 and 'ID' in find_account_text[0]:
                        account_id = find_account_text[0]['ID']
                        # Добавление камеры
                        camera_body = {
                            "AdminLogin": log,
                            "AdminPassword": pas,
                            "Name": name,
                            "AccountID": account_id,
                            "MasterID": 1,
                            "Login": "user1",
                            "Password": password,
                            "IPOrDomain": ip,
                            "Port": 554,
                            "HTTPPort": 80,
                            "OnvifMotionPort": 80,
                            "IsSound": 1,
                            "Protocol": "rtsp",
                            "MJPEG": "/av0_0"
                        }
                        encoded_camera_body = urllib.parse.urlencode(camera_body)
                        log_request(url_add_camera, "POST", encoded_camera_body)
                        r_camera = requests.request("POST", url_add_camera, data=encoded_camera_body, headers=headers, verify=True)
                        camera_text = json.loads(r_camera.text)
                        camera_id = camera_text['ID']
                        writer.writerow([name, ip, camera_id])
                    else:
                        # Добавление аккаунта
                        account_name = name
                        account_body = {
                            "AdminLogin": log,
                            "AdminPassword": pas,
                            "Name": account_name,
                            "MaxCameraCount": 50,
                            "MaxLoginCount": 5,
                            "MaxCameraOnlineTranslationCount": 30,
                            "MaxCameraArchivalTranslationCount": 30,
                            "MaxCameraUserOnlineTranslationCount": 30,
                            "MaxCameraUserArchivalTranslationCount": 30
                        }
                        encoded_account_body = urllib.parse.urlencode(account_body)
                        log_request(url_add_account, "POST", encoded_account_body)
                        r_account = requests.request("POST", url_add_account, data=encoded_account_body, headers=headers, verify=True)
                        account_text = json.loads(r_account.text)
                        account_id = account_text['ID']
                        # Повторная проверка аккаунта по имени
                        find_account_body = {"AdminLogin": log, "AdminPassword": pas, "Name": account_name}
                        encoded_find_account_body = urllib.parse.urlencode(find_account_body)
                        log_request(url_find_accounts, "POST", encoded_find_account_body)
                        r_find_account = requests.request("POST", url_find_accounts, data=encoded_find_account_body, headers=headers, verify=True)
                        find_account_text = json.loads(r_find_account.text)
                        if len(find_account_text) > 0 and 'ID' in find_account_text[0]:
                            account_id = find_account_text[0]['ID']
                            # Добавление камеры с использованием ID аккаунта
                            camera_body = {
                                "AdminLogin": log,
                                "AdminPassword": pas,
                                "Name": name,
                                "AccountID": account_id,
                                "MasterID": 1,
                                "Login": "user1",
                                "Password": password,
                                "IPOrDomain": ip,
                                "Port": 554,
                                "HTTPPort": 80,
                                "OnvifMotionPort": 80,
                                "IsSound": 1,
                                "Protocol": "rtsp",
                                "MJPEG": "/av0_0"
                            }
                            encoded_camera_body = urllib.parse.urlencode(camera_body)
                            log_request(url_add_camera, "POST", encoded_camera_body)
                            r_camera = requests.request("POST", url_add_camera, data=encoded_camera_body, headers=headers, verify=True)
                            camera_text = json.loads(r_camera.text)
                            camera_id = camera_text['ID']
                            writer.writerow([name, ip, camera_id])
                        else:
                            log_message(f"Error: {name}, {ip}")
            except Exception as e:
                log_message(f"Error: {name}, {ip}, {str(e)}")
