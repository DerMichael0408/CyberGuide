import streamlit as st
from utilities.icon import page_icon

# Predefined roles with descriptions
ROLES = {
    "Accountant": "Financial management and reporting responsibilities",
    "HR Manager": "Employee relations and policy enforcement",
    "IT Support": "System maintenance and technical troubleshooting",
    "Sales Executive": "Client acquisition and revenue generation",
    "Developer": "Software development and system implementation",
    "Compliance Officer": "Regulatory adherence monitoring"
}

def main():
    st.set_page_config(
        page_title="Role Assignment",
        page_icon="👤",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    page_icon("👤")
    st.header("Role Assignment", divider="red", anchor=False)

    # Initialize session state
    if 'selected_role' not in st.session_state:
        st.session_state.selected_role = None

    # Role selection
    col1, col2 = st.columns([3, 1])
    with col1:
        selected = st.selectbox(
            "Select Your Role",
            options=list(ROLES.keys()),
            index=0,
            help="Choose your primary organizational role"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Confirm Role", use_container_width=True):
            st.session_state.selected_role = selected
            st.success(f"Role updated to: {selected}", icon="✅")

    # Current role display
    if st.session_state.selected_role:
        st.subheader("Current Assignment", divider="gray")
        with st.container(border=True):
            c1, c2 = st.columns([2, 3])
            c1.markdown(f"**Selected Role:** {st.session_state.selected_role}")
            c2.markdown(f"**Typical Responsibilities:** {ROLES[st.session_state.selected_role]}")

    # Role descriptions
    with st.expander("View Role Descriptions", expanded=True):
        for role, desc in ROLES.items():
            st.markdown(f"**{role}**  \n{desc}")

if __name__ == "__main__":
    main() 