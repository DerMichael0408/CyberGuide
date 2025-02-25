import streamlit as st
import ollama
import re
import time

# Set page config for wider layout and custom title/icon
st.set_page_config(
    page_title="Password Creation Training",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    page_icon("3️⃣")
    st.subheader("Task 3: USB stick", divider="red", anchor=False)

    st.subheader("Download Models", anchor=False)
    model_name = st.text_input(
        "Enter the name of the model to download ↓", placeholder="mistral"
    )
    if st.button(f"📥 :green[**Download**] :red[{model_name}]"):
        if model_name:
            try:
                ollama.pull(model_name)
                st.success(f"Downloaded model: {model_name}", icon="🎉")
                st.balloons()
                sleep(1)
                st.rerun()
            except Exception as e:
                st.error(
                    f"""Failed to download model: {
                    model_name}. Error: {str(e)}""",
                    icon="😳",
                )
        else:
            st.warning("Please enter a model name.", icon="⚠️")

    st.divider()

    st.subheader("Create model", anchor=False)
    modelfile = st.text_area(
        "Enter the modelfile",
        height=100,
        placeholder="""FROM mistral
SYSTEM You are mario from super mario bros.""",
    )
    model_name = st.text_input(
        "Enter the name of the model to create", placeholder="mario"
    )
    if st.button(f"🆕 Create Model {model_name}"):
        if model_name and modelfile:
            try:
                ollama.create(model=model_name, modelfile=modelfile)
                st.success(f"Created model: {model_name}", icon="✅")
                st.balloons()
                sleep(1)
                st.rerun()
            except Exception as e:
                st.error(
                    f"""Failed to create model: {
                         model_name}. Error: {str(e)}""",
                    icon="😳",
                )
        else:
            st.warning("Please enter a **model name** and **modelfile**", icon="⚠️")

    st.divider()

    st.subheader("Delete Models", anchor=False)
    models_info = ollama.list()
    available_models = [m["name"] for m in models_info["models"]]

    if available_models:
        selected_models = st.multiselect("Select models to delete", available_models)
        if st.button("🗑️ :red[**Delete Selected Model(s)**]"):
            for model in selected_models:
                try:
                    ollama.delete(model)
                    st.success(f"Deleted model: {model}", icon="🎉")
                    st.balloons()
                    sleep(1)
                    st.rerun()
            else:
                system_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                
                context_message = f"The user has answered question {st.session_state.question_index}. Give brief feedback and then ask question {st.session_state.question_index + 1}."
                system_messages.append({"role": "user", "content": context_message})
                
                feedback_messages = system_messages + [
                    {"role": "user", "content": f"Question {st.session_state.question_index}: {QUESTIONS[st.session_state.question_index - 1]}"},
                    {"role": "user", "content": f"User's answer: {user_answer}"}
                ]
                
                response = ollama.chat(model="llava:latest", messages=feedback_messages)
                ai_message = response["message"]["content"]
                
                if f"Question {st.session_state.question_index + 1}/5:" not in ai_message:

                    feedback = ai_message.strip()

                    ai_message = f"{feedback}\n\nQuestion {st.session_state.question_index + 1}/5: {QUESTIONS[st.session_state.question_index]}"

                st.session_state.messages.append({"role": "assistant", "content": ai_message})
                
                st.session_state.question_index += 1
                
                st.rerun()

# Reset button (only show in completed state)
if st.session_state.training_complete:
    if st.button("Start New Training"):
        # Reset all session state variables
        st.session_state.messages = []
        st.session_state.question_index = 0
        st.session_state.started = False
        st.session_state.training_complete = False
        st.rerun()