# agent.py

import streamlit as st
from datetime import datetime, timedelta, timezone
import dateparser
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from gcalendar import get_free_slots, book_appointment

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# ✅ Do NOT use os.environ for Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3,
    google_api_key=GOOGLE_API_KEY  # ✅ this is what forces API key usage
)
def get_free_slots(start_time, end_time):
    for attempt in range(3):  # Try up to 3 times
        try:
            # Your existing code
            return result['calendars'][CALENDAR_ID]['busy']
        except Exception as e:
            if attempt < 2:  # Don't sleep on the last attempt
                time.sleep(1)  # Wait 1 second before retrying
            else:
                return f"Error checking calendar: {str(e)}"
                
def check_availability_wrapper(x):
    dt = dateparser.parse(x, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True})
    if not dt:
        return "Sorry, couldn't parse the time."
    return get_free_slots(
        dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc),
        (dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)) + timedelta(hours=1)
    )

def book_appointment_wrapper(x):
    dt = dateparser.parse(x, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True})
    if not dt:
        return "Sorry, couldn't parse booking time."
    return book_appointment(
        "Meeting",
        dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc),
        (dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)) + timedelta(hours=1)
    )

# tools as before...
tools = [
    Tool(
        name="CheckAvailability",
        func=check_availability_wrapper,
        description="Use this tool to check available time slots"
    ),
    Tool(
        name="BookAppointment",
        func=book_appointment_wrapper,
        description="Use this tool to book a calendar event"
    ),
]


agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
