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

@app.route('/questionset/batch', methods=['POST'])
def create_questionset_with_questions():
    data = request.json

    # Extract questionset details
    questionset_id = data['questionsetid']
    name = data['name']
    description = data['description']
    questions = data['questions']

    # Insert into questionsets table
    questionset_item = {
        'questionsetId': questionset_id,
        'name': name,
        'description': description,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    table.put_item(Item=questionset_item)

    # Insert into questions table
    for idx, question in enumerate(questions, start=1):
        question_id = f"question-{idx}"
        question_item = {
            'questionsetId': questionset_id,
            'questionId': question_id,
            'text': question['text'],
            'choices': question['choices'],
            'tags': question.get('tags', []),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        table_questions.put_item(Item=question_item)

    return jsonify({"message": "Questionset and questions inserted successfully."}), 201

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

""" 
We need to write an endpoint that inserts 
- 1 record in the questionsets table (patritionkey :questionsetId)
- & multiple records in the questions table  (patritionkey :questionsetId , sort key :questionId)
    - generate counter questionId
The client will send below request :  

POST /mcquery/v1/questionset/batch HTTP/1.1
Content-Type: application/json
Kong-Apikey: nXh1Le1zKx5eZ6UnViAUQuPyLFXWVizO
Host: kong-5e30d406e3usadj2j.kongcloud.dev
Content-Length: 741

{
  "questionsetid": "dynamodb-basics-2503151722",
  "name": "DynamoDB Advanced Use Cases Quiz 3",
  "description": "A set of questions to test knowledge on advanced features and use cases of Amazon DynamoDB.",
  "questions": [
    {
      "text": "How do DynamoDB transactions ensure atomicity and consistency?",
      "choices": [
        {
          "text": "By allowing multiple operations to be executed atomically with ACID guarantees.",
          "targetedResponse": "Correct! DynamoDB transactions ensure all-or-nothing execution of multiple operations, maintaining atomicity and consistency.",
          "isCorrect": true
        }
      ],
      "tags": [
        "acid",
        "dynamodb",
        "atomicity"
      ]
    }
  ]
}
"""