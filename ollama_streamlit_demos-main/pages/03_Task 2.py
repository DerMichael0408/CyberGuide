import streamlit as st
import ollama

# Define the scenario prompt (this is what the LLM will ask the user)
scenario_prompt = (
    "Quiz me about a phishing mail from www.gogle.com. Just ask me the questions: Is this a correct url?"
    
)

# Reset chat when switching to this page
if "current_page" not in st.session_state or st.session_state.current_page != "CyberGuide":
    st.session_state.messages = []  # Clear chat
    st.session_state.current_page = "CyberGuide"  # Set current page

# Initialize chat with the scenario if it's empty
if not st.session_state.messages:
    # Step 1: LLM generates a scenario question
    response_data = ollama.chat(
        model="mistral:7b",  # Adjust model name if needed
        messages=[{"role": "system", "content": scenario_prompt}]
    )
    llm_message = response_data["message"]["content"]

    # Step 2: Store the LLM's message as the first chat entry
    st.session_state.messages.append({"role": "assistant", "content": llm_message})

# Page title
st.title("Task 2")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input box
user_input = st.chat_input("Enter your response here...")

if user_input:
    # Store and display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # LLM responds based on user input
    response_data = ollama.chat(
        model="deepseek-r1:1.5b",
        messages=st.session_state.messages
    )
    llm_response = response_data["message"]["content"]

    # Store and display LLM response
    st.session_state.messages.append({"role": "assistant", "content": llm_response})
    with st.chat_message("assistant"):
        st.markdown(llm_response)