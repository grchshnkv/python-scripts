import csv
import requests
import psycopg2
import logging
import time

# Настройка логирования
logging.basicConfig(filename='ip_zabbix_logs.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Настройка логирования для удаленных аккаунтов
removed_logger = logging.getLogger('removed_accounts')
removed_handler = logging.FileHandler('is_removed.txt')
removed_handler.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
removed_handler.setFormatter(formatter)
removed_logger.addHandler(removed_handler)

# Подключение к базе данных PostgreSQL
conn = psycopg2.connect(
    dbname='db',
    user='grechushnikov',
    password='password',
    host='mdb.yandexcloud.net',
    port='8080'
)
cursor = conn.cursor()

# URL для POST запроса
url = 'https://proptech.ru:8080/intercom'

# Чтение файла ip_zabbix.csv с указанием разделителя
with open('ip_zabbix.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file, delimiter=';')  # ; разделитель

    # Обработка каждого IP из CSV
    for row in reader:
        ip = row['ip']  # В CSV есть колонка 'ip'
        if not ip:  # Пропускаем пустые строки
            continue

        failed_attempts = 0  # Счетчик неудачных попыток

        while failed_attempts < 5:
            # Выполнение запроса к базе данных для получения всех записей для данного IP
            cursor.execute("""
                SELECT accounts->'admin'->>'password' AS admin_password, is_removed 
                FROM access_control ac 
                WHERE ip_address = %s
            """, (ip,))
            results = cursor.fetchall()  # Получаем все записи

            if results:
                for result in results:
                    password = result[0]
                    is_removed = result[1]

                    # Проверяем, что пароль найден
                    if password:
                        # Подготовка параметров для POST запроса
                        params = {
                            'action': 'set_account',
                            'login': 'admin',
                            'password': password,
                            'srv': 'support',
                            'ip': ip,
                            'token2': 'token2',  
                            'account': 'admin'
                        }

                        # Логируем пароль перед отправкой запроса
                        logger.info(f'Sending request for IP: {ip} with password: {password}')

                        try:
                            # Выполнение POST запроса с таймаутом
                            response = requests.post(url, data=params, timeout=10)

                            # Обработка ответа
                            if response.status_code == 200:
                                if is_removed:
                                    # Логируем в отдельный файл для удаленных аккаунтов
                                    removed_logger.warning(f'Successful request for IP: {ip} with password: {password}, but account is marked as removed.')
                                else:
                                    logger.info(f'Successfully sent data for IP: {ip} with password: {password}')
                                break  # Выход из цикла при успешном запросе
                            else:
                                logger.warning(f'Failed to send data for IP: {ip}, Status code: {response.status_code}')
                                failed_attempts += 1
                        except requests.exceptions.Timeout:
                            logger.error(f'Timeout occurred for IP: {ip}.')
                            failed_attempts += 1
                        except requests.exceptions.RequestException as e:
                            logger.error(f'Error occurred for IP: {ip}: {e}')
                            failed_attempts += 1
                    else:
                        logger.warning(f'No valid password found for IP: {ip}.')
                        break  # Выход из цикла, если пароля нет
                break  # Выход из внешнего цикла, если данные были обработаны
            else:
                logger.warning(f'No data found for IP: {ip}.')
                break  # Выход из цикла, если данных нет

        # Если было 5 неудачных попыток, ждем 30 секунд
        if failed_attempts >= 5:
            logger.info(f'5 failed attempts for IP: {ip}. Waiting for 30 seconds before next attempt.')
            time.sleep(30)

# Закрытие соединения с базой данных
cursor.close()
conn.close()

