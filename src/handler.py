import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import os
import time

current_time = lambda: int(time.time())

def get_hash():
    hash_string = str(hash(str(current_time() * 100000)))
    return hash_string[4:14]

def get_table():
    is_local = os.environ['LOCAL_ENV']
    ddb = {}
    if is_local == "TRUE":
        print("local environment")
        ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
    else:
        print("live environment")
        ddb = boto3.resource('dynamodb')
    table_name = os.environ['TABLE_NAME']
    print(f"using table: {table_name}")
    table = ddb.Table(table_name)
    return table

def get_uuid():
    current_milli_time = lambda: int(round(time.time() * 1000))


def create_bucket_item(event, context):
    print(f"event: {event}")
    print(f"event.body: {event['body']}")

    table = get_table()
    body = json.loads(event['body'])
    print(f"body: {body}")
    name = body['name']
    url = body['url']
    if not body or not url:
        print(f"body didn't contain necessary fields: name, url")
    item = {
        'name': name,
        'url': url,
        'Id': get_hash()
    }
    try:
        urls = body['urls']
        item['urls'] = urls
        print(f"item: {item}")
        res = table.put_item(Item=item)
        print(f"res: {res}")
        code = res["ResponseMetadata"]['HTTPStatusCode']
    except Exception as e:
        print(f'failed to put urls')
        code = 504
        # 'created_at': current_time()

    response = {
        "statusCode": code,
        "body": item
    }

    return response

def get_one_bucket_item(event, context):
    table = get_table()

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

    table = get_table()

    response = table.scan()
    data = response['Items']
    print(f"data: {data}\n\n")
    items.extend(data)

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        print(f"res: {response}\n\n")
        items.extend(data)
        data.extend(response['Items'])

    # body = {
    #     "input": json.dumps(items)
    # }

    # print(f"body: {body}")

        # "body": json.dumps(items),
        # "body": items,
    response = {
        "body": json.dumps(items),
        "statusCode": 200
    }

    return response

def delete_item(event, context):
    """
    This function delete data from dynamodb table
    Returns
    -------
    
        Response Dictionary
    """
    table = get_table()
    response = {}
    code = 0
    try:
        item_id = event['pathParameters']['id']
        print(f"trying to delete Id: {item_id}")
        # response = table.delete_item(
        #     Item = {
        #            'Id': item_id
        #            }
        #     )
        response = table.delete_item(
            Key={"Id": item_id}
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print('success')
            code = 200
        else:
            print('fail')
            code = 404
    except Exception as e:
        print(f"Failed to get pathparameter id with error: {e}")
        response = {
            "statusCode": 500
        }
    #with delete_item function we delete the data from table
    return {
        "statusCode": code
    }

def delete_all(event, context):
    table = get_table()
    items = []
    response = table.scan()
    data = response['Items']
    print(f"data: {data}\n\n")
    items.extend(data)

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        print(f"res: {response}\n\n")
        items.extend(data)
        data.extend(response['Items'])

    for item in items:
        response = table.delete_item(
            Key={"Id": item['Id']}
        )
        print(f"delete item: {response}")

    return {
        "body": items,
        "statusCode": 200
    }