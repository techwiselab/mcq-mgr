import boto3
from flask import Flask, jsonify, request, send_from_directory
from boto3.dynamodb.conditions import Key
import os
from datetime import datetime, timezone


session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'ap-southeast-1')
)

# Initialize DynamoDB resource
dynamodb = session.resource('dynamodb')

# Initialize tables
table = dynamodb.Table('mcq-questionsets')
table_questions = dynamodb.Table('mcq-questions')
table_attempts = dynamodb.Table('mcq-attempts')

app = Flask(__name__)

@app.route('/questionsets', methods=['GET'])
def get_questionsets():
    # Scan the table to get all records
    response = table.scan()
    data = response['Items']
    return jsonify(data)

@app.route('/questions/<questionset_id>', methods=['GET'])
def get_questions(questionset_id):
    # Query the table to get all items that match the questionsetId
    response = table_questions.query(
        KeyConditionExpression=Key('questionsetId').eq(questionset_id)
    )
    items = response['Items']
    return jsonify(items)

@app.route('/attempts', methods=['POST'])
def upsert_attempt():
    item_to_upsert = request.json
    item_to_upsert['timestamp'] = datetime.now(timezone.utc).isoformat()
    # Upsert the item into the table
    table_attempts.put_item(Item=item_to_upsert)
    return jsonify({"message": "Item upserted successfully."})

@app.route('/attempts/<questionset_id>', methods=['GET'])
def get_attempt_by_questionset_id(questionset_id):
    # Query the table to get all items that match the questionsetId
    response = table_attempts.query(
            KeyConditionExpression=Key('questionsetId').eq(questionset_id)
    )
    items = response['Items']
    return jsonify(items)

@app.route('/attempts', methods=['GET'])
def get_all_attempts():
        # Scan the table to get all records
        response = table_attempts.scan()
        data = response['Items']
        return jsonify(data)

@app.route('/static/<path:filename>', methods=['GET'])
def serve_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)