import csv
import json
import re
from sphinx.util import requests

show_regex = False
write_to_file = True

url = 'https://cms-v3.neuro.net/api/v2/nlu/string/check'
header = {'Authorization': "Bearer " + response_json['refresh_token']}

if write_to_file:
    output_file = fc.selected.replace('.csv', '_output.csv')
    file = open(output_file, "w")

    # r'size=(?:50|51);'

reg_nd = r'human: [а-яё|\s|0-9]{0,}'
reg_d = r'human\(\d\d:\d\d:\d\d\): [а-яё|\s|0-9]{0,}'

reg_h_d = r'human\(\d\d:\d\d:\d\d\):'
reg_h_nd = r'human:'

with open(fc.selected, newline='') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=';')
    line_count = 0
    for row in csv_reader:
        line_count += 1
        if line_count > 0:
            for phrase in row:
                #                 print(phrase)
                try:
                    if 'human' in phrase:
                        if ')' in phrase:
                            reg = reg_d
                            reg_h = reg_h_d
                        else:
                            reg = reg_nd
                            reg_h = reg_h_nd
                        results = re.findall(reg, phrase)
                        results = re.findall(reg, phrase)
                        #                     print(results)

                        for result in results:
                            #                         print('result ===>')
                            #                         print(result)
                            #                         print('result <===')

                            human_phrase = re.sub(reg_h, '', result)

                            #                         print('human_phrase ==>')
                            #                         print(human_phrase)
                            #                         print('human_phrase <==')
                            param_tuples = {'agent_uuid': "f41c9b54-54e9-4c94-b625-a7443a33299b",
                                            'context': "",
                                            'language': "ru-RU",
                                            'use_synonyms': True,
                                            'utterance': human_phrase}
                            request = requests.post(url, json=param_tuples, headers=header)
                            request_json = json.loads(request.content)
                            phrase = request_json['utterance']
                            #                         print(request_json)
                            output = phrase + ';'
                            if 'entities' in request_json:
                                entities = request_json['entities']
                                for entity_key in entities.keys():
                                    value = entities.get(entity_key)['value']
                                    output = output + entity_key + ' = ' + value + ';'
                                    if show_regex:
                                        pattern = entities.get(entity_key)['pattern']
                                        output = output + ' regex = ' + pattern + ';'
                            else:
                                output = output + 'XXXXXXXXX'
                            if write_to_file:
                                file.writelines(output + '\n')
                            print(output)
                except:
                    pass

if write_to_file:
    file.close()
print('finish')