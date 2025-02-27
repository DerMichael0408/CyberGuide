import ollama
import streamlit as st
import os
from openai import OpenAI
from utilities.icon import page_icon
from utilities.styling import apply_custom_styling, set_dark_mode
from utilities.template import setup_page
from utilities.rag import retrieve_context

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
    # Use the common setup_page function instead of manual configuration
    setup_page(
        page_title="CyberGuide Expert",
        icon_emoji="💬",
        subtitle="Your Cyber Security Expert"
    )
    
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
    
    # Check for query parameters to handle chat navigation
    if 'chat' in st.query_params:
        try:
            chat_id = int(st.query_params['chat'])
            st.session_state.current_chat_id = chat_id
        except ValueError:
            pass
            
    # If current_chat_id is set, use that chat's messages
    if st.session_state.get('current_chat_id') is not None:
        chat_id = st.session_state.current_chat_id
        chat = next((c for c in st.session_state.chat_sessions if c['id'] == chat_id), None)
        
        # Display messages from the current chat
        if chat and 'messages' in chat:
            for message in chat['messages']:
                avatar = "🤖" if message["role"] == "assistant" else "😎"
                with message_container.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])
        else:
            # No messages in this chat yet
            pass
    else:
        # Display messages from the page-specific chat history
        for message in st.session_state[messages_key]:
            avatar = "🤖" if message["role"] == "assistant" else "😎"
            with message_container.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])


    if prompt := st.chat_input("Enter a prompt here..."):
        try:
            # Don't duplicate messages - remove redundant append
            if st.session_state.get('current_chat_id') is not None:
                chat_id = st.session_state.current_chat_id
                chat = next((c for c in st.session_state.chat_sessions if c['id'] == chat_id), None)
                
                if chat:
                    # Add to chat session's messages
                    chat['messages'].append({"role": "user", "content": prompt})
                    
                    # Update chat title if this is the first message
                    if len(chat['messages']) == 1:
                        # Use first few words for the chat title
                        words = prompt.split()
                        title = " ".join(words[:3])
                        if len(words) > 3:
                            title += "..."
                        chat['title'] = title
            else:
                # Add to page-specific chat history if not using chat sessions
                st.session_state[messages_key].append({"role": "user", "content": prompt})
            
            # Display the message
            message_container.chat_message("user", avatar="😎").markdown(prompt)

            # 🔍 Retrieve relevant cybersecurity knowledge from RAG
            most_relevant, retrieved_context = retrieve_context(prompt)

            # 🌟 Show the most relevant retrieved chunk prominently
            with st.container():
                st.markdown("### 📌 Most Relevant Retrieved Information")
                st.info(most_relevant)

            # 🔎 Debugging: Show full retrieved context in an expander
            with st.expander("🔍 **All Retrieved Cybersecurity Context**", expanded=False):
                st.info("\n\n".join(retrieved_context))

            with message_container.chat_message("assistant", avatar="🤖"):
                with st.spinner("model working..."):
                    # Determine which messages to use based on whether we're in a chat session
                    if st.session_state.get('current_chat_id') is not None:
                        chat_id = st.session_state.current_chat_id
                        chat = next((c for c in st.session_state.chat_sessions if c['id'] == chat_id), None)
                        messages_to_use = chat['messages'] if chat else st.session_state[messages_key]
                    else:
                        messages_to_use = st.session_state[messages_key]
                    
                    stream = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {
                                "role": "system",
                                "content": f"""                                 
                                🔹 **Retrieved Knowledge:** {most_relevant}
                                """,
                            },
                            {"role": "user", "content": prompt},  # ✅ User query is separate!
                        ],
                        stream=True,
                    )

                # Stream response and store it
                response = st.write_stream(stream)

            # Add the assistant response
            if st.session_state.get('current_chat_id') is not None:
                chat_id = st.session_state.current_chat_id
                chat = next((c for c in st.session_state.chat_sessions if c['id'] == chat_id), None)
                
                if chat:
                    # Add to chat session's messages
                    chat['messages'].append({"role": "assistant", "content": response})
            else:
                # Add to page-specific chat history if not using chat sessions
                st.session_state[messages_key].append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(e, icon="⛔️")            

    # if prompt := st.chat_input("Enter a prompt here..."):
    #     try:
    #         # Add user message to page-specific chat history
    #         st.session_state[messages_key].append(
    #             {"role": "user", "content": prompt})

    #         message_container.chat_message("user", avatar="😎").markdown(prompt)

    #         with message_container.chat_message("assistant", avatar="🤖"):
    #             with st.spinner("model working..."):
    #                 stream = client.chat.completions.create(
    #                     model=selected_model,
    #                     messages=[
    #                         {"role": m["role"], "content": m["content"]}
    #                         for m in st.session_state[messages_key]  # Use page-specific messages
    #                     ],
    #                     stream=True,
    #                 )
    #             # stream response
    #             response = st.write_stream(stream)
            
    #         # Add assistant response to page-specific chat history
    #         st.session_state[messages_key].append(
    #             {"role": "assistant", "content": response})

    #     except Exception as e:
    #         st.error(e, icon="⛔️")


if __name__ == "__main__":
    main()