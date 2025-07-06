# agent.py

import os
from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from gcalendar import get_free_slots, book_appointment
import dateparser
from datetime import datetime, timedelta, timezone

# Get API key with correct capitalization
try:
    import streamlit as st
    if hasattr(st, 'secrets') and "GooGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GooGLE_API_KEY"]  # Using your capitalization
    else:
        load_dotenv()
        api_key = os.getenv("GooGLE_API_KEY")  # Using your capitalization
except ImportError:
    load_dotenv()
    api_key = os.getenv("GooGLE_API_KEY")  # Using your capitalization

# Gemini LLM setup with fixed syntax and explicit API key
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3,
    convert_system_message_to_human=True,  # FIXED: Added missing comma
    google_api_key=api_key  # FIXED: Explicitly passing the API key
)

# Keeping your original tools
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
