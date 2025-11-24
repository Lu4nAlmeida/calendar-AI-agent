from google_auth_oauthlib.flow import InstalledAppFlow


def set_token():
    # Scopes define what you can access (calendar events, read/write)
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=8080)

    # Save the credentials (includes refresh token if offline access was granted)
    with open("token.json", "w") as token:
        token.write(creds.to_json())
