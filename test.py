from middleware import *

next_event = json.loads(list_events(max_amount=1))[0]

print(next_event)
print(next_event["id"])

print(get_current_date())

