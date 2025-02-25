import ollama
import streamlit as st
import os
from openai import OpenAI
from utilities.icon import page_icon
from utilities.rag import retrieve_context


st.set_page_config(
    page_title="CyberGuide",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Function to get the current page name
def get_current_page():
    # Get the filename of the current script
    current_file = os.path.basename(__file__)
    # Remove the extension
    page_name = os.path.splitext(current_file)[0]
    return page_name

# Get current page identifier
current_page = get_current_page()

# Function to get page-specific session state keys
def get_page_key(base_key):
    return f"{current_page}_{base_key}"

# Create page-specific messages key
messages_key = get_page_key("messages")

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
    page_icon("💬")
    st.header("CyberGuide")
    
    st.subheader("Your Cyber Security Expert", divider="red", anchor=False)
    
    # Optionally show current page for debugging
    # st.caption(f"Current page: {current_page}")

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

    # Initialize page-specific messages if they don't exist
    if messages_key not in st.session_state:
        st.session_state[messages_key] = []

    # Display messages from the page-specific chat history
    for message in st.session_state[messages_key]:
        avatar = "🤖" if message["role"] == "assistant" else "😎"
        with message_container.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter a prompt here..."):
        try:
            # Add user message to page-specific chat history
            st.session_state[messages_key].append(
                {"role": "user", "content": prompt})

            message_container.chat_message("user", avatar="😎").markdown(prompt)

            # 🔍 Retrieve relevant cybersecurity knowledge from RAG
            retrieved_context = retrieve_context(prompt)

            # 🔎 Debugging: Show retrieved context in the UI
            with st.expander("🔍 **Retrieved Cybersecurity Context**", expanded=False):
                st.info(retrieved_context)

            with message_container.chat_message("assistant", avatar="🤖"):
                with st.spinner("model working..."):
                    stream = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {
                                "role": "system",
                                "content": f""" 
                                Try to answer using the retrieved information as much as you can, if the data you need isn't available there, use your training.
                                
                                🔹 **Retrieved Knowledge:**
                                {retrieved_context}
                                """,
                            },
                            {"role": "user", "content": prompt},  # ✅ Keep user input separate!
                        ],
                        stream=True,
                    )

                # Stream response and store it
                response = st.write_stream(stream)

            
            # Add assistant response to page-specific chat history
            st.session_state[messages_key].append(
                {"role": "assistant", "content": response})

        except Exception as e:
            st.error(e, icon="⛔️")


if __name__ == "__main__":
    main()