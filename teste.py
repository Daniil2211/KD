from time import sleep
import datetime
from datetime import timedelta
import pytz

if __name__ == '__main__':
    import libneuro

    nn = libneuro.NeuroNetLibrary()
    nlu = libneuro.NeuroNluLibrary()
    nv = libneuro.NeuroVoiceLibrary()
    InvalidCallStateError = libneuro.InvalidCallStateError
    check_call_state = libneuro.check_call_state


def main():
    nn.env('flag', 'test_flag')
    nn.env('duration', 0)
    nn.call('+7' + nn.dialog['msisdn'], entry_point='main_online_container',
            on_success_call='after_call_success',
            on_failed_call='after_call_fail',
            proto_additional={
                'caller_id': '74951285170',
                'Remote-Party-ID': '<tel:74951285170>;party=calling;screen=yes;privacy=off',
            }, )


def main_online_container():
    try:
        main_online()
    except InvalidCallStateError as e:
        nn.log("Звонок завершен, пропускается выполнение функций")
        nn.log("Exception", str(e))
    except Exception as e:
        nn.log("Exception", str(e))
    finally:
        call_start_time = nn.env('call_start_time')
        Msk = pytz.timezone('Europe/Moscow')
        input_format = '%Y-%m-%dT%H:%M:%S.%f'
        datetime_call_start_time = datetime.datetime.strptime(call_start_time, input_format)
        nn.env('call_start', datetime_call_start_time.astimezone(Msk).strftime("%d-%m-%Y %H:%M:%S"))
        nn.log('Local time', datetime_call_start_time.astimezone(Msk).isoformat())
        nn.log('Local time', datetime_call_start_time.astimezone(Msk).strftime("%d-%m-%Y %H:%M:%S"))
        call_uuid = nn.env('call_uuid')
        # TODO: исправить тут
        nn.env('call_record',
               f"https://cms-v3.neuro.net/player?url=/api/v2/log/call/stream/{call_uuid}")
        if not nn.env('duration'):
            nn.env('duration', nv.get_call_duration())
        if nn.env('duration') == 0:
            nn.env('duration', nv.get_call_duration())
        nn.log('duration', nv.get_call_duration())
        nn.env('call_transcript', nv.get_call_transcription(
            return_format=nv.TRANSCRIPTION_FORMAT_TXT))
        nn.log('call_transcript', nv.get_call_transcription(
            return_format=nv.TRANSCRIPTION_FORMAT_TXT))
        nn.log('call_uuid', call_uuid)
        # TODO: исправить тут
        nn.log('call_record',
               f"https://cms-v3.neuro.net/player?url=/api/v2/log/call/stream/{call_uuid}")
        nn.log('attempt', nn.env('attempt'))
        nn.log('status', nn.env('status'))
        nn.log('result', nn.env('result'))


def main_online():
    nn.env('recall_is_needed', 'false')
    nn.env('result', 'сброс на приветствии')
    recall_count = nn.get_recall_count()
    if not recall_count:
        recall_count = 1
    nn.log('recall_count', recall_count)
    attempt = nn.env('attempt')
    if not attempt:
        nn.env('attempt', 1)
        attempt = nn.env('attempt')
    else:
        if attempt >= recall_count:
            nn.log('Использованы все попытки перезвонов')
            nn.dump()

            nn.dialog.result = nn.RESULT_DONE
            return
        attempt = attempt + 1
        nn.env('attempt', attempt)
    nn.log('attempt', attempt)
    nv.background('office_sound')
    tube_main()
    return


@check_call_state(nv)
def tube_logic(r):
    nn.log('unit', 'tube_logic')
    tube_logic_exec_count = nn.env('tube_logic_exec_count')
    if not tube_logic_exec_count:
        nn.env('tube_logic_exec_count', 1)
    else:
        tube_logic_exec_count = tube_logic_exec_count + 1
        nn.env('tube_logic_exec_count', tube_logic_exec_count)
        if tube_logic_exec_count and tube_logic_exec_count > 10:
            nn.log("Recursive execution detected")
            return
    # #1.2
    if not r:
        nn.log('condition', 'NULL')
        nn.env('result', 'NULL - молчание от клиента')
        tube_logic_NULL_NULL_count = nn.env('tube_logic_NULL_NULL_count')
        if not tube_logic_NULL_NULL_count:
            nn.env('tube_logic_NULL_NULL_count', 1)
            tube_logic_NULL_NULL_count = 1
        else:
            tube_logic_NULL_NULL_count = tube_logic_NULL_NULL_count + 1
            nn.env('tube_logic_NULL_NULL_count', tube_logic_NULL_NULL_count)
        if tube_logic_NULL_NULL_count == 1:
            tube_null_RETURN_LOGIC()
            return
        else:
            hangup_null_HANGUP()
            nn.env('recall_is_needed', 'true')
            return
        return
    # #1.3
    if not r.has_entities():
        nn.log('condition', 'DEFAULT')
        call_number = nn.env('call_number')
        if not call_number:
            call_number = '1'
        if call_number == '1':
            hello_main_1_RETURN_LOGIC()
            return
        else:
            hello_main_2_RETURN_LOGIC()
            return
    # #1.4
    if r.has_entity('voicemail'):
        if r.entity('voicemail') == 'true':
            nn.log('condition', 'voicemail=="true"')
            nn.env('result', 'автоответчик')
            hangup_HANGUP()
            nn.env('recall_is_needed', 'true')
            return


# #1.1
# Здравствуйте!
@check_call_state(nv)
def tube_main():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'tube_main')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['voicemail']) as r:
        nv.say('tube_main')
    return tube_logic(r)
    pass


# #1.2
# Алло..., меня слышно?
@check_call_state(nv)
def tube_null_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'tube_null')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['voicemail']) as r:
        nv.say('tube_null')
    return tube_logic(r)
    pass


@check_call_state(nv)
def hello_logic(r):
    nn.log('unit', 'hello_logic')
    hello_logic_exec_count = nn.env('hello_logic_exec_count')
    if not hello_logic_exec_count:
        nn.env('hello_logic_exec_count', 1)
    else:
        hello_logic_exec_count = hello_logic_exec_count + 1
        nn.env('hello_logic_exec_count', hello_logic_exec_count)
        if hello_logic_exec_count and hello_logic_exec_count > 10:
            nn.log("Recursive execution detected")
            return
    # #2.3
    if not r:
        nn.log('condition', 'NULL')
        nn.env('result', 'NULL - молчание от клиента')
        hello_logic_NULL_NULL_count = nn.env('hello_logic_NULL_NULL_count')
        if not hello_logic_NULL_NULL_count:
            nn.env('hello_logic_NULL_NULL_count', 1)
            hello_logic_NULL_NULL_count = 1
        else:
            hello_logic_NULL_NULL_count = hello_logic_NULL_NULL_count + 1
            nn.env('hello_logic_NULL_NULL_count', hello_logic_NULL_NULL_count)
        if hello_logic_NULL_NULL_count == 1:
            hello_null_RETURN_LOGIC()
            return
        else:
            hangup_null_HANGUP()
            nn.env('recall_is_needed', 'true')
            return
        return
    # #2.4
    if not r.has_entities():
        nn.log('condition', 'DEFAULT')
        nn.env('result', 'дефолтное возражение')
        hello_logic_DEFAULT_DEFAULT_count = nn.env('hello_logic_DEFAULT_DEFAULT_count')
        if not hello_logic_DEFAULT_DEFAULT_count:
            nn.env('hello_logic_DEFAULT_DEFAULT_count', 1)
            hello_logic_DEFAULT_DEFAULT_count = 1
        else:
            hello_logic_DEFAULT_DEFAULT_count = hello_logic_DEFAULT_DEFAULT_count + 1
            nn.env('hello_logic_DEFAULT_DEFAULT_count', hello_logic_DEFAULT_DEFAULT_count)
        if hello_logic_DEFAULT_DEFAULT_count == 1:
            hello_default_RETURN_LOGIC()
            return
        else:
            question1_main_RETURN_LOGIC()
            return
        return
    # #2.5
    if r.has_entity('voicemail'):
        if r.entity('voicemail') == 'true':
            nn.log('condition', 'voicemail=="true"')
            nn.env('result', 'автоответчик')
            hangup_HANGUP()
            nn.env('recall_is_needed', 'true')
            return
    # #2.6
    if r.has_entity('dont_disturb_child'):
        if r.entity('dont_disturb_child') == 'true':
            nn.log('condition', 'dont_disturb_child=="true"')
            nn.env('result', 'ребенок')
            just_2_hangup_HANGUP()
            return
    # #2.7
    if r.has_entity('dont_disturb_minor'):
        if r.entity('dont_disturb_minor') == 'true':
            nn.log('condition', 'dont_disturb_minor=="true"')
            nn.env('result', 'несовершеннолетний')
            just_2_hangup_HANGUP()
            return
    # #2.8
    if r.has_entity('wrong_time_sick'):
        if r.entity('wrong_time_sick') == 'true':
            nn.log('condition', 'wrong_time_sick=="true"')
            nn.env('result', 'абонент болеет')
            hello_logic_wrong_time_sick_true_count = nn.env('hello_logic_wrong_time_sick_true_count')
            if not hello_logic_wrong_time_sick_true_count:
                nn.env('hello_logic_wrong_time_sick_true_count', 1)
                hello_logic_wrong_time_sick_true_count = 1
            else:
                hello_logic_wrong_time_sick_true_count = hello_logic_wrong_time_sick_true_count + 1
                nn.env('hello_logic_wrong_time_sick_true_count', hello_logic_wrong_time_sick_true_count)
            if hello_logic_wrong_time_sick_true_count == 1:
                hello_sick_1_RETURN_LOGIC()
                return
            else:
                hello_sick_2_JUST_SAY()
                nn.env('recall_is_needed', 'true_72')
                hangup_HANGUP()
                return
            return
    # #2.10
    if r.has_entity('wrong_time_wheel'):
        if r.entity('wrong_time_wheel') == 'true':
            nn.log('condition', 'wrong_time_wheel=="true"')
            nn.env('result', 'абонент за рулем')
            hello_logic_wrong_time_wheel_true_count = nn.env('hello_logic_wrong_time_wheel_true_count')
            if not hello_logic_wrong_time_wheel_true_count:
                nn.env('hello_logic_wrong_time_wheel_true_count', 1)
                hello_logic_wrong_time_wheel_true_count = 1
            else:
                hello_logic_wrong_time_wheel_true_count = hello_logic_wrong_time_wheel_true_count + 1
                nn.env('hello_logic_wrong_time_wheel_true_count', hello_logic_wrong_time_wheel_true_count)
            if hello_logic_wrong_time_wheel_true_count == 1:
                hello_sick_1_RETURN_LOGIC()
                return
            else:
                hello_wheel_JUST_SAY()
                nn.env('recall_is_needed', 'true')
                hangup_HANGUP()
                return
            return
    # #2.11
    if r.has_entity('callback'):
        if r.entity('callback') == 'true':
            nn.log('condition', 'callback=="true"')
            nn.env('result', 'просьба перезвонить')
            hangup_recall_HANGUP()
            return
    # #2.12
    if r.has_entity('wrong_time'):
        if r.entity('wrong_time') == 'true':
            nn.log('condition', 'wrong_time=="true"')
            nn.env('result', 'клиент занят')
            hangup_recall_HANGUP()
            return
    # #2.13
    if r.has_entity('callback_phone'):
        if r.entity('callback_phone') == 'true':
            nn.log('condition', 'callback_phone=="true"')
            nn.env('result', 'у клиента проблемы с телефоном')
            hangup_recall_HANGUP()
            return
    # #2.14
    if r.has_entity('mistake'):
        if r.entity('mistake') == 'true':
            nn.log('condition', 'mistake=="true"')
            nn.env('result', 'ошибочно позвонили')
            just_2_hangup_HANGUP()
            return
    # #2.15
    if r.has_entity('dont_disturb'):
        if r.entity('dont_disturb') == 'true':
            nn.log('condition', 'dont_disturb=="true"')
            nn.env('result', 'больше не звонить')
            just_2_hangup_HANGUP()
            return
    # #2.16
    if r.has_entity('probable'):
        if r.entity('probable') == 'true':
            nn.log('condition', 'probable=="true"')
            nn.env('result', 'агрессия')
            just_2_hangup_HANGUP()
            return
    # #2.17
    if r.has_entity('robot'):
        if r.entity('robot') == 'true':
            nn.log('condition', 'robot=="true"')
            nn.env('result', 'распознан робот')
            hello_robot_JUST_SAY()
            question1_main_RETURN_LOGIC()
            return
    # #2.18
    if r.has_entity('what_surname'):
        if r.entity('what_surname') == 'true':
            nn.log('condition', 'what_surname=="true"')
            nn.env('result', 'вопрос про имя')
            hello_name_JUST_SAY()
            question1_main_RETURN_LOGIC()
            return
    # #2.19
    if r.has_entity('what_company'):
        if r.entity('what_company') == 'true':
            nn.log('condition', 'what_company=="true"')
            nn.env('result', 'вопрос какая компания')
            hello_what_company_JUST_SAY()
            question1_main_RETURN_LOGIC()
            return
    # #2.20
    if r.has_entity('how_long'):
        if r.entity('how_long') == 'true':
            nn.log('condition', 'how_long=="true"')
            nn.env('result', 'вопрос по времени беседы')
            hello_how_long_JUST_SAY()
            question1_main_RETURN_LOGIC()
            return
    # #2.21
    if r.has_entity('purpose_call'):
        if r.entity('purpose_call') == 'true':
            nn.log('condition', 'purpose_call=="true"')
            nn.env('result', 'вопрос о цели звонка')
            question1_main_RETURN_LOGIC()
            return
    # #2.22
    if r.has_entity('where_address'):
        if r.entity('where_address') == 'true':
            nn.log('condition', 'where_address=="true"')
            nn.env('result', 'вопрос о месте нахождения офиса')
            hello_city_JUST_RETURN()
            question1_main_RETURN_LOGIC()
            return
    # #2.23
    if r.has_entity('wait_bit'):
        if r.entity('wait_bit') == 'true':
            nn.log('condition', 'wait_bit=="true"')
            nn.env('result', 'абонент просит подождать')
            hello_logic_wait_bit_true_count = nn.env('hello_logic_wait_bit_true_count')
            if not hello_logic_wait_bit_true_count:
                nn.env('hello_logic_wait_bit_true_count', 1)
                hello_logic_wait_bit_true_count = 1
            else:
                hello_logic_wait_bit_true_count = hello_logic_wait_bit_true_count + 1
                nn.env('hello_logic_wait_bit_true_count', hello_logic_wait_bit_true_count)
            if hello_logic_wait_bit_true_count == 1:
                hello_wait_bit_JUST_RETURN()
                hello_null_RETURN_LOGIC()
                return
            else:
                hangup_null_HANGUP()
                nn.env('recall_is_needed', 'true')
                return
            return
    # #2.24
    if r.has_entity('repeat'):
        if r.entity('repeat') == 'true':
            nn.log('condition', 'repeat=="true"')
            nn.env('result', 'просьба повторить')
            hello_repeat_JUST_SAY()
            question1_main_RETURN_LOGIC()
            return
    # #2.25
    if r.has_entity('no'):
        if r.entity('no') == 'true':
            nn.log('condition', 'no=="true"')
            nn.env('result', 'у клиента нет времени на разговор')
            hangup_recall_HANGUP()
            return
    # #2.26
    if r.has_entity('dont_know'):
        if r.entity('dont_know') == 'true':
            nn.log('condition', 'dont_know=="true"')
            nn.env('result', 'клиент сомневается')
            hello_how_long_JUST_SAY()
            question1_main_RETURN_LOGIC()
            return
    # #2.27
    if r.has_entity('yes'):
        if r.entity('yes') == 'true':
            nn.log('condition', 'yes=="true"')
            nn.env('result', 'клиент согласен на разговор')
            question1_main_RETURN_LOGIC()
            return
    # #2.28
    if r.has_entity('agree'):
        if r.entity('agree') == 'true':
            nn.log('condition', 'agree=="true"')
            nn.env('result', 'клиент согласен на разговор')
            question1_main_RETURN_LOGIC()
            return
    # #2.29
    if r.has_entity('listening'):
        if r.entity('listening') == 'true':
            nn.log('condition', 'listening=="true"')
            nn.env('result', 'клиент согласен на разговор')
            question1_main_RETURN_LOGIC()
            return
    # #2.30
    if r.has_entity('speak'):
        if r.entity('speak') == 'true':
            nn.log('condition', 'speak=="true"')
            nn.env('result', 'клиент согласен на разговор')
            question1_main_RETURN_LOGIC()
            return
    # #2.31
    if r.has_entity('more_detail'):
        if r.entity('more_detail') == 'true':
            nn.log('condition', 'more_detail=="true"')
            nn.env('result', 'клиент согласен на разговор')
            question1_main_RETURN_LOGIC()
            return
    # #2.32
    if r.has_entity('got_acquainted'):
        if r.entity('got_acquainted') == 'true':
            nn.log('condition', 'got_acquainted=="true"')
            nn.env('result', 'клиент знакомился с Своё Родное')
            question2_main_RETURN_LOGIC()
            return
    # #2.33
    if r.has_entity('postponed_product'):
        if r.entity('postponed_product') == 'true':
            nn.log('condition', 'postponed_product=="true"')
            nn.env('result', 'клиент отложил для себя товар')
            question2_main_RETURN_LOGIC()
            return
    # #2.34
    if r.has_entity('colleague'):
        if r.entity('colleague') == 'true':
            nn.log('condition', 'colleague=="true"')
            nn.env('result', 'номер телефона коллеги')
            just_2_hangup_HANGUP()
            return
    # #2.35
    if r.has_entity('annoying_robots'):
        if r.entity('annoying_robots') == 'true':
            nn.log('condition', 'annoying_robots=="true"')
            nn.env('result', 'роботы раздражают')
            expert_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
    # #2.36
    if r.has_entity('connect_operator'):
        if r.entity('connect_operator') == 'true':
            nn.log('condition', 'connect_operator=="true"')
            nn.env('result', 'просьба перевести на живого человека')
            expert_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
    # #2.37
    if r.has_entity('bad_connection'):
        if r.entity('bad_connection') == 'true':
            nn.log('condition', 'bad_connection=="true"')
            nn.env('result', 'плохая связь')
            hello_logic_bad_connection_true_count = nn.env('hello_logic_bad_connection_true_count')
            if not hello_logic_bad_connection_true_count:
                nn.env('hello_logic_bad_connection_true_count', 1)
                hello_logic_bad_connection_true_count = 1
            else:
                hello_logic_bad_connection_true_count = hello_logic_bad_connection_true_count + 1
                nn.env('hello_logic_bad_connection_true_count', hello_logic_bad_connection_true_count)
            if hello_logic_bad_connection_true_count == 1:
                hello_null_RETURN_LOGIC()
                return
            else:
                hangup_answers_HANGUP()
                nn.env('recall_is_needed', 'true')
                return
            return
    # #2.38
    if r.has_entity('hear_me'):
        if r.entity('hear_me') == 'true':
            nn.log('condition', 'hear_me=="true"')
            nn.env('result', 'клиент акциентирует на себе внимание')
            hello_logic_hear_me_true_count = nn.env('hello_logic_hear_me_true_count')
            if not hello_logic_hear_me_true_count:
                nn.env('hello_logic_hear_me_true_count', 1)
                hello_logic_hear_me_true_count = 1
            else:
                hello_logic_hear_me_true_count = hello_logic_hear_me_true_count + 1
                nn.env('hello_logic_hear_me_true_count', hello_logic_hear_me_true_count)
            if hello_logic_hear_me_true_count == 1:
                hello_default_RETURN_LOGIC()
                return
            else:
                hangup_answers_HANGUP()
                nn.env('recall_is_needed', 'true')
                return
            return
    # #2.39
    if r.has_entity('goodbye'):
        if r.entity('goodbye') == 'true':
            nn.log('condition', 'goodbye=="true"')
            nn.env('result', 'до свидание')
            hello_logic_goodbye_true_count = nn.env('hello_logic_goodbye_true_count')
            if not hello_logic_goodbye_true_count:
                nn.env('hello_logic_goodbye_true_count', 1)
                hello_logic_goodbye_true_count = 1
            else:
                hello_logic_goodbye_true_count = hello_logic_goodbye_true_count + 1
                nn.env('hello_logic_goodbye_true_count', hello_logic_goodbye_true_count)
            if hello_logic_goodbye_true_count == 1:
                hello_default_RETURN_LOGIC()
                return
            else:
                just_hangup_HANGUP()
                return
            return


# #2.22
# Главный офис у нас находится в Москве, но наша платформа работает по всей России.
@check_call_state(nv)
def hello_city_JUST_RETURN():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'hello_city')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'no',
                             'wrong_time_sick',
                             'dont_disturb',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'bad_connection',
                             'what_surname',
                             'dont_disturb_minor',
                             'robot',
                             'dont_know',
                             'repeat',
                             'more_detail',
                             'speak',
                             'connect_operator',
                             'callback_phone',
                             'mistake',
                             'listening',
                             'voicemail',
                             'hear_me',
                             'yes',
                             'dont_disturb_child',
                             'wait_bit',
                             'probable',
                             'purpose_call',
                             'agree',
                             'colleague',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'callback',
                             'wrong_time']) as r:
        nv.say('hello_city')
    return
    pass


# #2.20
# Разговор займет всего пару минут.
@check_call_state(nv)
def hello_how_long_JUST_SAY():
    nn.log('unit', 'hello_how_long')
    nv.say('hello_how_long')
    return
    pass


# #2.4
# Извините не раслышала, ответите на вопрос?
@check_call_state(nv)
def hello_default_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'hello_default')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'no',
                             'wrong_time_sick',
                             'dont_disturb',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'bad_connection',
                             'what_surname',
                             'dont_disturb_minor',
                             'robot',
                             'dont_know',
                             'repeat',
                             'more_detail',
                             'speak',
                             'connect_operator',
                             'callback_phone',
                             'mistake',
                             'listening',
                             'voicemail',
                             'hear_me',
                             'yes',
                             'dont_disturb_child',
                             'wait_bit',
                             'probable',
                             'purpose_call',
                             'agree',
                             'colleague',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'callback',
                             'wrong_time']) as r:
        nv.say('hello_default')
    return hello_logic(r)
    pass


# #2.8
# А Вы сможете на пару вопросов ответить?
@check_call_state(nv)
def hello_sick_1_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'hello_sick_1')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'no',
                             'wrong_time_sick',
                             'dont_disturb',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'bad_connection',
                             'what_surname',
                             'dont_disturb_minor',
                             'robot',
                             'dont_know',
                             'repeat',
                             'more_detail',
                             'speak',
                             'connect_operator',
                             'callback_phone',
                             'mistake',
                             'listening',
                             'voicemail',
                             'hear_me',
                             'yes',
                             'dont_disturb_child',
                             'wait_bit',
                             'probable',
                             'purpose_call',
                             'agree',
                             'colleague',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'callback',
                             'wrong_time']) as r:
        nv.say('hello_sick_1')
    return hello_logic(r)
    pass


# #2.24
# Звоню по поводу маркетплейса Своё Родное.
@check_call_state(nv)
def hello_repeat_JUST_SAY():
    nn.log('unit', 'hello_repeat')
    nv.say('hello_repeat')
    return
    pass


# #2.19
# Платформа маркетплейса Своё родное, фермерская продукция.
@check_call_state(nv)
def hello_what_company_JUST_SAY():
    nn.log('unit', 'hello_what_company')
    nv.say('hello_what_company')
    return
    pass


# #2.1
# Платформа Своё Родное, меня зовут Ирина. У вас есть пару минут, ответить на 2-3 вопроса?
@check_call_state(nv)
def hello_main_1_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'hello_main_1')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'no',
                             'wrong_time_sick',
                             'dont_disturb',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'bad_connection',
                             'what_surname',
                             'dont_disturb_minor',
                             'robot',
                             'dont_know',
                             'repeat',
                             'more_detail',
                             'speak',
                             'connect_operator',
                             'callback_phone',
                             'mistake',
                             'listening',
                             'voicemail',
                             'hear_me',
                             'yes',
                             'dont_disturb_child',
                             'wait_bit',
                             'probable',
                             'purpose_call',
                             'agree',
                             'colleague',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'callback',
                             'wrong_time']) as r:
        nv.say('hello_main_1')
    return hello_logic(r)
    pass


# #2.1
# Я уже звонила Вам недавно. Платформа Своё Родное. У вас есть пару минут, ответить на 2-3 вопроса?
@check_call_state(nv)
def hello_main_2_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'hello_main_2')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'no',
                             'wrong_time_sick',
                             'dont_disturb',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'bad_connection',
                             'what_surname',
                             'dont_disturb_minor',
                             'robot',
                             'dont_know',
                             'repeat',
                             'more_detail',
                             'speak',
                             'connect_operator',
                             'callback_phone',
                             'mistake',
                             'listening',
                             'voicemail',
                             'hear_me',
                             'yes',
                             'dont_disturb_child',
                             'wait_bit',
                             'probable',
                             'purpose_call',
                             'agree',
                             'colleague',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'callback',
                             'wrong_time']) as r:
        nv.say('hello_main_2')
    return hello_logic(r)
    pass


# #2.3
# Сможете ответить на пару вопросов?
@check_call_state(nv)
def hello_null_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'hello_null')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'no',
                             'wrong_time_sick',
                             'dont_disturb',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'bad_connection',
                             'what_surname',
                             'dont_disturb_minor',
                             'robot',
                             'dont_know',
                             'repeat',
                             'more_detail',
                             'speak',
                             'connect_operator',
                             'callback_phone',
                             'mistake',
                             'listening',
                             'voicemail',
                             'hear_me',
                             'yes',
                             'dont_disturb_child',
                             'wait_bit',
                             'probable',
                             'purpose_call',
                             'agree',
                             'colleague',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'callback',
                             'wrong_time']) as r:
        nv.say('hello_null')
    return hello_logic(r)
    pass


# #2.23
# Да, конечно, подожду…(ожижание 15 секунд)
@check_call_state(nv)
def hello_wait_bit_JUST_RETURN():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'hello_wait_bit')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'no',
                             'wrong_time_sick',
                             'dont_disturb',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'bad_connection',
                             'what_surname',
                             'dont_disturb_minor',
                             'robot',
                             'dont_know',
                             'repeat',
                             'more_detail',
                             'speak',
                             'connect_operator',
                             'callback_phone',
                             'mistake',
                             'listening',
                             'voicemail',
                             'hear_me',
                             'yes',
                             'dont_disturb_child',
                             'wait_bit',
                             'probable',
                             'purpose_call',
                             'agree',
                             'colleague',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'callback',
                             'wrong_time']) as r:
        nv.say('hello_wait_bit')
    return
    pass


# #2.9
# Хорошо. Выздоравливайте, а я позвоню попозже. До свидание!
@check_call_state(nv)
def hello_sick_2_JUST_SAY():
    nn.log('unit', 'hello_sick_2')
    nv.say('hello_sick_2')
    return
    pass


# #2.10
# Поняла. Хорошей дороги. Перезвоню попозже. До свидание!
@check_call_state(nv)
def hello_wheel_JUST_SAY():
    nn.log('unit', 'hello_wheel')
    nv.say('hello_wheel')
    return
    pass


# #2.18
# Меня зовут Ирина.
@check_call_state(nv)
def hello_name_JUST_SAY():
    nn.log('unit', 'hello_name')
    nv.say('hello_name')
    return
    pass


# #2.17
# Я помошник платформы Своё Родное.
@check_call_state(nv)
def hello_robot_JUST_SAY():
    nn.log('unit', 'hello_robot')
    nv.say('hello_robot')
    return
    pass


@check_call_state(nv)
def question1_logic(r):
    nn.log('unit', 'question1_logic')
    question1_logic_exec_count = nn.env('question1_logic_exec_count')
    if not question1_logic_exec_count:
        nn.env('question1_logic_exec_count', 1)
    else:
        question1_logic_exec_count = question1_logic_exec_count + 1
        nn.env('question1_logic_exec_count', question1_logic_exec_count)
        if question1_logic_exec_count and question1_logic_exec_count > 10:
            nn.log("Recursive execution detected")
            return
    # #3.2
    if not r:
        nn.log('condition', 'NULL')
        nn.env('result', 'NULL - молчание от клиента')
        question1_logic_NULL_NULL_count = nn.env('question1_logic_NULL_NULL_count')
        if not question1_logic_NULL_NULL_count:
            nn.env('question1_logic_NULL_NULL_count', 1)
            question1_logic_NULL_NULL_count = 1
        else:
            question1_logic_NULL_NULL_count = question1_logic_NULL_NULL_count + 1
            nn.env('question1_logic_NULL_NULL_count', question1_logic_NULL_NULL_count)
        if question1_logic_NULL_NULL_count == 1:
            question1_null_RETURN_LOGIC()
            return
        else:
            hangup_null_HANGUP()
            nn.env('recall_is_needed', 'true')
            return
        return
    # #3.3
    if not r.has_entities():
        nn.log('condition', 'DEFAULT')
        nn.env('result', 'озвучена причина/дефолтное возражение')
        question1_logic_DEFAULT_DEFAULT_count = nn.env('question1_logic_DEFAULT_DEFAULT_count')
        if not question1_logic_DEFAULT_DEFAULT_count:
            nn.env('question1_logic_DEFAULT_DEFAULT_count', 1)
            question1_logic_DEFAULT_DEFAULT_count = 1
        else:
            question1_logic_DEFAULT_DEFAULT_count = question1_logic_DEFAULT_DEFAULT_count + 1
            nn.env('question1_logic_DEFAULT_DEFAULT_count', question1_logic_DEFAULT_DEFAULT_count)
        if question1_logic_DEFAULT_DEFAULT_count == 1:
            question1_default_RETURN_LOGIC()
            return
        else:
            question2_main_RETURN_LOGIC()
            return
        return
    # #3.4
    if r.has_entity('voicemail'):
        if r.entity('voicemail') == 'true':
            nn.log('condition', 'voicemail=="true"')
            nn.env('result', 'автоответчик')
            nn.env('recall_is_needed', 'true')
            hangup_HANGUP()
            return
    # #3.5
    if r.has_entity('wrong_time_sick'):
        if r.entity('wrong_time_sick') == 'true':
            nn.log('condition', 'wrong_time_sick=="true"')
            nn.env('result', 'абонент болеет')
            hello_sick_2_JUST_SAY()
            hangup_HANGUP()
            nn.env('recall_is_needed', 'true')
            return
    # #3.6
    if r.has_entity('wrong_time_wheel'):
        if r.entity('wrong_time_wheel') == 'true':
            nn.log('condition', 'wrong_time_wheel=="true"')
            nn.env('result', 'абонент за рулем')
            hello_wheel_JUST_SAY()
            hangup_HANGUP()
            nn.env('recall_is_needed', 'true')
            return
    # #3.7
    if r.has_entity('callback'):
        if r.entity('callback') == 'true':
            nn.log('condition', 'callback=="true"')
            nn.env('result', 'просьба перезвонить')
            hangup_recall_HANGUP()
            return
    # #3.8
    if r.has_entity('wrong_time'):
        if r.entity('wrong_time') == 'true':
            nn.log('condition', 'wrong_time=="true"')
            nn.env('result', 'клиент занят')
            hangup_recall_HANGUP()
            return
    # #3.9
    if r.has_entity('mistake'):
        if r.entity('mistake') == 'true':
            nn.log('condition', 'mistake=="true"')
            nn.env('result', 'ошибочно позвонили')
            just_2_hangup_HANGUP()
            return
    # #3.10
    if r.has_entity('dont_disturb'):
        if r.entity('dont_disturb') == 'true':
            nn.log('condition', 'dont_disturb=="true"')
            nn.env('result', 'больше не звонить')
            just_2_hangup_HANGUP()
            return
    # #3.11
    if r.has_entity('probable'):
        if r.entity('probable') == 'true':
            nn.log('condition', 'probable=="true"')
            nn.env('result', 'агрессия')
            just_2_hangup_HANGUP()
            return
    # #3.12
    if r.has_entity('robot'):
        if r.entity('robot') == 'true':
            nn.log('condition', 'robot=="true"')
            nn.env('result', 'распознан робот')
            question1_logic_robot_true_count = nn.env('question1_logic_robot_true_count')
            if not question1_logic_robot_true_count:
                nn.env('question1_logic_robot_true_count', 1)
                question1_logic_robot_true_count = 1
            else:
                question1_logic_robot_true_count = question1_logic_robot_true_count + 1
                nn.env('question1_logic_robot_true_count', question1_logic_robot_true_count)
            if question1_logic_robot_true_count == 1:
                question1_robot_1_JUST_SAY()
                offer_end_()
                return
            elif question1_logic_robot_true_count == 2:
                question1_robot_2_JUST_RETURN()
                offer_end_()
                return
            else:
                hangup_answers_HANGUP()
                nn.env('recall_is_needed', 'true')
                return
            return
    # #3.14
    if r.has_entity('what_surname'):
        if r.entity('what_surname') == 'true':
            nn.log('condition', 'what_surname=="true"')
            nn.env('result', 'вопрос про имя')
            question1_logic_what_surname_true_count = nn.env('question1_logic_what_surname_true_count')
            if not question1_logic_what_surname_true_count:
                nn.env('question1_logic_what_surname_true_count', 1)
                question1_logic_what_surname_true_count = 1
            else:
                question1_logic_what_surname_true_count = question1_logic_what_surname_true_count + 1
                nn.env('question1_logic_what_surname_true_count', question1_logic_what_surname_true_count)
            if question1_logic_what_surname_true_count == 1:
                question1_robot_1_JUST_SAY()
                offer_end_()
                return
            elif question1_logic_what_surname_true_count == 2:
                hello_name_JUST_SAY()
                offer_end_()
                return
            else:
                hangup_answers_HANGUP()
                nn.env('recall_is_needed', 'true')
                return
            return
    # #3.15
    if r.has_entity('what_company'):
        if r.entity('what_company') == 'true':
            nn.log('condition', 'what_company=="true"')
            nn.env('result', 'вопрос какая компания')
            question1_logic_what_company_true_count = nn.env('question1_logic_what_company_true_count')
            if not question1_logic_what_company_true_count:
                nn.env('question1_logic_what_company_true_count', 1)
                question1_logic_what_company_true_count = 1
            else:
                question1_logic_what_company_true_count = question1_logic_what_company_true_count + 1
                nn.env('question1_logic_what_company_true_count', question1_logic_what_company_true_count)
            if question1_logic_what_company_true_count == 1:
                hello_what_company_JUST_SAY()
                offer_end_()
                return
            elif question1_logic_what_company_true_count == 2:
                question1_what_company_JUST_SAY()
                offer_end_()
                return
            else:
                hangup_answers_HANGUP()
                nn.env('recall_is_needed', 'true')
                return
            return
    # #3.16
    if r.has_entity('how_long'):
        if r.entity('how_long') == 'true':
            nn.log('condition', 'how_long=="true"')
            nn.env('result', 'вопрос по времени беседы')
            question1_logic_how_long_true_count = nn.env('question1_logic_how_long_true_count')
            if not question1_logic_how_long_true_count:
                nn.env('question1_logic_how_long_true_count', 1)
                question1_logic_how_long_true_count = 1
            else:
                question1_logic_how_long_true_count = question1_logic_how_long_true_count + 1
                nn.env('question1_logic_how_long_true_count', question1_logic_how_long_true_count)
            if question1_logic_how_long_true_count == 1:
                hello_how_long_JUST_SAY()
                offer_end_()
                return
            elif question1_logic_how_long_true_count == 2:
                offer_end_()
                return
            else:
                hangup_answers_HANGUP()
                nn.env('recall_is_needed', 'true')
                return
            return
    # #3.17
    if r.has_entity('purpose_call'):
        if r.entity('purpose_call') == 'true':
            nn.log('condition', 'purpose_call=="true"')
            nn.env('result', 'вопрос о цели звонка')
            question1_logic_purpose_call_true_count = nn.env('question1_logic_purpose_call_true_count')
            if not question1_logic_purpose_call_true_count:
                nn.env('question1_logic_purpose_call_true_count', 1)
                question1_logic_purpose_call_true_count = 1
            else:
                question1_logic_purpose_call_true_count = question1_logic_purpose_call_true_count + 1
                nn.env('question1_logic_purpose_call_true_count', question1_logic_purpose_call_true_count)
            if question1_logic_purpose_call_true_count == 1:
                question1_purpose_RETURN_LOGIC()
                return
            elif question1_logic_purpose_call_true_count == 2:
                offer_end_()
                return
            else:
                hangup_answers_HANGUP()
                nn.env('recall_is_needed', 'true')
                return
            return
    # #3.18
    if r.has_entity('where_address'):
        if r.entity('where_address') == 'true':
            nn.log('condition', 'where_address=="true"')
            nn.env('result', 'вопрос о месте нахождения офиса')
            question1_logic_where_address_true_count = nn.env('question1_logic_where_address_true_count')
            if not question1_logic_where_address_true_count:
                nn.env('question1_logic_where_address_true_count', 1)
                question1_logic_where_address_true_count = 1
            else:
                question1_logic_where_address_true_count = question1_logic_where_address_true_count + 1
                nn.env('question1_logic_where_address_true_count', question1_logic_where_address_true_count)
            if question1_logic_where_address_true_count == 1:
                question1_city_JUST_RETURN()
                offer_end_()
                return
            elif question1_logic_where_address_true_count == 2:
                offer_end_()
                return
            else:
                question2_main_RETURN_LOGIC()
                return
            return
    # #3.19
    if r.has_entity('what_did_you_order'):
        if r.entity('what_did_you_order') == 'true':
            nn.log('condition', 'what_did_you_order=="true"')
            nn.env('result', 'клиент уточняет, что заказал')
            question1_logic_what_did_you_order_true_count = nn.env('question1_logic_what_did_you_order_true_count')
            if not question1_logic_what_did_you_order_true_count:
                nn.env('question1_logic_what_did_you_order_true_count', 1)
                question1_logic_what_did_you_order_true_count = 1
            else:
                question1_logic_what_did_you_order_true_count = question1_logic_what_did_you_order_true_count + 1
                nn.env('question1_logic_what_did_you_order_true_count', question1_logic_what_did_you_order_true_count)
            if question1_logic_what_did_you_order_true_count == 1:
                question1_what_order_JUST_RETURN()
                offer_end_()
                return
            elif question1_logic_what_did_you_order_true_count == 2:
                offer_end_()
                return
            else:
                question2_main_RETURN_LOGIC()
                return
            return
    # #3.20
    if r.has_entity('types_transportation'):
        if r.entity('types_transportation') == 'true':
            nn.log('condition', 'types_transportation=="true"')
            nn.env('result', 'вопрос про способы доставки')
            question1_logic_types_transportation_true_count = nn.env('question1_logic_types_transportation_true_count')
            if not question1_logic_types_transportation_true_count:
                nn.env('question1_logic_types_transportation_true_count', 1)
                question1_logic_types_transportation_true_count = 1
            else:
                question1_logic_types_transportation_true_count = question1_logic_types_transportation_true_count + 1
                nn.env('question1_logic_types_transportation_true_count',
                       question1_logic_types_transportation_true_count)
            if question1_logic_types_transportation_true_count == 1:
                question1_transportation_JUST_SAY()
                offer_end_()
                return
            elif question1_logic_types_transportation_true_count == 2:
                question1_delivery_date_JUST_SAY()
                offer_end_()
                return
            else:
                question2_main_RETURN_LOGIC()
                return
            return
    # #3.21
    if r.has_entity('transport_delivery_date'):
        if r.entity('transport_delivery_date') == 'true':
            nn.log('condition', 'transport_delivery_date=="true"')
            nn.env('result', 'вопрос про срок поставки')
            question1_delivery_date_JUST_SAY()
            question2_main_RETURN_LOGIC()
            return
    # #3.22
    if r.has_entity('expensive_shipping'):
        if r.entity('expensive_shipping') == 'true':
            nn.log('condition', 'expensive_shipping=="true"')
            nn.env('result', 'дорогая доставка')
            question1_expensive_shipping_JUST_SAY()
            question2_main_RETURN_LOGIC()
            return
    # #3.23
    if r.has_entity('free_shipping'):
        if r.entity('free_shipping') == 'true':
            nn.log('condition', 'free_shipping=="true"')
            nn.env('result', 'есть ли бесплатная доставка')
            question1_expensive_shipping_JUST_SAY()
            question2_main_RETURN_LOGIC()
            return
    # #3.24
    if r.has_entity('no_free_shipping'):
        if r.entity('no_free_shipping') == 'true':
            nn.log('condition', 'no_free_shipping=="true"')
            nn.env('result', 'нет бесплатной доставки')
            question1_no_free_JUST_RETURN()
            question2_main_RETURN_LOGIC()
            return
    # #3.25
    if r.has_entity('pickup_only'):
        if r.entity('pickup_only') == 'true':
            nn.log('condition', 'pickup_only=="true"')
            nn.env('result', 'клиент не знает, где точка самовывоза')
            question1_pickup_only_JUST_RETURN()
            question2_main_RETURN_LOGIC()
            return
    # #3.26
    if r.has_entity('no_shipping'):
        if r.entity('no_shipping') == 'true':
            nn.log('condition', 'no_shipping=="true"')
            nn.env('result', 'у производителя нет доставки')
            question1_logic_no_shipping_true_count = nn.env('question1_logic_no_shipping_true_count')
            if not question1_logic_no_shipping_true_count:
                nn.env('question1_logic_no_shipping_true_count', 1)
                question1_logic_no_shipping_true_count = 1
            else:
                question1_logic_no_shipping_true_count = question1_logic_no_shipping_true_count + 1
                nn.env('question1_logic_no_shipping_true_count', question1_logic_no_shipping_true_count)
            if question1_logic_no_shipping_true_count == 1:
                question1_no_shipping_1_JUST_RETURN()
                question2_main_RETURN_LOGIC()
                return
            elif question1_logic_no_shipping_true_count == 2:
                question1_no_shipping_2_JUST_RETURN()
                question2_main_RETURN_LOGIC()
                return
            else:
                question2_main_RETURN_LOGIC()
                return
            return
    # #3.28
    if r.has_entity('where_pickup_points'):
        if r.entity('where_pickup_points') == 'true':
            nn.log('condition', 'where_pickup_points=="true"')
            nn.env('result', 'где посмотреть пункты самовывоза')
            question1_pickup_only_JUST_RETURN()
            question2_main_RETURN_LOGIC()
            return
    # #3.29
    if r.has_entity('how_to_order'):
        if r.entity('how_to_order') == 'true':
            nn.log('condition', 'how_to_order=="true"')
            nn.env('result', 'клиент не знает как заказать')
            question1_how_to_order_JUST_RETURN()
            question3_main_RETURN_LOGIC()
            return
    # #3.30
    if r.has_entity('did_not_add'):
        if r.entity('did_not_add') == 'true':
            nn.log('condition', 'did_not_add=="true"')
            nn.env('result', 'не клиент добавлял в корзину товары')
            question1_did_not_add_JUST_SAY()
            hangup_dont_disturb_HANGUP()
            return
    # #3.31
    if r.has_entity('my_region'):
        if r.entity('my_region') == 'true':
            nn.log('condition', 'my_region=="true"')
            nn.env('result', 'клиент уточняет, есть ли фермеры в его регионе')
            question1_my_region_JUST_SAY()
            question2_main_RETURN_LOGIC()
            return
    # #3.32
    if r.has_entity('dont_order_different_products'):
        if r.entity('dont_order_different_products') == 'true':
            nn.log('condition', 'dont_order_different_products=="true"')
            nn.env('result', 'нет возможности заказать разных производителей')
            question1_different_products_JUST_RETURN()
            question2_main_RETURN_LOGIC()
            return
    # #3.33
    if r.has_entity('failure'):
        if r.entity('failure') == 'true':
            nn.log('condition', 'failure=="true"')
            nn.env('result', 'произошел технический сбой')
            expert_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
    # #3.34
    if r.has_entity('farmer_certificate'):
        if r.entity('farmer_certificate') == 'true':
            nn.log('condition', 'farmer_certificate=="true"')
            nn.env('result', 'у каких фермеров можно расплатиться сертификатом')
            question1_farmer_certificate_JUST_SAY()
            question2_main_RETURN_LOGIC()
            return
    # #3.35
    if r.has_entity('what_do_animals_eat'):
        if r.entity('what_do_animals_eat') == 'true':
            nn.log('condition', 'what_do_animals_eat=="true"')
            nn.env('result', 'чем питаются животные')
            question1_delivery_date_JUST_SAY()
            question2_main_RETURN_LOGIC()
            return
    # #3.36
    if r.has_entity('how_are_contained'):
        if r.entity('how_are_contained') == 'true':
            nn.log('condition', 'how_are_contained=="true"')
            nn.env('result', 'в каких условиях содержатся')
            question1_delivery_date_JUST_SAY()
            question2_main_RETURN_LOGIC()
            return
    # #3.37
    if r.has_entity('expiration_date'):
        if r.entity('expiration_date') == 'true':
            nn.log('condition', 'expiration_date=="true"')
            nn.env('result', 'где посмотреть срок годности')
            question1_expiration_date_JUST_SAY()
            question2_main_RETURN_LOGIC()
            return
    # #3.38
    if r.has_entity('payment_upon_receipt'):
        if r.entity('payment_upon_receipt') == 'true':
            nn.log('condition', 'payment_upon_receipt=="true"')
            nn.env('result', 'можно ли оплатить при получении')
            question1_payment_upon_receipt_JUST_RETURN()
            question2_main_RETURN_LOGIC()
            return
    # #3.39
    if r.has_entity('expensive'):
        if r.entity('expensive') == 'true':
            nn.log('condition', 'expensive=="true"')
            nn.env('result', 'дорого')
            question1_expensive_JUST_RETURN()
            question2_main_RETURN_LOGIC()
            return
    # #3.40
    if r.has_entity('wait_bit'):
        if r.entity('wait_bit') == 'true':
            nn.log('condition', 'wait_bit=="true"')
            nn.env('result', 'абонент просит подождать')
            question1_logic_wait_bit_true_count = nn.env('question1_logic_wait_bit_true_count')
            if not question1_logic_wait_bit_true_count:
                nn.env('question1_logic_wait_bit_true_count', 1)
                question1_logic_wait_bit_true_count = 1
            else:
                question1_logic_wait_bit_true_count = question1_logic_wait_bit_true_count + 1
                nn.env('question1_logic_wait_bit_true_count', question1_logic_wait_bit_true_count)
            if question1_logic_wait_bit_true_count == 1:
                question1_wait_bit_JUST_RETURN()
                question1_null_RETURN_LOGIC()
                return
            else:
                hangup_null_HANGUP()
                nn.env('recall_is_needed', 'true')
                return
            return
    # #3.41
    if r.has_entity('repeat'):
        if r.entity('repeat') == 'true':
            nn.log('condition', 'repeat=="true"')
            nn.env('result', 'просьба повторить')
            question1_logic_repeat_true_count = nn.env('question1_logic_repeat_true_count')
            if not question1_logic_repeat_true_count:
                nn.env('question1_logic_repeat_true_count', 1)
                question1_logic_repeat_true_count = 1
            else:
                question1_logic_repeat_true_count = question1_logic_repeat_true_count + 1
                nn.env('question1_logic_repeat_true_count', question1_logic_repeat_true_count)
            if question1_logic_repeat_true_count == 1:
                question1_repeat_JUST_SAY()
                offer_end_()
                return
            elif question1_logic_repeat_true_count == 2:
                question1_repeat_JUST_SAY()
                offer_end_()
                return
            else:
                hangup_answers_HANGUP()
                nn.env('recall_is_needed', 'true')
                return
            return
    # #3.42
    if r.has_entity('no'):
        if r.entity('no') == 'true':
            nn.log('condition', 'no=="true"')
            nn.env('result', 'отказ озвучить причину')
            question1_no_JUST_SAY()
            question2_main_RETURN_LOGIC()
            return
    # #3.43
    if r.has_entity('not_interesting'):
        if r.entity('not_interesting') == 'true':
            nn.log('condition', 'not_interesting=="true"')
            nn.env('result', 'клиент передумал оформлять заказ')
            question1_no_JUST_SAY()
            question2_main_RETURN_LOGIC()
            return
    # #3.44
    if r.has_entity('no_need'):
        if r.entity('no_need') == 'true':
            nn.log('condition', 'no_need=="true"')
            nn.env('result', 'клиент передумал оформлять заказ')
            question1_no_JUST_SAY()
            question2_main_RETURN_LOGIC()
            return
    # #3.45
    if r.has_entity('irrelevant'):
        if r.entity('irrelevant') == 'true':
            nn.log('condition', 'irrelevant=="true"')
            nn.env('result', 'клиент передумал оформлять заказ')
            question1_no_JUST_SAY()
            question2_main_RETURN_LOGIC()
            return
    # #3.46
    if r.has_entity('dont_know'):
        if r.entity('dont_know') == 'true':
            nn.log('condition', 'dont_know=="true"')
            nn.env('result', 'клиент еще думает по заказу')
            question1_no_JUST_SAY()
            question2_main_RETURN_LOGIC()
            return
    # #3.47
    if r.has_entity('yes'):
        if r.entity('yes') == 'true':
            nn.log('condition', 'yes=="true"')
            nn.env('result', 'клиент согласен озвучить причину')
            question1_logic_yes_true_count = nn.env('question1_logic_yes_true_count')
            if not question1_logic_yes_true_count:
                nn.env('question1_logic_yes_true_count', 1)
                question1_logic_yes_true_count = 1
            else:
                question1_logic_yes_true_count = question1_logic_yes_true_count + 1
                nn.env('question1_logic_yes_true_count', question1_logic_yes_true_count)
            if question1_logic_yes_true_count == 1:
                question1_yes_RETURN_LOGIC()
                return
            elif question1_logic_yes_true_count == 2:
                offer_end_()
                return
            else:
                hangup_answers_HANGUP()
                nn.env('recall_is_needed', 'true')
                return
            return
    # #3.48
    if r.has_entity('agree'):
        if r.entity('agree') == 'true':
            nn.log('condition', 'agree=="true"')
            nn.env('result', 'клиент согласен озвучить причину')
            question1_logic_agree_true_count = nn.env('question1_logic_agree_true_count')
            if not question1_logic_agree_true_count:
                nn.env('question1_logic_agree_true_count', 1)
                question1_logic_agree_true_count = 1
            else:
                question1_logic_agree_true_count = question1_logic_agree_true_count + 1
                nn.env('question1_logic_agree_true_count', question1_logic_agree_true_count)
            if question1_logic_agree_true_count == 1:
                question1_yes_RETURN_LOGIC()
                return
            elif question1_logic_agree_true_count == 2:
                offer_end_()
                return
            else:
                hangup_answers_HANGUP()
                nn.env('recall_is_needed', 'true')
                return
            return
    # #3.49
    if r.has_entity('not_money'):
        if r.entity('not_money') == 'true':
            nn.log('condition', 'not_money=="true"')
            nn.env('result', 'у клиента сейчас нет денег')
            question1_no_JUST_SAY()
            question2_main_RETURN_LOGIC()
            return
    # #3.50
    if r.has_entity('got_acquainted'):
        if r.entity('got_acquainted') == 'true':
            nn.log('condition', 'got_acquainted=="true"')
            nn.env('result', 'клиент знакомился с Своё Родное')
            question2_main_RETURN_LOGIC()
            return
    # #3.51
    if r.has_entity('postponed_product'):
        if r.entity('postponed_product') == 'true':
            nn.log('condition', 'postponed_product=="true"')
            nn.env('result', 'клиент отложил для себя товар')
            question2_main_RETURN_LOGIC()
            return
    # #3.52
    if r.has_entity('question'):
        if r.entity('question') == 'true':
            nn.log('condition', 'question=="true"')
            nn.env('result', 'клиент хочет задать вопрос')
            positive_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
    # #3.53
    if r.has_entity('annoying_robots'):
        if r.entity('annoying_robots') == 'true':
            nn.log('condition', 'annoying_robots=="true"')
            nn.env('result', 'роботы раздражают')
            expert_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
    # #3.54
    if r.has_entity('connect_operator'):
        if r.entity('connect_operator') == 'true':
            nn.log('condition', 'connect_operator=="true"')
            nn.env('result', 'просьба перевести на живого человека')
            expert_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
    # #3.55
    if r.has_entity('bad_connection'):
        if r.entity('bad_connection') == 'true':
            nn.log('condition', 'bad_connection=="true"')
            nn.env('result', 'плохая связь')
            question1_logic_bad_connection_true_count = nn.env('question1_logic_bad_connection_true_count')
            if not question1_logic_bad_connection_true_count:
                nn.env('question1_logic_bad_connection_true_count', 1)
                question1_logic_bad_connection_true_count = 1
            else:
                question1_logic_bad_connection_true_count = question1_logic_bad_connection_true_count + 1
                nn.env('question1_logic_bad_connection_true_count', question1_logic_bad_connection_true_count)
            if question1_logic_bad_connection_true_count == 1:
                question1_null_RETURN_LOGIC()
                return
            else:
                hangup_answers_HANGUP()
                nn.env('recall_is_needed', 'true')
                return
            return
    # #3.56
    if r.has_entity('hear_me'):
        if r.entity('hear_me') == 'true':
            nn.log('condition', 'hear_me=="true"')
            nn.env('result', 'клиент акциентирует на себе внимание')
            question1_logic_hear_me_true_count = nn.env('question1_logic_hear_me_true_count')
            if not question1_logic_hear_me_true_count:
                nn.env('question1_logic_hear_me_true_count', 1)
                question1_logic_hear_me_true_count = 1
            else:
                question1_logic_hear_me_true_count = question1_logic_hear_me_true_count + 1
                nn.env('question1_logic_hear_me_true_count', question1_logic_hear_me_true_count)
            if question1_logic_hear_me_true_count == 1:
                question1_default_RETURN_LOGIC()
                return
            else:
                hangup_answers_HANGUP()
                nn.env('recall_is_needed', 'true')
                return
            return
    # #3.57
    if r.has_entity('goodbye'):
        if r.entity('goodbye') == 'true':
            nn.log('condition', 'goodbye=="true"')
            nn.env('result', 'до свидание')
            question1_logic_goodbye_true_count = nn.env('question1_logic_goodbye_true_count')
            if not question1_logic_goodbye_true_count:
                nn.env('question1_logic_goodbye_true_count', 1)
                question1_logic_goodbye_true_count = 1
            else:
                question1_logic_goodbye_true_count = question1_logic_goodbye_true_count + 1
                nn.env('question1_logic_goodbye_true_count', question1_logic_goodbye_true_count)
            if question1_logic_goodbye_true_count == 1:
                hello_how_long_JUST_SAY()
                offer_end_()
                return
            else:
                just_hangup_HANGUP()
                return
            return


# #3.31
# У нас есть фермеры по всей России, нужно просто выбрать свой город.
# Также есть производители, которые доставляют в соседние города.
@check_call_state(nv)
def question1_my_region_JUST_SAY():
    nn.log('unit', 'question1_my_region')
    nv.say('question1_my_region')
    return
    pass


# #3.38
# В основном оплату принимают при получении. При общении с продавцом можно дополнительно уточнить эту информацию.
@check_call_state(nv)
def question1_payment_upon_receipt_JUST_RETURN():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question1_payment_upon_receipt')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question1_payment_upon_receipt')
    return
    pass


# #3.39
# Попробуйте поподробнее изучить наш ассортемент продуктов, уверена Вы найдете что-то, что Вам подойдет.
@check_call_state(nv)
def question1_expensive_JUST_RETURN():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question1_expensive')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question1_expensive')
    return
    pass


# #3.15
# Маркетплейс по продаже фермерской продукции Своё Родное от Россельхозбанка.
@check_call_state(nv)
def question1_what_company_JUST_SAY():
    nn.log('unit', 'question1_what_company')
    nv.say('question1_what_company')
    return
    pass


# #3.29
# Мы совершенствуемся и хотим как раз узнать, что нужно добавить, как улучшить, чтобы всё было понятно и удобно.
@check_call_state(nv)
def question1_how_to_order_JUST_RETURN():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question1_how_to_order')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question1_how_to_order')
    return
    pass


# #3.21
# Эту информацию вы можете уточнить у фермера во время контрольного звонка.
@check_call_state(nv)
def question1_delivery_date_JUST_SAY():
    nn.log('unit', 'question1_delivery_date')
    nv.say('question1_delivery_date')
    return
    pass


# #3.1
# Вы собирались сделать заказ на платформе, но так и не заказали. Для улучшения качества работы хотели уточнить причину?
@check_call_state(nv)
def question1_main_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question1_main')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question1_main')
    return question1_logic(r)
    pass


# #3.2
# Алло… Поделитесь, почему не завершили заказ?
@check_call_state(nv)
def question1_null_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question1_null')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question1_null')
    return question1_logic(r)
    pass


# #3.24
# Бесплатная доставка зависит от суммы минимального заказа и расчёт доставки у каждого продавца разный,
# еще можно при оформлении заказа эту информацию уточнить у фермера.
@check_call_state(nv)
def question1_no_free_JUST_RETURN():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question1_no_free')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question1_no_free')
    return
    pass


# #3.30
# Предлагаю Вам попробовать и оценить качество фермерской продукции. Уверена, Вам точно понравится.
@check_call_state(nv)
def question1_did_not_add_JUST_SAY():
    nn.log('unit', 'question1_did_not_add')
    nv.say('question1_did_not_add')
    return
    pass


# #3.47
# Я слушаю…
@check_call_state(nv)
def question1_yes_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question1_yes')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question1_yes')
    return question1_logic(r)
    pass


# #3.58
# 3.59
# 3.60
# Подскажите, почему не завершили заказ?
# Для улучшения качества работы, мне нужно узнать, почему решили не заказывать?
# Мы стараемся стать лучше, скажете почему не заказали в итоге?
@check_call_state(nv)
def offer_end_():
    offer_end_count = nn.env('offer_end_count')
    if not offer_end_count:
        nn.env('offer_end_count', 1)
        offer_end_count = 1
    else:
        offer_end_count = offer_end_count + 1
        nn.env('offer_end_count', offer_end_count)
    offer_end_count = offer_end_count % 3
    if offer_end_count == 0:
        offer_end_count = 3
    nn.log('unit', 'offer_end_' + str(offer_end_count))
    nv.set_default('listen', {'interruption_no_input_timeout': 1000,
                              'no_input_timeout': 10,
                              'recognition_timeout': 5000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 10})

    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('offer_end_' + str(offer_end_count))
    return question1_logic(r)
    pass


# #3.42
# Поняла Вас, а…
@check_call_state(nv)
def question1_no_JUST_SAY():
    nn.log('unit', 'question1_no')
    nv.say('question1_no')
    return
    pass


# #3.22
# У нас много производителей, где доставка бесплатная, нужно просто поставить фильтр.
@check_call_state(nv)
def question1_expensive_shipping_JUST_SAY():
    nn.log('unit', 'question1_expensive_shipping')
    nv.say('question1_expensive_shipping')
    return
    pass


# #3.40
# Хорошо, подожду…(ожижание 15 секунд)
@check_call_state(nv)
def question1_wait_bit_JUST_RETURN():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question1_wait_bit')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question1_wait_bit')
    return
    pass


# #3.26
# "Через фильтр можно выбрать ""с доставкой"" и Вы увидите всех фермеров у кого она есть."
@check_call_state(nv)
def question1_no_shipping_1_JUST_RETURN():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question1_no_shipping_1')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question1_no_shipping_1')
    return
    pass


# #3.41
# У Вас в корзине остались товары.
@check_call_state(nv)
def question1_repeat_JUST_SAY():
    nn.log('unit', 'question1_repeat')
    nv.say('question1_repeat')
    return
    pass


# #3.27
# Если не чего не появилось, значит в вашем регионе пока её нет.
# Но фермеры у нас появляются каждый день и может появиться доставка.
@check_call_state(nv)
def question1_no_shipping_2_JUST_RETURN():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question1_no_shipping_2')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question1_no_shipping_2')
    return
    pass


# #3.34
# Точную информацию, какие именно фермеры принимают сертификаты, вы можете посмотреть на сайте - farms.svoe.ru
@check_call_state(nv)
def question1_farmer_certificate_JUST_SAY():
    nn.log('unit', 'question1_farmer_certificate')
    nv.say('question1_farmer_certificate')
    return
    pass


# #3.3
# А если подвести итог, причина была какой?
@check_call_state(nv)
def question1_default_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question1_default')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question1_default')
    return question1_logic(r)
    pass


# #3.18
# Офис находится в Москве, но платформа работает с фермерами по всей России.
@check_call_state(nv)
def question1_city_JUST_RETURN():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question1_city')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question1_city')
    return
    pass


# #3.25
# Их можно посмотреть в информации о фермере, либо при заполнении заказа выбрать пункт самовывоза из списка.
@check_call_state(nv)
def question1_pickup_only_JUST_RETURN():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question1_pickup_only')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question1_pickup_only')
    return
    pass


# #3.13
# Да, я электронный помошник и передам всю информацию коллегам.
@check_call_state(nv)
def question1_robot_2_JUST_RETURN():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question1_robot_2')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question1_robot_2')
    return
    pass


# #3.32
# Так как у каждого фермера своя доставка - нет возможности добавить их в один заказ,
# но сейчас мы уже занимаемся решением этого вопроса.
@check_call_state(nv)
def question1_different_products_JUST_RETURN():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question1_different_products')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question1_different_products')
    return
    pass


# #3.37
# В описании всех товаров Вы можете увидеть информацию о сроке годности товара.
@check_call_state(nv)
def question1_expiration_date_JUST_SAY():
    nn.log('unit', 'question1_expiration_date')
    nv.say('question1_expiration_date')
    return
    pass


# #3.17
# Мы обзваниваем наших пользователей, чтобы получить обратную связь о качестве нашей работы.
# Вот и интересуемся, почему Вы не завершили покупку?
@check_call_state(nv)
def question1_purpose_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question1_purpose')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question1_purpose')
    return question1_logic(r)
    pass


# #3.19
# Какие конкретно продукты я сказать не могу, вижу только что в Вашей корзине есть товары.
@check_call_state(nv)
def question1_what_order_JUST_RETURN():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question1_what_order')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'irrelevant',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'pickup_only',
                             'what_company',
                             'expiration_date',
                             'what_surname',
                             'robot',
                             'no_need',
                             'voicemail',
                             'what_did_you_order',
                             'probable',
                             'agree',
                             'my_region',
                             'postponed_product',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'how_to_order',
                             'no',
                             'how_long',
                             'goodbye',
                             'bad_connection',
                             'no_shipping',
                             'not_interesting',
                             'how_are_contained',
                             'did_not_add',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'dont_order_different_products',
                             'what_do_animals_eat',
                             'mistake',
                             'no_free_shipping',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'purpose_call',
                             'payment_upon_receipt',
                             'expensive',
                             'callback',
                             'not_money',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question1_what_order')
    return
    pass


# #3.20
# Можно заказать доставку на дом или забрать из пункта самовывоза.
@check_call_state(nv)
def question1_transportation_JUST_SAY():
    nn.log('unit', 'question1_transportation')
    nv.say('question1_transportation')
    return
    pass


# #3.12
# Меня зовут Ирина и я помошник платформы Своё Родное.
@check_call_state(nv)
def question1_robot_1_JUST_SAY():
    nn.log('unit', 'question1_robot_1')
    nv.say('question1_robot_1')
    return
    pass


@check_call_state(nv)
def question2_logic(r):
    nn.log('unit', 'question2_logic')
    question2_logic_exec_count = nn.env('question2_logic_exec_count')
    if not question2_logic_exec_count:
        nn.env('question2_logic_exec_count', 1)
    else:
        question2_logic_exec_count = question2_logic_exec_count + 1
        nn.env('question2_logic_exec_count', question2_logic_exec_count)
        if question2_logic_exec_count and question2_logic_exec_count > 10:
            nn.log("Recursive execution detected")
            return
    # #4.2
    if not r:
        nn.log('condition', 'NULL')
        nn.env('result', 'NULL - молчание от клиента')
        question2_logic_NULL_NULL_count = nn.env('question2_logic_NULL_NULL_count')
        if not question2_logic_NULL_NULL_count:
            nn.env('question2_logic_NULL_NULL_count', 1)
            question2_logic_NULL_NULL_count = 1
        else:
            question2_logic_NULL_NULL_count = question2_logic_NULL_NULL_count + 1
            nn.env('question2_logic_NULL_NULL_count', question2_logic_NULL_NULL_count)
        if question2_logic_NULL_NULL_count == 1:
            question2_null_RETURN_LOGIC()
            return
        else:
            hangup_dont_disturb_HANGUP()
            return
        return
    # #4.3
    if not r.has_entities():
        nn.log('condition', 'DEFAULT')
        nn.env('result', 'озвучен товар/дефолтное возражение')
        question2_logic_DEFAULT_DEFAULT_count = nn.env('question2_logic_DEFAULT_DEFAULT_count')
        if not question2_logic_DEFAULT_DEFAULT_count:
            nn.env('question2_logic_DEFAULT_DEFAULT_count', 1)
            question2_logic_DEFAULT_DEFAULT_count = 1
        else:
            question2_logic_DEFAULT_DEFAULT_count = question2_logic_DEFAULT_DEFAULT_count + 1
            nn.env('question2_logic_DEFAULT_DEFAULT_count', question2_logic_DEFAULT_DEFAULT_count)
        if question2_logic_DEFAULT_DEFAULT_count == 1:
            question2_default_RETURN_LOGIC()
            return
        else:
            question3_main_RETURN_LOGIC()
            return
        return
    # #4.4
    if r.has_entity('wrong_time_sick'):
        if r.entity('wrong_time_sick') == 'true':
            nn.log('condition', 'wrong_time_sick=="true"')
            nn.env('result', 'абонент болеет')
            hangup_dont_disturb_HANGUP()
            return
    # #4.5
    if r.has_entity('wrong_time_wheel'):
        if r.entity('wrong_time_wheel') == 'true':
            nn.log('condition', 'wrong_time_wheel=="true"')
            nn.env('result', 'абонент за рулем')
            hangup_dont_disturb_HANGUP()
            return
    # #4.6
    if r.has_entity('callback'):
        if r.entity('callback') == 'true':
            nn.log('condition', 'callback=="true"')
            nn.env('result', 'просьба перезвонить')
            hangup_dont_disturb_HANGUP()
            return
    # #4.7
    if r.has_entity('wrong_time'):
        if r.entity('wrong_time') == 'true':
            nn.log('condition', 'wrong_time=="true"')
            nn.env('result', 'клиент занят')
            hangup_dont_disturb_HANGUP()
            return
    # #4.8
    if r.has_entity('dont_disturb'):
        if r.entity('dont_disturb') == 'true':
            nn.log('condition', 'dont_disturb=="true"')
            nn.env('result', 'больше не звонить')
            just_2_hangup_HANGUP()
            return
    # #4.9
    if r.has_entity('probable'):
        if r.entity('probable') == 'true':
            nn.log('condition', 'probable=="true"')
            nn.env('result', 'агрессия')
            just_2_hangup_HANGUP()
            return
    # #4.10
    if r.has_entity('robot'):
        if r.entity('robot') == 'true':
            nn.log('condition', 'robot=="true"')
            nn.env('result', 'распознан робот')
            question2_logic_robot_true_count = nn.env('question2_logic_robot_true_count')
            if not question2_logic_robot_true_count:
                nn.env('question2_logic_robot_true_count', 1)
                question2_logic_robot_true_count = 1
            else:
                question2_logic_robot_true_count = question2_logic_robot_true_count + 1
                nn.env('question2_logic_robot_true_count', question2_logic_robot_true_count)
            if question2_logic_robot_true_count == 1:
                question2_robot_JUST_SAY()
                question2_null_RETURN_LOGIC()
                return
            else:
                question3_main_RETURN_LOGIC()
                return
            return
    # #4.11
    if r.has_entity('what_surname'):
        if r.entity('what_surname') == 'true':
            nn.log('condition', 'what_surname=="true"')
            nn.env('result', 'вопрос про имя')
            question2_logic_what_surname_true_count = nn.env('question2_logic_what_surname_true_count')
            if not question2_logic_what_surname_true_count:
                nn.env('question2_logic_what_surname_true_count', 1)
                question2_logic_what_surname_true_count = 1
            else:
                question2_logic_what_surname_true_count = question2_logic_what_surname_true_count + 1
                nn.env('question2_logic_what_surname_true_count', question2_logic_what_surname_true_count)
            if question2_logic_what_surname_true_count == 1:
                question2_name_RETURN_LOGIC()
                return
            else:
                hello_name_JUST_SAY()
                question3_main_RETURN_LOGIC()
                return
            return
    # #4.12
    if r.has_entity('what_company'):
        if r.entity('what_company') == 'true':
            nn.log('condition', 'what_company=="true"')
            nn.env('result', 'вопрос какая компания')
            question2_logic_what_company_true_count = nn.env('question2_logic_what_company_true_count')
            if not question2_logic_what_company_true_count:
                nn.env('question2_logic_what_company_true_count', 1)
                question2_logic_what_company_true_count = 1
            else:
                question2_logic_what_company_true_count = question2_logic_what_company_true_count + 1
                nn.env('question2_logic_what_company_true_count', question2_logic_what_company_true_count)
            if question2_logic_what_company_true_count == 1:
                question2_what_company_RETURN_LOGIC()
                return
            else:
                hangup_answers_HANGUP()
                return
            return
    # #4.13
    if r.has_entity('how_long'):
        if r.entity('how_long') == 'true':
            nn.log('condition', 'how_long=="true"')
            nn.env('result', 'вопрос по времени беседы')
            question2_logic_how_long_true_count = nn.env('question2_logic_how_long_true_count')
            if not question2_logic_how_long_true_count:
                nn.env('question2_logic_how_long_true_count', 1)
                question2_logic_how_long_true_count = 1
            else:
                question2_logic_how_long_true_count = question2_logic_how_long_true_count + 1
                nn.env('question2_logic_how_long_true_count', question2_logic_how_long_true_count)
            if question2_logic_how_long_true_count == 1:
                hello_how_long_JUST_SAY()
                question2_null_RETURN_LOGIC()
                return
            else:
                question3_main_RETURN_LOGIC()
                return
            return
    # #4.14
    if r.has_entity('purpose_call'):
        if r.entity('purpose_call') == 'true':
            nn.log('condition', 'purpose_call=="true"')
            nn.env('result', 'вопрос о цели звонка')
            question2_logic_purpose_call_true_count = nn.env('question2_logic_purpose_call_true_count')
            if not question2_logic_purpose_call_true_count:
                nn.env('question2_logic_purpose_call_true_count', 1)
                question2_logic_purpose_call_true_count = 1
            else:
                question2_logic_purpose_call_true_count = question2_logic_purpose_call_true_count + 1
                nn.env('question2_logic_purpose_call_true_count', question2_logic_purpose_call_true_count)
            if question2_logic_purpose_call_true_count == 1:
                question2_purpose_RETURN_LOGIC()
                return
            else:
                question3_main_RETURN_LOGIC()
                return
            return
    # #4.15
    if r.has_entity('where_address'):
        if r.entity('where_address') == 'true':
            nn.log('condition', 'where_address=="true"')
            nn.env('result', 'вопрос о месте нахождения офиса')
            question2_logic_where_address_true_count = nn.env('question2_logic_where_address_true_count')
            if not question2_logic_where_address_true_count:
                nn.env('question2_logic_where_address_true_count', 1)
                question2_logic_where_address_true_count = 1
            else:
                question2_logic_where_address_true_count = question2_logic_where_address_true_count + 1
                nn.env('question2_logic_where_address_true_count', question2_logic_where_address_true_count)
            if question2_logic_where_address_true_count == 1:
                question2_city_JUST_SAY()
                question2_null_RETURN_LOGIC()
                return
            else:
                hangup_answers_HANGUP()
                return
            return
    # #4.16
    if r.has_entity('types_transportation'):
        if r.entity('types_transportation') == 'true':
            nn.log('condition', 'types_transportation=="true"')
            nn.env('result', 'вопрос про способы доставки')
            question1_transportation_JUST_SAY()
            question3_main_RETURN_LOGIC()
            return
    # #4.17
    if r.has_entity('transport_delivery_date'):
        if r.entity('transport_delivery_date') == 'true':
            nn.log('condition', 'transport_delivery_date=="true"')
            nn.env('result', 'вопрос про срок поставки')
            question1_delivery_date_JUST_SAY()
            question3_main_RETURN_LOGIC()
            return
    # #4.18
    if r.has_entity('expensive_shipping'):
        if r.entity('expensive_shipping') == 'true':
            nn.log('condition', 'expensive_shipping=="true"')
            nn.env('result', 'дорогая доставка')
            question1_expensive_shipping_JUST_SAY()
            question3_main_RETURN_LOGIC()
            return
    # #4.19
    if r.has_entity('free_shipping'):
        if r.entity('free_shipping') == 'true':
            nn.log('condition', 'free_shipping=="true"')
            nn.env('result', 'есть ли бесплатная доставка')
            question1_expensive_shipping_JUST_SAY()
            question3_main_RETURN_LOGIC()
            return
    # #4.20
    if r.has_entity('where_pickup_points'):
        if r.entity('where_pickup_points') == 'true':
            nn.log('condition', 'where_pickup_points=="true"')
            nn.env('result', 'где посмотреть пункты самовывоза')
            question1_pickup_only_JUST_RETURN()
            question3_main_RETURN_LOGIC()
            return
    # #4.21
    if r.has_entity('failure'):
        if r.entity('failure') == 'true':
            nn.log('condition', 'failure=="true"')
            nn.env('result', 'произошел технический сбой')
            expert_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
    # #4.22
    if r.has_entity('my_region'):
        if r.entity('my_region') == 'true':
            nn.log('condition', 'my_region=="true"')
            nn.env('result', 'клиент уточняет, есть ли фермеры в его регионе')
            question1_my_region_JUST_SAY()
            question3_main_RETURN_LOGIC()
            return
    # #4.23
    if r.has_entity('farmer_certificate'):
        if r.entity('farmer_certificate') == 'true':
            nn.log('condition', 'farmer_certificate=="true"')
            nn.env('result', 'у каких фермеров можно расплатиться сертификатом')
            question1_farmer_certificate_JUST_SAY()
            question3_main_RETURN_LOGIC()
            return
    # #4.24
    if r.has_entity('what_do_animals_eat'):
        if r.entity('what_do_animals_eat') == 'true':
            nn.log('condition', 'what_do_animals_eat=="true"')
            nn.env('result', 'чем питаются животные')
            question1_delivery_date_JUST_SAY()
            question3_main_RETURN_LOGIC()
            return
    # #4.25
    if r.has_entity('how_are_contained'):
        if r.entity('how_are_contained') == 'true':
            nn.log('condition', 'how_are_contained=="true"')
            nn.env('result', 'в каких условиях содержатся')
            question1_delivery_date_JUST_SAY()
            question3_main_RETURN_LOGIC()
            return
    # #4.26
    if r.has_entity('expiration_date'):
        if r.entity('expiration_date') == 'true':
            nn.log('condition', 'expiration_date=="true"')
            nn.env('result', 'где посмотреть срок годности')
            question1_expiration_date_JUST_SAY()
            question3_main_RETURN_LOGIC()
            return
    # #4.27
    if r.has_entity('payment_upon_receipt'):
        if r.entity('payment_upon_receipt') == 'true':
            nn.log('condition', 'payment_upon_receipt=="true"')
            nn.env('result', 'можно ли оплатить при получении')
            question2_payment_upon_receipt_JUST_SAY()
            question3_main_RETURN_LOGIC()
            return
    # #4.28
    if r.has_entity('wait_bit'):
        if r.entity('wait_bit') == 'true':
            nn.log('condition', 'wait_bit=="true"')
            nn.env('result', 'абонент просит подождать')
            question2_logic_wait_bit_true_count = nn.env('question2_logic_wait_bit_true_count')
            if not question2_logic_wait_bit_true_count:
                nn.env('question2_logic_wait_bit_true_count', 1)
                question2_logic_wait_bit_true_count = 1
            else:
                question2_logic_wait_bit_true_count = question2_logic_wait_bit_true_count + 1
                nn.env('question2_logic_wait_bit_true_count', question2_logic_wait_bit_true_count)
            if question2_logic_wait_bit_true_count == 1:
                question2_wait_bit_JUST_RETURN()
                question2_null_RETURN_LOGIC()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #4.29
    if r.has_entity('repeat'):
        if r.entity('repeat') == 'true':
            nn.log('condition', 'repeat=="true"')
            nn.env('result', 'просьба повторить')
            question2_logic_repeat_true_count = nn.env('question2_logic_repeat_true_count')
            if not question2_logic_repeat_true_count:
                nn.env('question2_logic_repeat_true_count', 1)
                question2_logic_repeat_true_count = 1
            else:
                question2_logic_repeat_true_count = question2_logic_repeat_true_count + 1
                nn.env('question2_logic_repeat_true_count', question2_logic_repeat_true_count)
            if question2_logic_repeat_true_count == 1:
                question2_purpose_RETURN_LOGIC()
                return
            else:
                hangup_answers_HANGUP()
                return
            return
    # #4.30
    if r.has_entity('yes'):
        if r.entity('yes') == 'true':
            nn.log('condition', 'yes=="true"')
            nn.env('result', 'клиенту всё понравилось')
            question3_main_RETURN_LOGIC()
            return
    # #4.31
    if r.has_entity('clear'):
        if r.entity('clear') == 'true':
            nn.log('condition', 'clear=="true"')
            nn.env('result', 'клиенту всё понравилось')
            question3_main_RETURN_LOGIC()
            return
    # #4.32
    if r.has_entity('no'):
        if r.entity('no') == 'true':
            nn.log('condition', 'no=="true"')
            nn.env('result', 'клиенту НЕ понравилось')
            question3_main_RETURN_LOGIC()
            return
    # #4.33
    if r.has_entity('no_need'):
        if r.entity('no_need') == 'true':
            nn.log('condition', 'no_need=="true"')
            nn.env('result', 'клиент не хочет отвечать на вопрос')
            question3_main_RETURN_LOGIC()
            return
    # #4.34
    if r.has_entity('dont_know'):
        if r.entity('dont_know') == 'true':
            nn.log('condition', 'dont_know=="true"')
            nn.env('result', 'клиент не может сейчас ответить на вопрос')
            question3_main_RETURN_LOGIC()
            return
    # #4.35
    if r.has_entity('got_acquainted'):
        if r.entity('got_acquainted') == 'true':
            nn.log('condition', 'got_acquainted=="true"')
            nn.env('result', 'клиент только познакомился с сайтом')
            question3_main_RETURN_LOGIC()
            return
    # #4.36
    if r.has_entity('question'):
        if r.entity('question') == 'true':
            nn.log('condition', 'question=="true"')
            nn.env('result', 'клиент хочет задать вопрос')
            positive_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
    # #4.37
    if r.has_entity('annoying_robots'):
        if r.entity('annoying_robots') == 'true':
            nn.log('condition', 'annoying_robots=="true"')
            nn.env('result', 'роботы раздражают')
            expert_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
    # #4.38
    if r.has_entity('connect_operator'):
        if r.entity('connect_operator') == 'true':
            nn.log('condition', 'connect_operator=="true"')
            nn.env('result', 'просьба перевести на живого человека')
            expert_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
    # #4.39
    if r.has_entity('bad_connection'):
        if r.entity('bad_connection') == 'true':
            nn.log('condition', 'bad_connection=="true"')
            nn.env('result', 'плохая связь')
            question2_logic_bad_connection_true_count = nn.env('question2_logic_bad_connection_true_count')
            if not question2_logic_bad_connection_true_count:
                nn.env('question2_logic_bad_connection_true_count', 1)
                question2_logic_bad_connection_true_count = 1
            else:
                question2_logic_bad_connection_true_count = question2_logic_bad_connection_true_count + 1
                nn.env('question2_logic_bad_connection_true_count', question2_logic_bad_connection_true_count)
            if question2_logic_bad_connection_true_count == 1:
                question2_null_RETURN_LOGIC()
                return
            else:
                hangup_answers_HANGUP()
                return
            return
    # #4.40
    if r.has_entity('hear_me'):
        if r.entity('hear_me') == 'true':
            nn.log('condition', 'hear_me=="true"')
            nn.env('result', 'клиент акциентирует на себе внимание')
            question2_logic_hear_me_true_count = nn.env('question2_logic_hear_me_true_count')
            if not question2_logic_hear_me_true_count:
                nn.env('question2_logic_hear_me_true_count', 1)
                question2_logic_hear_me_true_count = 1
            else:
                question2_logic_hear_me_true_count = question2_logic_hear_me_true_count + 1
                nn.env('question2_logic_hear_me_true_count', question2_logic_hear_me_true_count)
            if question2_logic_hear_me_true_count == 1:
                question2_default_RETURN_LOGIC()
                return
            else:
                hangup_answers_HANGUP()
                return
            return
    # #4.41
    if r.has_entity('goodbye'):
        if r.entity('goodbye') == 'true':
            nn.log('condition', 'goodbye=="true"')
            nn.env('result', 'до свидание')
            question2_logic_goodbye_true_count = nn.env('question2_logic_goodbye_true_count')
            if not question2_logic_goodbye_true_count:
                nn.env('question2_logic_goodbye_true_count', 1)
                question2_logic_goodbye_true_count = 1
            else:
                question2_logic_goodbye_true_count = question2_logic_goodbye_true_count + 1
                nn.env('question2_logic_goodbye_true_count', question2_logic_goodbye_true_count)
            if question2_logic_goodbye_true_count == 1:
                hello_how_long_JUST_SAY()
                question2_null_RETURN_LOGIC()
                return
            else:
                just_hangup_HANGUP()
                return
            return


# #4.14
# В данный момент хочу узнать, как Вам наш ассортимент товаров и что хотите еще добавить?
@check_call_state(nv)
def question2_purpose_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question2_purpose')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'no',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'expiration_date',
                             'bad_connection',
                             'what_surname',
                             'robot',
                             'no_need',
                             'how_are_contained',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'what_do_animals_eat',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'clear',
                             'probable',
                             'purpose_call',
                             'payment_upon_receipt',
                             'my_region',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'callback',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question2_purpose')
    return question2_logic(r)
    pass


# #4.2
# Подскажите? Что хотели бы добавить из товаров?
@check_call_state(nv)
def question2_null_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question2_null')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'no',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'expiration_date',
                             'bad_connection',
                             'what_surname',
                             'robot',
                             'no_need',
                             'how_are_contained',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'what_do_animals_eat',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'clear',
                             'probable',
                             'purpose_call',
                             'payment_upon_receipt',
                             'my_region',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'callback',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question2_null')
    return question2_logic(r)
    pass


# #4.11
# Меня зовут Ирина. И мне очень хочется услышать Ваше мнение о наших товарах и может посоветуете,
# какие еще надо добавить, скажите?
@check_call_state(nv)
def question2_name_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question2_name')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'no',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'expiration_date',
                             'bad_connection',
                             'what_surname',
                             'robot',
                             'no_need',
                             'how_are_contained',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'what_do_animals_eat',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'clear',
                             'probable',
                             'purpose_call',
                             'payment_upon_receipt',
                             'my_region',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'callback',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question2_name')
    return question2_logic(r)
    pass


# #4.27
# В основном оплату принимают при получении.
@check_call_state(nv)
def question2_payment_upon_receipt_JUST_SAY():
    nn.log('unit', 'question2_payment_upon_receipt')
    nv.say('question2_payment_upon_receipt')
    return
    pass


# #4.15
# Наша платформа работает с фермерами по всей России.
@check_call_state(nv)
def question2_city_JUST_SAY():
    nn.log('unit', 'question2_city')
    nv.say('question2_city')
    return
    pass


# #4.10
# Да, я электронный помошник платформы Своё Родное и передам всю информацию коллегам.
@check_call_state(nv)
def question2_robot_JUST_SAY():
    nn.log('unit', 'question2_robot')
    nv.say('question2_robot')
    return
    pass


# #4.12
# Маркетплейс по продаже фермерской продукции Своё Родное. Какие продукты хотите чтобы мы добавили?
@check_call_state(nv)
def question2_what_company_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question2_what_company')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'no',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'expiration_date',
                             'bad_connection',
                             'what_surname',
                             'robot',
                             'no_need',
                             'how_are_contained',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'what_do_animals_eat',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'clear',
                             'probable',
                             'purpose_call',
                             'payment_upon_receipt',
                             'my_region',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'callback',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question2_what_company')
    return question2_logic(r)
    pass


# #4.1
# Понравился ли Вам представленный ассортимент и какие продукты еще хотели бы видеть?
@check_call_state(nv)
def question2_main_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question2_main')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'no',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'expiration_date',
                             'bad_connection',
                             'what_surname',
                             'robot',
                             'no_need',
                             'how_are_contained',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'what_do_animals_eat',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'clear',
                             'probable',
                             'purpose_call',
                             'payment_upon_receipt',
                             'my_region',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'callback',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question2_main')
    return question2_logic(r)
    pass


# #4.3
# Прервалась связь... Скажите еще раз, пожалуйста, какие товары нужно добавить?
@check_call_state(nv)
def question2_default_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question2_default')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'no',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'expiration_date',
                             'bad_connection',
                             'what_surname',
                             'robot',
                             'no_need',
                             'how_are_contained',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'what_do_animals_eat',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'clear',
                             'probable',
                             'purpose_call',
                             'payment_upon_receipt',
                             'my_region',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'callback',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question2_default')
    return question2_logic(r)
    pass


# #4.28
# Конечно, подожду…(ожижание 15 секунд)
@check_call_state(nv)
def question2_wait_bit_JUST_RETURN():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question2_wait_bit')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['wrong_time_wheel',
                             'no',
                             'wrong_time_sick',
                             'dont_disturb',
                             'free_shipping',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'expiration_date',
                             'bad_connection',
                             'what_surname',
                             'robot',
                             'no_need',
                             'how_are_contained',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'what_do_animals_eat',
                             'question',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'clear',
                             'probable',
                             'purpose_call',
                             'payment_upon_receipt',
                             'my_region',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'callback',
                             'expensive_shipping',
                             'wrong_time']) as r:
        nv.say('question2_wait_bit')
    return
    pass


@check_call_state(nv)
def question3_logic(r):
    nn.log('unit', 'question3_logic')
    question3_logic_exec_count = nn.env('question3_logic_exec_count')
    if not question3_logic_exec_count:
        nn.env('question3_logic_exec_count', 1)
    else:
        question3_logic_exec_count = question3_logic_exec_count + 1
        nn.env('question3_logic_exec_count', question3_logic_exec_count)
        if question3_logic_exec_count and question3_logic_exec_count > 10:
            nn.log("Recursive execution detected")
            return
    # #5.2
    if not r:
        nn.log('condition', 'NULL')
        nn.env('result', 'NULL - молчание от клиента')
        question3_logic_NULL_NULL_count = nn.env('question3_logic_NULL_NULL_count')
        if not question3_logic_NULL_NULL_count:
            nn.env('question3_logic_NULL_NULL_count', 1)
            question3_logic_NULL_NULL_count = 1
        else:
            question3_logic_NULL_NULL_count = question3_logic_NULL_NULL_count + 1
            nn.env('question3_logic_NULL_NULL_count', question3_logic_NULL_NULL_count)
        if question3_logic_NULL_NULL_count == 1:
            offer_end3_()
            return
        else:
            hangup_dont_disturb_HANGUP()
            return
        return
    # #5.3
    if not r.has_entities():
        nn.log('condition', 'DEFAULT')
        nn.env('result', 'предложение по качеству работы/дефолтное возражение')
        question3_logic_DEFAULT_DEFAULT_count = nn.env('question3_logic_DEFAULT_DEFAULT_count')
        if not question3_logic_DEFAULT_DEFAULT_count:
            nn.env('question3_logic_DEFAULT_DEFAULT_count', 1)
            question3_logic_DEFAULT_DEFAULT_count = 1
        else:
            question3_logic_DEFAULT_DEFAULT_count = question3_logic_DEFAULT_DEFAULT_count + 1
            nn.env('question3_logic_DEFAULT_DEFAULT_count', question3_logic_DEFAULT_DEFAULT_count)
        if question3_logic_DEFAULT_DEFAULT_count == 1:
            question3_default_RETURN_LOGIC()
            return
        else:
            question4_main_RETURN_LOGIC()
            return
        return
    # #5.4
    if r.has_entity('callback'):
        if r.entity('callback') == 'true':
            nn.log('condition', 'callback=="true"')
            nn.env('result', 'просьба перезвонить')
            hangup_dont_disturb_HANGUP()
            return
    # #5.5
    if r.has_entity('wrong_time'):
        if r.entity('wrong_time') == 'true':
            nn.log('condition', 'wrong_time=="true"')
            nn.env('result', 'клиент занят')
            hangup_dont_disturb_HANGUP()
            return
    # #5.6
    if r.has_entity('dont_disturb'):
        if r.entity('dont_disturb') == 'true':
            nn.log('condition', 'dont_disturb=="true"')
            nn.env('result', 'больше не звонить')
            just_2_hangup_HANGUP()
            return
    # #5.7
    if r.has_entity('probable'):
        if r.entity('probable') == 'true':
            nn.log('condition', 'probable=="true"')
            nn.env('result', 'агрессия')
            just_2_hangup_HANGUP()
            return
    # #5.8
    if r.has_entity('robot'):
        if r.entity('robot') == 'true':
            nn.log('condition', 'robot=="true"')
            nn.env('result', 'распознан робот')
            question3_logic_robot_true_count = nn.env('question3_logic_robot_true_count')
            if not question3_logic_robot_true_count:
                nn.env('question3_logic_robot_true_count', 1)
                question3_logic_robot_true_count = 1
            else:
                question3_logic_robot_true_count = question3_logic_robot_true_count + 1
                nn.env('question3_logic_robot_true_count', question3_logic_robot_true_count)
            if question3_logic_robot_true_count == 1:
                question2_robot_JUST_SAY()
                offer_end3_()
                return
            else:
                question4_main_RETURN_LOGIC()
                return
            return
    # #5.9
    if r.has_entity('what_surname'):
        if r.entity('what_surname') == 'true':
            nn.log('condition', 'what_surname=="true"')
            nn.env('result', 'вопрос про имя')
            question3_logic_what_surname_true_count = nn.env('question3_logic_what_surname_true_count')
            if not question3_logic_what_surname_true_count:
                nn.env('question3_logic_what_surname_true_count', 1)
                question3_logic_what_surname_true_count = 1
            else:
                question3_logic_what_surname_true_count = question3_logic_what_surname_true_count + 1
                nn.env('question3_logic_what_surname_true_count', question3_logic_what_surname_true_count)
            if question3_logic_what_surname_true_count == 1:
                hello_name_JUST_SAY()
                offer_end3_()
                return
            else:
                question4_main_RETURN_LOGIC()
                return
            return
    # #5.10
    if r.has_entity('what_company'):
        if r.entity('what_company') == 'true':
            nn.log('condition', 'what_company=="true"')
            nn.env('result', 'вопрос какая компания')
            question3_logic_what_company_true_count = nn.env('question3_logic_what_company_true_count')
            if not question3_logic_what_company_true_count:
                nn.env('question3_logic_what_company_true_count', 1)
                question3_logic_what_company_true_count = 1
            else:
                question3_logic_what_company_true_count = question3_logic_what_company_true_count + 1
                nn.env('question3_logic_what_company_true_count', question3_logic_what_company_true_count)
            if question3_logic_what_company_true_count == 1:
                question1_what_company_JUST_SAY()
                offer_end3_()
                return
            else:
                question4_main_RETURN_LOGIC()
                return
            return
    # #5.11
    if r.has_entity('how_long'):
        if r.entity('how_long') == 'true':
            nn.log('condition', 'how_long=="true"')
            nn.env('result', 'вопрос по времени беседы')
            question3_logic_how_long_true_count = nn.env('question3_logic_how_long_true_count')
            if not question3_logic_how_long_true_count:
                nn.env('question3_logic_how_long_true_count', 1)
                question3_logic_how_long_true_count = 1
            else:
                question3_logic_how_long_true_count = question3_logic_how_long_true_count + 1
                nn.env('question3_logic_how_long_true_count', question3_logic_how_long_true_count)
            if question3_logic_how_long_true_count == 1:
                hello_how_long_JUST_SAY()
                offer_end3_()
                return
            else:
                question4_main_RETURN_LOGIC()
                return
            return
    # #5.12
    if r.has_entity('purpose_call'):
        if r.entity('purpose_call') == 'true':
            nn.log('condition', 'purpose_call=="true"')
            nn.env('result', 'вопрос о цели звонка')
            question3_logic_purpose_call_true_count = nn.env('question3_logic_purpose_call_true_count')
            if not question3_logic_purpose_call_true_count:
                nn.env('question3_logic_purpose_call_true_count', 1)
                question3_logic_purpose_call_true_count = 1
            else:
                question3_logic_purpose_call_true_count = question3_logic_purpose_call_true_count + 1
                nn.env('question3_logic_purpose_call_true_count', question3_logic_purpose_call_true_count)
            if question3_logic_purpose_call_true_count == 1:
                offer_end3_()
                return
            else:
                hangup_answers_HANGUP()
                return
            return
    # #5.13
    if r.has_entity('where_address'):
        if r.entity('where_address') == 'true':
            nn.log('condition', 'where_address=="true"')
            nn.env('result', 'вопрос о месте нахождения офиса')
            question3_logic_where_address_true_count = nn.env('question3_logic_where_address_true_count')
            if not question3_logic_where_address_true_count:
                nn.env('question3_logic_where_address_true_count', 1)
                question3_logic_where_address_true_count = 1
            else:
                question3_logic_where_address_true_count = question3_logic_where_address_true_count + 1
                nn.env('question3_logic_where_address_true_count', question3_logic_where_address_true_count)
            if question3_logic_where_address_true_count == 1:
                question2_city_JUST_SAY()
                offer_end3_()
                return
            else:
                hangup_answers_HANGUP()
                return
            return
    # #5.14
    if r.has_entity('don’t_order_different_products'):
        if r.entity('don’t_order_different_products') == 'true':
            nn.log('condition', 'don’t_order_different_products=="true"')
            nn.env('result', 'нет возможности заказать разных производителей')
            question3_different_products_JUST_SAY()
            question4_main_RETURN_LOGIC()
            return
    # #5.15
    if r.has_entity('failure'):
        if r.entity('failure') == 'true':
            nn.log('condition', 'failure=="true"')
            nn.env('result', 'произошел технический сбой')
            expert_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
    # #5.16
    if r.has_entity('farmer_certificate'):
        if r.entity('farmer_certificate') == 'true':
            nn.log('condition', 'farmer_certificate=="true"')
            nn.env('result', 'у каких фермеров можно расплатиться сертификатом')
            question1_farmer_certificate_JUST_SAY()
            question4_main_RETURN_LOGIC()
            return
    # #5.17
    if r.has_entity('what_do_animals_eat'):
        if r.entity('what_do_animals_eat') == 'true':
            nn.log('condition', 'what_do_animals_eat=="true"')
            nn.env('result', 'чем питаются животные')
            question1_delivery_date_JUST_SAY()
            question4_main_RETURN_LOGIC()
            return
    # #5.18
    if r.has_entity('how_are_contained'):
        if r.entity('how_are_contained') == 'true':
            nn.log('condition', 'how_are_contained=="true"')
            nn.env('result', 'в каких условиях содержатся')
            question1_delivery_date_JUST_SAY()
            question4_main_RETURN_LOGIC()
            return
    # #5.19
    if r.has_entity('expensive'):
        if r.entity('expensive') == 'true':
            nn.log('condition', 'expensive=="true"')
            nn.env('result', 'дорого')
            question3_expensive_JUST_SAY()
            question4_main_RETURN_LOGIC()
            return
    # #5.20
    if r.has_entity('wait_bit'):
        if r.entity('wait_bit') == 'true':
            nn.log('condition', 'wait_bit=="true"')
            nn.env('result', 'абонент просит подождать')
            question3_logic_wait_bit_true_count = nn.env('question3_logic_wait_bit_true_count')
            if not question3_logic_wait_bit_true_count:
                nn.env('question3_logic_wait_bit_true_count', 1)
                question3_logic_wait_bit_true_count = 1
            else:
                question3_logic_wait_bit_true_count = question3_logic_wait_bit_true_count + 1
                nn.env('question3_logic_wait_bit_true_count', question3_logic_wait_bit_true_count)
            if question3_logic_wait_bit_true_count == 1:
                question3_wait_bit_JUST_RETURN()
                offer_end3_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #5.21
    if r.has_entity('repeat'):
        if r.entity('repeat') == 'true':
            nn.log('condition', 'repeat=="true"')
            nn.env('result', 'просьба повторить')
            question3_logic_repeat_true_count = nn.env('question3_logic_repeat_true_count')
            if not question3_logic_repeat_true_count:
                nn.env('question3_logic_repeat_true_count', 1)
                question3_logic_repeat_true_count = 1
            else:
                question3_logic_repeat_true_count = question3_logic_repeat_true_count + 1
                nn.env('question3_logic_repeat_true_count', question3_logic_repeat_true_count)
            if question3_logic_repeat_true_count == 1:
                offer_end3_()
                return
            else:
                hangup_answers_HANGUP()
                return
            return
    # #5.22
    if r.has_entity('no'):
        if r.entity('no') == 'true':
            nn.log('condition', 'no=="true"')
            nn.env('result', 'нет предложений по улучшению')
            question4_main_RETURN_LOGIC()
            return
    # #5.23
    if r.has_entity('not_interesting'):
        if r.entity('not_interesting') == 'true':
            nn.log('condition', 'not_interesting=="true"')
            nn.env('result', 'нет предложений по улучшению')
            question4_main_RETURN_LOGIC()
            return
    # #5.24
    if r.has_entity('no_need'):
        if r.entity('no_need') == 'true':
            nn.log('condition', 'no_need=="true"')
            nn.env('result', 'нет предложений по улучшению')
            question4_main_RETURN_LOGIC()
            return
    # #5.25
    if r.has_entity('dont_know'):
        if r.entity('dont_know') == 'true':
            nn.log('condition', 'dont_know=="true"')
            nn.env('result', 'нет предложений по улучшению')
            question4_main_RETURN_LOGIC()
            return
    # #5.26
    if r.has_entity('yes'):
        if r.entity('yes') == 'true':
            nn.log('condition', 'yes=="true"')
            nn.env('result', 'есть предложение по улучшению')
            question3_logic_yes_true_count = nn.env('question3_logic_yes_true_count')
            if not question3_logic_yes_true_count:
                nn.env('question3_logic_yes_true_count', 1)
                question3_logic_yes_true_count = 1
            else:
                question3_logic_yes_true_count = question3_logic_yes_true_count + 1
                nn.env('question3_logic_yes_true_count', question3_logic_yes_true_count)
            if question3_logic_yes_true_count == 1:
                question3_yes_RETURN_LOGIC()
                return
            elif question3_logic_yes_true_count == 2:
                offer_end3_()
                return
            else:
                question4_main_RETURN_LOGIC()
                return
            return
    # #5.27
    if r.has_entity('agree'):
        if r.entity('agree') == 'true':
            nn.log('condition', 'agree=="true"')
            nn.env('result', 'есть предложение по улучшению')
            question3_logic_agree_true_count = nn.env('question3_logic_agree_true_count')
            if not question3_logic_agree_true_count:
                nn.env('question3_logic_agree_true_count', 1)
                question3_logic_agree_true_count = 1
            else:
                question3_logic_agree_true_count = question3_logic_agree_true_count + 1
                nn.env('question3_logic_agree_true_count', question3_logic_agree_true_count)
            if question3_logic_agree_true_count == 1:
                question3_yes_RETURN_LOGIC()
                return
            elif question3_logic_agree_true_count == 2:
                offer_end3_()
                return
            else:
                question4_main_RETURN_LOGIC()
                return
            return
    # #5.28
    if r.has_entity('got_acquainted'):
        if r.entity('got_acquainted') == 'true':
            nn.log('condition', 'got_acquainted=="true"')
            nn.env('result', 'клиент только познакомился с сайтом')
            question4_main_RETURN_LOGIC()
            return
    # #5.29
    if r.has_entity('question'):
        if r.entity('question') == 'true':
            nn.log('condition', 'question=="true"')
            nn.env('result', 'клиент хочет задать вопрос')
            positive_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
    # #5.30
    if r.has_entity('annoying_robots'):
        if r.entity('annoying_robots') == 'true':
            nn.log('condition', 'annoying_robots=="true"')
            nn.env('result', 'роботы раздражают')
            expert_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
    # #5.31
    if r.has_entity('connect_operator'):
        if r.entity('connect_operator') == 'true':
            nn.log('condition', 'connect_operator=="true"')
            nn.env('result', 'просьба перевести на живого человека')
            expert_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
    # #5.32
    if r.has_entity('bad_connection'):
        if r.entity('bad_connection') == 'true':
            nn.log('condition', 'bad_connection=="true"')
            nn.env('result', 'плохая связь')
            question3_logic_bad_connection_true_count = nn.env('question3_logic_bad_connection_true_count')
            if not question3_logic_bad_connection_true_count:
                nn.env('question3_logic_bad_connection_true_count', 1)
                question3_logic_bad_connection_true_count = 1
            else:
                question3_logic_bad_connection_true_count = question3_logic_bad_connection_true_count + 1
                nn.env('question3_logic_bad_connection_true_count', question3_logic_bad_connection_true_count)
            if question3_logic_bad_connection_true_count == 1:
                offer_end3_()
                return
            else:
                hangup_answers_HANGUP()
                return
            return
    # #5.33
    if r.has_entity('hear_me'):
        if r.entity('hear_me') == 'true':
            nn.log('condition', 'hear_me=="true"')
            nn.env('result', 'клиент акциентирует на себе внимание')
            question3_logic_hear_me_true_count = nn.env('question3_logic_hear_me_true_count')
            if not question3_logic_hear_me_true_count:
                nn.env('question3_logic_hear_me_true_count', 1)
                question3_logic_hear_me_true_count = 1
            else:
                question3_logic_hear_me_true_count = question3_logic_hear_me_true_count + 1
                nn.env('question3_logic_hear_me_true_count', question3_logic_hear_me_true_count)
            if question3_logic_hear_me_true_count == 1:
                offer_end3_()
                return
            else:
                hangup_answers_HANGUP()
                return
            return
    # #5.34
    if r.has_entity('goodbye'):
        if r.entity('goodbye') == 'true':
            nn.log('condition', 'goodbye=="true"')
            nn.env('result', 'до свидание')
            question3_logic_goodbye_true_count = nn.env('question3_logic_goodbye_true_count')
            if not question3_logic_goodbye_true_count:
                nn.env('question3_logic_goodbye_true_count', 1)
                question3_logic_goodbye_true_count = 1
            else:
                question3_logic_goodbye_true_count = question3_logic_goodbye_true_count + 1
                nn.env('question3_logic_goodbye_true_count', question3_logic_goodbye_true_count)
            if question3_logic_goodbye_true_count == 1:
                hello_how_long_JUST_SAY()
                offer_end3_()
                return
            else:
                just_hangup_HANGUP()
                return
            return


# #5.3
# Не поняла, повторите еще раз, пожалуйста.
@check_call_state(nv)
def question3_default_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question3_default')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['no',
                             'dont_disturb',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'bad_connection',
                             'what_surname',
                             'robot',
                             'not_interesting',
                             'no_need',
                             'how_are_contained',
                             'dont_know',
                             'repeat',
                             'connect_operator',
                             'what_do_animals_eat',
                             'question',
                             'hear_me',
                             'yes',
                             'wait_bit',
                             'probable',
                             'don’t_order_different_products',
                             'purpose_call',
                             'agree',
                             'expensive',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'callback',
                             'wrong_time']) as r:
        nv.say('question3_default')
    return question3_logic(r)
    pass


# #5.20
# Да, конечно, подожду…(ожижание 15 секунд)
@check_call_state(nv)
def question3_wait_bit_JUST_RETURN():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question3_wait_bit')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['no',
                             'dont_disturb',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'bad_connection',
                             'what_surname',
                             'robot',
                             'not_interesting',
                             'no_need',
                             'how_are_contained',
                             'dont_know',
                             'repeat',
                             'connect_operator',
                             'what_do_animals_eat',
                             'question',
                             'hear_me',
                             'yes',
                             'wait_bit',
                             'probable',
                             'don’t_order_different_products',
                             'purpose_call',
                             'agree',
                             'expensive',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'callback',
                             'wrong_time']) as r:
        nv.say('question3_wait_bit')
    return
    pass


# #5.35
# 5.36
# 5.37
# У Вас есть предложение по улучшению?
# Есть мысли, как сделать лучше сервис?
# Может у Вас есть идеи, как улучшить платформу?
@check_call_state(nv)
def offer_end3_():
    offer_end3_count = nn.env('offer_end3_count')
    if not offer_end3_count:
        nn.env('offer_end3_count', 1)
        offer_end3_count = 1
    else:
        offer_end3_count = offer_end3_count + 1
        nn.env('offer_end3_count', offer_end3_count)
    offer_end3_count = offer_end3_count % 3
    if offer_end3_count == 0:
        offer_end3_count = 3
    nn.log('unit', 'offer_end3_' + str(offer_end3_count))
    nv.set_default('listen', {'interruption_no_input_timeout': 1000,
                              'no_input_timeout': 10,
                              'recognition_timeout': 5000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 10})

    with nv.listen((None, None, 25, 'AND'),
                   entities=['no',
                             'dont_disturb',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'bad_connection',
                             'what_surname',
                             'robot',
                             'not_interesting',
                             'no_need',
                             'how_are_contained',
                             'dont_know',
                             'repeat',
                             'connect_operator',
                             'what_do_animals_eat',
                             'question',
                             'hear_me',
                             'yes',
                             'wait_bit',
                             'probable',
                             'don’t_order_different_products',
                             'purpose_call',
                             'agree',
                             'expensive',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'callback',
                             'wrong_time']) as r:
        nv.say('offer_end3_' + str(offer_end3_count))
    return question3_logic(r)
    pass


# #5.19
# Почти каждый день у нас появляются новые фермеры, возможно у них вам подойдет цена больше.
@check_call_state(nv)
def question3_expensive_JUST_SAY():
    nn.log('unit', 'question3_expensive')
    nv.say('question3_expensive')
    return
    pass


# #5.14
# На текущий момент данный функционал уже находится в разработке.
@check_call_state(nv)
def question3_different_products_JUST_SAY():
    nn.log('unit', 'question3_different_products')
    nv.say('question3_different_products')
    return
    pass


# #5.1
# Как бы Вы хотели повысить качество работы нашего сервиса?
@check_call_state(nv)
def question3_main_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question3_main')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['no',
                             'dont_disturb',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'bad_connection',
                             'what_surname',
                             'robot',
                             'not_interesting',
                             'no_need',
                             'how_are_contained',
                             'dont_know',
                             'repeat',
                             'connect_operator',
                             'what_do_animals_eat',
                             'question',
                             'hear_me',
                             'yes',
                             'wait_bit',
                             'probable',
                             'don’t_order_different_products',
                             'purpose_call',
                             'agree',
                             'expensive',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'callback',
                             'wrong_time']) as r:
        nv.say('question3_main')
    return question3_logic(r)
    pass


@check_call_state(nv)
def question4_logic(r):
    nn.log('unit', 'question4_logic')
    question4_logic_exec_count = nn.env('question4_logic_exec_count')
    if not question4_logic_exec_count:
        nn.env('question4_logic_exec_count', 1)
    else:
        question4_logic_exec_count = question4_logic_exec_count + 1
        nn.env('question4_logic_exec_count', question4_logic_exec_count)
        if question4_logic_exec_count and question4_logic_exec_count > 10:
            nn.log("Recursive execution detected")
            return
    # #6.2
    if not r:
        nn.log('condition', 'NULL')
        nn.env('result', 'NULL - молчание от клиента')
        question4_logic_NULL_NULL_count = nn.env('question4_logic_NULL_NULL_count')
        if not question4_logic_NULL_NULL_count:
            nn.env('question4_logic_NULL_NULL_count', 1)
            question4_logic_NULL_NULL_count = 1
        else:
            question4_logic_NULL_NULL_count = question4_logic_NULL_NULL_count + 1
            nn.env('question4_logic_NULL_NULL_count', question4_logic_NULL_NULL_count)
        if question4_logic_NULL_NULL_count == 1:
            question4_null_RETURN_LOGIC()
            return
        else:
            hangup_dont_disturb_HANGUP()
            return
        return
    # #6.3
    if not r.has_entities():
        nn.log('condition', 'DEFAULT')
        nn.env('result', 'дефолтное возражение')
        question4_logic_DEFAULT_DEFAULT_count = nn.env('question4_logic_DEFAULT_DEFAULT_count')
        if not question4_logic_DEFAULT_DEFAULT_count:
            nn.env('question4_logic_DEFAULT_DEFAULT_count', 1)
            question4_logic_DEFAULT_DEFAULT_count = 1
        else:
            question4_logic_DEFAULT_DEFAULT_count = question4_logic_DEFAULT_DEFAULT_count + 1
            nn.env('question4_logic_DEFAULT_DEFAULT_count', question4_logic_DEFAULT_DEFAULT_count)
        if question4_logic_DEFAULT_DEFAULT_count == 1:
            question4_default_RETURN_LOGIC()
            return
        else:
            positive_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
        return
    # #6.4
    if r.has_entity('callback'):
        if r.entity('callback') == 'true':
            nn.log('condition', 'callback=="true"')
            nn.env('result', 'просьба перезвонить')
            hangup_dont_disturb_HANGUP()
            return
    # #6.5
    if r.has_entity('wrong_time'):
        if r.entity('wrong_time') == 'true':
            nn.log('condition', 'wrong_time=="true"')
            nn.env('result', 'клиент занят')
            hangup_dont_disturb_HANGUP()
            return
    # #6.6
    if r.has_entity('dont_disturb'):
        if r.entity('dont_disturb') == 'true':
            nn.log('condition', 'dont_disturb=="true"')
            nn.env('result', 'больше не звонить')
            hangup_dont_disturb_HANGUP()
            return
    # #6.7
    if r.has_entity('probable'):
        if r.entity('probable') == 'true':
            nn.log('condition', 'probable=="true"')
            nn.env('result', 'агрессия')
            hangup_dont_disturb_HANGUP()
            return
    # #6.8
    if r.has_entity('robot'):
        if r.entity('robot') == 'true':
            nn.log('condition', 'robot=="true"')
            nn.env('result', 'распознан робот')
            question4_logic_robot_true_count = nn.env('question4_logic_robot_true_count')
            if not question4_logic_robot_true_count:
                nn.env('question4_logic_robot_true_count', 1)
                question4_logic_robot_true_count = 1
            else:
                question4_logic_robot_true_count = question4_logic_robot_true_count + 1
                nn.env('question4_logic_robot_true_count', question4_logic_robot_true_count)
            if question4_logic_robot_true_count == 1:
                question4_default_RETURN_LOGIC()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.9
    if r.has_entity('what_surname'):
        if r.entity('what_surname') == 'true':
            nn.log('condition', 'what_surname=="true"')
            nn.env('result', 'вопрос про имя')
            question4_logic_what_surname_true_count = nn.env('question4_logic_what_surname_true_count')
            if not question4_logic_what_surname_true_count:
                nn.env('question4_logic_what_surname_true_count', 1)
                question4_logic_what_surname_true_count = 1
            else:
                question4_logic_what_surname_true_count = question4_logic_what_surname_true_count + 1
                nn.env('question4_logic_what_surname_true_count', question4_logic_what_surname_true_count)
            if question4_logic_what_surname_true_count == 1:
                hello_name_JUST_SAY()
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.10
    if r.has_entity('what_company'):
        if r.entity('what_company') == 'true':
            nn.log('condition', 'what_company=="true"')
            nn.env('result', 'вопрос какая компания')
            question4_logic_what_company_true_count = nn.env('question4_logic_what_company_true_count')
            if not question4_logic_what_company_true_count:
                nn.env('question4_logic_what_company_true_count', 1)
                question4_logic_what_company_true_count = 1
            else:
                question4_logic_what_company_true_count = question4_logic_what_company_true_count + 1
                nn.env('question4_logic_what_company_true_count', question4_logic_what_company_true_count)
            if question4_logic_what_company_true_count == 1:
                question1_what_company_JUST_SAY()
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.11
    if r.has_entity('how_long'):
        if r.entity('how_long') == 'true':
            nn.log('condition', 'how_long=="true"')
            nn.env('result', 'вопрос по времени беседы')
            question4_logic_how_long_true_count = nn.env('question4_logic_how_long_true_count')
            if not question4_logic_how_long_true_count:
                nn.env('question4_logic_how_long_true_count', 1)
                question4_logic_how_long_true_count = 1
            else:
                question4_logic_how_long_true_count = question4_logic_how_long_true_count + 1
                nn.env('question4_logic_how_long_true_count', question4_logic_how_long_true_count)
            if question4_logic_how_long_true_count == 1:
                hello_how_long_JUST_SAY()
                question4_default_RETURN_LOGIC()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.12
    if r.has_entity('purpose_call'):
        if r.entity('purpose_call') == 'true':
            nn.log('condition', 'purpose_call=="true"')
            nn.env('result', 'вопрос о цели звонка')
            hangup_dont_disturb_HANGUP()
            return
    # #6.13
    if r.has_entity('where_address'):
        if r.entity('where_address') == 'true':
            nn.log('condition', 'where_address=="true"')
            nn.env('result', 'вопрос о месте нахождения офиса')
            question4_logic_where_address_true_count = nn.env('question4_logic_where_address_true_count')
            if not question4_logic_where_address_true_count:
                nn.env('question4_logic_where_address_true_count', 1)
                question4_logic_where_address_true_count = 1
            else:
                question4_logic_where_address_true_count = question4_logic_where_address_true_count + 1
                nn.env('question4_logic_where_address_true_count', question4_logic_where_address_true_count)
            if question4_logic_where_address_true_count == 1:
                question2_city_JUST_SAY()
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.14
    if r.has_entity('types_transportation'):
        if r.entity('types_transportation') == 'true':
            nn.log('condition', 'types_transportation=="true"')
            nn.env('result', 'вопрос про способы доставки')
            question4_logic_types_transportation_true_count = nn.env('question4_logic_types_transportation_true_count')
            if not question4_logic_types_transportation_true_count:
                nn.env('question4_logic_types_transportation_true_count', 1)
                question4_logic_types_transportation_true_count = 1
            else:
                question4_logic_types_transportation_true_count = question4_logic_types_transportation_true_count + 1
                nn.env('question4_logic_types_transportation_true_count',
                       question4_logic_types_transportation_true_count)
            if question4_logic_types_transportation_true_count == 1:
                question1_transportation_JUST_SAY()
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.15
    if r.has_entity('transport_delivery_date'):
        if r.entity('transport_delivery_date') == 'true':
            nn.log('condition', 'transport_delivery_date=="true"')
            nn.env('result', 'вопрос про срок поставки')
            question4_logic_transport_delivery_date_true_count = nn.env(
                'question4_logic_transport_delivery_date_true_count')
            if not question4_logic_transport_delivery_date_true_count:
                nn.env('question4_logic_transport_delivery_date_true_count', 1)
                question4_logic_transport_delivery_date_true_count = 1
            else:
                question4_logic_transport_delivery_date_true_count = question4_logic_transport_delivery_date_true_count + 1
                nn.env('question4_logic_transport_delivery_date_true_count',
                       question4_logic_transport_delivery_date_true_count)
            if question4_logic_transport_delivery_date_true_count == 1:
                question1_delivery_date_JUST_SAY()
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.16
    if r.has_entity('free_shipping'):
        if r.entity('free_shipping') == 'true':
            nn.log('condition', 'free_shipping=="true"')
            nn.env('result', 'есть ли бесплатная доставка')
            question4_logic_free_shipping_true_count = nn.env('question4_logic_free_shipping_true_count')
            if not question4_logic_free_shipping_true_count:
                nn.env('question4_logic_free_shipping_true_count', 1)
                question4_logic_free_shipping_true_count = 1
            else:
                question4_logic_free_shipping_true_count = question4_logic_free_shipping_true_count + 1
                nn.env('question4_logic_free_shipping_true_count', question4_logic_free_shipping_true_count)
            if question4_logic_free_shipping_true_count == 1:
                question1_expensive_shipping_JUST_SAY()
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.17
    if r.has_entity('where_pickup_points'):
        if r.entity('where_pickup_points') == 'true':
            nn.log('condition', 'where_pickup_points=="true"')
            nn.env('result', 'где посмотреть пункты самовывоза')
            question4_logic_where_pickup_points_true_count = nn.env('question4_logic_where_pickup_points_true_count')
            if not question4_logic_where_pickup_points_true_count:
                nn.env('question4_logic_where_pickup_points_true_count', 1)
                question4_logic_where_pickup_points_true_count = 1
            else:
                question4_logic_where_pickup_points_true_count = question4_logic_where_pickup_points_true_count + 1
                nn.env('question4_logic_where_pickup_points_true_count', question4_logic_where_pickup_points_true_count)
            if question4_logic_where_pickup_points_true_count == 1:
                question1_pickup_only_JUST_RETURN()
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.18
    if r.has_entity('failure'):
        if r.entity('failure') == 'true':
            nn.log('condition', 'failure=="true"')
            nn.env('result', 'произошел технический сбой')
            expert_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
    # #6.19
    if r.has_entity('my_region'):
        if r.entity('my_region') == 'true':
            nn.log('condition', 'my_region=="true"')
            nn.env('result', 'клиент уточняет, есть ли фермеры в его регионе')
            question4_logic_my_region_true_count = nn.env('question4_logic_my_region_true_count')
            if not question4_logic_my_region_true_count:
                nn.env('question4_logic_my_region_true_count', 1)
                question4_logic_my_region_true_count = 1
            else:
                question4_logic_my_region_true_count = question4_logic_my_region_true_count + 1
                nn.env('question4_logic_my_region_true_count', question4_logic_my_region_true_count)
            if question4_logic_my_region_true_count == 1:
                question1_my_region_JUST_SAY()
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.20
    if r.has_entity('farmer_certificate'):
        if r.entity('farmer_certificate') == 'true':
            nn.log('condition', 'farmer_certificate=="true"')
            nn.env('result', 'у каких фермеров можно расплатиться сертификатом')
            question4_logic_farmer_certificate_true_count = nn.env('question4_logic_farmer_certificate_true_count')
            if not question4_logic_farmer_certificate_true_count:
                nn.env('question4_logic_farmer_certificate_true_count', 1)
                question4_logic_farmer_certificate_true_count = 1
            else:
                question4_logic_farmer_certificate_true_count = question4_logic_farmer_certificate_true_count + 1
                nn.env('question4_logic_farmer_certificate_true_count', question4_logic_farmer_certificate_true_count)
            if question4_logic_farmer_certificate_true_count == 1:
                question1_farmer_certificate_JUST_SAY()
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.21
    if r.has_entity('what_do_animals_eat'):
        if r.entity('what_do_animals_eat') == 'true':
            nn.log('condition', 'what_do_animals_eat=="true"')
            nn.env('result', 'чем питаются животные')
            question4_logic_what_do_animals_eat_true_count = nn.env('question4_logic_what_do_animals_eat_true_count')
            if not question4_logic_what_do_animals_eat_true_count:
                nn.env('question4_logic_what_do_animals_eat_true_count', 1)
                question4_logic_what_do_animals_eat_true_count = 1
            else:
                question4_logic_what_do_animals_eat_true_count = question4_logic_what_do_animals_eat_true_count + 1
                nn.env('question4_logic_what_do_animals_eat_true_count', question4_logic_what_do_animals_eat_true_count)
            if question4_logic_what_do_animals_eat_true_count == 1:
                question1_delivery_date_JUST_SAY()
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.22
    if r.has_entity('how_are_contained'):
        if r.entity('how_are_contained') == 'true':
            nn.log('condition', 'how_are_contained=="true"')
            nn.env('result', 'в каких условиях содержатся')
            question4_logic_how_are_contained_true_count = nn.env('question4_logic_how_are_contained_true_count')
            if not question4_logic_how_are_contained_true_count:
                nn.env('question4_logic_how_are_contained_true_count', 1)
                question4_logic_how_are_contained_true_count = 1
            else:
                question4_logic_how_are_contained_true_count = question4_logic_how_are_contained_true_count + 1
                nn.env('question4_logic_how_are_contained_true_count', question4_logic_how_are_contained_true_count)
            if question4_logic_how_are_contained_true_count == 1:
                question1_delivery_date_JUST_SAY()
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.23
    if r.has_entity('expiration_date'):
        if r.entity('expiration_date') == 'true':
            nn.log('condition', 'expiration_date=="true"')
            nn.env('result', 'где посмотреть срок годности')
            question4_logic_expiration_date_true_count = nn.env('question4_logic_expiration_date_true_count')
            if not question4_logic_expiration_date_true_count:
                nn.env('question4_logic_expiration_date_true_count', 1)
                question4_logic_expiration_date_true_count = 1
            else:
                question4_logic_expiration_date_true_count = question4_logic_expiration_date_true_count + 1
                nn.env('question4_logic_expiration_date_true_count', question4_logic_expiration_date_true_count)
            if question4_logic_expiration_date_true_count == 1:
                question1_expiration_date_JUST_SAY()
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.24
    if r.has_entity('payment_upon_receipt'):
        if r.entity('payment_upon_receipt') == 'true':
            nn.log('condition', 'payment_upon_receipt=="true"')
            nn.env('result', 'можно ли оплатить при получении')
            question4_logic_payment_upon_receipt_true_count = nn.env('question4_logic_payment_upon_receipt_true_count')
            if not question4_logic_payment_upon_receipt_true_count:
                nn.env('question4_logic_payment_upon_receipt_true_count', 1)
                question4_logic_payment_upon_receipt_true_count = 1
            else:
                question4_logic_payment_upon_receipt_true_count = question4_logic_payment_upon_receipt_true_count + 1
                nn.env('question4_logic_payment_upon_receipt_true_count',
                       question4_logic_payment_upon_receipt_true_count)
            if question4_logic_payment_upon_receipt_true_count == 1:
                question2_payment_upon_receipt_JUST_SAY()
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.25
    if r.has_entity('wait_bit'):
        if r.entity('wait_bit') == 'true':
            nn.log('condition', 'wait_bit=="true"')
            nn.env('result', 'абонент просит подождать')
            question4_logic_wait_bit_true_count = nn.env('question4_logic_wait_bit_true_count')
            if not question4_logic_wait_bit_true_count:
                nn.env('question4_logic_wait_bit_true_count', 1)
                question4_logic_wait_bit_true_count = 1
            else:
                question4_logic_wait_bit_true_count = question4_logic_wait_bit_true_count + 1
                nn.env('question4_logic_wait_bit_true_count', question4_logic_wait_bit_true_count)
            if question4_logic_wait_bit_true_count == 1:
                question4_wait_bit_JUST_RETURN()
                question4_null_RETURN_LOGIC()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.26
    if r.has_entity('repeat'):
        if r.entity('repeat') == 'true':
            nn.log('condition', 'repeat=="true"')
            nn.env('result', 'просьба повторить')
            question4_logic_repeat_true_count = nn.env('question4_logic_repeat_true_count')
            if not question4_logic_repeat_true_count:
                nn.env('question4_logic_repeat_true_count', 1)
                question4_logic_repeat_true_count = 1
            else:
                question4_logic_repeat_true_count = question4_logic_repeat_true_count + 1
                nn.env('question4_logic_repeat_true_count', question4_logic_repeat_true_count)
            if question4_logic_repeat_true_count == 1:
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.27
    if r.has_entity('no'):
        if r.entity('no') == 'true':
            nn.log('condition', 'no=="true"')
            nn.env('result', 'НЕТ вопросов')
            hangup_dont_disturb_HANGUP()
            return
    # #6.28
    if r.has_entity('dont_know'):
        if r.entity('dont_know') == 'true':
            nn.log('condition', 'dont_know=="true"')
            nn.env('result', 'НЕТ вопросов')
            hangup_dont_disturb_HANGUP()
            return
    # #6.29
    if r.has_entity('yes'):
        if r.entity('yes') == 'true':
            nn.log('condition', 'yes=="true"')
            nn.env('result', 'ЕСТЬ вопросы')
            question4_logic_yes_true_count = nn.env('question4_logic_yes_true_count')
            if not question4_logic_yes_true_count:
                nn.env('question4_logic_yes_true_count', 1)
                question4_logic_yes_true_count = 1
            else:
                question4_logic_yes_true_count = question4_logic_yes_true_count + 1
                nn.env('question4_logic_yes_true_count', question4_logic_yes_true_count)
            if question4_logic_yes_true_count == 1:
                question3_yes_RETURN_LOGIC()
                return
            elif question4_logic_yes_true_count == 2:
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.30
    if r.has_entity('agree'):
        if r.entity('agree') == 'true':
            nn.log('condition', 'agree=="true"')
            nn.env('result', 'ЕСТЬ вопросы')
            question4_logic_agree_true_count = nn.env('question4_logic_agree_true_count')
            if not question4_logic_agree_true_count:
                nn.env('question4_logic_agree_true_count', 1)
                question4_logic_agree_true_count = 1
            else:
                question4_logic_agree_true_count = question4_logic_agree_true_count + 1
                nn.env('question4_logic_agree_true_count', question4_logic_agree_true_count)
            if question4_logic_agree_true_count == 1:
                question3_yes_RETURN_LOGIC()
                return
            elif question4_logic_agree_true_count == 2:
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.31
    if r.has_entity('clear'):
        if r.entity('clear') == 'true':
            nn.log('condition', 'clear=="true"')
            nn.env('result', 'НЕТ вопросов')
            hangup_dont_disturb_HANGUP()
            return
    # #6.32
    if r.has_entity('got_acquainted'):
        if r.entity('got_acquainted') == 'true':
            nn.log('condition', 'got_acquainted=="true"')
            nn.env('result', 'НЕТ вопросов')
            hangup_dont_disturb_HANGUP()
            return
    # #6.33
    if r.has_entity('annoying_robots'):
        if r.entity('annoying_robots') == 'true':
            nn.log('condition', 'annoying_robots=="true"')
            nn.env('result', 'роботы раздражают')
            expert_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
    # #6.34
    if r.has_entity('connect_operator'):
        if r.entity('connect_operator') == 'true':
            nn.log('condition', 'connect_operator=="true"')
            nn.env('result', 'просьба перевести на живого человека')
            expert_transfer_JUST_SAY()
            callback_manager_RETURN_LOGIC()
            return
    # #6.35
    if r.has_entity('bad_connection'):
        if r.entity('bad_connection') == 'true':
            nn.log('condition', 'bad_connection=="true"')
            nn.env('result', 'плохая связь')
            question4_logic_bad_connection_true_count = nn.env('question4_logic_bad_connection_true_count')
            if not question4_logic_bad_connection_true_count:
                nn.env('question4_logic_bad_connection_true_count', 1)
                question4_logic_bad_connection_true_count = 1
            else:
                question4_logic_bad_connection_true_count = question4_logic_bad_connection_true_count + 1
                nn.env('question4_logic_bad_connection_true_count', question4_logic_bad_connection_true_count)
            if question4_logic_bad_connection_true_count == 1:
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.36
    if r.has_entity('hear_me'):
        if r.entity('hear_me') == 'true':
            nn.log('condition', 'hear_me=="true"')
            nn.env('result', 'клиент акциентирует на себе внимание')
            question4_logic_hear_me_true_count = nn.env('question4_logic_hear_me_true_count')
            if not question4_logic_hear_me_true_count:
                nn.env('question4_logic_hear_me_true_count', 1)
                question4_logic_hear_me_true_count = 1
            else:
                question4_logic_hear_me_true_count = question4_logic_hear_me_true_count + 1
                nn.env('question4_logic_hear_me_true_count', question4_logic_hear_me_true_count)
            if question4_logic_hear_me_true_count == 1:
                offer_end4_()
                return
            else:
                hangup_dont_disturb_HANGUP()
                return
            return
    # #6.37
    if r.has_entity('goodbye'):
        if r.entity('goodbye') == 'true':
            nn.log('condition', 'goodbye=="true"')
            nn.env('result', 'до свидание')
            hangup_dont_disturb_HANGUP()
            return


# #6.38
# 6.39
# Есть ещё вопросы?
# Хотите что-то ещё узнать?

@check_call_state(nv)
def offer_end4_():
    offer_end4_count = nn.env('offer_end4_count')
    if not offer_end4_count:
        nn.env('offer_end4_count', 1)
        offer_end4_count = 1
    else:
        offer_end4_count = offer_end4_count + 1
        nn.env('offer_end4_count', offer_end4_count)
    offer_end4_count = offer_end4_count % 2
    if offer_end4_count == 0:
        offer_end4_count = 2
    nn.log('unit', 'offer_end4_' + str(offer_end4_count))
    nv.set_default('listen', {'interruption_no_input_timeout': 1000,
                              'no_input_timeout': 10,
                              'recognition_timeout': 5000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 10})

    with nv.listen((None, None, 25, 'AND'),
                   entities=['no',
                             'dont_disturb',
                             'free_shipping',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'expiration_date',
                             'bad_connection',
                             'what_surname',
                             'robot',
                             'how_are_contained',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'what_do_animals_eat',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'clear',
                             'probable',
                             'purpose_call',
                             'payment_upon_receipt',
                             'agree',
                             'my_region',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'callback',
                             'wrong_time']) as r:
        nv.say('offer_end4_' + str(offer_end4_count))
    return question4_logic(r)
    pass


# #6.25
# Хорошо, подожду…(ожижание 15 секунд)
@check_call_state(nv)
def question4_wait_bit_JUST_RETURN():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question4_wait_bit')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['no',
                             'dont_disturb',
                             'free_shipping',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'expiration_date',
                             'bad_connection',
                             'what_surname',
                             'robot',
                             'how_are_contained',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'what_do_animals_eat',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'clear',
                             'probable',
                             'purpose_call',
                             'payment_upon_receipt',
                             'agree',
                             'my_region',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'callback',
                             'wrong_time']) as r:
        nv.say('question4_wait_bit')
    return
    pass


# #6.29
# Я слушаю…
@check_call_state(nv)
def question3_yes_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question3_yes')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['no',
                             'dont_disturb',
                             'free_shipping',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'expiration_date',
                             'bad_connection',
                             'what_surname',
                             'robot',
                             'how_are_contained',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'what_do_animals_eat',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'clear',
                             'probable',
                             'purpose_call',
                             'payment_upon_receipt',
                             'agree',
                             'my_region',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'callback',
                             'wrong_time']) as r:
        nv.say('question3_yes')
    return question4_logic(r)
    pass


# #6.3
# Могу соединить Вас с коллегой и он ответит на все ваши вопросы, хорошо?
@check_call_state(nv)
def question4_default_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question4_default')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['no',
                             'dont_disturb',
                             'free_shipping',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'expiration_date',
                             'bad_connection',
                             'what_surname',
                             'robot',
                             'how_are_contained',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'what_do_animals_eat',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'clear',
                             'probable',
                             'purpose_call',
                             'payment_upon_receipt',
                             'agree',
                             'my_region',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'callback',
                             'wrong_time']) as r:
        nv.say('question4_default')
    return question4_logic(r)
    pass


# #6.1
# Может у Вас вопросы ко мне есть?
@check_call_state(nv)
def question4_main_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question4_main')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['no',
                             'dont_disturb',
                             'free_shipping',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'expiration_date',
                             'bad_connection',
                             'what_surname',
                             'robot',
                             'how_are_contained',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'what_do_animals_eat',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'clear',
                             'probable',
                             'purpose_call',
                             'payment_upon_receipt',
                             'agree',
                             'my_region',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'callback',
                             'wrong_time']) as r:
        nv.say('question4_main')
    return question4_logic(r)
    pass


# #6.2
# Алло… вопросы у Вас есть какие-нибудь?
@check_call_state(nv)
def question4_null_RETURN_LOGIC():
    nv.set_default('listen', {'interruption_no_input_timeout': 10,
                              'no_input_timeout': 10,
                              'recognition_timeout': 3000,
                              'speech_complete_timeout': 10,
                              'start_timeout ': 0,
                              'asr_complete_timeout': 5000})
    nn.log('unit', 'question4_null')
    with nv.listen((None, None, 25, 'AND'),
                   entities=['no',
                             'dont_disturb',
                             'free_shipping',
                             'how_long',
                             'goodbye',
                             'what_company',
                             'expiration_date',
                             'bad_connection',
                             'what_surname',
                             'robot',
                             'how_are_contained',
                             'dont_know',
                             'repeat',
                             'types_transportation',
                             'connect_operator',
                             'what_do_animals_eat',
                             'hear_me',
                             'yes',
                             'transport_delivery_date',
                             'where_pickup_points',
                             'wait_bit',
                             'clear',
                             'probable',
                             'purpose_call',
                             'payment_upon_receipt',
                             'agree',
                             'my_region',
                             'annoying_robots',
                             'where_address',
                             'got_acquainted',
                             'failure',
                             'farmer_certificate',
                             'callback',
                             'wrong_time']) as r:
        nv.say('question4_null')
    return question4_logic(r)
    pass


@check_call_state(nv)
def positive_logic(r):
    nn.log('unit', 'positive_logic')
    positive_logic_exec_count = nn.env('positive_logic_exec_count')
    if not positive_logic_exec_count:
        nn.env('positive_logic_exec_count', 1)
    else:
        positive_logic_exec_count = positive_logic_exec_count + 1
        nn.env('positive_logic_exec_count', positive_logic_exec_count)
        if positive_logic_exec_count and positive_logic_exec_count > 10:
            nn.log("Recursive execution detected")
            return


# #7.3
#
@check_call_state(nv)
def callback_manager_RETURN_LOGIC():
    nn.log('unit', 'callback_manager')
    nn.log('Звонок менеджеру start')
    nn.log('condition', 'callback=true')
    nn.env('result', 'соединили с менеджером 1')
    nn.env('callback', 'true')
    nn.env('duration', nv.get_call_duration())
    nn.env('hang_up_phone', 'Bridge')
    nv.bridge("sip:111@10.129.0.187:5061", channel='kd_systems_5684_v3'
              , proto_additional={"P-Asserted-Identity": "<tel:" + '7' + nn.dialog['msisdn'] + ">",
                                  'caller_id': '7' + nn.dialog['msisdn'],
                                  'Remote-Party-ID': "<tel:" + '7' + nn.dialog[
                                      'msisdn'] + '>;party=calling;screen=yes;privacy=off',
                                  'Diversion': '7' + nn.dialog['msisdn'] + ' <sip:7' + nn.dialog[
                                      'msisdn'] + '@10.129.0.187:5061>;reason=unconditional'
                                  }
              )
    nn.log('Звонок менеджеру finish')
    return
    pass


# #7.1
# Давайте я Вас сейчас переведу на моего коллегу. Оставайтесь на линии.
@check_call_state(nv)
def expert_transfer_JUST_SAY():
    nn.log('unit', 'expert_transfer')
    nv.say('expert_transfer')
    return
    pass


# #7.2
# Давайте я Вас сейчас переведу на моего коллегу и он ответит на Ваши вопросы. Оставайтесь на линии.
@check_call_state(nv)
def positive_transfer_JUST_SAY():
    nn.log('unit', 'positive_transfer')
    nv.say('positive_transfer')
    return
    pass


@check_call_state(nv)
def hangup_logic(r):
    nn.log('unit', 'hangup_logic')
    hangup_logic_exec_count = nn.env('hangup_logic_exec_count')
    if not hangup_logic_exec_count:
        nn.env('hangup_logic_exec_count', 1)
    else:
        hangup_logic_exec_count = hangup_logic_exec_count + 1
        nn.env('hangup_logic_exec_count', hangup_logic_exec_count)
        if hangup_logic_exec_count and hangup_logic_exec_count > 10:
            nn.log("Recursive execution detected")
            return


# #8.1
# Благодарю Вас за уделенное время. До свидания!
def hangup_dont_disturb_HANGUP():
    nn.log('unit', 'hangup_dont_disturb')
    nv.say('hangup_dont_disturb')
    nv.hangup()
    return


# #8.3
# Вас не слышно. Будет лучше, если я Вам перезвоню. Всего доброго, до свидания!
def hangup_null_HANGUP():
    nn.log('unit', 'hangup_null')
    nv.say('hangup_null')
    nv.hangup()
    return


# #8.2
# Мы перезвоним Вам позже, до свидания!
def hangup_recall_HANGUP():
    nn.log('unit', 'hangup_recall')
    nv.say('hangup_recall')
    nv.hangup()
    return


# #8.5
# До свидания!
def just_hangup_HANGUP():
    nn.log('unit', 'just_hangup')
    nv.say('just_hangup')
    nv.hangup()
    return


# #8.6
# Извините за беспокойство. До свидания!
def just_2_hangup_HANGUP():
    nn.log('unit', 'just_2_hangup')
    nv.say('just_2_hangup')
    nv.hangup()
    return


# #8.4
# Наверное, какие-то проблемы со связью, давайте я вам лучше перезвоню. До свидания!
def hangup_answers_HANGUP():
    nn.log('unit', 'hangup_answers')
    nv.say('hangup_answers')
    nv.hangup()
    return


def hangup_HANGUP():
    nn.log('unit', 'hangup_HANGUP')
    nv.hangup()
    return


# -----------------------------------------------
def nulify_global_variables():
    reset_global_variables()
    nn.env('tube_logic_exec_count', 0)
    nn.env('tube_logic_NULL_NULL_count', 0)
    nn.env('hello_logic_exec_count', 0)
    nn.env('hello_logic_NULL_NULL_count', 0)
    nn.env('hello_logic_DEFAULT_DEFAULT_count', 0)
    nn.env('hello_logic_wrong_time_sick_true_count', 0)
    nn.env('hello_logic_wrong_time_wheel_true_count', 0)
    nn.env('hello_logic_wait_bit_true_count', 0)
    nn.env('hello_logic_bad_connection_true_count', 0)
    nn.env('hello_logic_hear_me_true_count', 0)
    nn.env('hello_logic_goodbye_true_count', 0)
    nn.env('question1_logic_exec_count', 0)
    nn.env('question1_logic_NULL_NULL_count', 0)
    nn.env('question1_logic_DEFAULT_DEFAULT_count', 0)
    nn.env('question1_logic_robot_true_count', 0)
    nn.env('question1_logic_what_surname_true_count', 0)
    nn.env('question1_logic_what_company_true_count', 0)
    nn.env('question1_logic_how_long_true_count', 0)
    nn.env('question1_logic_purpose_call_true_count', 0)
    nn.env('question1_logic_where_address_true_count', 0)
    nn.env('question1_logic_what_did_you_order_true_count', 0)
    nn.env('question1_logic_types_transportation_true_count', 0)
    nn.env('question1_logic_no_shipping_true_count', 0)
    nn.env('question1_logic_wait_bit_true_count', 0)
    nn.env('question1_logic_repeat_true_count', 0)
    nn.env('question1_logic_yes_true_count', 0)
    nn.env('question1_logic_agree_true_count', 0)
    nn.env('question1_logic_bad_connection_true_count', 0)
    nn.env('question1_logic_hear_me_true_count', 0)
    nn.env('question1_logic_goodbye_true_count', 0)
    nn.env('offer_end_count', 0)
    nn.env('question2_logic_exec_count', 0)
    nn.env('question2_logic_NULL_NULL_count', 0)
    nn.env('question2_logic_DEFAULT_DEFAULT_count', 0)
    nn.env('question2_logic_robot_true_count', 0)
    nn.env('question2_logic_what_surname_true_count', 0)
    nn.env('question2_logic_what_company_true_count', 0)
    nn.env('question2_logic_how_long_true_count', 0)
    nn.env('question2_logic_purpose_call_true_count', 0)
    nn.env('question2_logic_where_address_true_count', 0)
    nn.env('question2_logic_wait_bit_true_count', 0)
    nn.env('question2_logic_repeat_true_count', 0)
    nn.env('question2_logic_bad_connection_true_count', 0)
    nn.env('question2_logic_hear_me_true_count', 0)
    nn.env('question2_logic_goodbye_true_count', 0)
    nn.env('question3_logic_exec_count', 0)
    nn.env('question3_logic_NULL_NULL_count', 0)
    nn.env('question3_logic_DEFAULT_DEFAULT_count', 0)
    nn.env('question3_logic_robot_true_count', 0)
    nn.env('question3_logic_what_surname_true_count', 0)
    nn.env('question3_logic_what_company_true_count', 0)
    nn.env('question3_logic_how_long_true_count', 0)
    nn.env('question3_logic_purpose_call_true_count', 0)
    nn.env('question3_logic_where_address_true_count', 0)
    nn.env('question3_logic_wait_bit_true_count', 0)
    nn.env('question3_logic_repeat_true_count', 0)
    nn.env('question3_logic_yes_true_count', 0)
    nn.env('question3_logic_agree_true_count', 0)
    nn.env('question3_logic_bad_connection_true_count', 0)
    nn.env('question3_logic_hear_me_true_count', 0)
    nn.env('question3_logic_goodbye_true_count', 0)
    nn.env('offer_end3_count', 0)
    nn.env('question4_logic_exec_count', 0)
    nn.env('question4_logic_NULL_NULL_count', 0)
    nn.env('question4_logic_DEFAULT_DEFAULT_count', 0)
    nn.env('question4_logic_robot_true_count', 0)
    nn.env('question4_logic_what_surname_true_count', 0)
    nn.env('question4_logic_what_company_true_count', 0)
    nn.env('question4_logic_how_long_true_count', 0)
    nn.env('question4_logic_where_address_true_count', 0)
    nn.env('question4_logic_types_transportation_true_count', 0)
    nn.env('question4_logic_transport_delivery_date_true_count', 0)
    nn.env('question4_logic_free_shipping_true_count', 0)
    nn.env('question4_logic_where_pickup_points_true_count', 0)
    nn.env('question4_logic_my_region_true_count', 0)
    nn.env('question4_logic_farmer_certificate_true_count', 0)
    nn.env('question4_logic_what_do_animals_eat_true_count', 0)
    nn.env('question4_logic_how_are_contained_true_count', 0)
    nn.env('question4_logic_expiration_date_true_count', 0)
    nn.env('question4_logic_payment_upon_receipt_true_count', 0)
    nn.env('question4_logic_wait_bit_true_count', 0)
    nn.env('question4_logic_repeat_true_count', 0)
    nn.env('question4_logic_yes_true_count', 0)
    nn.env('question4_logic_agree_true_count', 0)
    nn.env('question4_logic_bad_connection_true_count', 0)
    nn.env('question4_logic_hear_me_true_count', 0)
    nn.env('offer_end4_count', 0)
    nn.env('positive_logic_exec_count', 0)
    nn.env('hangup_logic_exec_count', 0)


def reset_global_variables():
    nn.env('result', '')
    nn.env('call_start', '')
    nn.env('duration', '')
    nn.env('call_transcript', '')
    nn.env('call_record', '')


def after_call_fail():
    nn.env('status', '-ERR')
    nn.env('result', None)
    nn.log('unit', 'after_call_fail')
    tz = nn.get_time_zone(nn.dialog['msisdn'])
    try:
        nn.env('region', str(tz['location']))
    except KeyError:
        nn.log('Неправильно указан номер')

    attempt = nn.env('attempt')
    nn.log('attempt', attempt)
    recall_count = nn.get_recall_count()
    if not recall_count:
        recall_count = 0
    nn.log('recall_count', recall_count)
    recall_delay = nn.get_recall_delay()
    if not recall_delay:
        recall_delay = 0
    nn.log('recall_delay', recall_delay)
    if attempt >= recall_count:
        nn.log('Использованы все попытки перезвонов')
        nn.dump()
        nulify_global_variables()
        nn.dialog.result = nn.RESULT_DONE
        return
    nn.log('attempt', attempt)

    # nn.log('Создаем новый звонок после -ERR в after_call')
    nn.call('+7' + nn.dialog['msisdn'], 'recall_delay', entry_point='main_online_container',
            on_success_call='after_call_success',
            on_failed_call='after_call_fail',
            proto_additional={
                'caller_id': '74951285170',
                'Remote-Party-ID': '<tel:74951285170>;party=calling;screen=yes;privacy=off',
            }, )

    nn.dump()
    nulify_global_variables()
    return


def after_call_success():
    nn.env('status', '+OK')
    nn.log('unit', 'after_call_success')

    nn.env('uuid', nn.env('call_uuid'))
    tz = nn.get_time_zone(nn.dialog['msisdn'])
    try:
        nn.env('region', str(tz['location']))
    except KeyError:
        nn.log('Неправильно указан номер')
    attempt = nn.env('attempt')
    if not attempt:
        attempt = 5
    nn.log('attempt', attempt)
    recall_count = nn.get_recall_count()
    if not recall_count:
        recall_count = 0
    nn.log('recall_count', recall_count)
    recall_delay = nn.get_recall_delay()
    if not recall_delay:
        recall_delay = "01:00"
    nn.log('recall_delay', recall_delay)
    if attempt >= recall_count:
        nn.log('Ипользованы все попытки перезвонов')
        nn.dump()
        nulify_global_variables()
        nn.dialog.result = nn.RESULT_DONE
        return
    nn.log('attempt', attempt)
    if nn.env('recall_is_needed') == 'true':
        nn.log('Создаем звонок из after_call_success')
        nn.call('+7' + nn.dialog['msisdn'], recall_delay, entry_point='main_online_container',
                on_success_call='after_call_success',
                on_failed_call='after_call_fail',
                proto_additional={
                    'caller_id': '74951285170',
                    'Remote-Party-ID': '<tel:74951285170>;party=calling;screen=yes;privacy=off',
                }, )
        nn.dump()
        nulify_global_variables()
        return

    if nn.env('recall_is_needed') == 'true_72':
        nn.log('Создаем звонок из after_call_success')
        nn.call('+7' + nn.dialog['msisdn'],
                datetime.utcnow() + timedelta(days=3),
                entry_point='main_online_container',
                on_success_call='after_call_success',
                on_failed_call='after_call_fail',
                proto_additional={
                    'caller_id': '74951285170',
                    'Remote-Party-ID': '<tel:74951285170>;party=calling;screen=yes;privacy=off',
                }, )
        nn.dump()
        nulify_global_variables()
        return

    nn.dump()
    nulify_global_variables()
    nn.dialog.result = nn.RESULT_DONE
    return
