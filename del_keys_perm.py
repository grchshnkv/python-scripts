import requests
import csv
import datetime

url = "https://proptech.ru:8080/intercom?action=del_keys&key=keyname&ip={}&token2=token2&srv=support"

with open('del_keys_perm_ip.csv', 'r') as file, open('log_del_keys_perm.txt', 'a') as log_file:
    reader = csv.DictReader(file)
    next(reader)  # Пропускаем первую строку с заголовками
    for row in reader:
        ip_address = row['ip']
        request_url = url.format(ip_address)

        response = requests.get(request_url)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{timestamp} - IP: {ip_address} - "

        if response.status_code == 200:
            log_message += "Request sent successfully\n"
            print(f"Request sent successfully for IP: {ip_address}")
        else:
            log_message += "Failed to send request\n"
            print(f"Failed to send request for IP: {ip_address}")

        log_file.write(log_message)
