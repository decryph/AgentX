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
    # If running on Streamlit Cloud, use secrets
    if has_streamlit and hasattr(st, 'secrets') and 'GOOGLE_CREDENTIALS_JSON' in st.secrets:
        try:
            # Parse JSON from secrets
            creds_dict = json.loads(st.secrets['GOOGLE_CREDENTIALS_JSON'])
            credentials = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=SCOPES)
            print("Using credentials from Streamlit secrets")
        except Exception as e:
            print(f"Error parsing credentials from secrets: {e}")
            raise
    else:
        # Local development fallback
        SERVICE_ACCOUNT_FILE = "C:\\Users\\SHRUTI\\Desktop\\AgentX\\formal-incline-465110-f3-8ade757f5d04.json"
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('calendar', 'v3', credentials=credentials)
    return service

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
