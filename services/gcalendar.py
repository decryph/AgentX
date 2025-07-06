# services/calendar.py

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone

# Try to import streamlit
try:
    import streamlit as st
    has_streamlit = True
except ImportError:
    has_streamlit = False

SCOPES = ['https://www.googleapis.com/auth/calendar']

# Get calendar ID from environment or Streamlit secrets
if has_streamlit and hasattr(st, 'secrets') and 'GOOGLE_CALENDAR_ID' in st.secrets:
    CALENDAR_ID = st.secrets['GOOGLE_CALENDAR_ID']
else:
    CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID','shryabeauty123@gmail.com')

def get_gcalendar():
    if has_streamlit and hasattr(st, 'secrets') and 'SERVICE_ACCOUNT_KEY' in st.secrets:
        try:
            import tempfile
            import json

            key_json = st.secrets["SERVICE_ACCOUNT_KEY"]

            # Write secret JSON to a temp file
            with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as f:
                f.write(key_json)
                f.flush()
                service_account_path = f.name

            credentials = service_account.Credentials.from_service_account_file(
                service_account_path, scopes=SCOPES
            )
            print("✅ Using credentials from Streamlit secrets")
        except Exception as e:
            print("❌ Error loading credentials from Streamlit secrets:", e)
            raise
    else:
        # Fallback: local dev only (optional)
        SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "path/to/your-local.json")
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )

    return build("calendar", "v3", credentials=credentials)


# Rest of your functions remain the same
def get_free_slots(start_time, end_time):
    # Your existing function...
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
    # Your existing function...
    service = get_gcalendar()

    event = {
        'summary': summary,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
    }

    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return event.get('htmlLink')
