# agent.py

import os
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from gcalendar import get_free_slots, book_appointment
import dateparser
from datetime import datetime, timedelta, timezone

# Handle API key for both local and cloud environments
try:
    import streamlit as st
    # Use Streamlit secrets when available
    if hasattr(st, 'secrets') and "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        # Fall back to .env file
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
except ImportError:
    # Local environment only
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

# Gemini LLM setup - FIXED ERRORS
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",  # FIXED: correct model name
    temperature=0.3,
    convert_system_message_to_human=True,  # FIXED: added missing comma
    google_api_key=api_key  # FIXED: explicitly provide API key
)

# Simplified calendar function
def check_availability(time_str):
    dt = dateparser.parse(time_str, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True})
    if not dt:
        return "Sorry, I couldn't understand the time you provided."
    
    # Ensure timezone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    
    return get_free_slots(dt, dt + timedelta(hours=1))

# Tools with simplified implementations
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
