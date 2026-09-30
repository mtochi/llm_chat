import time
import streamlit as st
from google import genai
from google.genai import types
from google.genai import errors
from functions import get_secret, reset_chat

api_key = get_secret("API_KEY")

client = genai.Client(api_key=api_key)

st.title("Chat Assistant")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if not st.session_state.chat_history:
    st.session_state.chat_history.append(("assistant", "Hi! How can I help you?"))

user_message = st.chat_input("Type your message...")
for role, message in st.session_state.chat_history:
    st.chat_message(role).write(message)

temperature = st.sidebar.slider(
                label = "Select the temperature",
                min_value=0.0,
                max_value=2.0,
                value=1.0
            )

if st.sidebar.button("Reset chat"):
    reset_chat()

if user_message:
    st.chat_message("user").write(user_message)
    st.session_state.chat_history.append(("user", user_message))

    system_prompt = f"""
    You are a friendly and a programming tutor.
    Always explain concepts in a simple and clear way, using examples when possible.
    If the user asks something unrelated to programming, politely bring the conversation back to programming topics.
    """

    model_name = "gemini-3.1-flash-lite"
    response = None

    context = [
        {"role": "model" if role == "asistant" else "user", "parts": [{"text": msg}]} for role, msg in st.session_state.chat_history ]

    for attempt in range(3):
        try:
            
            response = client.models.generate_content(
                model=model_name,
                contents=context,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=temperature,
                    max_output_tokens = 1000
                ),
            )
            break
        except errors.ServerError:
            if attempt < 2:
                time.sleep(10)
        except errors.APIError as e:
            st.error(f"API error: {e}")
            break

    if response is not None:
        assistant_reply = response.text
        st.chat_message("assistant").write(assistant_reply)
        st.session_state.chat_history.append(("assistant", assistant_reply))
    else:
        st.error("Gemini's free tier is busy right now — try again in a minute.")