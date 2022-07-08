import msvcrt
import re
import sys
from datetime import datetime

import requests
import openpyxl

def get_values(items):
    # values = [[randrange(10, 99)]]
    # values = [[randrange(10, 99) for _ in range(0, 6)]]
    # values = [[randrange(10, 99)] for _ in range(0, 3)]
    values = [[items[y][x] for x in range(0, 4)] for y in range(0, len(items))]
    return values


def start_analytics(v1, v2, v3, set_result):
    print('ANALYTICS:')
    try:
        str_encode = b'\xff\xfe9\x00X\x00u\x00X\x00X\x00H\x00b\x00P\x00'

        r = requests.post('https://api-v3.neuro.net/api/v2/ext/auth',
                          auth=("mylaw.api@gmail.com", str_encode.decode('UTF-16')))
        refresh_token = r.json()['refresh_token']
        print("Аутентификация прошла успешно!")
    except requests.ConnectionError:
        # nn.log('Error!')
        print("Ошибка аутентификации!")
        print("Нажмите esc, чтобы выйти")
        while True:
            if msvcrt.kbhit():
                k = ord(msvcrt.getch())
                if k == 27:
                    sys.exit()

    company_uuids = ['96857848-a88f-4cb0-bad8-6f70f3ec6211', '1c07c539-916c-4519-b26a-2c7a67a6f24e',
                     'e3cd14a1-a289-4d2f-86ab-182dc5e889ce', '859acaa5-5cd3-4e13-ab27-2f903fed5515',
                     '083a00b2-0685-481b-b307-22ba56091648', '1c07c539-916c-4519-b26a-2c7a67a6f24e',
                     '92235ed7-8dec-49b9-ad3b-e639f077d9cd', '8a48cafd-1c2c-4380-939f-340914ab8710',
                     'd2069c81-b66a-4e8d-88b9-46e60ee01a34', '118802bc-f84b-47ed-bf49-a1ac2f7a0432',
                     '70196014-fa26-48fe-b586-84a752eee58f']

    all_agents = {}
    for company_uuid in company_uuids:
        try:
            print('Получение агентов...')
            url = f'https://api-v3.neuro.net/api/v2/ext/company-agents?company_uuid={company_uuid}'
            header = {'Authorization': "Bearer " + refresh_token,
                      'Content-Type': 'application/json'}

            r = requests.get(url, headers=header)
            all_agents[company_uuid] = r.json()
        except requests.ConnectionError:
            # nn.log('Error!')
            print("Ошибка при получении агентов!")
            print("Нажмите esc, чтобы выйти")
            while True:
                if msvcrt.kbhit():
                    k = ord(msvcrt.getch())
                    if k == 27:
                        sys.exit()
    agent_name = 'agent_uuid'
    agent_uuid = v1
    time_start = v2
    time_end = v3
    agent_exists = False

    if agent_uuid != 'all_agents':
        x = str(input('Введите agent_uuid >>> '))
        agent_uuid = x
        while True:
            for company_uuid in company_uuids:
                for agent in all_agents[company_uuid]:
                    # print(agent)
                    # print(agent.keys())
                    if agent['agent_uuid'] == agent_uuid:
                        agent_name = agent['name']
                        print('Агент', agent_name, 'найден!')
                        agent_exists = True
            if agent_exists is True:
                print('Результаты будут записаны в', agent_name+'.xlsx')
                break
            print('Агент не найден...')
            # print('Доступные агенты:')
            # for company_uuid in company_uuids:
            #     for agent in all_agents[company_uuid]:
            #         print(agent['agent_uuid'])
            print('Попробуйте еще раз:')
            x = str(input('Введите agent_uuid >>> '))
            agent_uuid = x

    start_time = datetime.now()
    NUM_SECONDS_IN_A_MIN = 60
    book = openpyxl.Workbook()
    sheet = book.active
    row = 1

    sheet['A1'] = "KEY"
    sheet['B1'] = "QUESTION"
    sheet['C1'] = "ANSWER"
    sheet['D1'] = "AMOUNT"
    if set_result != 'none':
        sheet['E1'] = "RESULT"


    agents_statistic = {}
    for company_uuid in company_uuids:
        for agent in all_agents[company_uuid]:
            try:
                '''time_start = (datetime.datetime.now(timezone(time_zone)) - datetime.timedelta(minutes=5, hours=(
                                                        3 + hour_offset))).strftime("%Y-%m-%d %H:%M:%S")
                                            time_end = (datetime.datetime.now(timezone(time_zone)) - datetime.timedelta(
                                                hours=(3 + hour_offset))).strftime("%Y-%m-%d %H:%M:%S")'''

                #print('agent_uuid = ' + agent_uuid)
                if agent['agent_uuid'] == agent_uuid and agent_uuid != 'all_agents' or agent_uuid == 'all_agents':

                    r = requests.post('https://api-v3.neuro.net/api/v2/ext/statistic/dialog-report',
                                      json={"agent_uuid": agent['agent_uuid'],
                                            "start": time_start,
                                            "end": time_end},
                                      headers={
                                          'Authorization': "Bearer " + refresh_token})

                    agents_statistic[agent['name']] = r.json()
                    for keyy, valuee in agents_statistic.items():
                        key = keyy
                        value = valuee

                    print('Получение данных...', key)

                    my_list = []
                    d1 = {}
                    # print(agents_statistic.keys())

                    if len(value['result']) > 0:  # если есть логи
                        # d1 = {}
                        check_list = {}
                        a = b = g = []
                        # print(key, '->', value)
                        for log in value.get('result'):
                            if 'call_transcript' in log.keys():
                                if len(log['call_transcript']) > 0:
                                    str_1 = log['call_transcript']
                                    result_list_of_conv = re.split(r';', str_1)
                                    if len(result_list_of_conv) > 1:
                                        if set_result == 'none':
                                            result_list_of_conv.reverse()
                                            for j in range(len(result_list_of_conv)):
                                                str_1 = result_list_of_conv[j]
                                                if re.search(r'bot', str_1) is None:  # если строка не бот
                                                    if re.search(r'\):', result_list_of_conv[j - 1]) is None:
                                                        str_b = result_list_of_conv[j - 1]
                                                    else:
                                                        res_2 = re.split(r'\):', result_list_of_conv[j - 1])
                                                        str_b = str(res_2[1])
                                                    if re.search(r'\):', str_1) is None:
                                                        str_h = str_1
                                                    else:
                                                        res_2 = re.split(r'\):', str_1)
                                                        str_h = str(res_2[1])
                                                    flag = False
                                                    if str_b in d1.keys():
                                                        n = next((i for i, x in enumerate(d1[str_b]) if x[0] == str_h),
                                                                 None)
                                                        if n is not None:  # если есть строка(human) в ключе (bot)
                                                            d1[str_b][n][1] = d1[str_b][n][
                                                                                  1] + 1  # d1[str_b][number][0] - ответ (human)
                                                        else:  # d1[str_b][number][1] - их кол-во
                                                            d1[str_b].append([str_h, 1])
                                                    else:
                                                        d1[str_b] = [[str_h, 1]]
                                                    break
                                        else:
                                            if 'result' in log.keys():
                                                if set_result == str(log['result']):
                                                    # print(log)
                                                    result_list_of_conv.reverse()
                                                    for j in range(len(result_list_of_conv)):
                                                        str_1 = result_list_of_conv[j]
                                                        if re.search(r'bot', str_1) is None:  # если строка не бот
                                                            if re.search(r'\):', result_list_of_conv[j - 1]) is None:
                                                                str_b = result_list_of_conv[j - 1]
                                                            else:
                                                                res_2 = re.split(r'\):', result_list_of_conv[j - 1])
                                                                str_b = str(res_2[1])
                                                            if re.search(r'\):', str_1) is None:
                                                                str_h = str_1
                                                            else:
                                                                res_2 = re.split(r'\):', str_1)
                                                                str_h = str(res_2[1])
                                                            flag = False
                                                            if str_b in d1.keys():
                                                                n = next(
                                                                    (i for i, x in enumerate(d1[str_b]) if x[0] == str_h),
                                                                    None)
                                                                if n is not None:  # если есть строка(human) в ключе (bot)
                                                                    d1[str_b][n][1] = d1[str_b][n][1] + 1  # d1[str_b][number][0] - ответ (human)
                                                                else:  # d1[str_b][number][1] - их кол-во
                                                                    d1[str_b].append([str_h, 1])
                                                            else:
                                                                d1[str_b] = [[str_h, 1]]
                                                            break
                        finish_set_result = 'SET result="' + str(set_result) + '"'
                        set_result_flag = False
                        if set_result != 'none':
                            set_result_flag = True
                        for key_t, value_t in d1.items():
                            print('\t', key_t, '->')
                            for k in value_t:
                                print('\t\t', k)
                                sheet[row][0].value = key
                                sheet[row][1].value = key_t
                                sheet[row][2].value = str(k[0])
                                sheet[row][3].value = str(k[1])
                                if set_result_flag is True:
                                    sheet[row][4].value = str(finish_set_result)
                                row += 1
                        print('Данные обрабатываются. Пожалуйста, подождите...')
            except requests.ConnectionError:
                print('Проблемы на сервере! (ошибкка при получение данных)')
                print("Нажмите esc, чтобы выйти")
                while True:
                    if msvcrt.kbhit():
                        k = ord(msvcrt.getch())
                        if k == 27:
                            sys.exit()
    print('Время выполнения: %d мин' % ((datetime.now() - start_time).total_seconds()/NUM_SECONDS_IN_A_MIN))
    if agent['name'] == 'all_agents':
        book.save("result.xlsx")
    else:
        book.save(agent_name+'.xlsx')
    book.close()


def menu():
    d = 0
    d1 = ''
    d2 = ''
    while True:
        print("##############################################################################")
        print('# Данная программа заносит аналитику со всех агентов в result.xlsx           #')
        print('# этот файл появится в папке с программой                                    #')
        print('# Если вы будете загружать большой промежуток времени - наберитесь терпения  #')
        print('# Во время выполнения не взаимодействуйте с файлом                           #')
        print('# -------------------------------------------------------------------------- #')
        print('# Для того, чтобы начать выгрузку возражений, введите временной промежуток   #')
        print('# Пример ввода(YY-MM-DD):                                                    #')
        print('# "Введите дату >>> 2022-06-01 00:00:00"                                     #')
        print('# "Введите дату >>> 2022-06-29 12:00:00"                                     #')
        print('# Для выхода из программы введите "0" или "выход"                            #')
        print("##############################################################################")
        x = str(input('Введите дату >>> '))
        if x == '0' or x == 'выход':
            print("Выход из программы")
            break
        if re.findall(r'^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$', x):
            print(str(d+1) + 'ая дата:',  x)
            d = d + 1
            if d == 1:
                d1 = x
            if d == 2:
                d2 = x
                my_str = 'all_agents'
                while True:
                    print("##############################################################################")
                    print('# Нажмите 1, если вы хотите получить данные по всем агентам                  #')
                    print('# Нажмите 2, если вы хотите получить данные по одному агенту                 #')
                    print("##############################################################################")
                    x = str(input('>>> '))
                    if x == '1':
                        break
                    if x == '2':
                        my_str = 'one_agent'

                        while True:
                            print("##############################################################################")
                            print('# Нажмите 1, если вы хотите учитывать SET result                             #')
                            print('# Нажмите 2, если вы не хотите учитывать SET result                          #')
                            print("##############################################################################")
                            x = str(input('>>> '))
                            if x == '2':
                                my_set_result = 'none'
                                break
                            if x == '1':
                                x = str(input('Введите SET result >>> '))
                                my_set_result = x
                                break

                        break
                start_analytics(my_str, d1, d2, my_set_result)
                break
        else:
            print('Попробуйте еще раз')
    print("Программа закончена")
    print("Нажмите esc, чтобы выйти")
    while True:
        if msvcrt.kbhit():
            k = ord(msvcrt.getch())
            if k == 27:
                sys.exit()



if __name__ == '__main__':
    menu()

