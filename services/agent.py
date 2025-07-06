# agent.py

import streamlit as st
import os
from datetime import datetime, timedelta, timezone
import dateparser
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from gcalendar import get_free_slots, book_appointment

# ✅ Explicitly pull from Streamlit secrets
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY  # Optional fallback

# ✅ Gemini model setup
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3,
    google_api_key=GOOGLE_API_KEY
)

# ✅ Define tools for LangChain agent
tools = [
    Tool(
        name="CheckAvailability",
        func=lambda x: (
            lambda dt: (
                print(f"DEBUG: Parsed datetime: {dt}, Type: {type(dt)}, Has timezone: {dt.tzinfo is not None}"),
                get_free_slots(
                    dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc),
                    (dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)) + timedelta(hours=1)
                )
            )[1] if dt else "Sorry, I couldn't understand the time you provided."
        )(dateparser.parse(x, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True})),
        description="Use this tool to check available time slots"
    ),
    Tool(
        name="BookAppointment",
        func=lambda x: (
            lambda dt: (
                print(f"DEBUG: Booking for datetime: {dt}"),
                book_appointment(
                    "Meeting",
                    dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc),
                    (dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)) + timedelta(hours=1)
                )
            )[1] if dt else "Sorry, I couldn't understand the time you provided for booking."
        )(dateparser.parse(x, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True})),
        description="Use this tool to book a calendar event"
    ),
]

# ✅ Final LangChain agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
