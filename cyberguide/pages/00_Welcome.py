import streamlit as st
from utilities.icon import page_icon
from utilities.template import setup_page
import ollama

def extract_model_names(models_info):
    """Safe model name extraction"""
    if not models_info or not hasattr(models_info, "models"):
        return ()
    return tuple(model.model for model in models_info.models)

def main():
    # Use setup_page instead of st.set_page_config
    setup_page(
        page_title="Welcome to CyberGuide",
        icon_emoji="🛡️",
        subtitle="Your Interactive Cybersecurity Training Tool"
    )
    
    st.markdown("""
    CyberGuide helps you develop essential security skills through interactive scenarios tailored to your role.
    Learn to identify and respond to common security threats in a safe, guided environment.
    """)
    
    # Role selection
    st.subheader("1️⃣ Select Your Role", anchor=False)
    
    # Predefined roles with descriptions
    ROLES = {
        "Accountant": "Financial management and reporting responsibilities",
        "HR Manager": "Employee relations and policy enforcement",
        "IT Support": "System maintenance and technical troubleshooting",
        "Sales Executive": "Client acquisition and revenue generation",
        "Developer": "Software development and system implementation",
        "Compliance Officer": "Regulatory adherence monitoring"
    }
    
    # Initialize session state
    if 'selected_role' not in st.session_state:
        st.session_state.selected_role = None
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected = st.selectbox(
            "Select Your Role",
            options=list(ROLES.keys()),
            index=0,
            help="Choose your organizational role"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Confirm Role", use_container_width=True):
            st.session_state.selected_role = selected
            st.success(f"Role updated to: {selected}", icon="✅")
    
    # Current role display
    if st.session_state.selected_role:
        st.info(f"Current Role: **{st.session_state.selected_role}**", icon="👤")
    
    st.divider()
    
    # Training Tasks
    st.subheader("2️⃣ Complete Training Tasks", anchor=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Beginner Level")
        
        task1_col, task2_col = st.columns(2)
        with task1_col:
            if st.button("Task 1: Password Creation", use_container_width=True):
                st.switch_page("pages/03_Password Creation.py")
            st.caption("Create and manage secure passwords")
            
        with task2_col:
            if st.button("Task 2: Phishing Awareness", use_container_width=True):
                st.switch_page("pages/05_Phishing.py")
            st.caption("Interactive phishing scenario")
    
    with col2:
        st.markdown("### Advanced Level")
        
        task3_col, empty_col = st.columns(2)
        with task3_col:
            if st.button("Task 3: Social Engineering", use_container_width=True):
                st.switch_page("pages/04_Social Engineering.py")
            st.caption("Social engineering threats")
            
        # Task 4 removed as requested
    
    st.divider()
    
    # Model Information
    st.subheader("3️⃣ Available AI Models", anchor=False)
    
    # Check available models
    try:
        models_info = ollama.list()
        available_models = extract_model_names(models_info)
        
        # Recommended models
        recommended_models = ["deepseek", "llama3", "mistral"]
        installed_recommended = [model for model in recommended_models if any(model in available for available in available_models)]
        missing_recommended = [model for model in recommended_models if not any(model in available for available in available_models)]
    except:
        installed_recommended = []
        missing_recommended = recommended_models
    
    # Show model recommendations
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Recommended Models
        
        - **qwen2.5**: Works well with retrieved infromation. Moderate thinking duration before answering.
        - **llava**: Great for general explanations. Tends to give short and concise answers. Short thinking duration before answering.
        - **Mistral**: Good alternative for the other models mentioned. Moderate thinking duration before answering.
        
        These models must be installed via Ollama before use.
        """)
    
    with col2:
        if installed_recommended:
            st.success("Installed Models:", icon="✅")
            for model in installed_recommended:
                st.markdown(f"- {model}")
        
        if missing_recommended:
            st.warning("Missing Recommended Models:", icon="⚠️")
            for model in missing_recommended:
                st.markdown(f"- {model}")
            
            if st.button("Go to Model Management"):
                st.switch_page("pages/06_Model Management.py")

if __name__ == "__main__":
    main() 