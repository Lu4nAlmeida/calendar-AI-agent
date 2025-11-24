import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from main import set_token
import datetime
import os


SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = None

if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
else:
    set_token()
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)


service = build("calendar", "v3", credentials=creds)

def get_current_date():
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


def delete_event(eventId: str):
    print(type(eventId), eventId)
    try:
        service.events().delete(calendarId="primary", eventId=eventId).execute()
        print(f"Event {eventId} deleted.")
        return f"Deleted event: {eventId}"
    except Exception as e:
        print(f"Error in deleting event: {e}")
        return "Could not delete event due to an error."


def edit_event(eventId: str):
    event = service.events().update(calendarId="primary", eventId=eventId).execute()
    print(f"Event {event} updated.")


def list_events(start_date=get_current_date(), end_date=None, max_amount=20):
    # Call the Calendar API
    print(f"Getting the next {max_amount} events")
    if end_date == "":
        end_date = None

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_date,
            timeMax=end_date,
            maxResults=max_amount,
            singleEvents=True,
            orderBy="startTime",

        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        return "No upcoming events found."

    events_list = []
    for event in events:
        important_keys = ['etag', 'id', 'summary', 'start', 'end', 'recurringEventId', 'reminders', 'eventType']
        e = {key: event[key] for key in important_keys if key in event}
        events_list.append(e)

    return json.dumps(events_list)


def create_event(event: dict):
    try:
        result = service.events().insert(calendarId='primary', body=event).execute()
        print("✅ Event successfully created:", result.get("htmlLink"))
        return {"status": "success", "link": result.get("htmlLink"), "event": event}
    except Exception as e:
        print("❌ Failed to create event:", e)
        return {"status": "error", "message": str(e), "event": event}



# TO-DO: implement update_event, add a search_event function


print("testing...")
'''
item = "{\"event\":{\"summary\":\"Homework\",\"start\":{\"dateTime\":\"2025-10-16T15:00:00\",\"timeZone\":\"Asia/Ho_Chi_Minh\"},\"end\":{\"dateTime\":\"2025-10-16T16:00:00\",\"timeZone\":\"Asia/Ho_Chi_Minh\"}}}"
create_event(json.loads(item))
'''