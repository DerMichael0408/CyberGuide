import ollama
import streamlit as st
import os
from openai import OpenAI
from utilities.icon import page_icon
from utilities.rag import retrieve_context

st.set_page_config(
    page_title="CyberGuide",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for enhanced aesthetics
st.markdown("""
<style>
    /* Model Selection Styling */
    .model-select-container {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px 15px;
        margin-bottom: 15px;
        border: 1px solid #e9ecef;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .model-hint {
        color: #6c757d;
        font-size: 0.8em;
        margin-top: 5px;
    }
    
    /* Chat Message Styling */
    .stChatMessage {
        margin-bottom: 12px;
    }
    
    .user-message {
        background-color: #e6f3ff;
        border-radius: 10px;
        padding: 12px;
    }
    
    .assistant-message {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 12px;
    }
    
    /* Retrieved Context Styling */
    .retrieved-context {
        background-color: #e6f3ff;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 15px;
        border-left: 4px solid #FF4B4B;
    }
    
    /* Spinner Styling */
    .stSpinner > div {
        border-color: #FF4B4B transparent #FF4B4B transparent;
    }
</style>
""", unsafe_allow_html=True)

# Function to get the current page name
def get_current_page():
    current_file = os.path.basename(__file__)
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
    
    st.subheader("Your Cyber Security Expert", divider="red", anchor=False)

    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # required, but unused
    )

    # Model selection container
    st.markdown("""
    <div class="model-select-container">
        <div style="flex-grow:1;">
            <h4 style="margin-bottom: 5px;">🤖 Model Selection</h4>
            <div class="model-hint">
                Tip: Add more models in the Model Management page
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    models_info = ollama.list()
    available_models = extract_model_names(models_info)

    if available_models:
        selected_model = st.selectbox(
            "Available Local Models", 
            available_models,
            help="Choose from your locally available Ollama models"
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
            st.session_state[messages_key].append({"role": "user", "content": prompt})
            message_container.chat_message("user", avatar="😎").markdown(prompt)

            # 🔍 Retrieve relevant cybersecurity knowledge from RAG
            most_relevant, retrieved_context = retrieve_context(prompt)

            # 🌟 Show the most relevant retrieved chunk prominently
            st.markdown(
                f"""
                <div class="retrieved-context">
                    <h4>📌 Most Relevant Retrieved Information</h4>
                    {most_relevant}
                </div>
                """, 
                unsafe_allow_html=True
            )

            # 🔎 Debugging: Show full retrieved context in an expander
            with st.expander("🔍 **All Retrieved Cybersecurity Context**", expanded=False):
                st.info("\n\n".join(retrieved_context))

            with message_container.chat_message("assistant", avatar="🤖"):
                with st.spinner("model working..."):
                    stream = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {
                                "role": "system",
                                "content": f"""                                 
                                **Retrieved Knowledge:** {most_relevant}
                                """,
                            },
                            {"role": "user", "content": prompt},  # ✅ User query is separate!
                        ],
                        stream=True,
                    )

                # Stream response and store it
                response = st.write_stream(stream)

            # Add assistant response to page-specific chat history
            st.session_state[messages_key].append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(e, icon="⛔️")            

if __name__ == "__main__":
    main()