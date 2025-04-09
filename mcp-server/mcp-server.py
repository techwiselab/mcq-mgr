from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
import boto3
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key
from typing import Dict, Any, List
from pydantic import BaseModel
from typing import List, Optional

class Choice(BaseModel):
    """
    Represents a choice for a question.

    Attributes:
        text (str): The text of the choice.
        targeted_response (str): Feedback provided when this choice is selected.
        is_correct (bool): Indicates if the choice is correct.
    """
    text: str
    targeted_response: str
    is_correct: bool


class Question(BaseModel):
    """
    Represents a question in the questionset.

    Attributes:
        text (str): The text of the question.
        choices (List[Choice]): A list of choices for the question.
        tags (Optional[List[str]]): A list of tags for the question.
    """
    text: str
    choices: List[Choice]
    tags: Optional[List[str]] = None


class Questionset(BaseModel):
    """
    Represents a questionset with associated questions.

    Attributes:
        questionset_id (str): Unique identifier for the questionset.
        name (str): Name of the questionset.
        description (str): Description of the questionset.
        questions (List[Question]): A list of questions in the questionset.
    """
    questionset_id: str
    name: str
    description: str
    questions: List[Question]

# Load environment variables from the .env file
load_dotenv()

print('Initializing AWS DynamoDB session ...')

# Initialize AWS DynamoDB session
session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'ap-southeast-1')
)

print('Initializing DynamoDB resource ...')
# Initialize DynamoDB resource
dynamodb = session.resource('dynamodb')

# Initialize tables
table = dynamodb.Table('mcq-questionsets')
table_questions = dynamodb.Table('mcq-questions')

print('Starting server ...')
# Create an MCP server
mcp = FastMCP("Terminal Server")

@mcp.tool()
def create_questionset_with_questions(tool_input_body: Dict[str, Any]) -> Dict[str, Any]:
# def create_questionset_with_questions(tool_input: Questionset) -> Dict[str, Any]:
    """
    Create a questionset with associated questions in DynamoDB.

    Args:
        tool_input_body: An object containing a questionset with one or more questions.
            Example:
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
                            },
                            {
                                "text": "By using eventual consistency for all operations.",
                                "targetedResponse": "Incorrect. Eventual consistency does not guarantee atomicity.",
                                "isCorrect": false
                            }
                        ],
                        "tags": ["acid", "dynamodb", "atomicity"]
                    }
                ]
            }

    Returns:
        Dict[str, Any]: A dictionary containing a success message.
            Example:
            {
                "message": "Questionset and questions inserted successfully."
            }
    """

    tool_input= tool_input_body['tool_input_body']
    # Extract questionset details
    questionset_id = tool_input['questionsetid']
    name = tool_input['name']
    description = tool_input['description']
    questions = tool_input['questions']

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

    return {"message": "Questionset and questions inserted successfully."}

if __name__ == "__main__":
    mcp.run("stdio")