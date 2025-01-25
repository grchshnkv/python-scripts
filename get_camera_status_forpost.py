import sys
import time
import requests
import json
import csv
import subprocess
import urllib.parse
import urllib3

# Отключение предупреждения InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url0 = "https://vs.domru.ru/system-api/FindCameras"
url1 = "https://vs.domru.ru/system-api/GetCameraState"
log = "grechushnikov.ir"
pas = "password"

u = 0
s = 0
rw = open('onvif_state.csv', 'a', newline='')
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

with open('ip_addresses.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)  # Пропуск первой строки с названиями столбцов
    writer = csv.writer(rw)
    for row in reader:
        IP = row[0].strip()
        s = s + 1
        try:
            # Ping
            ping_process = subprocess.Popen(["ping", "-c", "1", IP], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ping_output, ping_error = ping_process.communicate()
            if ping_process.returncode == 0:
                body0 = {"AdminLogin": log, "AdminPassword": pas, "IP": IP}
                encoded_body0 = urllib.parse.urlencode(body0)
                r0 = requests.request("POST", url0, data=encoded_body0, headers=headers, verify=True)
                text0 = json.loads(r0.text)
                cam_found = False  # Флаг для отслеживания, была ли найдена камера
                for a in text0:
                    if 'ID' in a:
                        print(a)
                        cam = a
                        cam_id = cam['ID']
                        Quota = cam['Quota']
                        # Преобразование значения Quota из секунд в сутки
                        Quota = int(Quota / 60 / 60 / 24)
                        u = u + 1
                        try:
                            body1 = {"AdminLogin": log, "AdminPassword": pas, "ID": cam_id}
                            #encoded_body1 = urllib.parse.urlencode(body1)
                            r1 = requests.request("POST", url1, data=body1, headers=headers, verify=True)
                            text1 = json.loads(r1.text)
                            State = text1['State']
                            Onvif_State = text1['OnvifState']
                            print(IP, cam_id, State, Onvif_State, Quota)
                            rw.write(IP + ', ' + str(cam_id) + ', ' + str(State) + ', ' + str(Onvif_State) + ', ' + str(Quota) + '\n')
                            cam_found = True  # Установить флаг, что камера была найдена
                            break  # Прервать цикл, чтобы не обрабатывать остальные записи для этой камеры
                        except:
                            print('Status Error', IP)
                            rw.write(IP + ', Status Error\n')
                if not cam_found:
                    print('Not ID Cam:', IP)
                    rw.write(IP + ', Not ID Cam\n')
            else:
                print('IP not available:', IP)
                rw.write(IP + ', IP not available\n')
                continue  # Пропустить присвоение cam_id = 0 для недоступных камер
        except:
            print('Cannot find camera', IP)
            rw.write(IP + ', Cannot find camera\n')
        if s != u and not cam_found:
            s = u
            cam_id = 0
            print(IP, cam_id)
            rw.write(IP + ', ' + str(cam_id) + '\n')
        time.sleep(0.1)

rw.close()