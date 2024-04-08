import os
import json
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from dotenv import load_dotenv

load_dotenv()

client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))

def extract(readme: str) -> dict:
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
Extract data from the README to the following format

{
  "description": "A very short description of the project less than 256 characters, concise and abstractive enough to use as search query for similar projects",
  "value_proposition": "The value proposition of the project, what makes it unique",
  "target_audience": "The target audience of the project (developers, data scientists, ...)",
  "project_type": "The type of the project (library, framework, tool, saas, ...)",
  "project_sector": "The sector of the project (web development, data science, ...)",
}
""".strip()
  
  messages = [
    ChatMessage(role="system", content=system_prompt),
    ChatMessage(role="user", content=readme)
  ]

  response = client.chat(
        model="mistral-medium-latest", 
        messages=messages, 
        response_format={
          "type": "json_object",
          "schema": {
            "description": "string",
            "value_proposition": "string",
            "target_audience": "string",
            "project_type": "string",
            "project_sector": "string",
          }
        },
    )

  response = response.choices[0].message.content

  response = response.split('{')[1]
  response = response.split('}')[0]

  response = "{" + response + "}"

  response = json.loads(response)
  return response