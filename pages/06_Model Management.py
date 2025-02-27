import streamlit as st
import ollama
from time import sleep
from utilities.template import setup_page, mark_task_complete, show_task_completion_status

# Use the template setup function for consistent styling and sidebar
setup_page(
    page_title="Model Management",
    icon_emoji="🤖",
    skip_header=True
)

def main():
    role_suffix = f" (Role: {st.session_state.selected_role})" if 'selected_role' in st.session_state else ""
    st.subheader(f"Task 4: Model Management{role_suffix}", divider="red", anchor=False)

    # Show task completion status at the top
    show_task_completion_status(4)
    
    st.markdown("""
    As a security professional, understanding AI model management is crucial for deploying 
    secure AI solutions. This task will teach you the basics of model management using Ollama.
    """)

    # Check if Ollama service is running
    ollama_status = "Running"
    try:
        models_info = ollama.list()
        # Check if models key exists and initialize to empty list if not
        if "models" not in models_info:
            models_info["models"] = []
    except Exception as e:
        ollama_status = f"Not Running (Error: {str(e)})"
        models_info = {"models": []}
        st.error(f"⚠️ Ollama service is not running. Please start the Ollama service first.", icon="🚫")
        st.info("If you haven't installed Ollama yet, visit [Ollama's website](https://ollama.com/) to download and install it.")

    st.info(f"**Ollama Status**: {ollama_status}")

    st.subheader("Download Models", anchor=False)
    model_name = st.text_input(
        "Enter the name of the model to download ↓", placeholder="mistral"
    )
    
    download_button = st.button(f"📥 :green[**Download**] :red[{model_name}]")
    if download_button:
        if ollama_status != "Running":
            st.error("Cannot download models when Ollama is not running.", icon="🚫")
        elif model_name:
            try:
                ollama.pull(model_name)
                st.success(f"Downloaded model: {model_name}", icon="🎉")
                
                # Mark task as complete
                mark_task_complete(4)
                
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
    create_button = st.button(f"🆕 Create Model {model_name}")
    if create_button:
        if ollama_status != "Running":
            st.error("Cannot create models when Ollama is not running.", icon="🚫")
        elif model_name and modelfile:
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
    
    # Safely get available models
    available_models = []
    if "models" in models_info and models_info["models"]:
        available_models = [m.get("name", "") for m in models_info["models"] if "name" in m]

    if available_models:
        selected_models = st.multiselect("Select models to delete", available_models)
        delete_button = st.button("🗑️ :red[**Delete Selected Model(s)**]")
        if delete_button:
            if ollama_status != "Running":
                st.error("Cannot delete models when Ollama is not running.", icon="🚫")
            else:
                for model in selected_models:
                    try:
                        ollama.delete(model)
                        st.success(f"Deleted model: {model}", icon="🎉")
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
        st.info("No models available for deletion. Download a model first.", icon="🦗")


if __name__ == "__main__":
    main()
