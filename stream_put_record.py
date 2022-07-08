import os

import boto3
from pprint import pprint

client = boto3.client('s3') # example client, could be any
my_region = client.meta.region_name


def put_record(folder, database, stream, message):
  client = boto3.client('kinesis', endpoint_url="https://yds.serverless.yandexcloud.net", region_name=my_region)
  response = client.put_record(
    StreamName=f"/ru-central1/{folder}/{database}/{stream}".format(folder=folder, database=database, stream=stream),
    Data=message,
    PartitionKey=message
  )
  return response

def create_stream(folder, database, stream, shard_count, ACCESS_ID=None, ACCESS_KEY=None):
  client = boto3.client('kinesis', endpoint_url="https://yds.serverless.yandexcloud.net", region_name=my_region,
                        aws_access_key_id=ACCESS_ID, aws_secret_access_key= ACCESS_KEY)
  response = client.create_stream(
    StreamName=f"/ru-central1/{folder}/{database}/{stream}".format(folder=folder, database=database, stream=stream),
    ShardCount=shard_count
  )
  return response

if __name__ == '__main__':

  print(client.meta.method_to_api_mapping)

  folder_kd = "b1gni921dik64gto5tgq"
  database_kd = "etnsn57fl32nbb2f2qr7"
  stream_kd = "oleg-kd"
  message = "message"

  # create_stream_response = create_stream(
  #   folder=f"{folder_kd}",
  #   database=f"{database_kd}",
  #   stream=f"{stream_kd}",
  #   shard_count=2)
  # print("The stream has been created successfully")
  # pprint(create_stream_response)

  # put_record_response = put_record(
  #     folder=f"{folder_kd}",
  #     database=f"{database_kd}",
  #     stream=f"{stream_kd}",
  #     message=f"{data}")
  #
  # print("The record has been sent successfully")
  # pprint(put_record_response)