import pyaudio
import wave
import boto3
from pprint import pprint

client = boto3.client('s3') # example client, could be any
my_region = client.meta.region_name

print(f"My region is {my_region}")



def put_record(folder, database, stream, message):
  client = boto3.client('kinesis', endpoint_url="https://yds.serverless.yandexcloud.net", region_name=my_region)
  response = client.put_record(
    StreamName=f"/ru-central1/{folder}/{database}/{stream}".format(folder=folder, database=database, stream=stream),
    Data=message,
    PartitionKey=message
  )
  return response

def create_stream(folder, database, stream, shard_count):
    client = boto3.client('kinesis', endpoint_url="https://yds.serverless.yandexcloud.net", region_name=my_region)
    response = client.create_stream(
      StreamName=f"/ru-central1/{folder}/{database}/{stream}".format(folder=folder, database=database, stream=stream),
      ShardCount=shard_count
    )
    return response

chunk = 1024
sample_format = pyaudio.paInt16
channels = 1
rate = 44100
seconds = 3
filename = "output_sound.wav"
p = pyaudio.PyAudio()

print('Recording...')

stream = p.open(format=sample_format, channels=channels, rate=rate,
				frames_per_buffer=chunk, input_device_index=1, input=True)

frames = []

client = boto3.client('kinesis', endpoint_url="https://yds.serverless.yandexcloud.net", region_name=my_region)

folder_kd = "b1gni921dik64gto5tgq"
database_kd = "etnsn57fl32nbb2f2qr7"
stream_kd = "oleg-kd"
# message = data

for i in range(0, int(rate / chunk * seconds)):
	data = stream.read(chunk)
	frames.append(data)

# 	put_record_response = put_record(
# 		folder=f"{folder_kd}",
# 		database=f"{database_kd}",
# 		stream=f"{stream_kd}",
# 		message=f"{data}")
#
# print("The record has been sent successfully")
# pprint(put_record_response)

create_stream_response = create_stream(
	folder=f"{folder_kd}",
	database=f"{database_kd}",
	stream=f"{stream_kd}",
    shard_count=2)
print("The stream has been created successfully")
pprint(create_stream_response)

stream.stop_stream()
stream.close()
p.terminate()

print('Finished recording!')

wf = wave.open(filename, 'wb')
wf.setnchannels(channels)
wf.setsampwidth(p.get_sample_size(sample_format))
wf.setframerate(rate)
wf.writeframes(b''.join(frames))
wf.close()

# import pyaudio
# p = pyaudio.PyAudio()
# for i in range(p.get_device_count()):
# 	print(i, p.get_device_info_by_index(i)['name'])

# 0 Microsoft Sound Mapper - Input
# 1 Набор микрофонов (Realtek(R) Au
# 2 Microsoft Sound Mapper - Output
# 3 Динамики (Realtek(R) Audio)
# 4 Первичный драйвер записи звука
# 5 Набор микрофонов (Realtek(R) Audio)
# 6 Первичный звуковой драйвер
# 7 Динамики (Realtek(R) Audio)
# 8 ASIO4ALL v2
# 9 Динамики (Realtek(R) Audio)
# 10 Набор микрофонов (Realtek(R) Audio)
# 11 Стерео микшер (Realtek HD Audio Stereo input)
# 12 Speakers 1 (Realtek HD Audio output with HAP)
# 13 Speakers 2 (Realtek HD Audio output with HAP)
# 14 Динамик ПК (Realtek HD Audio output with HAP)
# 15 Mic in at front panel (black) (Mic in at front panel (black))
# 16 Headphones (Realtek HD Audio 2nd output)
# 17 Набор микрофонов (Realtek HD Audio Mic input)

