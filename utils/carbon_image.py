import os
import json

from carbon import Carbon
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from dotenv import load_dotenv

load_dotenv()

client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))

def create_codeblock_image(
  readme:str
):
  """
    Create an image containing a code block for demonstration purposes.

    This function takes a `readme` string as input, which represents the content
    to be displayed within the code block. It integrates this content into an
    image using Carbon.sh service, which generates an aesthetically pleasing
    representation of the code block.

    Parameters
    ----------
    readme : str
        The content to be displayed within the code block.

    Returns
    -------
    None
        This function does not return any value. It prints the generated image
        URL to the console.

    Notes
    -----
    This function uses the Carbon.sh service to generate the image containing
    the code block. The `readme` string should contain the code or text to be
    displayed within the code block.

    Raises
    ------
    (Any exceptions that may be raised during the execution of the function)

    Examples
    --------
    >>> create_codeblock_image("print('Hello, world!')")
    (Image URL printed to console)
    """
  system_prompt = """
You are an implementation developer.

We want you to create a code block in order to integrate it into an image for demonstration purpose.

We only want a code block without introduction or conclusion.
""".strip()
  max_retries = 3
  retry_count = 0
  
  try:
    messages = [
      ChatMessage(role="system", content=system_prompt),
      ChatMessage(role="user", content=readme)
    ]

    response = client.chat(
          model="mistral-medium-latest", 
          messages=messages,
      )


    carbon_client = Carbon()

    carbon_img = carbon_client.create(response)

    print(carbon_img)

  except Exception as e:
    print(f"An error occurred: {e}")
    
