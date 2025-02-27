import streamlit as st
import os
from pathlib import Path

def apply_custom_styling():
    """
    Apply custom CSS styling to the Streamlit app
    """
    css = """
    <style>
        /* ULTRA AGGRESSIVE HIDING of ALL default Streamlit navigation elements */
        /* Main header and navigation container */
        header[data-testid="stHeader"],
        header.st-emotion-cache-18ni7ap.ezrtsby2,
        div.st-emotion-cache-z5fcl4.ezrtsby0,
        header.css-18ni7ap.ezrtsby2,
        div.css-z5fcl4.ezrtsby0,
        [data-testid="stHeader"],
        [data-testid="baseButton-headerNoPadding"],
        [data-baseweb="popover"],
        header.css-*,
        header.st-emotion-cache-*,
        header {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0 !important;
            width: 0 !important;
            position: absolute !important;
            z-index: -1 !important;
            pointer-events: none !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            clip: rect(0, 0, 0, 0) !important;
        }
        
        /* Hamburger menu and collapsible controls */
        button[kind="header"],
        [data-testid="collapsedControl"],
        [data-testid="stDecoration"],
        .main-menu-button,
        .st-emotion-cache-19rxjzo,
        .st-emotion-cache-1erivf3,
        [data-testid="stToolbar"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0 !important;
            width: 0 !important;
            position: absolute !important;
            pointer-events: none !important;
            z-index: -1 !important;
        }
        
        /* View fullscreen and other controls */
        .viewerBadge_container,
        .stDeployButton,
        .stToolbar,
        [data-testid="stAppViewBlockContainer"] button {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
        }
        
        /* Main styling */
        .main .block-container {
            padding-top: 2rem;
            padding-left: 2rem;
            margin-left: 0;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #f0f2f6;
            padding-top: 1rem;
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 0rem;
        }
        
        /* Sidebar expander styling */
        [data-testid="stExpander"] {
            border: none;
            border-radius: 10px;
            margin-bottom: 0.5rem;
        }
        
        [data-testid="stExpander"] > div:first-child {
            border-radius: 10px;
            background-color: rgba(49, 51, 63, 0.1);
        }
        
        /* Task items highlighting */
        .task-item {
            border-left: 3px solid #f63366;
            padding-left: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        /* Dark mode toggle */
        .dark-mode-toggle {
            margin-top: 1rem;
            margin-bottom: 1rem;
            padding: 0.5rem;
            border-radius: 10px;
            background-color: rgba(49, 51, 63, 0.1);
        }
        
        /* Better styled theme buttons */
        .theme-button {
            padding: 8px 16px;
            border-radius: 5px;
            margin: 4px;
            text-align: center;
            cursor: pointer;
            display: inline-block;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .light-button {
            background-color: #f0f2f6;
            color: #262730;
            border: 1px solid #d2d2d2;
        }
        
        .dark-button {
            background-color: #262730;
            color: #ffffff;
            border: 1px solid #444;
        }
        
        .active-theme {
            box-shadow: 0 0 0 2px #f63366;
        }
        
        /* Chat history styling */
        .chat-session {
            padding: 0.5rem;
            margin-bottom: 0.5rem;
            border-radius: 10px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .chat-session:hover {
            background-color: rgba(49, 51, 63, 0.1);
        }
        
        .active-chat {
            background-color: rgba(246, 51, 102, 0.1);
            border-left: 3px solid #f63366;
        }
        
        /* Task completion indicators */
        .completed-task {
            color: #00cc66;
        }
        
        .pending-task {
            color: #f63366;
        }
        
        /* Utility classes */
        .center-align {
            text-align: center;
        }
        
        .bold-text {
            font-weight: bold;
        }
        
        .small-text {
            font-size: 0.8rem;
        }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

def set_dark_mode():
    """
    Apply dark mode styling
    """
    dark_mode_css = """
    <style>
        /* Dark Mode Overrides - Basic Version */
        [data-testid="stSidebar"] {
            background-color: #262730 !important;
            color: #ffffff !important;
        }
        
        [data-testid="stExpander"] > div:first-child {
            background-color: rgba(255, 255, 255, 0.1) !important;
        }
        
        .stApp {
            background-color: #0e1117 !important;
            color: #ffffff !important;
        }
        
        button[kind="secondary"] {
            background-color: #3b3f4b !important;
            color: #ffffff !important;
            border: 1px solid rgba(250, 250, 250, 0.2) !important;
        }
        
        button[kind="secondary"]:hover {
            background-color: #4e5361 !important;
            border: 1px solid rgba(250, 250, 250, 0.3) !important;
        }
        
        [data-testid="stMarkdownContainer"] p,
        .stMarkdown p,
        button p,
        div p {
            color: #ffffff !important;
        }
        
        .sidebar-link {
            color: #ffffff !important;
            text-decoration: none !important;
        }
        
        [data-testid="stSidebar"] a {
            color: #ffffff !important;
        }
        
        [data-testid="stSidebar"] .stMarkdown p {
            color: #ffffff !important;
        }
        
        [data-testid="stSidebar"] .stMarkdown h3 {
            color: #ffffff !important;
        }
        
        .dark-mode-toggle {
            background-color: rgba(255, 255, 255, 0.05) !important;
        }
        
        .active-chat {
            background-color: rgba(255, 75, 107, 0.2) !important;
            border-left: 3px solid #ff4b6b !important;
        }
        
        button[data-testid="stChatInputSubmitButton"] {
            background-color: #3b82f6 !important;
            fill: white !important;
        }
        
        button[data-testid="stChatInputSubmitButton"] svg {
            fill: white !important;
        }
    </style>
    """
    
    st.markdown(dark_mode_css, unsafe_allow_html=True)

def create_sidebar_header():
    """
    Create the header section of the sidebar with proper navigation
    """
    with st.sidebar:
        # Add welcome message if user has submitted their name and role
        if ('name_submitted' in st.session_state and st.session_state.name_submitted and 
            'selected_role' in st.session_state and st.session_state.selected_role):
            
            # Get user info
            first_name = st.session_state.first_name
            role = st.session_state.selected_role
            
            # Check current theme
            is_dark_mode = st.session_state.get('theme_mode', 'Light') == 'Dark'
            
            # Create a subtle welcome message with dark mode support
            bg_color = "rgba(20, 20, 25, 0.2)" if is_dark_mode else "rgba(49, 51, 63, 0.05)"
            text_color = "#e0e0e0" if is_dark_mode else "inherit"
            highlight_color = "#80b0ff" if is_dark_mode else "#4169E1"
            
            st.markdown(
                f"""
                <div style="padding: 10px; border-radius: 5px; background-color: {bg_color}; 
                margin-bottom: 15px; font-size: 0.9rem; color: {text_color};">
                    Welcome {first_name}, you are assigned to <span style="color: {highlight_color};">{role}</span>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        st.markdown("### CyberGuide")
        st.markdown("Your interactive security training tool")
        
        # Add Welcome and CyberGuide Expert at the top
        st.markdown("#### Main Pages")
        
        # Welcome button with proper navigation
        if st.button("👋 Welcome Page", key="sidebar_welcome_btn", use_container_width=True,
                    help="Return to the welcome page"):
            try:
                st.switch_page("pages/00_Welcome.py")
            except Exception as e:
                st.error(f"Navigation error: {e}")
                try:
                    # Alternative path format
                    st.switch_page("00_Welcome.py")
                except Exception:
                    st.warning("Try navigating to Welcome page manually")
        
        # CyberGuide Expert button with proper navigation    
        if st.button("💬 CyberGuide Expert", key="sidebar_expert_btn", use_container_width=True,
                    help="Chat with the CyberGuide AI"):
            try:
                st.switch_page("01_CyberGuide Expert.py") 
            except Exception as e:
                st.error(f"Navigation error: {e}")
                try:
                    # Alternative path format
                    st.switch_page("pages/01_CyberGuide Expert.py")
                except Exception:
                    st.warning("Try navigating to CyberGuide Expert page manually")
        
        st.markdown("---")

def create_sidebar_tasks():
    """
    Create the tasks section in the sidebar with proper navigation
    """
    with st.sidebar:
        st.markdown("### Training Tasks")
        
        # Display task completion header with count
        completed_count = sum([
            st.session_state.get('task1_completed', False),
            st.session_state.get('task2_completed', False),
            st.session_state.get('task3_completed', False)
        ])
        
        st.markdown(f"**{completed_count}/3 Tasks Completed**")
        
        # Create a container with border to visually group tasks
        with st.container(border=True):
            # Task 1: Password Creation
            task1_completed = st.session_state.get('task1_completed', False)
            icon1 = "✅" if task1_completed else "⏳"
            label1 = f"{icon1} Task 1: Password Creation"
            if st.button(label1, key="sidebar_password_btn", use_container_width=True,
                      help="Create and manage strong passwords"):
                try:
                    st.switch_page("pages/03_Password Creation.py")
                except Exception as e:
                    st.error(f"Navigation error: {e}")
                    st.warning("Alternative path: Try clicking on pages/03_Password Creation")
            
            # Task 2: Social Engineering (moved from Task 3)
            task3_completed = st.session_state.get('task3_completed', False)
            icon2 = "✅" if task3_completed else "⏳"
            label2 = f"{icon2} Task 2: Social Engineering"
            if st.button(label2, key="sidebar_security_btn", use_container_width=True,
                      help="Learn essential security protocols"):
                try:
                    st.switch_page("pages/04_Social Engineering.py")
                except Exception as e:
                    st.error(f"Navigation error: {e}")
                    st.warning("Alternative path: Try clicking on pages/04_Social Engineering")
            
            # Task 3: Phishing Awareness (moved from Task 2)
            task2_completed = st.session_state.get('task2_completed', False)
            icon3 = "✅" if task2_completed else "⏳"
            label3 = f"{icon3} Task 3: Phishing Awareness"
            if st.button(label3, key="sidebar_phishing_awareness_btn", use_container_width=True, 
                      help="Learn to identify and report suspicious emails"):
                try:
                    st.switch_page("pages/05_Phishing.py")
                except Exception as e:
                    st.error(f"Navigation error: {e}")
                    st.warning("Alternative path: Try clicking on pages/05_Phishing")
        
        # Add a note explaining the tasks
        st.caption("Complete all 3 tasks for your security certification")
        st.markdown("---")

def create_sidebar_resources():
    """
    Create the resources section in the sidebar with proper navigation
    """
    with st.sidebar:
        with st.expander("Resources"):
            # Dashboard navigation
            if st.button("Dashboard", key="sidebar_dashboard_btn", use_container_width=True,
                        help="View your security dashboard"):
                try:
                    st.switch_page("pages/07_Your Dashboard.py")
                except Exception as e:
                    st.error(f"Navigation error: {e}")
                    st.warning("Try navigating to Dashboard page manually")
                
            # Guidelines navigation
            if st.button("Company Guidelines", key="sidebar_guidelines_btn", use_container_width=True,
                        help="Read company security policies"):
                try:
                    st.switch_page("pages/08_Company Guidelines.py")
                except Exception as e:
                    st.error(f"Navigation error: {e}")
                    st.warning("Try navigating to Guidelines page manually")
                
            # Model Management navigation
            if st.button("Model Management", key="sidebar_model_btn", use_container_width=True,
                        help="Manage AI models"):
                try:
                    st.switch_page("pages/06_Model Management.py")
                except Exception as e:
                    st.error(f"Navigation error: {e}")
                    st.warning("Try navigating to Model Management page manually")
                
            # Multi-Modal navigation
            if st.button("Multi-Modal", key="sidebar_multimodal_btn", use_container_width=True,
                        help="Image and text analysis"):
                try:
                    st.switch_page("pages/11_Multi-Modal.py")
                except Exception as e:
                    st.error(f"Navigation error: {e}")
                    st.warning("Try navigating to Multi-Modal page manually")

def create_theme_toggle():
    """
    Create a sleek dark/light mode toggle switch in the sidebar
    """
    with st.sidebar:
        # Add divider before theme section
        st.divider()
        
        # Initialize the theme in session state if not already set
        if 'theme_mode' not in st.session_state:
            st.session_state.theme_mode = 'Light'
        
        # Use a container with border for the theme toggle
        with st.container(border=True):
            st.markdown("#### Display Settings")
            
            # Add custom styling for the toggle switch
            st.markdown("""
            <style>
            /* Toggle switch container */
            .toggle-switch-container {
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 10px 0;
            }
            
            /* The switch - the box around the slider */
            .switch {
                position: relative;
                display: inline-block;
                width: 60px;
                height: 30px;
                margin: 0 10px;
            }
            
            /* Hide default HTML checkbox */
            .switch input {
                opacity: 0;
                width: 0;
                height: 0;
            }
            
            /* The slider */
            .slider {
                position: absolute;
                cursor: pointer;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: #F3F4F6;
                transition: .4s;
                border-radius: 34px;
                border: 1px solid #E5E7EB;
            }
            
            .slider:before {
                position: absolute;
                content: "☀️";
                display: flex;
                align-items: center;
                justify-content: center;
                height: 24px;
                width: 24px;
                left: 3px;
                bottom: 2px;
                background-color: white;
                transition: .4s;
                border-radius: 50%;
                font-size: 16px;
            }
            
            .dark .slider {
                background-color: #1F2937;
                border: 1px solid #374151;
            }
            
            .dark .slider:before {
                content: "🌙";
                background-color: #111827;
                transform: translateX(30px);
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Direct theme toggle without buttons
            current_theme = st.session_state.theme_mode
            use_dark_mode = current_theme == 'Dark'
            
            # Create a form for the toggle so we can update without buttons
            with st.form(key="theme_form", clear_on_submit=False):
                # Create a radio button that looks like our toggle
                # Use HTML/CSS to style it like our toggle
                is_dark = "dark" if use_dark_mode else ""
                html_toggle = f"""
                <div class="toggle-switch-container {is_dark}">
                    <label class="switch">
                        <input type="checkbox" name="theme_toggle" {"checked" if use_dark_mode else ""}>
                        <span class="slider"></span>
                    </label>
                </div>
                """
                st.markdown(html_toggle, unsafe_allow_html=True)
                
                # Use a small, hidden submit button
                st.markdown("""
                <style>
                [data-testid="baseButton-formSubmitter"] {
                    visibility: hidden !important;
                    height: 0 !important;
                    position: absolute !important;
                    top: -100px !important;
                }
                </style>
                """, unsafe_allow_html=True)
                submitted = st.form_submit_button("Update Theme", type="secondary")
            
            # Inject JavaScript to auto-submit the form when toggle is clicked
            st.markdown("""
            <script>
                // Function to set up toggle event listener
                function setupToggle() {
                    // Find all toggle inputs
                    const toggles = document.querySelectorAll('input[name="theme_toggle"]');
                    
                    // Add click event handler to each toggle
                    toggles.forEach(toggle => {
                        toggle.addEventListener('change', function() {
                            // Find and click the closest form submit button
                            const formContainer = this.closest('form');
                            if (formContainer) {
                                const submitBtn = formContainer.querySelector('button[data-testid="baseButton-formSubmitter"]');
                                if (submitBtn) {
                                    submitBtn.click();
                                }
                            }
                        });
                    });
                }
                
                // Call setup function
                setupToggle();
                
                // Watch for DOM changes to handle dynamically added elements
                const observer = new MutationObserver(mutations => {
                    setupToggle();
                });
                
                // Start observing
                observer.observe(document.body, { childList: true, subtree: true });
            </script>
            """, unsafe_allow_html=True)
            
            # Handle the theme change when form is submitted
            if submitted:
                # Toggle the theme
                if current_theme == 'Light':
                    st.session_state.theme_mode = 'Dark'
                    # DO NOT apply dark mode here - it should only be applied in setup_page
                else:
                    st.session_state.theme_mode = 'Light'
                
                # Force rerun to apply changes
                st.rerun()

def create_chat_history():
    """
    Create a chat history section in the sidebar
    """
    with st.sidebar:
        with st.expander("Chat History", expanded=True):
            # Initialize chat sessions if they don't exist
            if 'chat_sessions' not in st.session_state:
                st.session_state.chat_sessions = []
                st.session_state.current_chat_id = None
            
            # New chat button
            if st.button("+ New Chat"):
                new_chat_id = len(st.session_state.chat_sessions)
                st.session_state.chat_sessions.append({
                    'id': new_chat_id,
                    'title': f"Chat {new_chat_id + 1}",
                    'messages': []
                })
                st.session_state.current_chat_id = new_chat_id
                st.rerun()
            
            # Display existing chats
            for chat in st.session_state.chat_sessions:
                chat_class = "active-chat" if st.session_state.current_chat_id == chat['id'] else "chat-session"
                if st.markdown(f'<div class="{chat_class}">{chat["title"]}</div>', unsafe_allow_html=True):
                    st.session_state.current_chat_id = chat['id']
                    st.rerun()

def initialize_sidebar():
    """
    Initialize the complete sidebar structure
    """
    create_sidebar_header()
    create_sidebar_tasks()
    create_chat_history()
    create_sidebar_resources()
    create_theme_toggle()
