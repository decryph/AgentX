# 🧵 AgentX Bot

### Your Friendly AI Calendar Stylist ✨

AgentX is a conversational AI assistant that books appointments on Google Calendar — just by chatting with you.

Whether you're juggling clients, planning calls, or trying to find a quiet hour to breathe — TailorTalk is your go-to scheduling buddy.



 ### 💡 What Can It Do?

🗓️ **Natural Language Booking**  
> _“Book a meeting tomorrow at 3pm”_ → 📅 Done.

🧠 **LLM-Powered Smart Agent**  
> Understands your intent, parses time, and acts.

🔄 **Checks Availability (Optional)**  
> Can be extended to avoid conflicts before booking.

🔗 **Sends Live Calendar Links**  
> Click and view the event right in your Google Calendar.

⚡ **No OAuth Hassle**  
> Uses a secure service account — deploy once, forget forever.

---

## 🛠️ Tech Stack

| Layer       | Tech                             |
|------------|----------------------------------|
| 🤖 AI Core   | [Gemini 2.0 Flash] via `langchain-google-genai` |
| 🧠 Agent     | LangChain Tools + Agent (Zero-Shot ReAct) |
| 📅 Calendar | Google Calendar API (`freeBusy`, `insert`) |
| 💬 UI       | Streamlit Chat (`st.chat_input`, `st.chat_message`) |
| 🧪 NLP      | `dateparser` (understands natural time) |
| 🔐 Secrets  | `secrets.toml` (no key leaks) |
| ☁️ Hosting  | Streamlit Cloud (publicly accessible) |

---

## 🚀 Live Demo

✨ Try it out here:  
👉 [https://agentx-shruti.streamlit.app](https://agentx-shruti.streamlit.app)

---

## 📸 Screenshots

> Booking in action:

![image](https://github.com/user-attachments/assets/3c55dd29-e18e-44e9-b5cf-d1ce8549b874)

> Google Calendar confirmation:

![image](https://github.com/user-attachments/assets/882b2eed-ab94-4052-96ab-192f4b7e0373)


---

## 📁 Folder Structure

```bash
AgentX/
├── frontend/
│   └── app.py              # Streamlit chat interface
├── services/
│   ├── agent.py            # LangChain agent logic
│   └── gcalendar.py        # Google Calendar integration
├── .streamlit/
│   └── secrets.toml        # Secure API keys + calendar ID
├── requirements.txt        # Python dependencies
└── README.md               # You are here
