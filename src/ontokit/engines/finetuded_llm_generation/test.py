student_1_description = "David Nguyen is a sophomore majoring in computer science at Stanford University. He is Asian American and has a 3.8 GPA. David is known for his programming skills and is an active member of the university's Robotics Club. He hopes to pursue a career in artificial intelligence after graduating."
student_2_description = "Ravi Patel is a sophomore majoring in computer science at the University of Michigan. He is South Asian Indian American and has a 3.7 GPA. Ravi is an active member of the university's Chess Club and the South Asian Student Association. He hopes to pursue a career in software engineering after graduating."
import json
import openai
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored

GPT_MODEL = "gpt-3.5-turbo-0613"
openai.api_key = "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"


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
    }
    json_data = {"model": model, "messages": messages}
    if tools is not None:
        json_data.update({"tools": tools})
    if tool_choice is not None:
        json_data.update({"tool_choice": tool_choice})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e


def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "tool": "magenta",
    }

    for message in messages:
        if message["role"] == "system":
            print(
                colored(
                    f"system: {message['content']}\n", role_to_color[message["role"]]
                )
            )
        elif message["role"] == "user":
            print(
                colored(f"user: {message['content']}\n", role_to_color[message["role"]])
            )
        elif message["role"] == "assistant" and message.get("function_call"):
            print(
                colored(
                    f"assistant: {message['function_call']}\n",
                    role_to_color[message["role"]],
                )
            )
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(
                colored(
                    f"assistant: {message['content']}\n", role_to_color[message["role"]]
                )
            )
        elif message["role"] == "tool":
            print(
                colored(
                    f"function ({message['name']}): {message['content']}\n",
                    role_to_color[message["role"]],
                )
            )


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_multiple_student_profiles",
            "description": "Extract multiple student profile information",
            "parameters": {
                "type": "object",
                "properties": {
                    "students": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "personal_info": {
                                    "type": "object",
                                    "properties": {
                                        "first_name": {
                                            "type": "string",
                                            "description": "First name of the student.",
                                        },
                                        "last_name": {
                                            "type": "string",
                                            "description": "Last name of the student.",
                                        },
                                    },
                                    "required": ["first_name", "last_name"],
                                },
                                "academic_info": {
                                    "type": "object",
                                    "properties": {
                                        "major": {
                                            "type": "string",
                                            "description": "Major subject.",
                                        },
                                        "school": {
                                            "type": "string",
                                            "description": "The university name.",
                                        },
                                        "gpa": {
                                            "type": "integer",
                                            "description": "GPA of the student.",
                                        },
                                    },
                                    "required": ["major", "school", "gpa"],
                                },
                                "extracurriculars": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of extracurricular activities and clubs.",
                                },
                            },
                            "required": [
                                "personal_info",
                                "academic_info",
                                "extracurriculars",
                            ],
                        },
                    }
                },
                "required": ["students"],
            },
        },
    }
]


messages = []
messages.append(
    {
        "role": "system",
        "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.",
    }
)
messages.append(
    {
        "role": "user",
        "content": "Extract the data from following text: "
        + student_2_description
        + student_1_description,
    }
)
chat_response = chat_completion_request(messages, tools=tools)
assistant_message = chat_response.json()["choices"][0]["message"]

# Extrahierung der 'arguments'
arguments_json = assistant_message['tool_calls'][0]['function']['arguments']

# Konvertierung des 'arguments'-Strings in ein JSON-Objekt
arguments_data = json.loads(arguments_json)

# Ausgabe der extrahierten Daten
print(json.dumps(arguments_data, indent=2))
