import os
import dateparser
from datetime import datetime, timedelta, timezone
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from gcalendar import get_free_slots, book_appointment

# Try to import streamlit, but don't fail if it's not there
try:
    import streamlit as st
except ImportError:
    st = None

# --- Correctly load the API Key ---
api_key = None
if st and hasattr(st, 'secrets') and "GOOGLE_API_KEY" in st.secrets:
    # Use the key from Streamlit secrets when deployed
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    # Fallback for local development (requires python-dotenv)
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

# --- Gemini LLM setup (Fixed syntax and model name) ---
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    temperature=0.3,
    convert_system_message_to_human=True, # Added missing comma
    google_api_key=api_key
)

# --- Simplified Tool Functions ---
def check_availability_tool(time_str: str) -> str:
    """Helper function to parse time and check for free slots."""
    parsed_time = dateparser.parse(time_str, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True})
    if not parsed_time:
        return "Sorry, I couldn't understand the time you provided."
    
    # Ensure the datetime is timezone-aware
    start_time = parsed_time.astimezone(timezone.utc)
    end_time = start_time + timedelta(hours=1)
    
    print(f"DEBUG: Checking availability for: {start_time}")
    return get_free_slots(start_time, end_time)

# Note: The book_appointment tool is still hardcoded.
# A real implementation would need to parse details from the input string.
def book_appointment_tool(details_str: str) -> str:
    """Helper function to book an appointment."""
    # This is a placeholder. You need to parse 'details_str' for real values.
    summary = "New Meeting"
    start_time = datetime.now(timezone.utc) + timedelta(hours=2)
    end_time = start_time + timedelta(hours=1)
    return book_appointment(summary, start_time, end_time)


tools = [
    Tool(
        name="CheckAvailability",
        func=check_availability_tool,
        description="Use this to check for available time slots. Input should be a date and time, like 'tomorrow at 3pm'."
    ),
    Tool(
        name="BookAppointment",
        func=book_appointment_tool,
        description="Use this to book a calendar event. The input should contain the event details."
    ),
]

# Agent creation
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
