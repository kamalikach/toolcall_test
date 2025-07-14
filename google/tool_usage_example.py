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

chat_provider = ChatMessageProvider('chats.txt')
email_provider = EmailMessageProvider('emails.txt')

TOOLS = {
    EMAIL_FUNCTION_DECLARATION["name"]: {
        "declaration": EMAIL_FUNCTION_DECLARATION,
        "provider": email_provider,
        "method": "get_email_message",  # method to call on provider
    },
    CHAT_FUNCTION_DECLARATION["name"]: {
        "declaration": CHAT_FUNCTION_DECLARATION,
        "provider": chat_provider,
        "method": "get_chat_message",
    },
    # Add more tools here
}

function_declarations = [tool["declaration"] for tool in TOOLS.values()]


def process_next_message():
        contents = [
            types.Content(role="user", parts=[types.Part(text=USER_PROMPT)])
        ]

        tools = types.Tool(function_declarations=function_declarations)
        config = types.GenerateContentConfig(tools=[tools])

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=config,
        )

        candidate = response.candidates[0]
        content_parts = candidate.content.parts

        function_call_part = next((part for part in content_parts if part.function_call), None)

        if function_call_part:
            function_call = function_call_part.function_call
            print(f"Function to call: {function_call.name}")
            print(f"Arguments: {function_call.args}")

            tool = TOOLS.get(function_call.name)
            if not tool:
                print(f"Unknown tool requested: {function_call.name}")
                return

            provider = tool["provider"]
            method_name = tool["method"]
            method = getattr(provider, method_name, None)
            if not method:
                print(f"Provider does not implement method: {method_name}")
                return

            result = method()
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

            print('Final Response:', final_response.text)

        else:
            print("No function call found in the response.")
            print("Response text:", response.text)
            print("All parts in response:")
            for idx, part in enumerate(content_parts):
                print(f" Part {idx}: {part}")



if __name__ == '__main__':


    # Call process_next_message multiple times in a loop for clarity
    for _ in range(4):
        process_next_message()

