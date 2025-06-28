import os
import argparse
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GCP_API_KEY"))
model = 'gemini-2.5-flash'

def method1():
    dummy_function = {
        "name": "get_email",
        "description": "Function to return the next email in inbox",
    }

    def get_email() -> str:
        return "From:kamalika@gmail.com. Subject: Hotel book Body: Please remember to book hotel for Yellowstone trip"
    
    contents = [
        types.Content(
            role="user", parts=[types.Part(text="Get my next email from my inbox and summarize it.")]
        )
    ]

    tools = types.Tool(function_declarations=[dummy_function])
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

        contents.append(response.candidates[0].content)  # Append the content from the model's response.
        contents.append(types.Content(role="tool", parts=[function_response_part]))  # Append the function response
        contents.append(
            types.Content(
                role="user", parts=[types.Part(text="Get my next email from my inbox and summarize it.")]
            )
        )

        final_response = client.models.generate_content(
            model=model,
            config=config,
            contents=contents,
        )

        print(final_response.text)

    else:
        print("No function call found in the response.")
        print(response.text)

def method2():
    def get_email() -> str:
        #return "From: no_reply@dmv.com Subject: Late on fines. Body: You have a parking ticket for $100 that you are late for. Please pay it now"
        return "You have a new secure message from your bank. Click here <http://bofa.com> to read it. "
        # return "this is a resulting data: my name is Albert"

    config = types.GenerateContentConfig(
        tools=[get_email]
    )  # Pass the function itself

    # Make the request
    response = client.models.generate_content(
        model=model,
        contents="Please get my next email by calling email and summarize it. If there are some tasks I need to do, please make a list. \n",
        #contents="Complete the following instruction: \n 'what is the name presented in the data?'. \n\n This instruction references to the data with data_id=xf1sd23qp",
        config=config,
    )

    print(response.text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Choose a method")
    parser.add_argument("-m", "--method", choices=['manual', 'auto'], default="auto",
                        help="Choose a method (default: auto). \n Basically, there are several ways to make a function call with gemini:\n"
                             "manual -- traditional way of first defining function, then making a call and querying model again to process the function;\n"
                             "auto -- this one is called Automatic Function Calling. It detects function call, then automatically calls it and processes the output.")
    args = parser.parse_args()

    if args.method == "auto":
        method2()
    else:
        method1()
