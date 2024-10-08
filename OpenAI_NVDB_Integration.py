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

def getTunnelsWithHighestÅDT(higherThanValue):
  response = requests.get('https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekter/67?overlapp=540(4623>={higherThanValue})')
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
          "description": "Returnerer alle sjøtunneler objekter i Norge (inneholder id (kan brukes i getSpecificTunnelById) for å få infoen til en tunnel) og metadata.",
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
        "name":"getSpecificOceanTunnel",
        "description":"Returnerer informasjon om en tunnel ved å bruke id-en til tunnelen. Kan hente ut informasjon som navnet til en tunnel, strekning til en tunnel og lokasjon, etc",
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
    }
  ]





  
  messages=[
      {"role": "system", "content": "Du er en ekspert på norske veier og skal alltid svare på norsk. Hvis du ikke har datagrunnlag til spørsmålet så svarer du at du mangler data"},
      {"role": "user", "content": userQuestion}
  ]
  
  if messages is None:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools,
        tool_choice="auto",
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
                "content": function_response,
            })
        
        # Send updated conversation back to the model recursively
        return run_conversation(messages, depth + 1, max_depth)
    
    return response


  
    

#print(getNVDBInfo(107))
#print(getAllNVDBFylker())
#print(getAllOceanTunnels())
#print(getSpecificOceanTunnel(78730377))

print(run_conversation())


"""

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

      print("\n These tools/functions are called \n")
      print(tool_call)
      print("\n", function_name, "\n")
      print("\n", function_to_call, "\n")
      print("\n", function_args, "\n")
      print("Second response:\n")
      print("\n", function_response)



  second_response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto",
  )

  response_message2 = second_response.choices[0].message
  tool_calls2 = response_message2.tool_calls

  if tool_calls2:
    available_functions2 = {"getAllNVDBFylker": getAllNVDBFylker, 
    "getSpecificOceanTunnel": getSpecificOceanTunnel}

    messages.append(response_message2)
    print("\n\n\n", messages, "\n\n\n")
    for tool_call2 in tool_calls2:
      function_name2 = tool_call2.function.name
      function_to_call2 = available_functions2[function_name2]
      function_args2 = json.loads(tool_call2.function.arguments)
      function_response2 = function_to_call2()
      messages.append(
          {
              "tool_call_id": tool_call2.id,
              "role": "tool",
              "name": function_name2,
              "content": function_response2,
          }
      )  # extend conversation with function respons

      print("\n These tools/functions are called \n")
      print(tool_call2)
      print("\n", function_name2, "\n")
      print("\n", function_to_call2, "\n")
      print("\n", function_args2, "\n")
      print("Function response 2:\n")
      print("\n", function_response2)

  third_response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages
  )

  print("\n\n Final response: \n")
  return third_response
  """