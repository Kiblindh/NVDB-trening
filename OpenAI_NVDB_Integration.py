from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()
client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")


def getNVDBInfo(id):
  response = requests.get("https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekter/" + str(id) + "/statistikk") #example is id 107
  if response.status_code == 200:
    data = response.json()
    return str(data)
  
  else:
    return "The request didn't work"


def getAllNVDBFylker():
  response = requests.get("https://nvdbapiles-v3.atlas.vegvesen.no/omrader/fylker")
  if response.status_code == 200:
    data = response.json()
    return str(data)
  
  else:
    return "The request didn't work"

def run_conversation():

  tools = [
    {
      "type":"function",
      "function":{
        "name":"getAllNVDBFylker",
        "description":"Return all nvdb fylker",
        "parameters":{
          "type":"object",
          "properties":{
            "navn":{
              "type":"string",
              "description":"The name of the fylke, Akershus etc"
            },
            "organisasjonsnummer":{
              "type":"integer",
              "description":"This gives the organization number of the fylke"
            },
            "nummer":{
              "type":"integer",
              "description":"This is a number representing the fylke"
            }
          }
        }
      }
    }
  ]
  messages=[
      {"role": "system", "content": "You are an expert on information about norwegian roads"},
      {"role": "user", "content": "Can you give me a list of all the fylke in Norway sorted by their number"}
  ]

  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
    tools=tools,
    tool_choice="auto",
  )

  response_message = response.choices[0].message
  print(response_message)
  tool_calls = response_message.tool_calls
  
  if tool_calls:
    available_functions = {"getAllNVDBFylker": getAllNVDBFylker,}
    messages.append(response_message)
    for tool_call in tool_calls:
      function_name = tool_call.function.name
      function_to_call = available_functions[function_name]
      function_args = json.loads(tool_call.function.arguments)
      function_response = function_to_call(
      )
      messages.append(
          {
              "tool_call_id": tool_call.id,
              "role": "tool",
              "name": function_name,
              "content": function_response,
          }
      )  # extend conversation with function response

  second_response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
  )
  return second_response

    

#print(getNVDBInfo(107))
print(getAllNVDBFylker())
print(run_conversation())