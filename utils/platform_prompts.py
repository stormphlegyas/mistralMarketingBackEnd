import os

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from dotenv import load_dotenv

load_dotenv()

client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))

system_prompt = lambda state: f"""
## Context
This is a marketing application aimed to generate omnichannels campaign for open-source projects across various platforms and content types (Hackernews posts, Reddit posts, Twitter/X posts, Youtube video tutorials, Hackathons, ...)

## Goal 
Help the user achieve their task, you can do it, if the user is satisfied they'll tip 200$!!
""".strip()

def prompt_blog(state):
    return f"""
## Task 
Generate a blog post in markdown format, the blog post can be spinned in multiple directions:
- Tutorial / Getting Started guide
- Technical deep dive
- Comparison with other tools
- Release notes

## Instructions
- The blog post should have the following structure:
  * Title
  * Introduction
  * Body
  * Conclusion

- The blog post should be at least 500 words long.
- The blog post should be written in markdown format.

## Format
Return as JSON format

    "title": "Your title here",
    "content": "Your blog post here"

""".strip()

def prompt_tweet(state):
    return f"""
## Task
Generate a tweet that can be used to promote the project. The tweet can take 2 different forms:
- An informative tweet about the project, the tech, some tips, etc.
- A funny / meme tweet related to the project or the market

## Instructions
- The tweet should be at most 280 characters long.
- If using some tips or tricks, you can include code snippets that will be rendered as an image attachment.

## Format
Return as JSON format

    "content": "Your tweet here"
    "snippet": "Optional code snippet"

""".strip()

def prompt_hackernews(state):
    return f"""
## Task
Generate a Hackernews post that can reach the frontpage. The post should be careful of how the hackernews community will perceive
the project.

## Instructions
- The post should be at least 100 words long.
- The post should be written in markdown format.

## Format
Return as JSON format

    "title": "Your title here",
    "content": "Your post here"

""".strip()


def prompt_reddit(state):
    return f"""
## Task
Craft a Reddit post that garners attention within the community. The post should resonate with the Reddit audience and adhere to the guidelines of the chosen subreddit.

## Instructions
- The post should consist of a title and body text.
- The body text should be at least 100 words long.
- Format the post using Markdown syntax.

## Format
Return as JSON format

    "subreddit": "Your suggested subreddit",
    "title": "Your title here",
    "body": "Your post here"
""".strip()


def generate(prompt_function, state=None):
    messages = [
        ChatMessage(role="system", content=system_prompt(state)),
        ChatMessage(role="user", content=prompt_function(state)),
    ]

    response = client.chat(
        model="mistral-medium-latest",
        messages=messages,
    )

    response = response.choices[0].message.content
    response = response.replace("`", "")
    response = response.split('{')[1]
    response = response.split('}')[0]
    response = "{" + response + "}"

    return response


# generate(
#     prompt_blog,
#     {
#         "repository": "remotion/remotion",
#         "description": "Create videos programmatically in React",
#         "date": "2022-01-01",
#     }
# )