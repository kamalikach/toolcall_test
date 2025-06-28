import os
import argparse
from google import genai
from google.genai import types
from tools import *

client = genai.Client(api_key=os.getenv("GCP_API_KEY"))
model = 'gemini-2.5-flash'

#####function declarations for the tools

email_function_declaration = {
        "name": "get_email",
        "description": "Function to return the next email in inbox",
}
chat_function_declaration = {
        "name": "get_chat",
        "description": "Function to get my next chat message"
}


user_prompt_text = "Get my next email message and summarize it."

def method1(tools_list):

    chat_provider = tools_list[0]
    email_provider = tools_list[1]
    
    contents = [
        types.Content(
            role="user", parts=[types.Part(text=user_prompt_text)]
        )
    ]

    tools = types.Tool(function_declarations=[email_function_declaration, chat_function_declaration])
    config = types.GenerateContentConfig(tools=[tools])
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )

    if response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call
        print(f"Function to call: {function_call.name}")
        print(f"Arguments: {function_call.args}")

        if function_call.name == "get_email":
            result = email_provider.get_email_message()
            print(f"Function execution result: {result}")
        elif function_call.name == "get_chat":
            result = chat_provider.get_chat_message()
            print(f"Function execution result: {result}")

        function_response_part = types.Part.from_function_response(
            name=function_call.name,
            response={"result": result},
            )

        contents.append(response.candidates[0].content) # Append the content from the model's response.
        contents.append(types.Content(role="user", parts=[function_response_part])) # Append the function response

        final_response = client.models.generate_content(
            model=model,
            config=config,
            contents=contents,
        )

        print('Final Response:', final_response.text)

    else:
        print("No function call found in the response.")
        print(response.text)




if __name__ == '__main__':
        chat_provider = ChatMessageProvider('chats.txt')
        email_provider = EmailMessageProvider('emails.txt')
    
        method1([chat_provider, email_provider])
        method1([chat_provider, email_provider])
        method1([chat_provider, email_provider])
        method1([chat_provider, email_provider])
    
