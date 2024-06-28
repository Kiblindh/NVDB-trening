from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
import json

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


def getNVDBInfo(url):
  response = requests.get(url)
  if response.status_code == 200:
    data = response.json()
    return str(data)
  
  else:
    return "The request didn't work"

    

print(getNVDBInfo("https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekter/107/statistikk"))
#print(completion.choices[0].message)    