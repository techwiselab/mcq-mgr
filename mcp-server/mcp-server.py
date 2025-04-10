from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
import boto3
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from typing import Annotated
from typing import List, Optional

class Choice(BaseModel):
    """
    Represents one of the choices for the answer in a multiple choice question.
    """
    text: Annotated[
        str,
        Field(
            description="The text of the choice.",
            examples=[
                "The backend service is overloaded. Scale the backend service to handle more requests.",
                "The API Gateway stage-level throttling limit is being exceeded. Update the stage-level throttling settings to allow more requests per second."
            ]
        )
    ]
    targeted_response: Annotated[
        str,
        Field(
            description="Feedback provided when this choice is selected. If this is a wrong choice, it should mentor the user to understand why the choice is wrong. Use well-formatted plain text with escaped special characters.",
            examples=[
                "Incorrect. While backend service scaling is important, throttling in API Gateway is unrelated to backend service capacity.",
                "Correct! Stage-level throttling limits are commonly configured to control request rates. Increasing the limit can resolve the issue."
            ]
        )
    ]
    is_correct: Annotated[
        bool,
        Field(
            description="Indicates if the choice is correct.",
            examples=[False, True]
        )
    ]


class Question(BaseModel):
    """
    Represents a question in the questionset.

    Attributes:
        text (str): The text of the question.
        choices (List[Choice]): A list of choices for the question.
        tags (Optional[List[str]]): A list of tags for the question.
    """
    text: Annotated[
        str,
        Field(
            description="The text of the question. Ideally should be a scenario-based question. Use well-formatted plain text with escaped special characters.",
            example="Your company is using AWS API Gateway to expose a REST API for a backend service. During a load test, you notice that some requests are being throttled. What is the most likely cause, and how can you resolve it?"
        )
    ]
    choices: Annotated[
        List[Choice],
        Field(
            description="List of choices for the question. Always shuffle the choices so that the correct answer is at a different index for each question."
        )
    ]
    tags: Annotated[
        Optional[List[str]],
        Field(
            description="List of tags for the question. All tags must be in lower case. These will be keywords from the text of the question or from the text of the right or wrong choice.",
            max_items=10,
            example=["api gateway", "throttling", "stage-level throttling", "backend service"]
        )
    ]

class Questionset(BaseModel):
    """
    A questionset with associated questions.
    """
    questionset_id: Annotated[
        str, 
        Field(
            max_length=50, 
            description="Unique identifier for the questionset. Must have -YYMMDDhhss as the suffix.",
            example="aws-api-gateway-2503151722"
        )
    ]
    name: Annotated[
        str, 
        Field(
            max_length=100, 
            description="Name of the questionset.",
            example="AWS API Gateway"
        )
    ]
    description: Annotated[
        str, 
        Field(
            max_length=1000, 
            description="Description of the questionset.",
            example="This set of scenario-based multiple-choice questions is designed to test and reinforce your understanding of AWS API Gateway functionality. It challenges you to apply concepts in real-world contexts, helping deepen your practical knowledge of API Gateway."
        )
    ]
    questions: Annotated[list[Question], Field(max_length=10, description="List of questions in the questionset.")] 

class ShrimpTank(BaseModel):
    class Shrimp(BaseModel):
        name: Annotated[str, Field(max_length=10)]

    shrimp: list[Shrimp]

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
def name_shrimp(
    tank: ShrimpTank,
    # You can use pydantic Field in function signatures for validation.
    extra_names: Annotated[list[str], Field(max_length=10)],
) -> list[str]:
    """List all shrimp names in the tank"""
    return [shrimp.name for shrimp in tank.shrimp] + extra_names
@mcp.tool()
def create_questionset_with_questions(tool_input: Questionset) -> Dict[str, str]:
    """
    Create a questionset with associated questions in the backend.
    """

    # Extract questionset details using dot notation
    questionset_id = tool_input.questionset_id
    name = tool_input.name
    description = tool_input.description
    questions = tool_input.questions

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
            'text': question.text,
            'choices': [choice.dict() for choice in question.choices],
            'tags': question.tags or [],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        table_questions.put_item(Item=question_item)

    return {"message": "Questionset and questions inserted successfully."}

if __name__ == "__main__":
    mcp.run("stdio")