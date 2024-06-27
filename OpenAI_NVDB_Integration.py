from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()




client = OpenAI()


client.api_key = os.getenv("OPENAI_API_KEY")

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem about bugs in code."}
  ]
)


def run_conversation (content):
    tools = [
        {"type": "function",
        "function": {
            "name" : "get_road"
        }
        
        }
    ]

print(completion.choices[0].message)    