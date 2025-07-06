# agent.py

import os
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from gcalendar import get_free_slots, book_appointment
import dateparser
from datetime import datetime, timedelta, timezone

# Get API key from Streamlit secrets or environment
try:
    import streamlit as st
    api_key = st.secrets["GOOGLE_API_KEY"] if "GOOGLE_API_KEY" in st.secrets else os.getenv("GOOGLE_API_KEY")
except ImportError:
    # Local development
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

# Gemini LLM setup with correct model name and API key
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",  # Corrected model name
    temperature=0.3,
    convert_system_message_to_human=True,  # Added missing comma
    google_api_key=api_key  # Explicitly provide API key
)

# Simplified calendar tool function
def check_availability(time_str):
    dt = dateparser.parse(time_str, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True})
    if not dt:
        return "Sorry, I couldn't understand the time you provided."
        
    # Ensure timezone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
        
    # Check availability
    return get_free_slots(dt, dt + timedelta(hours=1))

# Tools with simplified functions
tools = [
    Tool(
        name="CheckAvailability",
        func=check_availability,
        description="Use this tool to check available time slots. Input should be a date and time."
    ),
    Tool(
        name="BookAppointment",
        func=lambda x: book_appointment("Meeting", datetime.now(timezone.utc) + timedelta(hours=2), datetime.now(timezone.utc) + timedelta(hours=3)),
        description="Use this tool to book a calendar event"
    ),
]

# Agent creation
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
