# -*- coding: utf-8 -*-
from flask import Flask, Response
from prometheus_client import generate_latest, Gauge
from jira import JIRA
import datetime
from gevent.pywsgi import WSGIServer


app = Flask(__name__)

task_count = Gauge('jira_task_count', 'Number of tasks by assignee', ['assignee'])
unassigned_count = Gauge('jira_unassigned', 'Number of unassigned tasks')
clarification_count = Gauge('jira_clarification', 'Number of tasks in clarification')
local_rework_count = Gauge('jira_local_rework', 'Number of tasks in local rework')
rework_count = Gauge('jira_rework', 'Number of tasks in rework')
in_progress_count = Gauge('jira_in_progress', 'Number of tasks in progress')
resolved_count = Gauge('jira_resolved', 'Number of resolved tasks')
created_count = Gauge('jira_created', 'Number of created tasks')
in_progress_now_count = Gauge('jira_in_progress_now', 'Number of tasks in progress now')
tp1l_count = Gauge('jira_tp1l', 'Number of tasks for TP_1L')
tpck1l_count = Gauge('jira_tpck1l', 'Number of tasks for TPCK_1L')
tp2l_count = Gauge('jira_tp2l', 'Number of tasks for TP_2L')
tpck2l_count = Gauge('jira_tpck2l', 'Number of tasks for TPCK_2L')
to_count = Gauge('jira_to', 'Number of tasks for TO')
tpcs_count = Gauge('jira_tpcs', 'Number of tasks for TPCS')
spsk1l_count = Gauge('jira_spsk1l', 'Number of tasks for SPSK_1L')
spsk2l_count = Gauge('jira_spsk2l', 'Number of tasks for SPSK_2L')
other_count = Gauge('jira_other', 'Number of tasks for OTHER')
ola_now_count = Gauge('jira_ola_now', 'Number of tasks for OLA_NOW')
ola_full_count = Gauge('jira_ola_full', 'Number of tasks for OLA_FULL')
ola_failed_count = Gauge('jira_ola_failed', 'Number of tasks for OLA_FAILED')
ola_percentage_count = Gauge('ola_percentage_count', 'Numer of tasks for OLA_PERCENTAGE')
critical_count = Gauge('critical_count', 'Numer of tasks for CRITICAL')
projects_count = Gauge('projects_count', 'Numer of tasks for PROJECTS')
unknown_bugs_count = Gauge('unknown_bugs_count', 'Numer of bugs for UNKNOWN')
onboarding_bugs_count = Gauge('onboarding_bugs_count', 'Numer of bugs for ONBOARDING')
automation_bugs_count = Gauge('automation_bugs_count', 'Numer of bugs for AUTOMATION')
rnd_bugs_count = Gauge('rnd_bugs_count', 'Numer of bugs for RND')
intercom_bugs_count = Gauge('intercom_bugs_count', 'Numer of bugs for INTERCOM')


def get_jira_tasks():
    # Конфигурация Jira
    options = 'https://ticket.ertelecom.ru'
    login = 'grechushnikov.ir'
    api_key = 'api_key'

    # Инициализация объекта JIRA
    jira = JIRA(options, token_auth=(api_key))

    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)

    jql_query = 'issuetype = Task AND project = domsup AND component = "Домофония" AND (status changed by [Сотрудник] to "Обратная связь" during ([today], [today]) OR issueFunction in commented("by [Сотрудник] after [today] before [tomorrow]")) ORDER BY summary ASC, key DESC'
    unassigned_jql_query = 'project = DOMSUP AND ((assignee = C3PO OR component is EMPTY OR "Время до назначения" = Running()) AND status not in (Закрыта, "Обратная связь") AND issuetype = Task OR issuetype = Проект AND assignee = C3PO)'
    clarification_jql_query = 'project = DOMSUP AND component = "Домофония" AND status in ("Получение вводных")'
    local_rework_jql_query = 'project = DOMSUP AND issuetype = Task AND status = Доработка AND component = Домофония AND issueFunction not in hasLinks(блокируется)'
    rework_jql_query = 'project = domsup AND component in (Домофония, MyHome, "Домофония b2c") AND status = Доработка AND component != "Поддержка ОКЦ"'
    in_progress_jql_query = 'project = domsup AND issuetype = Task AND component in (Домофония) AND status not in (Закрыта, "Обратная связь", Доработка, "Получение вводных")'
    resolved_jql_query = f'issuetype = Task AND project = DOMSUP AND resolved >= startOfDay() and resolved <= endOfDay() and component = "Домофония"'
    created_jql_query = f'issuetype = Task AND project = DOMSUP AND created >= startOfDay() and created <= endOfDay() and component = "Домофония"'
    in_progress_now_jql_query = 'project = DOMSUP AND issuetype = Task AND component = "Домофония" AND status in ("In Progress")'
    tp1l_jql_query = 'issuetype = Task AND project = domsup AND component = Домофония AND createdDate >= startOfDay() AND createdDate <= endOfDay() AND text ~ \'"Должность пользователя: первой линии Подразделение пользователя: Направление технической поддержки b2c в регионе"~2\' and (labels = ТП_1Л or labels is EMPTY)'
    tpck1l_jql_query = 'issuetype = Task AND project = domsup AND component = Домофония AND createdDate >= startOfDay() AND createdDate <= endOfDay() AND text ~ \'"Должность пользователя: первой линии Подразделение пользователя: Направление технической поддержки b2c в цифровых каналах"~2\' and (labels = ТПЦК_1Л or labels is EMPTY)'
    tp2l_jql_query = 'issuetype = Task AND project = domsup AND component = Домофония AND createdDate >= startOfDay() AND createdDate <= endOfDay() AND text ~ \'"Должность пользователя: второй линии Подразделение пользователя: Направление технической поддержки b2c в регионе"~2\' and (labels = ТП_2Л or labels is EMPTY)'
    tpck2l_jql_query = 'issuetype = Task AND project = domsup AND component = Домофония AND createdDate >= startOfDay() AND createdDate <= endOfDay() AND text ~ \'"Должность пользователя: второй линии Подразделение пользователя: Направление технической поддержки b2c в цифровых каналах"~2\' and (labels = ТПЦК_2Л or labels is EMPTY)'
    to_jql_query = 'issuetype = Task AND project = domsup AND component = Домофония AND createdDate >= startOfDay() AND createdDate <= endOfDay() AND ("Должность заказчика" in ("Руководитель территории", "Инженер активного оборудования", "Руководитель участка", "Сервисный инженер", "Руководитель отдела капитального строительства сети", "Руководитель территориального отдела", "Ведущий инженер по строительству сети", "Инженер по строительству сети", "Ведущий менеджер по развитию территорий", "Техник аварийно-восстановительных работ b2c", "Ведущий инженер-проектировщик", "Руководитель территории частного сектора", "Руководитель отдела эксплуатации сети", "Инженер-проектировщик") or reporter = service_rmsi_uk) and (labels = ТО or labels is EMPTY)'
    tpcs_jql_query = 'issuetype = Task AND project = domsup AND component = Домофония AND createdDate >= startOfDay() AND createdDate <= endOfDay() and "Должность заказчика" in ("Работник технической поддержки SD-2430065", "Специалист по тестированию SD-2830073", "SD-1936667") and (labels = ТП_ЦС or labels is EMPTY)'
    spsk1l_jql_query = 'issuetype = Task AND project = domsup AND component = Домофония AND createdDate >= startOfDay() AND createdDate <= endOfDay() AND (text ~ \'"Должность пользователя: первой линии Подразделение пользователя: Направление поддержки и сохранения клиентов b2c"~2\' OR "Отдел заказчика" in ("Направление поддержки и сохранения клиентов b2c в регионах Центр", "Направление поддержки и сохранения клиентов b2c в регионе Сибирь", "Направление поддержки и сохранения клиентов b2c в регионе Урал", "Направление поддержки и сохранения клиентов b2c в цифровых канал", "Направление поддержки и сохранения клиентов b2c в регионе Столиц") and "Должность заказчика" in("Ведущий специалист первой линии", "Специалист первой линии")) and (labels = СПСК_1Л or labels is EMPTY)'
    spsk2l_jql_query = 'issuetype = Task AND project = domsup AND component = Домофония AND createdDate >= startOfDay() AND createdDate <= endOfDay() AND (text ~ \'"Должность пользователя: второй линии Подразделение пользователя: Направление поддержки и сохранения клиентов b2c"~2\' OR "Отдел заказчика" in ("Направление поддержки и сохранения клиентов b2c в регионах Центр", "Направление поддержки и сохранения клиентов b2c в регионе Сибирь", "Направление поддержки и сохранения клиентов b2c в регионе Урал", "Направление поддержки и сохранения клиентов b2c в цифровых канал", "Направление поддержки и сохранения клиентов b2c в регионе Столиц") and "Должность заказчика" in("Ведущий специалист второй линии", "Специалист второй линии")) and (labels = СПСК_2Л or labels is EMPTY)'
    other_jql_query = 'project = "PropTech Support" AND component = Домофония AND labels not in(ТП_1Л, ТП_2Л, ТПЦК_1Л, ТПЦК_1Л, ТО, ТП_ЦС, СПСК_2Л, СПСК_1Л) and createdDate >= startOfDay() and createdDate <=endOfDay()'
    ola_now_jql_query = 'project = domsup AND issuetype = Task AND component in (Домофония) AND status not in (Закрыта, "Обратная связь", Доработка, "Получение вводных") and (OLA = breached() OR "Время ожидания поддержки" = breached() OR "Время решения" = breached())'
    ola_full_jql_query = 'project = DOMSUP and issuetype = task and component = Домофония and status = Закрыта and status changed AFTER startOfMonth()'
    ola_failed_jql_query = 'project = DOMSUP and issuetype = task and component = Домофония and status = Закрыта and OLA = breached() and status changed AFTER startOfMonth()'
    critical_jql_query = 'project = DOM AND status not in (Закрыта) AND issuetype in (Авария) AND issue != DOM-7592 AND (created >= startOfMonth() OR status != Закрыта)'
    projects_jql_query = 'project = DOMSUP AND issuetype = Проект AND status not in (Закрыта)'
    unknown_bugs_jql_query = 'project = DOM AND status not in (Закрыта) AND issuetype in (Bug) AND component = "Домофония b2c" and assignee not in (ezhov.an, shevchenko.ob2, evdokimov.dl, maltceva.to)'
    onboarding_bugs_jql_query = 'project = DOM AND status not in (Закрыта) AND issuetype in (Bug) AND component = "Домофония b2c" and assignee = ezhov.an'
    automation_bugs_jql_query = 'project = DOM AND status not in (Закрыта) AND issuetype in (Bug) AND component = "Домофония b2c" and assignee = shevchenko.ob2'
    rnd_bugs_jql_query = 'project = DOM AND status not in (Закрыта) AND issuetype in (Bug) AND component = "Домофония b2c" and assignee = evdokimov.dl'
    intercom_bugs_jql_query= 'project = DOM AND status not in (Закрыта) AND issuetype in (Bug) AND component = "Домофония b2c" and assignee = maltceva.to'

    # Получение количества неназначенных задач
    unassigned_issues = jira.search_issues(unassigned_jql_query, maxResults=False)
    unassigned_count.set(len(unassigned_issues))


    # Получение количества задач в clarification
    clarification_issues = jira.search_issues(clarification_jql_query, maxResults=False)
    clarification_count.set(len(clarification_issues))

    # Получение количества задач в local rework
    local_rework_issues = jira.search_issues(local_rework_jql_query, maxResults=False)
    local_rework_count.set(len(local_rework_issues))

    # Получение количества задач в rework
    rework_issues = jira.search_issues(rework_jql_query, maxResults=False)
    rework_count.set(len(rework_issues))

    # Получение количества задач в работе
    in_progress_issues = jira.search_issues(in_progress_jql_query, maxResults=False)
    in_progress_count.set(len(in_progress_issues))

    # Получение количества решенных задач
    resolved_issues = jira.search_issues(resolved_jql_query, maxResults=False)
    resolved_count.set(len(resolved_issues))

    # Получение количества созданных задач
    created_issues = jira.search_issues(created_jql_query, maxResults=False)
    created_count.set(len(created_issues))

    # Получение количества задач в статусе "В работе"
    in_progress_now_issues = jira.search_issues(in_progress_now_jql_query, maxResults=False)
    in_progress_now_count.set(len(in_progress_now_issues))

    # Получение количества задач для TP_1L
    tp1l_issues = jira.search_issues(tp1l_jql_query, maxResults=False)
    tp1l_count.set(len(tp1l_issues))

    # Получение количества задач для TPCK_1L
    tpck1l_issues = jira.search_issues(tpck1l_jql_query, maxResults=False)
    tpck1l_count.set(len(tpck1l_issues))

    # Получение количества задач для TP_2L
    tp2l_issues = jira.search_issues(tp2l_jql_query, maxResults=False)
    tp2l_count.set(len(tp2l_issues))

    # Получение количества задач для TPCK_2L
    tpck2l_issues = jira.search_issues(tpck2l_jql_query, maxResults=False)
    tpck2l_count.set(len(tpck2l_issues))

    # Получение количества задач для TO
    to_issues = jira.search_issues(to_jql_query, maxResults=False)
    to_count.set(len(to_issues))

    # Получение количества задач для TPCS
    tpcs_issues = jira.search_issues(tpcs_jql_query, maxResults=False)
    tpcs_count.set(len(tpcs_issues))

    # Получение количества задач для SPSK_1L
    spsk1l_issues = jira.search_issues(spsk1l_jql_query, maxResults=False)
    spsk1l_count.set(len(spsk1l_issues))

    # Получение количества задач для SPSK_2L
    spsk2l_issues = jira.search_issues(spsk2l_jql_query, maxResults=False)
    spsk2l_count.set(len(spsk2l_issues))

    # Получение количества задач для OTHER
    other_issues = jira.search_issues(other_jql_query, maxResults=False)
    other_count.set(len(other_issues))

    # Получение количества текущей просрочки
    ola_now_issues = jira.search_issues(ola_now_jql_query, maxResults=False)
    ola_now_count.set(len(ola_now_issues))

    # Получение количества решенных задач за месяц
    ola_full_issues = jira.search_issues(ola_full_jql_query, maxResults=False)
    ola_full_count.set(len(ola_full_issues))

    # Получение количества просрочки за месяц
    ola_failed_issues = jira.search_issues(ola_failed_jql_query, maxResults=False)
    ola_failed_count.set(len(ola_failed_issues))

    # Получение количества аварий
    critical_issues = jira.search_issues(critical_jql_query, maxResults=False)
    critical_count.set(len(critical_issues))

    # Получение количества проектов
    projects_issues = jira.search_issues(projects_jql_query, maxResults=False)
    projects_count.set(len(projects_issues))

    # Получение количества неназначенных багов
    unknown_bugs_issues = jira.search_issues(unknown_bugs_jql_query, maxResults=False)
    unknown_bugs_count.set(len(unknown_bugs_issues))

    # Получение количества багов на onboarding
    onboarding_bugs_issues = jira.search_issues(onboarding_bugs_jql_query, maxResults=False)
    onboarding_bugs_count.set(len(onboarding_bugs_issues))

    # Получение количества багов на automation
    automation_bugs_issues = jira.search_issues(automation_bugs_jql_query, maxResults=False)
    automation_bugs_count.set(len(automation_bugs_issues))

    # Получение количества багов на rnd
    rnd_bugs_issues = jira.search_issues(rnd_bugs_jql_query, maxResults=False)
    rnd_bugs_count.set(len(rnd_bugs_issues))

    # Получение количества багов на intercom
    intercom_bugs_issues = jira.search_issues(intercom_bugs_jql_query, maxResults=False)
    intercom_bugs_count.set(len(intercom_bugs_issues))

    ola_full = len(ola_full_issues)
    ola_failed = len(ola_failed_issues)

    if ola_full > 0:
        percentage = ((ola_full - ola_failed) / ola_full) * 100
    else:
        percentage = 0

    ola_percentage_count.set(percentage)

    assignees = ['user1', 'user2', 'user3', 'grechushnikov.ir', 'user4']

    task_stats = {}
    for assignee in assignees:
        modified_query = jql_query.replace('[Сотрудник]', assignee).replace('[today]',str(today)).replace('[tomorrow]', str(tomorrow))
        issues = jira.search_issues(modified_query, maxResults=False)
        num_tasks = len(issues)
        task_stats[assignee] = num_tasks

    for assignee, count in task_stats.items():
        task_count.labels(assignee=assignee).set(count)

@app.route('/metrics')
def metrics():
    get_jira_tasks()
    in_progress_count.collect()
    ola_percentage_count.collect()
    return Response(generate_latest(), mimetype='text/plain')

if __name__ == '__main__':
    http_server = WSGIServer(('', 8000), app.wsgi_app)
    http_server.serve_forever()
