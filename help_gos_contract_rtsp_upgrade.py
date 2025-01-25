import requests
import logging
import subprocess
import time

logger = logging.getLogger('MotionDetect')
logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

with open('no_ip.log', 'w') as file:
    file.close()
with open('no_ping.log', 'w') as file:
    file.close()
with open('request_timeout.log', 'w') as file:
    file.close()
with open('error_pwd.log', 'w') as file:
    file.close()
with open('success_edit.log', 'w') as file:
    file.close()
with open('not_beward.log', 'w') as file:
    file.close()
with open('success_auth.log', 'w') as file:
    file.close()
with open('others.log', 'w') as file:
    file.close()
with open('ip.csv', 'w') as file:
    file.close()


def get_correct_pwd(url, ip, pwd):
    logger.warning('На {} пароль {} не подошел. Начинаю перебор стандартных паролей.'.format(ip, pwd))
    all_passwords = ['password1', 'password2', 'password3', 'password4', 'password5']
    r = 0
    for elem in all_passwords:
        request = requests.get(url, auth=('admin', elem), timeout=5)
        r += 1
        if 'Unauthorized' not in request.text:
            return elem
        if r in (2):
            time.sleep(30)
    else:
        return False


count = 0
with open('ip_address.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')  # Указан разделитель ";"
    next(reader)  # Пропустить заголовки столбцов
    for row in reader:
        if len(row) < 2:
            continue  # Пропустить строки с недостаточным количеством колонок
        ip_address = row[0].strip()  # Первый столбец - IP-адрес
        pwd = row[1].strip()          # Второй столбец - пароль
        count += 1
        print('Прогресс: {}/{}'.format(count, 823))
        try:
            output = subprocess.check_output(['ping', '-c', '1', '{}'.format(ip_address)], timeout=2)
            url = "http://{}/cgi-bin/systeminfo_cgi".format(ip_address)
            request = requests.get(url, auth=('admin', pwd), timeout=5)
            if 'Unauthorized' in request.text:
                result = get_correct_pwd(url, ip_address, pwd)
                if not result:
                    text = 'На {} не смог подобрать пароль\n'.format(ip_address)
                    logger.error(text)
                    with open('error_pwd.log', 'a') as file:
                        file.write(text)
                else:
                    url = "http://{}/cgi-bin/pwdgrp_cgi?action=update&username=admin&password={}".format(
                        ip_address, pwd.replace('#', '%23')
                    )
                    request2 = requests.get(url, auth=('admin', result), timeout=5)
                    if 'ok' in request2.text.lower():
                        text = 'На панели с ip {} успешно изменил пароль\n'.format(ip_address)
                        logger.info(text)
                        with open('success_edit.log', 'a') as file:
                            file.write(text)
                        with open('ip.csv', 'a') as file:
                            file.write('{}\n'.format(ip_address))
            elif '404' in request.text:
                text = 'ip {} не BEWARD\n'.format(ip_address)
                logger.warning(text)
                with open('not_beward.log', 'a') as file:
                    file.write(text)
            elif 'UpTime' in request.text:
                text = 'На панели с ip {} все хорошо и готова к смене пароля\n'.format(ip_address)
                logger.info(text)
                with open('success_auth.log', 'a') as file:
                    file.write(text)
                with open('ip.csv', 'a') as file:
                    file.write('{}\n'.format(ip_address))
            else:
                text = 'На {} какие-то странности. Использовал для авторизации пароль: {}\n'.format(ip_address, pwd)
                logger.warning(text)
                with open('others.log', 'a') as file:
                    file.write(text)
        except subprocess.CalledProcessError:
            text = 'Хоста с ip {} не существует\n'.format(ip_address)
            logger.error(text)
            with open('no_ip.log', 'a') as file:
                file.write(text)
        except subprocess.TimeoutExpired:
            text = 'Панель с ip {} недоступна по сети\n'.format(ip_address)
            logger.error(text)
            with open('no_ping.log', 'a') as file:
                file.write(text)
        except requests.ConnectTimeout:
            text = 'Не смог достучаться до {}. Запрос отбился по тайм-ауту\n'.format(ip_address)
            logger.error(text)
            with open('request_timeout.log', 'a') as file:
                file.write(text)
        except Exception as e:
            text = 'Что-то пошло не так с {}: {}\n'.format(ip_address, str(e))
            logger.error(text)
            with open('others.log', 'a') as file:
                file.write(text)