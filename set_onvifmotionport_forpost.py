import requests
import json
import csv

#url = "https://vs.domru.ru/system-api/EditCamera"
url = "https://vs-spb.domru.ru/system-api/EditCamera"
log = "grechushnikov.ir"
#pas = "password"
pas = "password"

with open('ID_cam_spb.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file, delimiter=';')
    results = []
    for row in reader:
        if 'ID' in row and 'OnvifMotionPort' in row:
            ID = row['ID']
            OnvifMotionPort = row['OnvifMotionPort']

            payload = {
                "AdminLogin": log,
                "AdminPassword": pas,
                "ID": ID,
                "OnvifMotionPort": OnvifMotionPort
            }

            # Отправка POST-запроса с указанными параметрами
            response = requests.post(url, data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})

            # Обработка ответа
            data = json.loads(response.text)

            if 'ID' in data:
                edited_ID = data['ID']
                results.append([edited_ID])
                print("ID:", edited_ID)
            else:
                print("Ошибка при обновлении камеры с ID:", ID)
        else:
            print("Ошибка чтения файла quota.csv: отсутствует столбец 'ID' или 'OnvifMotionPort'")

with open('results_spb.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['ID'])
    writer.writerows(results)
