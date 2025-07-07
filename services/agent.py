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
                
def check_availability_wrapper(x):
    dt = dateparser.parse(x, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True})
    if not dt:
        return "Oops! Couldn't understand the time you meant. Could you rephrase it?"

    start = dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
    end = start + timedelta(hours=1)

    slots = get_free_slots(start, end)

    if isinstance(slots, str):
        return slots  # It's an error message

    if not slots:
        return "You're free during that time slot! 🎉"

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
