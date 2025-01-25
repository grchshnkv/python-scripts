import logging
from jira import JIRA
import csv
import psycopg2
import requests
import subprocess
import urllib.parse

# Настройка логирования
logging.basicConfig(filename='open_the_door_logs.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def ping_ip(ip_address):
    try:
        # Выполняем команду ping
        output = subprocess.check_output(['ping', '-c', '1', ip_address], stderr=subprocess.STDOUT, universal_newlines=True)
        return True  # Если команда выполнена успешно, IP доступен
    except subprocess.CalledProcessError:
        return False  # Если произошла ошибка, IP недоступен


def log_request(method, url, **kwargs):
    logging.info(f"Sending {method} request to {url} with params: {kwargs.get('params', {})} and data: {kwargs.get('data', {})}")


def perform_action(jira, ticket_key, action_id):
    try:
        issue = jira.issue(ticket_key)

        # Получаем доступные переходы
        transitions = jira.transitions(issue)

        # Выполняем действие с указанным ID
        for transition in transitions:
            if transition['id'] == str(action_id):  # Приводим к строке, если необходимо
                jira.transition_issue(issue, transition['id'])
                logging.info(f'Ticket {ticket_key} has been transitioned using action ID {action_id}.')
                return

        logging.warning(f'Action with ID {action_id} not found for ticket {ticket_key}.')

    except Exception as e:
        logging.error(f'Error performing action on ticket {ticket_key}: {e}')


def get_jira_tasks():
    logging.info("Starting to get Jira tasks.")

    # Конфигурация Jira
    options = 'https://ticket.ertelecom.ru'
    login = 'grechushnikov.ir'
    api_key = 'api_key'

    # Инициализация объекта JIRA
    jira = JIRA(options, token_auth=(api_key))

    open_the_door_query = 'project = domsup AND issuetype = Task AND component in (Домофония) AND status not in (Закрыта, "Обратная связь", Доработка, "Получение вводных") AND "Симптом обращения" in cascadeOption("Сложность с открытием двери в МП Умный дом.ру") and created > "-1h"'

    # Получение тикетов по запросу
    issues = jira.search_issues(open_the_door_query)
    logging.info(f"Found {len(issues)} issues.")

    # Выполняем действие с ID 151 для найденных тикетов
    action_id = 151  # ID действия
    for issue in issues:
        perform_action(jira, issue.key, action_id)  # Выполняем действие с ID 151

    cursor = None
    conn = None

    # Список паролей для перебора
    passwords = ['password1', 'password2', 'password3', 'password4']

    try:
        # Подключение к базе данных PostgreSQL
        conn = psycopg2.connect(
            dbname='db1',
            user='grechushnikov',
            password='password',
            host='mdb.yandexcloud.net',
            port='8080'
        )
        cursor = conn.cursor()
        logging.info("Connected to the database.")

        for issue in issues:
            custom_field_value = issue.fields.customfield_15409
            logging.info(f"Processing issue {issue.key} with custom field value: {custom_field_value}")

            sql_query = f"""
            select s.account_id, sp.place_id, acp.access_control_id, ac.ip_address, ac.type_id, ac.hardware_model_id,
            ac.accounts->'admin'->>'login' as admin_login, ac.accounts->'admin'->>'password' as admin_password,
            ac.accounts->'api'->>'login' as api_login, ac.accounts->'api'->>'password' as api_password
            from subscriber s 
            inner join subscriber_place sp on sp.subscriber_id = s.id 
            inner join access_control_place acp on acp.place_id = sp.place_id 
            inner join access_control ac on ac.id = acp.access_control_id 
            where s.account_id in ('{custom_field_value}') and acp.is_removed = false and ac.access_control_role_id in (1,3,2,8);
            """

            cursor.execute(sql_query)
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]

            for row in rows:
                type_id = row[column_names.index('type_id')]
                ip_address = row[column_names.index('ip_address')]
                hardware_model_id = row[column_names.index('hardware_model_id')]
                api_user = row[column_names.index('api_login')]
                api_password = row[column_names.index('api_password')]
                admin_password = row[column_names.index('admin_password')]

                logging.info(f"Checking IP address: {ip_address}")

                if ping_ip(ip_address):
                    logging.info(f"IP {ip_address} is reachable.")
                    if type_id == 2:
                        comment = f"На платформе КД заведен как BUP (IP: {ip_address}). Обратитесь в город, чтобы исправили на SIP"
                        jira.add_comment(issue, comment)
                        logging.info(f"Added comment to issue {issue.key}: {comment}")
                    elif type_id == 1:
                        if hardware_model_id == 53:
                            open_url = f'http://{api_user}:{api_password}@{ip_address}/api/v1/doors/1/open'
                            get_url = f'http://{api_user}:{api_password}@{ip_address}/api/v1/doors/1'

                            log_request('POST', open_url)
                            response_open = requests.post(open_url)
                            logging.info(
                                f"Response for opening door: {response_open.status_code}, {response_open.text}")

                            log_request('GET', get_url)
                            response_get = requests.get(get_url)
                            logging.info(
                                f"Response for getting door info: {response_get.status_code}, {response_get.text}")

                            if response_open.status_code == 204 and response_get.status_code == 200:
                                comment = f"Дверь открывается корректно (IP: {ip_address}). Проверьте повторно."
                                jira.add_comment(issue, comment)
                                logging.info(f"Added comment to issue {issue.key}: {comment}")
                            else:
                                comment = f"На панели неправильный пароль (IP: {ip_address}), необходимо проверить авторизацию на КД."
                                jira.add_comment(issue, comment)
                                logging.info(f"Added comment to issue {issue.key}: {comment}")

                        elif hardware_model_id in [2, 5]:
                            # Экранирование пароля администратора
                            escaped_admin_password = urllib.parse.quote(admin_password, safe='')
                            url = "http://{}/cgi-bin/systeminfo_cgi".format(ip_address)
                            log_request('GET', url, auth=('admin', admin_password))

                            # Отправка запроса с использованием auth
                            response = requests.get(url, auth=('admin', admin_password), timeout=15)

                            # Проверка на наличие "Unauthorized" в ответе
                            if "Unauthorized" not in response.text:
                                comment = f"Авторизация на КД корректна (IP: {ip_address}). Проверьте повторно."
                                jira.add_comment(issue, comment)
                                logging.info(f"Added comment to issue {issue.key}: {comment}")
                            else:
                                # Флаг для отслеживания успешной авторизации
                                successful_auth = False

                                for password in passwords:
                                    escaped_password = urllib.parse.quote(password, safe='')
                                    url = "http://{}/cgi-bin/systeminfo_cgi".format(ip_address)
                                    log_request('GET', url, auth=('admin', password))

                                    # Отправка запроса с использованием auth
                                    response = requests.get(url, auth=('admin', password), timeout=15)

                                    if "Unauthorized" not in response.text:
                                        logging.info(f"Successfully authenticated with password: {password}")

                                        # Формирование комментария с отображением первых двух символов пароля
                                        masked_password = password[:2] + '*' * (len(password) - 2)
                                        comment = f"Успешная авторизация с паролем: {masked_password} (IP: {ip_address})."
                                        jira.add_comment(issue, comment)
                                        logging.info(f"Added comment to issue {issue.key}: {comment}")

                                        successful_auth = True  # Устанавливаем флаг успешной авторизации
                                        break  # Выход из цикла, если пароль найден
                                    else:
                                        logging.warning(f"Failed to authenticate with password: {password}")

                                # Если ни один пароль не подошел, добавляем комментарий в тикет
                                if not successful_auth:
                                    comment = "Не удалось подобрать пароль. Проверьте также пароль Pa*****. Если он тоже не подошел, то отправьте ТС для сброса пароля на месте."
                                    jira.add_comment(issue, comment)
                                    logging.info(f"Added comment to issue {issue.key}: {comment}")

        with open('problems_open_the_door.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Записываем заголовки только если файл пустой
            if file.tell() == 0:
                writer.writerow(['Ticket Link', 'Custom Field Value'])

            for issue in issues:
                ticket_key = issue.key
                custom_field_value = issue.fields.customfield_15409
                ticket_link = f'https://ticket.ertelecom.ru/browse/{ticket_key}'
                writer.writerow([ticket_link, custom_field_value])
                logging.info(f"Wrote to CSV: {ticket_link}, {custom_field_value}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
            logging.info("Cursor closed.")
        if conn:
            conn.close()
            logging.info("Database connection closed.")


# Вызов функции
get_jira_tasks()


