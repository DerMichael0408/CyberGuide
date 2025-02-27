import streamlit as st
from utilities.icon import page_icon
import ollama
from utilities.styling import apply_custom_styling, set_dark_mode
from utilities.template import setup_page

def extract_model_names(models_info):
    """Safe model name extraction"""
    if not models_info or not hasattr(models_info, "models"):
        return ()
    return tuple(model.model for model in models_info.models)

# Enhanced role descriptions with security implications
ROLE_DESCRIPTIONS = {
    "Accountant": {
        "short": "Financial management and reporting responsibilities",
        "detailed": "As an Accountant, you handle sensitive financial data and payment systems. You're a key target for invoice fraud, financial malware, and phishing campaigns targeting financial credentials.",
        "security_focus": "Data confidentiality, secure transactions, phishing awareness"
    },
    "HR Manager": {
        "short": "Employee relations and policy enforcement",
        "detailed": "HR Managers process personal employee information and have access to sensitive systems. You're a target for social engineering attacks seeking employee data or credential access.",
        "security_focus": "Identity protection, secure communication, policy compliance"
    },
    "IT Support": {
        "short": "System maintenance and technical troubleshooting",
        "detailed": "In IT Support, you have elevated access to systems and user accounts. Your credentials are highly valuable to attackers seeking to gain administrative access.",
        "security_focus": "Access controls, patch management, privileged account security"
    },
    "Sales Executive": {
        "short": "Client acquisition and revenue generation",
        "detailed": "Sales Executives handle client information and often access CRM systems while traveling. You may be targeted through fraudulent client communications or public wifi attacks.",
        "security_focus": "Mobile security, client data protection, safe remote work"
    },
    "Developer": {
        "short": "Software development and system implementation",
        "detailed": "Developers have access to source code and test environments. Security vulnerabilities in your code can impact the entire organization, making secure coding practices essential.",
        "security_focus": "Secure coding, dependency management, credential protection"
    },
    "Compliance Officer": {
        "short": "Regulatory adherence monitoring",
        "detailed": "Compliance Officers oversee sensitive regulatory documentation and processes. You're a target for attacks aimed at bypassing compliance controls or accessing regulated information.",
        "security_focus": "Documentation security, regulatory requirements, audit protection"
    }
}

def main():
    # Use the common setup_page function instead of manual configuration
    setup_page(
        page_title="Welcome to CyberGuide",
        icon_emoji="🛡️",
        subtitle="Your Interactive Cybersecurity Training Tool"
    )
    
    st.markdown("""
    CyberGuide helps you develop essential security skills through interactive scenarios tailored to your role.
    Learn to identify and respond to common security threats in a safe, guided environment.
    """)
    
    # Name input (added before role selection)
    st.subheader("👤 Your Information", anchor=False, divider="gray")
    
    # Initialize session state for names
    if 'first_name' not in st.session_state:
        st.session_state.first_name = ""
    if 'last_name' not in st.session_state:
        st.session_state.last_name = ""
    if 'name_submitted' not in st.session_state:
        st.session_state.name_submitted = False
    
    # Display current name if submitted
    if st.session_state.name_submitted:
        with st.container(border=True):
            st.success(f"✅ **Name Submitted:** {st.session_state.first_name} {st.session_state.last_name}")
            
            # Button to change name
            if st.button("Change Name", use_container_width=True, key="change_name_btn", 
                       help="Click to update your name"):
                st.session_state.name_submitted = False
                st.rerun()
    
    # Show name input if not submitted
    else:
        st.info("Please enter your name to begin")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            first_name = st.text_input("First Name", value=st.session_state.first_name, key="first_name_input")
            
        with col2:
            last_name = st.text_input("Last Name", value=st.session_state.last_name, key="last_name_input")
        
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            submit_button_disabled = not (first_name and last_name)
            if st.button("✅ Submit", use_container_width=True, key="submit_name_btn", 
                       disabled=submit_button_disabled,
                       help="Click to confirm your name"):
                if first_name and last_name:
                    st.session_state.first_name = first_name
                    st.session_state.last_name = last_name
                    st.session_state.name_submitted = True
                    st.success(f"Name set to: {first_name} {last_name}")
                    st.rerun()
                else:
                    st.error("Please enter both first and last name")
    
    # Role selection (moved from being a task to an initial setup)
    st.subheader("👤 Select Your Role", anchor=False, divider="gray")
    
    # Role selection should only be enabled if name is submitted
    role_section_disabled = not st.session_state.name_submitted
    
    if role_section_disabled:
        st.warning("Please enter your name above before selecting a role")
    
    # Initialize session state
    if 'selected_role' not in st.session_state:
        st.session_state.selected_role = None

    # Display current role if selected
    if st.session_state.selected_role:
        with st.container(border=True):
            role = st.session_state.selected_role
            st.success(f"✅ **Role Selected:** You've selected the role of {role}")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"### Your Role: {role}")
                st.markdown(f"**Security Focus:**  \n{ROLE_DESCRIPTIONS[role]['security_focus']}")
                
                # Button to change role
                if st.button("Change Role", use_container_width=True, key="change_role_btn", 
                           help="Click to select a different role"):
                    st.session_state.selected_role = None
                    st.rerun()
            
            with col2:
                st.markdown(f"### Role Security Profile")
                st.markdown(ROLE_DESCRIPTIONS[role]['detailed'])

    # Show role selection if no role is selected and name is submitted
    elif st.session_state.name_submitted:
        st.info("Select your organizational role to receive tailored security guidance")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            selected = st.selectbox(
                "Select Your Role",
                options=list(ROLE_DESCRIPTIONS.keys()),
                index=None,
                placeholder="Choose a role...",
                key="role_selector"
            )
            
            if selected:
                st.markdown(f"**Role Description:**  \n{ROLE_DESCRIPTIONS[selected]['detailed']}")
                st.markdown(f"**Security Focus:**  \n{ROLE_DESCRIPTIONS[selected]['security_focus']}")
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            confirm_button_disabled = selected is None
            if st.button("✅ Confirm Role", use_container_width=True, key="confirm_role_btn", 
                       disabled=confirm_button_disabled,
                       help="Click to confirm your selected role"):
                if selected:
                    st.session_state.selected_role = selected
                    st.success(f"Role set to: {selected}")
                    st.rerun()
                else:
                    st.error("Please select a role first")
    
        # Display all role descriptions in an expander
        with st.expander("View All Role Descriptions", expanded=False):
            for role, details in ROLE_DESCRIPTIONS.items():
                st.markdown(f"### {role}")
                st.markdown(details['detailed'])
                st.markdown(f"**Security Focus:** {details['security_focus']}")
                st.markdown("---")
    
    # Task selection
    st.subheader("Complete the Security Tasks", anchor=False, divider="gray")
    
    tasks_col1, tasks_col2 = st.columns(2)
    
    with tasks_col1:
        st.markdown("""
        #### Task 1: Password Creation
        Create and manage strong, unique passwords
        """)
        if st.button("Start Password Task ➡️", key="password_btn"):
            try:
                st.switch_page("pages/03_Password Creation.py")
            except Exception:
                st.warning("Navigation error. Try clicking the task in the sidebar.")
            
        st.markdown("""
        #### Task 3: Phishing Awareness
        Learn to identify and report suspicious emails
        """)
        if st.button("Start Phishing Awareness ➡️", key="phishing_btn"):
            try:
                st.switch_page("pages/05_Phishing.py")
            except Exception:
                st.warning("Navigation error. Try clicking the task in the sidebar.")
            
    with tasks_col2:
        st.markdown("""
        #### Task 2: Social Engineering
        Learn essential security procedures and practices
        """)
        if st.button("Start Social Engineering ➡️", key="security_btn"):
            try:
                st.switch_page("pages/04_Social Engineering.py")
            except Exception:
                st.warning("Navigation error. Try clicking the task in the sidebar.")
        
    # Add task completion tracker
    st.markdown("<hr style='margin-top: 1.5rem; margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
    
    # Display task completion info in a more prominent container
    with st.container(border=True):
        completed_count = sum([
            st.session_state.get('task1_completed', False),
            st.session_state.get('task2_completed', False),
            st.session_state.get('task3_completed', False)
        ])
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Tasks Completed", f"{completed_count}/3")
        
        with col2:
            # Progress bar
            progress = completed_count / 3
            st.progress(progress, text=f"Training progress: {int(progress * 100)}%")
            
            if completed_count == 3:
                st.success("🎉 Congratulations! You've completed all security tasks!")
            elif completed_count > 0:
                st.info(f"Keep going! You've completed {completed_count} out of 3 tasks.")
            else:
                st.warning("You haven't completed any tasks yet. Start with Task 1 above.")
    
    # Resources section
    st.subheader("Additional Resources", anchor=False, divider="gray")
    
    resources_col1, resources_col2, resources_col3 = st.columns(3)
    
    with resources_col1:
        st.markdown("#### Dashboard")
        st.markdown("Track your security training progress")
        if st.button("View Dashboard", key="dashboard_btn"):
            try:
                st.switch_page("pages/07_Your Dashboard.py")
            except Exception:
                st.warning("Navigation error. Try clicking Dashboard in the sidebar.")
            
    with resources_col2:
        st.markdown("#### Company Guidelines")
        st.markdown("Review key security policies")
        if st.button("View Guidelines", key="guidelines_btn"):
            try:
                st.switch_page("pages/08_Company Guidelines.py")
            except Exception:
                st.warning("Navigation error. Try clicking Guidelines in the sidebar.")
            
    with resources_col3:
        st.markdown("#### AI Security Assistant")
        st.markdown("Get personalized security advice")
        if st.button("Chat with CyberGuide", key="chat_btn"):
            try:
                st.switch_page("pages/01_CyberGuide Expert.py")
            except Exception:
                st.warning("Navigation error. Try clicking CyberGuide Expert in the sidebar.")

if __name__ == "__main__":
    main() 