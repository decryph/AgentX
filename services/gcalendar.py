# services/calendar.py

import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = st.secrets["GOOGLE_CALENDAR_ID"]
key_json = st.secrets["SERVICE_ACCOUNT_KEY"]

with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as f:
    f.write(key_json)
    f.flush()
    SERVICE_ACCOUNT_FILE = f.name


# Check if a time is busy
from datetime import datetime, timedelta, timezone

def get_gcalendar():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
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

