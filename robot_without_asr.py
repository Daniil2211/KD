import msvcrt
import random
import re
import json
import sys

import requests
import pandas as pd

print("##############################################################################")
print('# !!! ВНИМАНИЕ. ВСЕМ ЧИТАТЬ ИНСТРУКЦИЮ !!!                                   #')
print('# Данная программа проверяет скрипты на исправность                          #')
print('# Файл с названием скрипта должен быть в той же директории                   #')
print('# Все результаты будут в самой консоли и в файле result.xlsx (2 листа)       #')
print("##############################################################################")

agent_uuid = str(input('Введите agent_uuid >>> '))
skript_name = str(input('Введите название файла со скриптом (файл формата .xlsx)>>> '))
phrases_list_result = []

# skript_name = 'Скрипт Ментор Сольюшенс'
# agent_uuid = '7086bc4c-1c1b-47fe-b990-99aa098fabeb'
break_flag = False

skript = pd.read_excel('./' + skript_name + '.xlsx')

# print(skript[skript.keys()[0]])
list_of_numbers = skript[skript.keys()[0]].tolist()
list_of_logic_name = skript[skript.keys()[1]].tolist()
list_of_prompt_name = skript[skript.keys()[3]].tolist()
list_of_prompt_text = skript[skript.keys()[4]].tolist()
list_of_pattern = skript[skript.keys()[5]].tolist()
list_of_entity = skript[skript.keys()[6]].tolist()
list_of_goto = skript[skript.keys()[7]].tolist()

error_list = []


# 'Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5',
# 'NULL - не сказано ни одного слова', 'Unnamed: 7', 'Unnamed: 8'

# A(0) - # number_of_element; B(1) - Logic_name; C; D(3) - Prompt_name; E(4) - Prompt_text; F(5) -  Pattern;
# G(6) -  Entity; H(7) -  GoTo;


def check_some_logic():
    start_phrase = ''
    if current_logic_num == 1:
        start_phrase = list_of_prompt_text[list_of_numbers.index('#1.1')]
    if current_logic_num == 2:
        start_phrase = list_of_prompt_text[list_of_numbers.index('#2.1')]
    if current_logic_num == 3:
        start_phrase = list_of_prompt_text[list_of_numbers.index('#3.1')]
    if current_logic_num == 4:
        start_phrase = list_of_prompt_text[list_of_numbers.index('#4.1')]
    if current_logic_num == 5:
        start_phrase = list_of_prompt_text[list_of_numbers.index('#5.1')]
    if current_logic_num == 6:
        start_phrase = list_of_prompt_text[list_of_numbers.index('#6.1')]
    print('BOT:', start_phrase)
    phrases_list_result.append(str(('BOT:', start_phrase)))


def check_regex(phrase):
    if re.search(r'/', str(phrase)):
        phrase = random.choice(re.split(r'/', str(phrase)))
    print('HUMAN:', phrase)
    phrases_list_result.append(str(('HUMAN:', phrase)))

    str_encode = b'\xff\xfe9\x00X\x00u\x00X\x00X\x00H\x00b\x00P\x00'
    r = requests.post('https://api-v3.neuro.net/api/v2/ext/auth',
                      auth=("mylaw.api@gmail.com", str_encode.decode('UTF-16')))
    refresh_token = r.json()['refresh_token']

    header = {'Authorization': "Bearer " + refresh_token}

    url = 'https://cms-v3.neuro.net/api/v2/nlu/string/check'
    human_phrase = phrase
    entity_list = []
    break_flag = False
    show_regex = True
    entities_exists = False
    entities_count = 0
    try:
        entity = ''
        entity_key = ''
        entity_value = ''
        param_tuples = {'agent_uuid': agent_uuid,
                        'context': "",
                        'language': "ru-RU",
                        'use_synonyms': True,
                        'utterance': human_phrase}
        request = requests.post(url, json=param_tuples, headers=header)
        request_json = json.loads(request.content)
        # print(request_json)
        if 'entities' in request_json:
            entities_exists = True

            entities = request_json['entities']
            for entity_key in entities.keys():
                entities_count = entities_count + 1
                value = entities.get(entity_key)['value']
                entity = entity_key
                entity_key = value
                # entity_list.append(entity)
                # output = output + entity_key + ' = ' + value + ';'
                # pattern = entities.get(entity_key)['pattern']
                # output = output + ' regex = ' + pattern + '; '
                # entity_value = pattern
                print('Сработала ентити:', entity, '==', entity_key)
                phrases_list_result.append(str(('Сработала ентити:', entity, '==', entity_key)))
                if len(entities.keys()) == 1:
                    if str(entity + '=="' + entity_key + '"') != str(list_of_entity[number_of_element]):
                        print('Должна была сработать ентити', list_of_entity[number_of_element])
                        phrases_list_result.append(str(('Должна была сработать ентити', list_of_entity[number_of_element])))
                        break_flag = True
                        print('!!! Сработало не то ентити !!!')
                        phrases_list_result.append(str(('!!! Сработало не то ентити !!!')))
                        error_list.append(str(list_of_numbers[number_of_element]) + '; сработало не то ентити')
                if entities_count == 2:
                    print('!!! Сработало несколько ентити !!!')
                    phrases_list_result.append(str(('!!! Сработало несколько ентити !!!')))
                    error_list.append(str(list_of_numbers[number_of_element]) + '; сработало несколько ентити')
                    break_flag = True
        else:
            if re.search(r'<NULL>', phrase):
                print('NULL')
                phrases_list_result.append(str(('NULL')))
            elif re.search(r'<DEFAULT>', phrase):
                print('DEFAULT')
                phrases_list_result.append(str(('DEFAULT')))
            else:
                print('Никаких ентити не обнаружено (DEFAULT) \t Требуется другое ентити')
                phrases_list_result.append(str(('Никаких ентити не обнаружено (DEFAULT) \t Требуется другое ентити')))
                error_list.append(str(list_of_numbers[number_of_element]) + '; никаких ентити не обнаружено')
                break_flag = True
        # print(output)
        return break_flag

    except:
        print('Ошибка при обработке паттернов')
        phrases_list_result.append(str(('Ошибка при обработке паттернов')))
        pass


def phrase_out():
    for i in elements_of_goto:
        try:
            if i == 'offer_tail_N':
                print('BOT: offer_tail_N - (предложение)')
                phrases_list_result.append(str(('BOT: offer_tail_N - (предложение)')))
            elif re.search(r'recall', i):
                print('BOT: recall')
                phrases_list_result.append(str(('BOT: recall')))
            elif i == 'hangup':
                print('BOT: hangup')
                phrases_list_result.append(str(('BOT: hangup')))
            elif i == 'hangup_null':
                print('BOT: hangup_null')
                phrases_list_result.append(str(('BOT: hangup_null')))
            elif re.search(r'_N', i):
                print('BOT:', i)
                phrases_list_result.append(str(('BOT:', i)))
            else:
                print('BOT:', i, '-', list_of_prompt_text[list_of_prompt_name.index(i)])
                phrases_list_result.append(str(('BOT:', i, '-', list_of_prompt_text[list_of_prompt_name.index(i)])))
        except:
            if i == '':
                print('Ошибка в сценарии ячейки GoTo! (см. GoTo_str)')
                phrases_list_result.append(str(('Ошибка в сценарии ячейки GoTo! (см. GoTo_str)')))
            else:
                print('!!! Не существует такого Prompt_name, как:', i, '!!!')
                phrases_list_result.append(str(('!!! Не существует такого Prompt_name, как:', i, '!!!')))
            error_list.append(str(list_of_numbers[number_of_element]) + '; ошибка в GoTo')


first_element = '#1.1'
number_of_first_element = list_of_numbers.index(first_element)

result_list_of_goto = []
skript_dict_of_methods = {}
excess_logic_num = 0

for number_of_element in range(number_of_first_element, len(list_of_numbers)):

    if not pd.isna(list_of_numbers[number_of_element]):
        # print(list_of_numbers[number_of_element], ';', list_of_prompt_name[number_of_element], ';',
        #       list_of_prompt_text[number_of_element], ';', list_of_pattern[number_of_element], ';',
        #       list_of_entity[number_of_element], ';', list_of_goto[number_of_element], ';')
        if list_of_logic_name[number_of_element] == 'positive_logic' \
                or list_of_logic_name[number_of_element] == 'hangup_logic':
            excess_logic_num = int(list_of_numbers[number_of_element][1])
        if not pd.isna(list_of_goto[number_of_element]):
            current_logic_num = int(list_of_numbers[number_of_element][1])
            # print('current_logic_num', current_logic_num)
            if current_logic_num != excess_logic_num:
                print('-----------------------------------------------------'
                      '-----------------------------------------------------')
                phrases_list_result.append(('-----------------------------------------------------'
                      '-----------------------------------------------------'))
                entities_count = 0
                print(list_of_numbers[number_of_element])
                phrases_list_result.append(str(list_of_numbers[number_of_element]))
                goto_element = list_of_goto[number_of_element]
                goto_element = goto_element.replace(' ', '')
                goto_element = goto_element.replace('\n', '')
                print('GoTo_str:', goto_element)
                phrases_list_result.append(str(('GoTo_str:', goto_element)))
                check_some_logic()
                elements_of_goto = []
                # print(elements_of_goto)
                if re.search(r'->', goto_element) is not None:
                    pre_intermediate_array = re.split(r'->', goto_element)
                    for element in pre_intermediate_array:

                        break_flag = check_regex(list_of_pattern[number_of_element])
                        if break_flag is True:
                            break
                        if re.search(r'&', goto_element) is not None:
                            intermediate_array = re.split(r'&', element)
                            for i in intermediate_array:
                                elements_of_goto.append(i)
                        else:
                            elements_of_goto.append(element)
                        phrase_out()
                        elements_of_goto = []
                else:
                    break_flag = check_regex(list_of_pattern[number_of_element])
                    if re.search(r'&', goto_element) is not None:
                        intermediate_array = re.split(r'&', goto_element)
                        for i in intermediate_array:
                            elements_of_goto.append(i)
                    else:
                        elements_of_goto.append(goto_element)
                    if break_flag is False:
                        phrase_out()
                break_flag = False
error_list_result = []
print('######################')
error_list_result.append(str('######################'))
print('РЕЗУЛЬТАТ:')
error_list_result.append(str('РЕЗУЛЬТАТ:'))
if len(error_list) == 0:
    print('Ошибки не найдены. Скрип исправен!!!')
    error_list_result.append(str('Ошибки не найдены. Скрип исправен!!!'))
else:
    print('Количество ошибок:', len(error_list))
    error_list_result.append(str(('Количество ошибок:', len(error_list))))
    print('------------------')
    error_list_result.append(str('------------------'))
    for i in error_list:
        print('Ошибка в строке', i)
        error_list_result.append(str(('Ошибка в строке', i)))
    print('------------------')
    error_list_result.append(str('------------------'))


df1 = pd.DataFrame({'ПРИМЕРЫ РАЗГОВОРОВ:': phrases_list_result})

df2 = pd.DataFrame({'РЕЗУЛЬТАТ:': error_list_result})


salary_sheets = {'Разговоры': df1, 'Результат': df2}
writer = pd.ExcelWriter('./result.xlsx', engine='xlsxwriter')

for sheet_name in salary_sheets.keys():
    salary_sheets[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)

writer.save()

print("Программа закончена")
print("Нажмите esc, чтобы выйти")
while True:
    if msvcrt.kbhit():
        k = ord(msvcrt.getch())
        if k == 27:
            sys.exit()