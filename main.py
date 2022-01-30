import requests
from datetime import datetime
import time

bot_token = 0
chat_id = 0


def send_message():
    url = f'https://api.telegram.org/bot{bot_token}/SendMessage?chat_id={chat_id}&parse_mode=Markdown&text="Hello"'
    resp = requests.get(url)


r = requests.post('https://api-v3.neuro.net/api/v2/ext/auth', auth=("mylaw.api@gmail.com", "9XuXXHbP"))
data_auth = r.json()
refresh_token = data_auth["refresh_token"]

start_time = str(datetime.now())

r = requests.post('https://api-v3.neuro.net/api/v2/ext/statistic/dialog-report',
                  json={"agent_uuid": "22392c1b-48e7-488d-82c9-d3c6d1a96c75", "start": start_time,
                        "end": str(datetime.now())}, headers={
                        'Authorization': "Bearer " + refresh_token})
data_dialogs = r.json()
initial_total = data_dialogs["total"]

while True:
    time.sleep(900)
    r = requests.post('https://api-v3.neuro.net/api/v2/ext/statistic/dialog-report',
                      json={"agent_uuid": "22392c1b-48e7-488d-82c9-d3c6d1a96c75", "start": start_time,
                            "end": str(datetime.now())}, headers={
                            'Authorization': "Bearer " + refresh_token})
    data_dialogs = r.json()
    current_total = data_dialogs["total"]
    if current_total == initial_total:
        send_message()
        break
    initial_total = current_total
#hello world