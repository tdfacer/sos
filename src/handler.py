import boto3
from boto3.dynamodb.conditions import Key, Attr
import json

def create_bucket_item(event, context):
    print(f"event: {event}")
    print(f"event.body: {event['body']}")
    ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
    table = ddb.Table('BucketItems')
    body = json.loads(event['body'])
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

def insert_data(recList):
    table = dynamodb.Table('BucketItems')
    for i in range(len(recList)):
        record = recList[i]
        table.put_item(
            Item={
                'username': record['username'],
                'lastname': record['lastname']
            }
        )


def get_one_bucket_item(event, context):
    ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
    table = ddb.Table('BucketItems')

    found_item = {}
    response = {}
    try:
        id = event['pathParameters']['id']
        print(f'id: {id}')
        response = table.query(
            KeyConditionExpression=Key('Id').eq(id)
        )
        print(f'response: {response}')
        found_item = response['Items'][0]
        print(f'item one: {found_item}')
        response = {
            "statusCode": 200,
            "body": found_item
        }
    except Exception as e:
        print(f'error when parsing path parameter: {e}')
        response = {
            "statusCode": 404
        }

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": found_item
    }

    return response

def get_bucket_items(event, context):
    items = []

    dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

    table = dynamodb.Table('BucketItems')

    response = table.scan()
    data = response['Items']
    print(f"data: {data}\n\n")
    items.extend(data)

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        print(f"res: {response}\n\n")
        items.extend(data)
        data.extend(response['Items'])

    body = {
        "input": json.dumps(items)
    }

    response = {
        "body": items,
        "statusCode": 200
    }

    return response