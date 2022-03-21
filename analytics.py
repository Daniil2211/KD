import requests

refresh_token = ''
try:
    str_encode = b'\xff\xfe9\x00X\x00u\x00X\x00X\x00H\x00b\x00P\x00'

    r = requests.post('https://api-v3.neuro.net/api/v2/ext/auth', auth=("mylaw.api@gmail.com", str_encode.decode('UTF-16')))
    refresh_token = r.json()['refresh_token']
except requests.ConnectionError:
    # nn.log('Error!')
    exit()

company_uuids = ['96857848-a88f-4cb0-bad8-6f70f3ec6211', '1c07c539-916c-4519-b26a-2c7a67a6f24e', 'e3cd14a1-a289-4d2f-86ab-182dc5e889ce',
                 'd2069c81-b66a-4e8d-88b9-46e60ee01a34', '70196014-fa26-48fe-b586-84a752eee58f']

all_agents = {}
for company_uuid in company_uuids:
    try:
        url = f'https://api-v3.neuro.net/api/v2/ext/company-agents?company_uuid={company_uuid}'
        header = {'Authorization': "Bearer " + refresh_token,
                  'Content-Type': 'application/json'}

        r = requests.get(url, headers=header)

        all_agents[company_uuid] = r.json()
    except requests.ConnectionError:
        # nn.log('Error!')
        exit()

time_start = "2022-02-21 14:25:00"
time_end = "2022-02-21 14:35:00"

agents_statistic = {}
for company_uuid in company_uuids:
    for agent in all_agents[company_uuid]:
        try:
            '''time_start = (datetime.datetime.now(timezone(time_zone)) - datetime.timedelta(minutes=5, hours=(
                        3 + hour_offset))).strftime("%Y-%m-%d %H:%M:%S")
            time_end = (datetime.datetime.now(timezone(time_zone)) - datetime.timedelta(
                hours=(3 + hour_offset))).strftime("%Y-%m-%d %H:%M:%S")'''
            r = requests.post('https://api-v3.neuro.net/api/v2/ext/statistic/dialog-report',
                              json={"agent_uuid": agent['agent_uuid'],
                                    "start": time_start,
                                    "end": time_end},
                              headers={
                                  'Authorization': "Bearer " + refresh_token})

            agents_statistic[agent['name']] = r.json()

        except requests.ConnectionError:
            # nn.log('Error!')
            exit()
print(agents_statistic)