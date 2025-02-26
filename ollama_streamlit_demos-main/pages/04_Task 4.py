import streamlit as st
import ollama
from time import sleep
from utilities.template import setup_page, mark_task_complete, show_task_completion_status
from utilities.icon import page_icon

# Use the common setup_page function instead of manual configuration
setup_page(
    page_title="Security Protocols",
    icon_emoji="🔒",
    skip_header=True
)

def main():
    role_suffix = f" (Role: {st.session_state.selected_role})" if 'selected_role' in st.session_state else ""
    st.subheader(f"Task 3: Security Protocols{role_suffix}", divider="red", anchor=False)

    # Show task completion status 
    show_task_completion_status(3)
    
    st.subheader("Security Model Downloads", anchor=False)
    st.markdown("""
    As part of your security training, you'll need to download security models 
    that can help identify potential threats and vulnerabilities.
    """)
    model_name = st.text_input(
        "Enter the name of the security model to download ↓", placeholder="mistral"
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
                    
                    # Mark task as complete when user successfully deletes a model
                    mark_task_complete(3)
                    
                    st.balloons()
                    sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(
                        f"""Failed to delete model: {
                        model}. Error: {str(e)}""",
                        icon="😳",
                    )
    else:
        st.info("No models available for deletion.", icon="🦗")


if __name__ == "__main__":
    main()
