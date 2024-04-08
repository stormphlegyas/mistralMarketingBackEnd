import os
import json
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from dotenv import load_dotenv

load_dotenv()

client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))

def plan(metadata: str) -> dict:
  """
  Takes a README and extracts the following properties
  
  Parameters:
      readme (str): The README content

  Returns:
      dict: A dictionary containing the extracted properties
  """
  
  system_prompt = """
## Context
This is a marketing application aimed to generate omnichannels campaign for open-source projects across various platforms and content types (Hackernews posts, Reddit posts, Twitter/X posts, Youtube video tutorials, Hackathons, ...)

## Goal 
Extract data from the README to the following format, the goal is to extract the relevant platforms to promote the project on.
Do this from the app profile sent by the user

## Format
JSON object following format:
{
  "platforms": "A list of strings designating the different possible platforms among the following list ['Hackernews', 'Blog', 'Reddit', 'Twitter', 'ProductHunt']",
}
""".strip()
  max_retries = 3
  retry_count = 0
  
  try:
    messages = [
      ChatMessage(role="system", content=system_prompt),
      ChatMessage(role="user", content=f"""
  # App profile
  {json.dumps(metadata, indent=2)}
  """)
    ]

    response = client.chat(
          model="mistral-medium-latest", 
          messages=messages, 
          response_format={
            "schema": {
              "platforms": "string[]" # A list of strings
            }
          },
      )

    response = response.choices[0].message.content
    response = response.replace("`", "")
    
    response = response.split('{')[1]
    response = response.split('}')[0]

    response = "{" + response + "}"

    response = json.loads(response)

    return response

  except Exception as e:
    retry_count += 1
    print(f"An error occurred: {e}. Retrying... (Attempt {retry_count}/{max_retries})")