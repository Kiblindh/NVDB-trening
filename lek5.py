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

def get_current_weather(location, unit="fahrenheit"):
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

def get_current_location():
    locations = ["Tokyo", "San Francisco", "Paris"]
    location = random.choice(locations)
    return json.dumps({"location": location})

# Available tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_location",
            "description": "Get a random current location",
            "parameters": {},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]

# Dictionary of available functions
available_functions = {
    "get_current_location": get_current_location,
    "get_current_weather": get_current_weather,
}

# Main function to run the conversation
def run_conversation(messages=None, depth=0, max_depth=3):
    if messages is None:
        messages = [{"role": "user", "content": "Please tell me the weather of a random location."}]
    
    # Send the conversation and available functions to the model
    response = client.chat.completions.create(
        model="gpt-4",
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
                "content": function_response,
            })
        
        # Send updated conversation back to the model recursively
        return run_conversation(messages, depth + 1, max_depth)
    
    return response

# Run the conversation and print the final output
response = run_conversation()
print(f"\n\nFinal Output:\n{response.choices[0].message.content}")
