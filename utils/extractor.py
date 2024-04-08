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
  
  Parameters
  ----------
  readme : str
      The README content
  
  Returns
  -------
  dict
      A dictionary containing the extracted properties
  
  Raises
  ------
  RuntimeError
      If extraction fails after maximum retries
      
  Examples
  --------
  >>> extract("Sample README content")
  {'description': 'Sample description',
    'value_proposition': 'Sample value proposition',
    'target_audience': 'Sample target audience',
    'project_type': 'Sample project type',
    'project_sector': 'Sample project sector'}
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
  max_retries = 3
  retry_count = 0
  
  while retry_count < max_retries:
    try:
      messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": readme}
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
      
    except Exception as e:
      retry_count += 1
      print(f"An error occurred: {e}. Retrying... (Attempt {retry_count}/{max_retries})")
  
  return {"error": "Exceeded maximum retries, unable to extract data from the README."}