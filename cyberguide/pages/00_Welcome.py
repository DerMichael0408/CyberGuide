import streamlit as st
from utilities.icon import page_icon
from utilities.template import setup_page

def main():
    # Use setup_page instead of st.set_page_config
    setup_page(
        page_title="Welcome to CyberGuide",
        icon_emoji="🛡️",
        subtitle="Your Interactive Cybersecurity Training Tool"
    )
    
    # Custom CSS for enhanced styling
    st.markdown("""
    <style>
        /* General styling improvements */
        .main {
            padding: 2rem 3rem;
        }
        
        /* Section styling */
        .section-header {
            background-color: #f8f9fa;
            border-left: 5px solid #2196F3;
            padding: 12px 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-weight: bold;
            color: #1E3A8A;
        }
        
        /* Card styling */
        .task-card {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid #e2e8f0;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .task-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        }
        
        .task-icon {
            font-size: 24px;
            margin-right: 10px;
            vertical-align: middle;
        }
        
        .task-title {
            font-weight: bold;
            color: #1E3A8A;
            margin-bottom: 5px;
            font-size: 16px;
        }
        
        .task-description {
            color: #6B7280;
            font-size: 14px;
            margin-top: 5px;
        }
        
        /* Model management area */
        .model-management {
            background-color: #f0f9ff;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            border-left: 5px solid #2196F3;
        }
        
        /* Responsive buttons */
        .stButton button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        /* Button hover effects */
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* Progress indicator */
        .progress-indicator {
            display: flex;
            align-items: center;
            margin-top: 10px;
            margin-bottom: 20px;
        }
        
        .progress-step {
            background-color: #e2e8f0;
            color: #64748b;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
        }
        
        .progress-step.active {
            background-color: #3B82F6;
            color: white;
        }
        
        .progress-line {
            flex-grow: 1;
            height: 3px;
            background-color: #e2e8f0;
            margin-right: 15px;
        }
        
        .progress-line.active {
            background-color: #3B82F6;
        }
        
        /* Divider styling */
        hr {
            margin: 30px 0;
            border: none;
            height: 1px;
            background: linear-gradient(to right, rgba(0,0,0,0), rgba(0,0,0,0.1), rgba(0,0,0,0));
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Introduction text
    st.markdown("""
    CyberGuide helps you develop essential security skills through interactive scenarios tailored to your role.
    Learn to identify and respond to common security threats in a safe, guided environment.
    """)
    
    # Progress indicator
    st.markdown("""
    <div class="progress-indicator">
        <div class="progress-step active">1</div>
        <div class="progress-line active"></div>
        <div class="progress-step">2</div>
        <div class="progress-line"></div>
        <div class="progress-step">3</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Role selection
    st.markdown('<div class="section-header">1️⃣ Select Your Role</div>', unsafe_allow_html=True)
    
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
    
    # Role selection area - without the blue box
    col1, col2 = st.columns([3, 1])
    with col1:
        selected = st.selectbox(
            "Select Your Department Role",
            options=list(ROLES.keys()),
            index=0,
            help="Choose your organizational role"
        )
        if selected in ROLES:
            st.caption(f"Role description: {ROLES[selected]}")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Confirm Role", use_container_width=True, type="primary"):
            st.session_state.selected_role = selected
            st.success(f"Role updated to: {selected}", icon="✅")
    
    # Current role display
    if st.session_state.selected_role:
        st.info(f"Current Role: **{st.session_state.selected_role}**", icon="👤")
    
    # Divider
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Training Tasks
    st.markdown('<div class="section-header">2️⃣ Complete Training Tasks</div>', unsafe_allow_html=True)
    
    # Beginner and Advanced columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Beginner Level")
        
        # Password Creation Task
        st.markdown("""
        <div class="task-card">
            <div class="task-title"><span class="task-icon">🔒</span> Password Creation</div>
            <div class="task-description">Learn to create and manage secure passwords following best practices</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Start Password Training", key="pwd_btn", use_container_width=True):
            st.switch_page("pages/03_Password Creation.py")
        
        # Phishing Awareness Task
        st.markdown("""
        <div class="task-card">
            <div class="task-title"><span class="task-icon">🎣</span> Phishing Awareness</div>
            <div class="task-description">Identify and respond to phishing attempts in realistic scenarios</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Start Phishing Training", key="phish_btn", use_container_width=True):
            st.switch_page("pages/05_Phishing.py")
    
    with col2:
        st.markdown("### Advanced Level")
        
        # Social Engineering Task
        st.markdown("""
        <div class="task-card">
            <div class="task-title"><span class="task-icon">🕵️</span> Social Engineering</div>
            <div class="task-description">Recognize manipulation tactics and protect sensitive information</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Start Social Engineering Training", key="social_btn", use_container_width=True):
            st.switch_page("pages/04_Social Engineering.py")
        
        # Your Dashboard
        st.markdown("""
        <div class="task-card">
            <div class="task-title"><span class="task-icon">📊</span> Security Dashboard</div>
            <div class="task-description">View your progress and security assessment results</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("View Your Dashboard", key="dashboard_btn", use_container_width=True):
            st.switch_page("pages/07_Your Dashboard.py")
    
    # Divider
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Model Management
    st.markdown('<div class="section-header">3️⃣ AI Model Management</div>', unsafe_allow_html=True)
    
    # Model management card
    st.markdown("""
    <div class="model-management">
        <h3 style="color: #2196F3; margin-top: 0;">Local LLM Configuration</h3>
        <p>CyberGuide uses powerful local AI models to deliver personalized training experiences without compromising data privacy.</p>
        <p>Visit the Model Management page to:</p>
        <ul>
            <li>Install and configure recommended LLM models</li>
            <li>Manage model settings for optimal performance</li>
            <li>Access guidance on model selection for training scenarios</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🤖 Go to Model Management", use_container_width=True, type="primary"):
            st.switch_page("pages/06_Model Management.py")
    
    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 40px; color: #6B7280; font-size: 14px;">
        CyberGuide Training Platform • Version 1.0 • © 2025
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()