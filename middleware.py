import json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import datetime
import os


SCOPES = ['https://www.googleapis.com/auth/calendar']

if not os.path.exists("token.json"):
    load_dotenv()
    flow = InstalledAppFlow.from_client_secrets_file(os.getenv("CREDENTIALS_FILE"), SCOPES)
    creds = flow.run_local_server(port=8080)

    # Save the credentials (includes refresh token if offline access was granted)
    with open("token.json", "w") as token:
        token.write(creds.to_json())

creds = Credentials.from_authorized_user_file("token.json", SCOPES)


service = build("calendar", "v3", credentials=creds)

def get_current_date():
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


def delete_event(eventId: str):
    try:
        service.events().delete(calendarId="primary", eventId=eventId).execute()
        print(f"Event {eventId} deleted.")
        return f"Deleted event: {eventId}"
    except Exception as e:
        print(f"❌ Error in deleting event: {e}")
        return f"Could not delete event due to an error: {e}"


def list_events(start_date=get_current_date(), end_date=None, max_amount=20):
    if end_date == "":
        end_date = None

    try:
        print(f"Getting the next {max_amount} events, from {start_date} to {end_date}")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_date,
                timeMax=end_date,
                maxResults=max_amount,
                singleEvents=False, # TO-DO: Try some testing with this set to false (more token efficient)
                orderBy="startTime",

            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return "No upcoming events found."

        events_list = []
        for event in events:
            important_keys = ['etag', 'id', 'summary', 'description', 'colorId', 'start', 'end', 'creator', 'organizer', 'attendees', 'recurringEventId', 'reminders', 'eventType']
            e = {key: event[key] for key in important_keys if key in event} # Filters non-important keys
            events_list.append(e)

        return json.dumps(events_list)
    except Exception as e:
        print(f"❌ Error in getting events: {e}")
        return f"Could not get events due to an error: {e}"


def create_event(event: dict):
    try:
        result = service.events().insert(calendarId='primary', body=event).execute()
        print("✅ Event successfully created:", result.get("htmlLink"))
        return {"status": "success", "link": result.get("htmlLink"), "event": event}
    except Exception as e:
        print("❌ Failed to create event:", e)
        return f"Could not create event due to an error: {e}"


def update_event(eventId: str, event: dict):
    try:
        service.events().update(calendarId="primary", eventId=eventId, body=event).execute()
        print(f"Event {eventId} updated.")
        return f"Updated event: {eventId}"
    except Exception as e:
        print(f"❌ Failed to update event: {e}")
        return f"Could not update event due to an error: {e}"


print("testing...")