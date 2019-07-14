import boto3
import json


# # For a Boto3 client.
# table = ddb.Table('BucketItems')

# res = table.put_item(
#    Item={
#         'name': 'First Item',
#         'url': 'www.example.com',
#         'Id': 'test'
#     }
# )


def create_bucket_item(event, context):
    print(f"event: {event}")
    print(f"event.body: {event['body']}")
    # ddb = boto3.client('dynamodb', endpoint_url='http://localhost:8000')
    ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
    table = ddb.Table('BucketItems')
    # body = event['body']
    #body = event['body']
    # body = json.parevent['body']
    print('before body')
    body = json.loads(event['body'])
    print('after body')
    # print(type(body))
    # body = json.loads(event['body'])
    print(f"body: {body}")
    name = body['name']
    print('after name')
    url = body['url']
    my_id = body['id']
    if not body or not url or  not id:
        print(f"body didn't contain necessary fields: name, url, id")
    item = {
        'name': name,
        'url': url,
        'Id': my_id
    }
    print(f"item: {item}")
    res = table.put_item(Item=item)
    print(f"res: {res}")
    res_body = {
        "message": "Put item",
    }
    code = res["ResponseMetadata"]['HTTPStatusCode']

    response = {
        "statusCode": code,
        "body": json.dumps(res_body)
    }

    return response
    # response = client.put_item(
    #     TableName='BucketItems',
    #     Item={
    #         'string': {
    #             'S': 'string',
    #             'N': 'string',
    #             'B': b'bytes',
    #             'SS': [
    #                 'string',
    #             ],




def get_one_bucket_item(event, context):
    ddb = boto3.client('dynamodb', endpoint_url='http://localhost:8000')
    response = ddb.list_tables()
    print(response)

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
