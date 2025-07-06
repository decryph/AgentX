# app.py

import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services')))
from agent import agent  # imports your LangChain Gemini agent

import re

def style_response(text):
    url_match = re.search(r'(https?://\S+)', text)
    if url_match:
        link = url_match.group(1)
        return f"📅 Appointment booked! [View it here]({link})"
    return text


st.set_page_config(page_title="TailorTalk Bot", page_icon="🧵", layout="centered")
st.markdown("""
    <div style='text-align: center; padding: 10px 0;'>
        <h1 style='color: #dc9d77;'>🧵 TailorTalk Bot</h1>
        <p style='font-size: 16px; color: #888;'>Your friendly AI calendar stylist ✨</p>
    </div>
""", unsafe_allow_html=True)


# Keep chat history in session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
# Alternative styling with just a border
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"], unsafe_allow_html=True)
    else:  # assistant
        with st.chat_message("assistant"):
            st.markdown(
                "<div style='padding:12px 16px; background-color:#263238; color:#a8d8ea; border-radius:10px; line-height:1.5'>{}</div>".format(msg["content"]),
                unsafe_allow_html=True
            )

# Chat input
user_input = st.chat_input("How can I help you today?")

if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Call the agent
with st.chat_message("assistant"):
   response = agent.run(user_input)
   styled_response = style_response(response)
   st.markdown(
        f"<div style='padding:12px 16px; background-color:#263238; color:#a8d8ea; border-radius:10px; line-height:1.5'>{styled_response}</div>",
        unsafe_allow_html=True
    )
st.session_state.messages.append({"role": "assistant", "content": styled_response})
