# agent.py

import os
from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from gcalendar import get_free_slots, book_appointment
# Load .env file
load_dotenv()

# Gemini LLM setup
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3,
    convert_system_message_to_human=True
)

# Wrap your calendar tools

import dateparser
from datetime import datetime, timedelta, timezone

# ... other code ...

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
