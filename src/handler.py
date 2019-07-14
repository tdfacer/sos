import boto3
import json

def create_bucket_item(event, context):
    print(f"event: {event}")
    print(f"event.body: {event['body']}")
    ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
    table = ddb.Table('BucketItems')
    body = json.loads(event['body'])
    # body = json.load(event['body'])
    print(f"body: {body}")
    name = body['name']
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

def get_bucket_items(event, context):
    # ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
    # ddb = boto3.client('dynamodb', endpoint_url='http://localhost:8000')
    # ddb = boto3.service('dynamodb', endpoint_url='http://localhost:8000')
    # response = ddb.list_tables()
    # print(response)
    # import boto3

    items = []

    dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

    table = dynamodb.Table('BucketItems')

    response = table.scan()
    print(f"response: {response}\n\n")
    data = response['Items']
    print(f"type of data: {type(data)}")
    print(f"type of data[0]: {type(data[0])}")
    print(f"data: {data}\n\n")
    # newlist = items + data
    # items.append(data)
    items.extend(data)
    # items.append(json.dumps(data))

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        print(f"res: {response}\n\n")
        # items.append(data)
        items.extend(data)
        data.extend(response['Items'])



    # client = boto3.client('dynamodb', endpoint_url='http://localhost:8000')
    # paginator = client.get_paginator('scan')
    # print(f"paginator: {paginator}")

    # num = 0
    # for page in paginator.paginate():
    #     print(f'page {num}: {page}')
    #     items.append(page)

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": json.dumps(items)
    }

        # body = json.dumps(body)
        # "body": json.dumps(body),
    response = {
        "body": body,
        "statusCode": 200
    }
    # response = {
    #     "statusCode": 200,
    #     "body": json.dumps(body)
    # }

    return response