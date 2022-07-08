import csv

import numpy as np
from matplotlib import pyplot as plt

with open('from_01-03-2022 15_11_00_to_31-03-2022 16_11_59.csv', 'r', encoding='UTF-8') as f:
    data = csv.DictReader(f, delimiter=';')
    # msisdn, status, result, call_start, duration, attempt, call_uuid, call_transcript, call_record, call_start_time, city
    duration_dict = {}
    for i in range(200):
        duration_dict[i] = 0
    values = duration_dict.values()
    k = duration_dict.keys()
    print(k)
    print(values)
    for row in data:
        if row['duration'] != '':
            a = int(row['duration'])
            if int(a) > 200:
                print('Over 200!!!')
            else:
                duration_dict[a] = duration_dict[a] + 1

        # print(', '.join(row))
        # print(row['call_start'], row['duration'])
    # for row in data:
    #     print(row)

    for key_t, value_t in duration_dict.items():
        if value_t != 0:
            print('\t', key_t, '->', value_t)


plt.title('ITConcept16', fontsize=12)
plt.bar(np.arange(200), duration_dict.values())
plt.xticks(np.arange(200), duration_dict.keys(), rotation=90, fontsize=5)
plt.ylabel('Количество звонков', fontsize=12)
plt.xlabel('Длительность звонка', fontsize=12)
plt.show()