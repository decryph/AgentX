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

# tools as before...
tools = [
    Tool(
        name="CheckAvailability",
        func=lambda x: (
            lambda dt: get_free_slots(
                dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc),
                (dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)) + timedelta(hours=1)
            )
        )[1] if (dt := dateparser.parse(x, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True})) else "Sorry, couldn't parse the time."
    ),
    Tool(
        name="BookAppointment",
        func=lambda x: (
            lambda dt: book_appointment(
                "Meeting",
                dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc),
                (dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)) + timedelta(hours=1)
            )
        )[1] if (dt := dateparser.parse(x, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True})) else "Sorry, couldn't parse booking time."
    ),
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
