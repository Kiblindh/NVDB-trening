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
  
def getAllOceanTunnels():
  response = requests.get('https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekter/581?egenskap=egenskap(9517)=13432')
  if response.status_code == 200:
    data = response.json()
    return str(data)
  
  else:
    return "The request didn't work"

def getSpecificOceanTunnel(id):
  response = requests.get('https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekter/581/' + str(id))
  if response.status_code == 200:
    data = response.json()
    return str(data)
  
  else:
    return "The request didn't work"

def run_conversation():

  userQuestion = input("Hva er spørsmålet ditt?")
  tools = [
    {
      "type":"function",
      "function":{
        "name":"getAllNVDBFylker",
        "description":"Returner alle nvdb fylker",
        "parameters":{
          "type":"object",
          "properties":{
            "navn":{
              "type":"string",
              "description":"Navnet til et fylke, Akershus etc"
            },
            "organisasjonsnummer":{
              "type":"integer",
              "description":"Dette er organisasjonsnummeret til et fylke"
            },
            "nummer":{
              "type":"integer",
              "description":"Dette er et nummer som representerer fylket"
            }
          }
        }
      }
    },
    {
      "type":"function",
      "function":{
          "name":"getAllOceanTunnels",
          "description": "Returnerer alle sjøtunneler i Norge med objekter (inneholder id (kan brukes i getSpecificTunnelById) og url) og metadata. Dette kan du gjøre ved å først kalle din gitte funksjon og deretter kalle funksjonen getSpecificOceanTunnel med id-en til tunnelen du vil ha mer informasjon om. ",
          "parameters":{
            "type":"object",
            "properties":{
              "objekter":{
                "type":"object",
                "description":"Inneholder informasjon om tunnelobjekter"
              },
              "metadata":{
                "type":"object",
                "description":"Inneholder metadata om alle tunnelene"
            },
          },
        }
      }
    },
    {
      "type":"function",
      "function":{
        "name":"getSpecificOceanTunnel",
        "description":"Returnerer informasjon om en tunnel ved å bruke id-en til tunnelen. Kan hente ut informasjon som navnet til en tunnel, strekning til en tunnel og lokasjon, etc",
        "parameters":{
          "type":"object",
          "properties":{
            "id":{
              "type":"integer",
              "description":"Id som representerer en tunnel"
            },
            "egenskaper":{
              "type":"object",
              "description":"Data til tunnelen"
            },
            "metadata":{
              "type":"object",
              "description":"Metadata om tunnellen"
            }
          }
        }
      }
    },
  ]
  messages=[
      {"role": "system", "content": "Du er en ekspert på norske veier og skal alltid svare på norsk. Hvis du ikke har datagrunnlag til spørsmålet så svarer du at du mangler data"},
      {"role": "user", "content": userQuestion}
  ]

  response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto",
  )

  response_message = response.choices[0].message
  tool_calls = response_message.tool_calls
  print("\nFirst response:\n" + str(response_message))
  
  if tool_calls:
    available_functions = {"getAllNVDBFylker": getAllNVDBFylker, 
    "getAllOceanTunnels": getAllOceanTunnels, 
    "getSpecificOceanTunnel": getSpecificOceanTunnel}

    messages.append(response_message)
    for tool_call in tool_calls:
      function_name = tool_call.function.name
      function_to_call = available_functions[function_name]
      function_args = json.loads(tool_call.function.arguments)
      function_response = function_to_call()
      messages.append(
          {
              "tool_call_id": tool_call.id,
              "role": "tool",
              "name": function_name,
              "content": function_response,
          }
      )  # extend conversation with function respons


  second_response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
  )

  print("\n\n Final response: \n")
  return second_response

    

#print(getNVDBInfo(107))
#print(getAllNVDBFylker())
#print(getAllOceanTunnels())
#print(getSpecificOceanTunnel(78730377))

print(run_conversation())