import os
import json
import random
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the functions for retrieving information
def getNVDBInfo(id):
  response = requests.get("https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekter/" + str(id) + "/statistikk") #example is id 107
  if response.status_code == 200:
    data = response.json()
    return data
  
  else:
    return "The request didn't work"


def getAllNVDBFylker():
  response = requests.get("https://nvdbapiles-v3.atlas.vegvesen.no/omrader/fylker")
  if response.status_code == 200:
    data = response.json()
    return data
  
  else:
    return "The request didn't work"
  
def getAllOceanTunnels():
  response = requests.get('https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekter/581?egenskap=egenskap(9517)=13432')
  if response.status_code == 200:
    data = response.json()
    return data
  
  else:
    return "The request didn't work"

def getSpecificTunnelById(id):
  response = requests.get('https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekter/581/' + str(id))
  if response.status_code == 200:
    data = response.json()
    return data
  
  else:
    return "The request didn't work"

def getTrafficIdOfAllTunnelSections(): #Returnerer id-ene til alle trafikkmengdeobjekter i alle tunnelløp
  response = requests.get('https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekter/540?overlapp=67')
  if response.status_code == 200:
    data = response.json()
    return data
  else:
    return "The request didn't work"

def getTunnelSectionTrafficById(id): #Returnerer trafikkmengde-objekt i et tunnelløp ved å bruke id-en til et tunnelløp
  response = requests.get('https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekter/540/' + str(id))
  if response.status_code == 200:
    data = response.json()
    return data
  else:
    return "The request didn't work"

# Available tools
tools = [
    {
      "type":"function",
      "function":{
        "name":"getAllNVDBFylker",
        "description":"Returner alle nvdb fylker",
        "parameters":{
          "type":"object",
          "properties":{
          }
        }
      }
    },
    {
      "type":"function",
      "function":{
          "name":"getAllOceanTunnels",
          "description": "Returnerer alle sjøtunneler objekter i Norge (inneholder id (brukes i getSpecificTunnelById) for å få infoen til en tunnel) og metadata.",
          "parameters":{
            "type":"object",
            "properties":{
              
          },
        }
      }
    },
    {
      "type":"function",
      "function":{
        "name":"getSpecificTunnelById",
        "description":"Returnerer informasjon om en tunnel ved å bruke id-en til tunnelen, gir informasjon som navnet til en tunnel, strekning til en tunnel og lokasjon, etc",
        "parameters":{
          "type":"object",
          "properties":{
            "id":{
              "type":"integer",
              "description":"Id som representerer en tunnel"
            },
          },
          "required":["id"],
        }
      }
    },
    {
      "type":"function",
      "function":{
        "name":"getTrafficIdOfAllTunnelSections",
        "description":"Returnerer id-ene til alle trafikkmengde-objekter i alle tunnelløp.",
        "parameters":{
          "type":"object",
          "properties":{}
        }
      }
    },
    {
      "type":"function",
      "function":{
        "name":"getTunnelSectionTrafficById",
        "description":"Returnerer trafikkmengde-objektet ved å bruke id-en til et trafikkmengdeobjekt. Kan hente ut informasjon som ådt, strekning, etc i et tunnelløp. Id-en kan oppnås ved å bruke getTrafficIdOfAllTunnelSections-funksjonen",
        "parameters":{
          "type":"object",
          "properties":{
            "id":{
              "type":"integer",
              "description":"Id som representerer en tunnel seksjon"
            },
          },
          "required":["id"],
        }
      }
    }
  ]

# Dictionary of available functions
available_functions = {
    "getSpecificTunnelById": getSpecificTunnelById,
    "getAllOceanTunnels": getAllOceanTunnels,
    "getAllNVDBFylker": getAllNVDBFylker,
    "getTunnelSectionTrafficById": getTunnelSectionTrafficById,
    "getTrafficIdOfAllTunnelSections": getTrafficIdOfAllTunnelSections,
}

userQuestion = input("Hva lurer du på?")

# Main function to run the conversation
def run_conversation(messages=None, depth=0, max_depth=20):
    if messages is None:
        messages = [{"role": "user", "content": userQuestion}, {"role": "system", "content": "Du er ekspert på norske veier. Du skal alltid svare på norsk og gi dataen du baserte svaret ditt på i json-format i din endelige respons."}]
    
    # Send the conversation and available functions to the model
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    print("\nResponse")
    print(response)
    
    # Get the model's response and tool calls
    response_message = response.choices[0].message
    print(response_message)
    tool_calls = response_message.tool_calls
    print(tool_calls)
    
    if tool_calls and depth < max_depth:
        print("\nTool Call")
        print(tool_calls)
        
        # Extend conversation with assistant's reply
        messages.append(response_message)
        
        # Process each tool call
        for tool_call in tool_calls:
            print("\n ----Tool Call------")
            print(tool_call)
            function_name = tool_call.function.name
            print(f"Function Name: {function_name}")
            function_to_call = available_functions[function_name]
            
            # Call the function with arguments if present
            function_args = tool_call.function.arguments
            print(f"Function Arguments: {function_args}")
            if function_args:
                function_args = json.loads(function_args)
                function_response = function_to_call(**function_args)
            else:
                function_response = function_to_call()
            
            # Add function response to messages
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_response),
            })
        
        # Send updated conversation back to the model recursively
        return run_conversation(messages, depth + 1, max_depth)
    
    return response

# Run the conversation and print the final output
response = run_conversation()
print(f"\n\nFinal Output:\n{response.choices[0].message.content}")
