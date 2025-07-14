import os
from google import genai
from google.genai import types
from tools import *
from tool_definitions import * 

# Initialize client and model
client = genai.Client(api_key=os.getenv("GCP_API_KEY"))
MODEL_NAME = 'gemini-2.5-flash'

# User prompt asking for next email message summary
USER_PROMPT = "Get my next email message and summarize it."

def process_next_message(chat_provider, email_provider):
    """
    Requests the next message (email or chat) from the model and processes the function call.
    If no function call is found, prints the plain text response and all response parts for debugging.
    """
    contents = [
        types.Content(role="user", parts=[types.Part(text=USER_PROMPT)])
    ]

    tools = types.Tool(function_declarations=[EMAIL_FUNCTION_DECLARATION, CHAT_FUNCTION_DECLARATION])
    config = types.GenerateContentConfig(tools=[tools])

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=config,
    )

    candidate = response.candidates[0]
    content_parts = candidate.content.parts

    # Check if any part has a function call
    function_call_part = None
    for part in content_parts:
        if part.function_call:
            function_call_part = part
            break

    if function_call_part:
        function_call = function_call_part.function_call
        print(f"Function to call: {function_call.name}")
        print(f"Arguments: {function_call.args}")

        if function_call.name == "get_email":
            result = email_provider.get_email_message()
        elif function_call.name == "get_chat":
            result = chat_provider.get_chat_message()
        else:
            print(f"Unknown function call: {function_call.name}")
            return

        print(f"Function execution result: {result}")

        function_response_part = types.Part.from_function_response(
            name=function_call.name,
            response={"result": result},
        )

        contents.append(candidate.content)
        contents.append(types.Content(role="user", parts=[function_response_part]))

        final_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=config,
        )

        print("Final Response Text:", final_response.text)

    else:
        print("No function call found in the response.")
        print("Response text:", response.text)
        print("All parts in response:")
        for idx, part in enumerate(content_parts):
            print(f" Part {idx}: {part}")


if __name__ == '__main__':
    chat_provider = ChatMessageProvider('chats.txt')
    email_provider = EmailMessageProvider('emails.txt')

    # Call process_next_message multiple times in a loop for clarity
    for _ in range(4):
        process_next_message(chat_provider, email_provider)

