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

def get_response(message, code=200):
    if isinstance(message, str):
        return {
            'statusCode': code,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({ "message": message })
        }
    return {
        'statusCode': code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(message)
    }

def get_item_from_table(table, id):
    item_exists = table.query(
        KeyConditionExpression=Key('Id').eq(id)
    )
    items = item_exists['Items']
    if len(items) == 0:
        return (False, {})
    return (True, item_exists['Items'][0])

def create_bucket_item(event, context):
    print(f'event: {event}')
    table = get_table()
    body = json.loads(event['body'])
    code = 0
    item = {}
    try:
        name = body['name']
        urls = body['urls']
        activity = body['activity']
        description = body['description']
        complete = body['complete']
    except KeyError as e:
        print(f'KeyError: {e}')
        return get_response(str(e), 400)
    id = get_hash()
    item = {
        'name': name,
        'activity': activity,
        'urls': urls,
        'description': description,
        'complete': complete,
        'Id': id
    }
    try:
        res = table.put_item(Item=item)
        code = res["ResponseMetadata"]['HTTPStatusCode']
        new_item = get_item_from_table(table, id)
        if not new_item[0]:
            raise Exception("Something went wrong.  Failed to get new item after creating it.")
        return get_response(new_item[1], code)
    except Exception as e:
        return get_response(str(e), 504)

def get_one_bucket_item(event, context):
    table = get_table()
    try:
        id = event['pathParameters']['id']
        item = get_item_from_table(table, id)
        return get_response(item[1])
    except Exception as e:
        print(f'error when parsing path parameter: {e}')
        return get_response(f"Not found: {str(e)}", 404)

def get_bucket_items(event, context):
    items = []
    table = get_table()
    try:
        response = table.scan()
        data = response['Items']
        items.extend(data)

        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(data)
            data.extend(response['Items'])
    except Exception as e:
        items = { "error_message": f"{str(e)}"}
        return get_response(items, 500)
    return get_response(items)

def delete_item(event, context):
    table = get_table()
    response = {}
    code = 0
    try:
        item_id = event['pathParameters']['id']
        response = table.delete_item(
            Key={"Id": item_id}
        )
        response_code = response['ResponseMetadata']['HTTPStatusCode']
        if response_code != 200:
            return get_response("Failed to delete item.", response_code)
    except Exception as e:
        print(f"Failed to get pathparameter id with error: {e}")
        return get_response(f"Failed to delete item with error message: {e}.", 500)
    return get_response(f"{item_id} deleted")

def delete_all(event, context):
    try:
        table = get_table()
        items = []
        response = table.scan()
        data = response['Items']
        items.extend(data)

        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(data)
            data.extend(response['Items'])

        for item in items:
            response = table.delete_item(
                Key={"Id": item['Id']}
            )
        return get_response(items)
    except Exception as e:
        return get_response(f"Failed to delete all: {e}", 500)

def update_bucket_item(event, context):
    try:
        id = event['pathParameters']['id']
        complete = event['queryStringParameters']['complete']
        table = get_table()

        item_exists = get_item_from_table(table, id)
        if not item_exists[0]:
            raise Exception(f"Item with ID {id} not found")

        update_expr = 'SET complete = :i'
        response = table.update_item(
            Key={"Id": id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues={
                ':i': complete
            }
        )
        code = response['ResponseMetadata']['HTTPStatusCode']
        item = get_item_from_table(table, id)
        return get_response(item[0], code)
    except Exception as e:
        return get_response(f"{str(e)}", 500)

def update_urls(event, context):
    try:
        id = event['pathParameters']['id']
        body = json.loads(event['body'])
        url = body['url']

        table = get_table()
        item = get_item_from_table(table, id)
        if not item[0]:
            raise Exception(f"Item with ID {id} not found")
        result = table.update_item(
            Key={
                'Id': id
            },
            UpdateExpression="SET urls = list_append(urls, :i)",
            ExpressionAttributeValues={
                ':i': [url],
            },
            ReturnValues="UPDATED_NEW"
        )
        response_code = result['ResponseMetadata']['HTTPStatusCode']
        if response_code == 200 and 'Attributes' in result:
            return get_response(get_item_from_table(table, id)[1])
        else:
            return get_response("error", response_code)
    except Exception as e:
        return get_response(f"Error updating item: {str(e)}", 500)