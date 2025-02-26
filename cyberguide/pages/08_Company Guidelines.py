import streamlit as st
import ollama
from openai import OpenAI
from utilities.icon import page_icon
from utilities.template import setup_page

def extract_model_names(models_info):
    """Safe model name extraction like other pages"""
    if not models_info or not hasattr(models_info, "models"):
        return ()
    return tuple(model.model for model in models_info.models)

def main():
    # Use the common setup_page function instead of manual configuration
    setup_page(
        page_title="Company Guidelines",
        icon_emoji="📜",
        subtitle="Review key security policies"
    )
    
    # Initialize client
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
    )
    
    # Model selection like Cyber Security Expert
    models_info = ollama.list()
    available_models = extract_model_names(models_info)
    
    if not available_models:
        st.error("No models available. Please download one first.", icon="⛔️")
        st.stop()
    
    selected_model = st.selectbox(
        "Select AI Model",
        available_models,
        index=0,
        help="Choose which model to use for guidelines analysis"
    )
    
    # 3. Page content
    with st.expander("📁 Upload New Guidelines", expanded=True):
        uploaded_file = st.file_uploader(
            "Choose a text file", 
            type=["txt"],
            help="Upload your company's security guidelines document (TXT format)"
        )
        
        if uploaded_file:
            try:
                guidelines = uploaded_file.getvalue().decode("utf-8")
                st.session_state.guidelines = guidelines
                st.success("File uploaded successfully!", icon="✅")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}", icon="⛔️")
    
    st.divider()
    
    # RAG-enhanced chat interface
    if 'guidelines' in st.session_state:
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "system",
                    "content": f"""ALWAYS use this context to answer questions:
                    ### COMPANY SECURITY GUIDELINES ###
                    {st.session_state.guidelines}
                    
                    Respond following these rules:
                    1. Answer in 1-3 sentences
                    2. Begin with "According to our guidelines..." when possible
                    3. If unsure, say "This isn't covered in our policies"
                    4. Never invent information
                    5. Highlight relevant section numbers if present"""
                }
            ]
        
        st.subheader("Guidelines Chat Assistant", divider="gray", anchor=False)
        
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] != "system":  # Don't show system prompt
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask about company guidelines..."):
            try:
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Display user message
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Generate AI response
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing guidelines..."):
                        response = client.chat.completions.create(
                            model=selected_model,
                            messages=[
                                {"role": "system", "content": f"Current guidelines: {st.session_state.guidelines}"},
                                *st.session_state.messages
                            ],
                            stream=True,
                        )
                    
                    # Stream response
                    response_text = st.write_stream((chunk.choices[0].delta.content or "") for chunk in response)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
            
            except Exception as e:
                st.error(f"Error generating response: {str(e)}", icon="⛔️")
    else:
        st.info("Upload guidelines above to enable the chat assistant", icon="ℹ️")

if __name__ == "__main__":
    main() 