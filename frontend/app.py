# app.py

import os, sys
import streamlit as st
import re

# FIX THIS 👇
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services')))

from agent import agent


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

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("How can I help you today?")

if user_input:
    # Show user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Call the agent
    with st.chat_message("assistant"):
        try:
            print("🧠 Sending to agent:", user_input)
            response = agent.run(user_input)
            styled_response = style_response(response)
            st.markdown(
                f"<div style='padding:12px 16px; background-color:#263238; color:#a8d8ea; border-radius:10px; line-height:1.5'>{styled_response}</div>",
                unsafe_allow_html=True
            )
        except Exception as e:
            error_msg = f"⚠️ Bot crashed: {e}"
            print("❌ ERROR:", e)
            styled_response = error_msg
            st.error(error_msg)

    st.session_state.messages.append({"role": "assistant", "content": styled_response})
