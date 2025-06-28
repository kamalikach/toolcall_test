import os
import argparse
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GCP_API_KEY"))
model = 'gemini-2.5-flash'


email_function_declaration = {
        "name": "get_email",
        "description": "Function to return the next email in inbox",
    }

def get_email() -> str:
        return "From:kamalika@gmail.com. Subject: Hotel book Body: Please remember to book hotel for ICML trip"
    
user_prompt_text = "Get my next email from my inbox and summarize it."

def method1():
    contents = [
        types.Content(
            role="user", parts=[types.Part(text=user_prompt_text)]
        )
    ]

    tools = types.Tool(function_declarations=[email_function_declaration])
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
            result = get_email()
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
        method1()
