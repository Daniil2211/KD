import csv
import re
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

my_duration = []
my_result = []
my_call_uuid = []
my_call_record = []
my_msisdn = []

with open('ITConcept16_from_01-04-2022 07_23_00_to_30-04-2022 08_23_59.csv', 'r', encoding='UTF-8') as f:
    data = csv.DictReader(f, delimiter=';')
    # msisdn, status, result, call_start, duration, attempt, call_uuid, call_transcript, call_record, call_start_time, city (c32e5fb9-2229-486d-bb38-c5f46340a037)
    duration_dict = {}
    for i in range(200):
        duration_dict[i] = 0
    res_limit = 29
    bot_limit = 20 + 10
    for row in data:
        if row['call_uuid'] == 'a8777275-c359-481c-adcc-15157c0a0b24':
            print(row)
        if row['duration'] != '':
            a = int(row['duration'])
            if int(a) < 200:
                duration_dict[a] = duration_dict[a] + 1
                if row['result'] == 'сброс на приветствии' and a > res_limit:
                    str_1 = row['call_transcript']
                    if re.search(r'human', str_1) is None or row['call_transcript'] == '':
                        # print('duration: ', row['duration'], 'result: ', row['result'], 'call_transcript: ',
                        #       row['call_transcript'],
                        #       'call_record: ', row['call_record'])
                        my_duration.append(row['duration'])
                        my_result.append(row['result'])
                        my_call_uuid.append(row['call_uuid'])
                        my_call_record.append(row['call_record'])
                        my_msisdn.append(row['msisdn'])
                if row['result'] == 'автоответчик' and a > bot_limit:
                    str_1 = row['call_transcript']
                    result_list_of_conv = re.split(r';', str_1)
                    if len(result_list_of_conv[1]) < 35 and re.search(r'номер заблокирован', str_1) is None:
                        # print('duration: ', row['duration'], 'result: ', row['result'], 'call_transcript: ',
                        #       row['call_transcript'], 'call_record: ',
                        #       row['call_record'])
                        my_duration.append(row['duration'])
                        my_result.append(row['result'])
                        my_call_uuid.append(row['call_uuid'])
                        my_call_record.append(row['call_record'])
                        my_msisdn.append(row['msisdn'])
            if row['result'] == 'NULL - молчание от клиента' and re.search(r'human', row['call_transcript']) is None:
                if int(a) > 50:
                    # print('duration: ', row['duration'], 'result: ', row['result'], 'call_transcript: ',
                    #       row['call_transcript'], 'call_record: ', row['call_record'])
                    my_duration.append(row['duration'])
                    my_result.append(row['result'])
                    my_call_uuid.append(row['call_uuid'])
                    my_call_record.append(row['call_record'])
                    my_msisdn.append(row['msisdn'])
            # if int(a) >= 200:
            #     print('duration: ', row['duration'], 'result: ', row['result'], 'call_transcript: ',
            #           row['call_transcript'], 'call_record: ', row['call_record'])

print('my_msisdn: ', len(my_msisdn), my_msisdn)
print('my_duration', len(my_duration), my_duration)

df = pd.DataFrame({'msisdn': my_msisdn,
                   'duration': my_duration,
                   'result': my_result,
                   'call_uuid': my_call_uuid,
                   'call_record': my_call_record})
df.to_excel('./ShopRealPrice_1_0.xlsx')
