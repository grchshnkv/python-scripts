import requests
import json
import csv

url = "https://vs.domru.ru/system-api/EditCamera"
log = "grechushnikov.ir"
pas = "password"

with open('quota.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file, delimiter=';')
    results = []
    for row in reader:
        if 'ID' in row and 'Quota' in row:
            ID = row['ID']
            Quota = row['Quota']

            payload = {
                "AdminLogin": log,
                "AdminPassword": pas,
                "ID": ID,
                "Quota": Quota
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
            print("Ошибка чтения файла quota.csv: отсутствует столбец 'ID' или 'Quota'")

with open('results.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['ID'])
    writer.writerows(results)
