#  pip install google-genai
import os
import requests

from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GCP_API_KEY"))

# Retrieve an image
image_path = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Palace_of_Westminster_from_the_dome_on_Methodist_Central_Hall.jpg/2560px-Palace_of_Westminster_from_the_dome_on_Methodist_Central_Hall.jpg"
image_bytes = requests.get(image_path).content
image = types.Part.from_bytes(
  data=image_bytes, mime_type="image/jpeg"
)

# Create a prompt
prompt = "Caption this image."
response = client.models.generate_content(
    model="gemini-2.5-flash-preview-05-20",
    contents=[
        image_path,
        prompt,
    ]
)

print(">" + response.text)