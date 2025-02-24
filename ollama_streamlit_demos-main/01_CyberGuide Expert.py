import streamlit as st
from openai import OpenAI
from utilities.icon import page_icon

st.set_page_config(
    page_title="CyberGuide",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def extract_model_names(models_info) -> tuple:
    """
    Extracts model names safely from the ListResponse object returned by ollama.list().
    """
    if not models_info or not hasattr(models_info, "models"):
        return ()

    return tuple(model.model for model in models_info.models)


def main():
    """
    The main function that runs the application.
    """
    st.sidebar.title("CyberGuide Navigation")

    page_icon("💬")
    st.header("CyberGuide")
    
    st.subheader("Your Cyber Security Expert", divider="red", anchor=False)

    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # required, but unused
    )

    models_info = ollama.list()
    available_models = extract_model_names(models_info)

    if available_models:
        selected_model = st.selectbox(
            "Pick a model available locally on your system ↓", available_models
        )

    else:
        st.warning("You have not pulled any model from Ollama yet!", icon="⚠️")
        if st.button("Go to settings to download a model"):
            st.page_switch("pages/03_⚙️_Settings.py")

    message_container = st.container(height=500, border=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    if message["role"] != "system":  # Don't show system prompt in chat history
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User input field
user_input = st.chat_input("Reply here...")

if user_input:
    # Append user input to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate AI response using Ollama
    response = ollama.chat(model="llava:latest", messages=st.session_state.messages)

    # Extract and append the assistant's reply
    ai_message = response["message"]["content"]
    st.session_state.messages.append({"role": "assistant", "content": ai_message})

    # Display AI response
    with st.chat_message("assistant"):
        st.markdown(ai_message)
