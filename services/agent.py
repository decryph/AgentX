# agent.py

import streamlit as st
from datetime import datetime, timedelta, timezone
import dateparser
import time
import logging
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

logger = logging.getLogger(__name__)
def get_free_slots(start_time, end_time):
    for attempt in range(3):  # Try up to 3 times
        try:
            # Your API call to Google Calendar here
            result = actual_api_call_to_get_slots(start_time, end_time)
            return result['calendars'][CALENDAR_ID]['busy']
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            if "ResourceExhausted" in str(e):
                return "Sorry, the calendar API has exceeded its daily limit. Try again later."
            if attempt < 2:
                time.sleep(1)  # wait before retry
            else:
                return f"Error checking calendar: {str(e)}"
                
def check_availability_wrapper(x):
    dt = dateparser.parse(x, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True})
    if not dt:
        return "Oops! Couldn't figure out the time you meant. Could you rephrase it?"

    start = dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
    end = start + timedelta(hours=1)

    slots = get_free_slots(start, end)

    if isinstance(slots, str):  # means an error message was returned
        return slots

    if not slots:
        return "You're all free during this time! 🎉"
    
    formatted = "\n".join([f"{s['start']} to {s['end']}" for s in slots])
    return f"You're busy during:\n{formatted}"


def book_appointment_wrapper(x):
    dt = dateparser.parse(x, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True})
    if not dt:
       return "Apologies! I'm having trouble connecting to the calendar right now. Please try again in a few minutes."

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
