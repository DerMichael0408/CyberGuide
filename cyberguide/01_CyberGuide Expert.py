import ollama
import streamlit as st
import os
from openai import OpenAI
from utilities.icon import page_icon
from utilities.rag import retrieve_context
from utilities.template import setup_page

# Disable the parallel tokenizer warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Use setup_page for consistent styling
setup_page(
    page_title="CyberGuide Expert",
    icon_emoji="💬",
    subtitle="Your AI-powered cybersecurity assistant"
)

# Additional CSS for features specific to this page
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

# Function to get chat-specific session state keys
def get_chat_key(base_key):
    """
    Creates a unique key for each chat based on the current page and chat ID
    Makes each chat truly independent with its own message history
    """
    # Make sure chat sessions are initialized before trying to access
    if 'chat_sessions' not in st.session_state:
        st.session_state.chat_sessions = [{'id': 0, 'title': 'New Chat', 'messages': []}]
        
    if 'current_chat_id' not in st.session_state:
        st.session_state.current_chat_id = 0
    
    # Get current chat ID to make each chat truly independent
    chat_id = st.session_state.current_chat_id
    
    # Safety check - ensure chat_id exists in available chats
    chat_exists = False
    for chat in st.session_state.chat_sessions:
        if chat['id'] == chat_id:
            chat_exists = True
            break
            
    # If chat doesn't exist, default to first available chat
    if not chat_exists and len(st.session_state.chat_sessions) > 0:
        chat_id = st.session_state.chat_sessions[0]['id']
        st.session_state.current_chat_id = chat_id
    
    return f"{current_page}_chat{chat_id}_{base_key}"

# Create chat-specific messages key - unique for each chat
messages_key = get_chat_key("messages")

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
    #st.subheader("Your Cyber Security Expert", divider="red", anchor=False)

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

    try:
        # List available models
        models_info = ollama.list()
        available_models = extract_model_names(models_info)
    except Exception as e:
        st.warning(f"Error listing models: {str(e)[:100]}", icon="⚠️")
        available_models = ()

    if available_models:
        # Get previously selected model if it exists
        default_index = 0
        if "selected_model" in st.session_state and st.session_state.selected_model in available_models:
            default_index = available_models.index(st.session_state.selected_model)
            
        selected_model = st.selectbox(
            "Available Local Models", 
            available_models,
            index=default_index,
            help="Choose from your locally available Ollama models"
        )
        
        # Store the selected model in session state
        st.session_state.selected_model = selected_model
    else:
        # If no models are available, set a default fallback model
        fallback_model = "llava:latest"
        if "selected_model" not in st.session_state:
            st.session_state.selected_model = fallback_model
            
        # Show warning and settings link
        st.warning("No models available. Make sure Ollama is running.", icon="⚠️")
        if st.button("Go to settings to download a model"):
            st.page_switch("pages/03_⚙️_Settings.py")

    message_container = st.container(height=500, border=True)

    # Initialize page-specific messages if they don't exist
    if messages_key not in st.session_state:
        # Check if there are messages in the current chat
        if ('chat_sessions' in st.session_state and 
            'current_chat_id' in st.session_state and 
            len(st.session_state.chat_sessions) > 0):
            
            # Find the current chat
            current_chat_id = st.session_state.current_chat_id
            for chat in st.session_state.chat_sessions:
                if chat['id'] == current_chat_id:
                    # Use messages from this chat if they exist
                    st.session_state[messages_key] = list(chat['messages']) if 'messages' in chat and chat['messages'] else []
                    break
            else:
                # If chat not found, initialize empty
                st.session_state[messages_key] = []
        else:
            # No chat sessions yet, initialize empty
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
            
            # Also save user message to the current chat session
            if ('chat_sessions' in st.session_state and 
                'current_chat_id' in st.session_state):
                current_chat_id = st.session_state.current_chat_id
                for chat in st.session_state.chat_sessions:
                    if chat['id'] == current_chat_id:
                        chat['messages'] = list(st.session_state[messages_key])
                        break

            # 🔍 Retrieve relevant cybersecurity knowledge from RAG
            try:
                most_relevant, retrieved_context = retrieve_context(prompt)
            except Exception as e:
                # If retrieval fails, provide fallback content
                most_relevant = "Unable to retrieve context due to an error. Proceeding with general knowledge."
                retrieved_context = []
                st.warning(f"Retrieval error: {str(e)[:100]}")

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
            if retrieved_context:
                with st.expander("🔍 **All Retrieved Cybersecurity Context**", expanded=False):
                    st.info("\n\n".join(retrieved_context))

            with message_container.chat_message("assistant", avatar="🤖"):
                model_error = False
                try:
                    with st.spinner("Model working..."):
                        # Try with direct ollama method
                        try:
                            # Create a placeholder for the streaming response
                            response_placeholder = st.empty()
                            response_text = ""
                            
                            stream_response = ollama.chat(
                                model=st.session_state.selected_model,
                                messages=[
                                    {
                                        "role": "system",
                                        "content": f"Retrieved Knowledge: {most_relevant}"
                                    },
                                    {"role": "user", "content": prompt}
                                ],
                                stream=True
                            )
                            
                            # Accumulate response chunks and update the placeholder
                            response_chunks = []
                            for chunk in stream_response:
                                if 'message' in chunk and 'content' in chunk['message']:
                                    content = chunk['message']['content']
                                    if content:
                                        response_chunks.append(content)
                                        # Update the placeholder with all accumulated text
                                        response_text = "".join(response_chunks)
                                        response_placeholder.markdown(response_text)
                            
                            # Set the final response
                            response = response_text
                            
                        except Exception as e1:
                            # If direct ollama fails, try with OpenAI client
                            stream = client.chat.completions.create(
                                model=st.session_state.selected_model,
                                messages=[
                                    {
                                        "role": "system",
                                        "content": f"""                                 
                                        **Retrieved Knowledge:** {most_relevant}
                                        """,
                                    },
                                    {"role": "user", "content": prompt},
                                ],
                                stream=True,
                            )
                            # Stream response and store it
                            response = st.write_stream(stream)
                        
                except Exception as e:
                    # If all methods fail, show an error and use a fallback message
                    st.error(f"Model error: {str(e)[:100]}...")
                    response = "I'm sorry, I encountered an error generating a response. Please try again or try with a different model."
                    model_error = True

            # Add assistant response to page-specific chat history
            st.session_state[messages_key].append({"role": "assistant", "content": response})
            
            # Save the updated messages to the current chat session
            if ('chat_sessions' in st.session_state and 
                'current_chat_id' in st.session_state):
                current_chat_id = st.session_state.current_chat_id
                for chat in st.session_state.chat_sessions:
                    if chat['id'] == current_chat_id:
                        # Update messages
                        chat['messages'] = list(st.session_state[messages_key])
                        
                        # Update chat title automatically if needed
                        if chat['title'] == "New Chat" and not model_error:
                            content = prompt.strip()
                            if len(content) <= 25:
                                chat['title'] = content
                            else:
                                chat['title'] = content[:22] + "..."
                        break

        except Exception as e:
            st.error(f"Error: {str(e)[:100]}", icon="⛔️")            

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {str(e)[:100]}")
        st.warning("Please try refreshing the page or restarting the application.")