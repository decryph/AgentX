# services/calendar.py
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone

# Try to import streamlit, but don't fail if it's not there
try:
    import streamlit as st
except ImportError:
    st = None

SCOPES = ['https://www.googleapis.com/auth/calendar']

# --- Correctly load the Calendar ID ---
if st and hasattr(st, 'secrets') and "GOOGLE_CALENDAR_ID" in st.secrets:
    CALENDAR_ID = st.secrets["GOOGLE_CALENDAR_ID"]
else:
    # Fallback for local development
    CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID', 'primary')


def get_gcalendar():
    """Builds the Google Calendar service object, using secrets when available."""
    credentials = None
    # Check if running in Streamlit Cloud and secrets are available
    if st and hasattr(st, 'secrets') and "GOOGLE_CREDENTIALS_JSON" in st.secrets:
        creds_json_str = st.secrets["GOOGLE_CREDENTIALS_JSON"]
        creds_info = json.loads(creds_json_str)
        credentials = service_account.Credentials.from_service_account_info(
            creds_info, scopes=SCOPES
        )
    else:
        # Fallback for local development
        # IMPORTANT: Ensure this JSON file is in your services folder or provide the correct path
        local_path = os.path.join(os.path.dirname(__file__), "formal-incline-465110-f3-8ade757f5d04.json")
        if os.path.exists(local_path):
             credentials = service_account.Credentials.from_service_account_file(
                local_path, scopes=SCOPES)
        else:
            raise FileNotFoundError("Service account JSON not found for local development.")

    service = build('calendar', 'v3', credentials=credentials)
    return service



def get_free_slots(start_time, end_time):
    service = get_gcalendar()
    
    # Ensure UTC timezone
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    else:
        start_time = start_time.astimezone(timezone.utc)
        
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)
    else:
        end_time = end_time.astimezone(timezone.utc)
    
    # Format times correctly for Google Calendar API
    start_str = start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    end_str = end_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    
    print(f"DEBUG: Start time: {start_str}")
    print(f"DEBUG: End time: {end_str}")
    
    request_body = {
        "timeMin": start_str,
        "timeMax": end_str,
        "timeZone": "UTC",
        "items": [{"id": CALENDAR_ID}]
    }

    try:
        result = service.freebusy().query(body=request_body).execute()
        busy_times = result['calendars'][CALENDAR_ID]['busy']
        return busy_times
    except Exception as e:
        print(f"ERROR: {e}")
        print(f"Request body: {request_body}")
        return f"Error checking availability: {str(e)}"
    

def book_appointment(summary, start_time, end_time):
    service = get_gcalendar()

    event = {
        'summary': summary,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
    }

    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return event.get('htmlLink')

