import requests
import csv

# Удаление лишних знаков ";" из csv файла
input_file = 'setkeys.csv'
output_file = 'setkeys_cleaned.csv'

with open(input_file, 'r') as file:
    reader = csv.reader(file, delimiter=';')
    rows = []
    for row in reader:
        cleaned_row = [cell.strip(';') for cell in row]
        rows.append(cleaned_row)

with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(rows)

# Отправка POST запросов и логирование результатов
url = "https://proptech.ru:8080/intercom?action=set_keys_mode&key={}&token2=token2&ip=127.0.0.1&srv=support"

with open(output_file, 'r') as file:
    reader = csv.reader(file)
    with open('setkeys_logs.txt', 'w') as log_file:
        for row in reader:
            key = row[0]
            response = requests.post(url.format(key))
            log_file.write("Response for key {}: {}\n".format(key, response.text))
            print("Response for key {}: {}".format(key, response.text))

print("Логирование запросов завершено. Результаты записаны в файл setkeys_logs.txt")
