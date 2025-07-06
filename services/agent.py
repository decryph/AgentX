import os
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from gcalendar import get_free_slots, book_appointment
import dateparser
from datetime import datetime, timedelta, timezone

# Try to import streamlit
try:
    import streamlit as st
    has_streamlit = True
except ImportError:
    has_streamlit = False
    from dotenv import load_dotenv
    load_dotenv()

# Get API key correctly
if has_streamlit and hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = os.getenv("GOOGLE_API_KEY")

# Gemini LLM setup with explicit API key and correct model name
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",  # Fixed model name
    temperature=0.3,
    convert_system_message_to_human=True,  # Fixed missing comma
    google_api_key=api_key  # Explicitly provide API key
)

# Define tools
def check_availability_tool(time_str):
    parsed_time = dateparser.parse(time_str, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True})
    if not parsed_time:
        return "Sorry, I couldn't understand the time you provided."
    
    if parsed_time.tzinfo is None:
        parsed_time = parsed_time.replace(tzinfo=timezone.utc)
    else:
        parsed_time = parsed_time.astimezone(timezone.utc)
    
    return get_free_slots(parsed_time, parsed_time + timedelta(hours=1))

tools = [
    Tool(
        name="CheckAvailability",
        func=check_availability_tool,
        description="Use this tool to check available time slots"
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
