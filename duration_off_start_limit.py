import csv

import numpy as np
from matplotlib import pyplot as plt

with open('from_01-03-2022 09_35_00_to_31-03-2022 10_35_59.csv', 'r', encoding='UTF-8') as f:
    data = csv.DictReader(f, delimiter=';')
    # msisdn, status, result, call_start, duration, attempt, call_uuid, call_transcript, call_record, call_start_time, city
    duration_dict = {}
    for i in range(200):
        duration_dict[i] = 0
    duration_off_start = 0
    duration_off_start_sum = 0
    for row in data:
        if row['duration'] != '':
            a = int(row['duration'])
            if int(a) < 200:
                if row['result'] == 'сброс на приветствии' and a > 5:
                    duration_dict[a] = duration_dict[a] + 1
                    duration_off_start = duration_off_start + 1
                    duration_off_start_sum = duration_off_start_sum + a

    duration_off_start_res = duration_off_start_sum / duration_off_start
    duration_off_start_res = duration_off_start_res * 2
    res_limit = int(duration_off_start_res)
    print('res_limit:', res_limit)



        # print(', '.join(row))
        # print(row['call_start'], row['duration'])
    # for row in data:
    #     print(row)

    # for key_t, value_t in duration_dict.items():
    #     if value_t != 0:
    #         print('\t', key_t, '->', value_t)


