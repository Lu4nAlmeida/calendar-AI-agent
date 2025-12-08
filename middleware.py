import json
import time
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import datetime
import os
from difflib import SequenceMatcher


SCOPES = ['https://www.googleapis.com/auth/calendar']

if not os.path.exists("env/token.json"):
    load_dotenv(dotenv_path='env/.env')
    flow = InstalledAppFlow.from_client_secrets_file(os.getenv("CREDENTIALS_FILE"), SCOPES)
    creds = flow.run_local_server(port=8080)

    # Save the credentials (includes refresh token if offline access was granted)
    with open("env/token.json", "w") as token:
        token.write(creds.to_json())

creds = Credentials.from_authorized_user_file("env/token.json", SCOPES)


service = build("calendar", "v3", credentials=creds)

def get_current_date():
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


def next_year():
    return (datetime.datetime.today() + datetime.timedelta(days=365)).astimezone().replace(microsecond=0).isoformat()


def count_days(end_date, start_date=get_current_date()):
    print(f"Counting days from {start_date} to {end_date}.")

    # parse ISO dates (accepts YYYY-MM-DD or full ISO timestamp)
    start = datetime.datetime.fromisoformat(start_date).date()
    end = datetime.datetime.fromisoformat(end_date).date()

    return (end - start).days


def delete_event(eventId: str, calendarId="primary"):
    try:
        service.events().delete(calendarId=calendarId, eventId=eventId).execute()
        print(f"Event {eventId} deleted.")
        return f"Deleted event: {eventId}"
    except Exception as e:
        print(f"❌ Error in deleting event: {e}")
        return f"Could not delete event due to an error: {e}"


def list_events(start_date=get_current_date(), end_date=None, max_amount=20, calendarId="primary"):
    if end_date == "":
        end_date = None

    try:
        if max_amount < 1000:
            print(f"Getting the next {max_amount} events, from {start_date} to {end_date} in the {calendarId} calendar.")
        events_result = (
            service.events()
            .list(
                calendarId=calendarId,
                timeMin=start_date,
                timeMax=end_date,
                maxResults=max_amount,
                singleEvents=True,
                orderBy="startTime"
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


def create_event(event: dict, calendarId="primary"):
    try:
        result = service.events().insert(calendarId=calendarId, body=event).execute()
        print("✅ Event successfully created:", result.get("htmlLink"))
        return {"status": "success", "link": result.get("htmlLink"), "event": event, "ID": result["id"]}
    except Exception as e:
        print("❌ Failed to create event:", e)
        return f"Could not create event due to an error: {e}"


def update_event(eventId: str, event: dict, calendarId="primary"):
    try:
        service.events().update(calendarId=calendarId, eventId=eventId, body=event).execute()
        print(f"Event {eventId} updated.")
        return f"Updated event: {eventId}"
    except Exception as e:
        print(f"❌ Failed to update event: {e}")
        return f"Could not update event due to an error: {e}"


def search_event(keyword: str, calendarId="primary"):
    print(f"Searching for \'{keyword}\' on the {calendarId} calendar...")
    start_time = time.time()
    threshold = 0.6
    keyword_lower = keyword.lower()
    events = json.loads(list_events(max_amount=9999, end_date=next_year(), calendarId=calendarId))

    exact_matches = [
        event for event in events
        if ('summary' in event and keyword_lower in event['summary'].lower())
           or ('description' in event and keyword_lower in event['description'].lower())
    ]

    if exact_matches:
        print(f"Found {len(exact_matches)} exact matches in {time.time() - start_time:.2f} seconds")
        return exact_matches

    # If no exact matches, search for close matches
    def similarity(a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    close_matches = [
        event for event in events
        if ('summary' in event and similarity(keyword, event['summary']) >= threshold)
           or ('description' in event and similarity(keyword, event['description']) >= threshold)
    ]

    print(f"No exact matches. Found {len(close_matches)} close matches in {time.time() - start_time:.2f} seconds")
    return close_matches

print("testing...")
