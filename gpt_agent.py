from openai import OpenAI
from middleware import create_event, get_current_date, list_events, delete_event
import json
from pathlib import Path


OPENAI_API_KEY = Path("api.txt").read_text().strip()

client = OpenAI(api_key=OPENAI_API_KEY)

context = f'''
You are a Google Calendar AI Agent Assistant, your job is to help the user organize their own calendar.
Currently the project is very early in development, and we are running the first tests to check if you are able to interact with the calendar API through the function tools given.
Current Date: {get_current_date()}
Timezone: Asia/Ho_Chi_Minh
'''

# Test prompts
'Can you create 3 events this afternoon? Eat dinner at 8pm, do homework at 6pm and sleep at 10pm'
'Can you create a recurring event reminding me to eat lunch everyday at 1pm?'
'Can you delete my next event?'
'Can you delete my next recurring event?'
'What is my next event?'

# Load tool definitions
with open('tools.json', 'r') as file:
    tools = json.load(file)

# Conversation history
input_list = [{"role": "developer", "content": context}]

print("Google Calendar Assistant is active. Type 'exit' to quit.\n")

waiting_function_output = False

while True:
    if not waiting_function_output:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        # Append user message
        input_list.append({"role": "user", "content": user_input})

    # Send to model
    response = client.responses.create(
        model="gpt-5",
        tools=tools,
        input=input_list,
    )

    # Add model response to context
    input_list += response.output

    # Handle any function calls
    for item in response.output:
        if item.type == "function_call":
            args = json.loads(item.arguments)
            if item.name == "list_events":
                events = list_events(**args)
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({"events": events})
                })
            elif item.name == "create_event":
                event = create_event(args)
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({"event": event})
                })
            elif item.name == "delete_event":
                status = delete_event(**args)
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({"event": status})
                })


    if response.output_text != "":
        print("\nAssistant:", response.output_text, "\n")
        waiting_function_output = False
    else:
        waiting_function_output = True
