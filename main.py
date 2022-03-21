r = requests.post('https://api-v3.neuro.net/api/v2/ext/auth', auth=("mylaw.api@gmail.com", "9XuXXHbP"))
response_json = r.json()

url = 'https://cms-v3.neuro.net/api/v2/log/dialog'
header = {'Authorization': "Bearer " + response_json['refresh_token'],
          'Content-Type': 'application/json'}
param_tuples = {'limit': 100,
                'offset': 0,
                'where': {
                    'agent_uuid': "03ec4ccc-a775-4395-9abe-49cefbfac9fc",
                    'call_uuid': [nn.env("call_uuid")],
                    'dialog_uuid': [nn.env("dialog_uuid")],
                    'end_date': "30-01-2022 13:14:58",
                    'msisdn': [nn.dialog['msisdn']],
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

nn.log("Start request: ", str(datetime.datetime.now()))
nn.log("total_count: ", rr.json()['total_count'])
nn.log("Finish request: ", str(datetime.datetime.now()))


timing = time.time()
my_time = 60 * 60 * 24
while True:
    if time.time() - timing > my_time:
        timing = time.time()
        r = requests.post('https://cms-v3.neuro.net/api/v2/ext/auth/refresh', json={'refresh_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NDQ2ODc3MTYsImV4cCI6MTY0NDc3NDExNiwidXVpZCI6ImZiOGFiNGRlLTQ1NDQtNDJmYi1hZmZmLThhNGE1ODRlMThlZCJ9.cibHECxGXG66LDaaoxtT7QfLpCZhkvRmAW7pouPSpJU'})