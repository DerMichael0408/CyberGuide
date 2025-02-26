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

def get_current_page():
    current_file = os.path.basename(__file__)
    page_name = os.path.splitext(current_file)[0]
    return page_name

current_page = get_current_page()

def get_page_key(base_key):
    return f"{current_page}_{base_key}"

messages_key = get_page_key("messages")

def extract_model_names(models_info) -> tuple:
    if not models_info or not hasattr(models_info, "models"):
        return ()
    return tuple(model.model for model in models_info.models)

def main():
    page_icon("💬")
    st.header("CyberGuide")
    st.subheader("Your Cyber Security Expert", divider="red", anchor=False)
    
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # API key required but not used with local models
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

    if messages_key not in st.session_state:
        st.session_state[messages_key] = []

    for message in st.session_state[messages_key]:
        avatar = "🤖" if message["role"] == "assistant" else "😎"
        with message_container.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter a prompt here..."):
        try:
            st.session_state[messages_key].append({"role": "user", "content": prompt})
            message_container.chat_message("user", avatar="😎").markdown(prompt)

            # 🔍 Retrieve relevant background context from the cybersecurity scenarios database.
            retrieved_context = retrieve_context(prompt)

            # Optionally display the retrieved context for debugging or transparency.
            with st.expander("🔍 **Retrieved Cybersecurity Context**", expanded=False):
                st.info(retrieved_context)

            # Build a system prompt that instructs the LLM to use the retrieved context as background knowledge
            # but to generate a synthesized, conversational answer rather than simply quoting it.
            system_prompt = (
                "You are CyberGuide, an interactive cybersecurity training assistant. "
                "Your task is to help regular employees understand IT security by guiding them through scenarios "
                "and answering their cybersecurity questions. Use the following background knowledge to inform your response, "
                "but do not simply repeat it verbatim. Instead, synthesize the key points into clear, friendly, and actionable advice. "
                "If the query is scenario-based, walk the user through the necessary steps to solve the scenario. "
                "\n\nBackground Knowledge:\n"
                f"{retrieved_context}"
            )

            with message_container.chat_message("assistant", avatar="🤖"):
                with st.spinner("model working..."):
                    stream = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt},
                        ],
                        stream=True,
                    )
                response = st.write_stream(stream)
            st.session_state[messages_key].append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(e, icon="⛔️")

if __name__ == "__main__":
    main()
