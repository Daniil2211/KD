import requests
from datetime import datetime
import time
import json

#def send_message():
#    url = f'https://api.telegram.org/bot{bot_token}/SendMessage?chat_id={chat_id}&parse_mode=Markdown&text="Hello"'
#    resp = requests.get(url)

tg_api_token = '5184647613:AAEPob6ZN6Pvm6PlOEbIpdYnjnY21635Mqk'
tg_chat_id = '922463874'

def send_tg_message(text='Cell execution completed.'):
    requests.post(
        'https://api.telegram.org/' +
        'bot{}/sendMessage'.format(tg_api_token),
        params=dict(chat_id=tg_chat_id, text=text)
    )

url = 'https://cms-v3.neuro.net/api/v2/log/dialog'
r = requests.post('https://api-v3.neuro.net/api/v2/ext/auth', auth=("mylaw.api@gmail.com", "9XuXXHbP"))
data_auth = r.json()
refresh_token = data_auth["refresh_token"]

nn.log("")
header = {'Authorization': "Bearer " + refresh_token,
          'Content-Type': 'application/json'}
param_tuples = {'limit': 100,
                'offset': 0,
                'where': {
                    'agent_uuid': "03ec4ccc-a775-4395-9abe-49cefbfac9fc",
                    'call_uuid': [],
                    'dialog_uuid': [],
                    'end_date': "30-01-2022 13:14:58",
                    'msisdn': ['9313689670'],
                    'start_date': "23-01-2022 13:14:58"}}
rr = requests.post(url, headers=header, json=param_tuples)
rr.json()

nn.log("URL: ", rr.url)
nn.log("ENCODING: ", rr.encoding)
nn.log("STATUS_CODE: ", rr.status_code)
nn.log("HEADERS: ", rr.headers)
nn.log("TEXT: ", rr.text)
nn.log("CONTENT: ", rr.content)
nn.log("JSON: ", rr.json)


