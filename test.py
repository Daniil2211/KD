import json
import re
import requests


def get_module_by_str(my_str, my_mass):
    # print(f'my_str - {my_str}')
    my_str = my_str.replace('(', '\(')
    my_str = my_str.replace(')', '\)')
    needed_str = ''
    for i in my_mass:
        if re.search(my_str, i):
            if re.search(f'{my_str}\r\n#', i):
                continue
            else:
                needed_str = i
                break
    if needed_str == '':
        needed_str = 'None'
    return needed_str


def get_function_by_name(my_str, my_mass):
    function = ''
    for i in my_mass:
        i_items = i.split('\r\n')
        # print(i_items[0])
        if f'{my_str}:' == i_items[0]:
            print(f'Function {my_str} found!\n')
            function = i
            break
    if function == '':
        function = 'None'
    return function

def get_prev_str_in_mass_from_module_by_cur_str(my_str, my_mass):
    previous_item = ''
    main_logic_name = ''
    # print('RESULT', my_str, 'RES', my_mass)
    for e in my_mass:
        first_item = e
        # if first_item == my_str:
        if first_item == my_str:
            main_logic_name = previous_item.replace(' ', '')
            # print(f'!!! main_logic_name is {main_logic_name} !!!')
            break
        previous_item = e
    if main_logic_name == '':
        main_logic_name = 'None'
    return main_logic_name

input_agent_uuid = '0bd4418a-1a2a-448d-9c09-1a86f57d18e8'
# input_agent_uuid = 'dd1bf28b-68a5-4cf7-b305-791df54886d2'

try:
    str_encode = b'\xff\xfe9\x00X\x00u\x00X\x00X\x00H\x00b\x00P\x00'
    # r = requests.post('https://api-v3.neuro.net/api/v2/ext/auth',
    #                   auth=("mylaw.api@gmail.com", str_encode.decode('UTF-16')))
    r = requests.post('https://api-v3.neuro.net/api/v2/ext/auth',
                      auth=("mendorill@kd-systems.ru", 'ZFBA6mR3Jf'))
    refresh_token = r.json()['refresh_token']
except requests.ConnectionError:
    print(r.json())

try:
    print('Получение агента...')
    url = f'https://cms-v3.neuro.net/api/v2/logic/logic_unit/default?agent_uuid=dd1bf28b-68a5-4cf7-b305-791df54886d2'
    header = {'Authorization': "Bearer " + refresh_token,
              'Content-Type': 'application/json'}

    r = requests.get(url, headers=header)
    result = r.json()
except requests.ConnectionError:
    print("Ошибка при получении агентa!")

class MyString:
    def __init__(self, phrases):
        self.phrases = phrases
        self.current = 0


def get_regex_result(input_str, uuid):
    if input_str == '':
        print('HUMAN: silence')
    else:
        print('input_str:', input_str)
    url = 'https://cms-v3.neuro.net/api/v2/nlu/string/check'
    human_phrase = input_str
    entities_count = 0
    agent_uuid = uuid
    if input_str == '':
        return 'silence', 'silence'
    try:
        param_tuples = {'agent_uuid': agent_uuid,
                        'context': "",
                        'language': "ru-RU",
                        'use_synonyms': True,
                        'utterance': human_phrase}
        request = requests.post(url, json=param_tuples, headers=header)
        request_json = json.loads(request.content)
        if 'entities' in request_json:
            entities = request_json['entities']
            for entity_key in entities.keys():
                entities_count = entities_count + 1
                value = entities.get(entity_key)['value']
                entity = entity_key
                entity_key = value
                print('Сработала ентити:', entity, '==', entity_key)
            return entity, entity_key
        else:
            return 'None', 'None'
    except:
        print('Ошибка при обработке паттернов')
        pass


def check_logic_by_regex_result(input_logic, reg_res_value, reg_res_value_key):
    has_entity_flag = False
    my_res = 'None'
    reg_res_val = f'r.has_entity(\'{reg_result_value}\'):'

    # print('reg_res_value:', reg_res_value)

    use_logic = input_logic.split(f'\r\n    if ')

    if reg_res_value == 'silence':
        for i in use_logic:
            if re.search(f'not r:', i):
                my_res = get_prev_str_in_mass_from_module_by_cur_str('            return', i.split('\r\n'))
                return my_res


    if re.search('\(', reg_res_val):
        use_reg_res = reg_res_val.replace(')', '\)')
        use_reg_res = use_reg_res.replace('(', '\(')
    else:
        use_reg_res = reg_res_val

    sub_muss = []
    for i in use_logic:
        if re.search(use_reg_res, i):
            if re.search(f'r.entity\(\'{reg_res_value}\'\) == \'{reg_res_value_key}\'', i):
                my_res = get_prev_str_in_mass_from_module_by_cur_str('                return', i.split('\r\n'))
                if my_res == 'None':
                    my_res = get_prev_str_in_mass_from_module_by_cur_str('            return', i.split('\r\n'))
                if my_res == 'return':
                    my_res = get_prev_str_in_mass_from_module_by_cur_str('                return', i.split('\r\n'))
                sub_muss = i.split('\r\n')
                break

    if re.search('nn.env', my_res):
        my_res = my_res.replace(',', ', ')
        my_st = f'                {my_res}'
        my_res = get_prev_str_in_mass_from_module_by_cur_str(my_st, sub_muss)

    if my_res == 'None':
        my_res = get_prev_str_in_mass_from_module_by_cur_str(f'    return', input_logic.split('\r\n'))

    return my_res

# nn.env('SpecialEntityList', 'false')

def do_module(my_module):
    # print(my_module)
    sub_res = get_prev_str_in_mass_from_module_by_cur_str(f'    pass', my_module.split('\r\n')).replace('return', '')
    my_res = get_prev_str_in_mass_from_module_by_cur_str(f'    return {sub_res}', my_module.split('\r\n'))
    # print('my_res:', my_res)
    if my_res == 'None':
        my_res = get_prev_str_in_mass_from_module_by_cur_str(f'    return', my_module.split('\r\n'))
    return my_res, sub_res

# повторите; я занят; что за компания; да мне интересно; я не хочу
input_string = 'привет/повторите/хорошо/согласен'
input_mass = MyString(input_string.split('/'))
# input_mass.current = input_mass.current + 1


print('Logic name:', result['name'])
python_code = str(result['python_code'])

str_mass = python_code.split('def ')

i_str = get_module_by_str(f'main_online():', str_mass)
i_items = i_str.split('\r\n')
main_function_name = get_prev_str_in_mass_from_module_by_cur_str(f'    return', i_items)
print(f'main_function_name is {main_function_name}')

main_module = get_function_by_name(main_function_name, str_mass)

# input_mass.current = input_mass.current + 1
main_logic_name = get_prev_str_in_mass_from_module_by_cur_str(f'    pass', main_module.split('\r\n')).replace('return', '')

# main_logic_name = 'question1_logic(r)'

print('START:')
bot_say = get_prev_str_in_mass_from_module_by_cur_str(f'    return {main_logic_name}', main_module.split('\r\n'))
print(f'BOT: {bot_say}')
print(f'Main logic name is {main_logic_name}')
reg_result_value, reg_result_value_key = get_regex_result(input_mass.phrases[input_mass.current], input_agent_uuid)
input_mass.current = input_mass.current + 1

main_logic_module = get_module_by_str(f'{main_logic_name}:', str_mass)
next_step = check_logic_by_regex_result(main_logic_module, f'{reg_result_value}', f'{reg_result_value_key}')
my_module = get_module_by_str(f'{next_step}:', str_mass)
action_in_logic, next_logic = do_module(my_module)
print(f'{main_logic_name} -> {action_in_logic}')

while True:
    print('\nNext step in logic ', next_logic)
    cur_logic_name = next_logic
    # bot_say = get_prev_str_in_mass_from_module_by_cur_str(f'    return {cur_logic_name}', main_module.split('\r\n'))
    # print(f'BOT: {bot_say}')
    # print(f'Main logic name is {cur_logic_name}')

    reg_result_value, reg_result_value_key = get_regex_result(input_mass.phrases[input_mass.current], input_agent_uuid)
    input_mass.current = input_mass.current + 1

    cur_logic_module = get_module_by_str(f'{cur_logic_name}:', str_mass)
    next_step = check_logic_by_regex_result(cur_logic_module, f'{reg_result_value}', f'{reg_result_value_key}')
    print('next_step:', next_step)
    if re.search('manager', next_step):
        break
    elif re.search('expert', next_step):
        break
    my_module = get_module_by_str(f'{next_step}:', str_mass)
    action_in_logic, next_logic = do_module(my_module)
    print(f'{cur_logic_name} -> {action_in_logic}')

    if (input_mass.current >= len(input_mass.phrases)):
        break
print('END.')