import boto3

client = boto3.client('kinesis', endpoint_url="https://yds.serverless.yandexcloud.net", region_name="ru-central-1")

client.put_record(
    StreamName="/ru-central1/b1gni921dik64gto5tgq/etnsn57fl32nbb2f2qr7/oleg-kd",
    Data=...,
    PartitionKey=...
)