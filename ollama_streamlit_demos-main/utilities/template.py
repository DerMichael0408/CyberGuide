import streamlit as st
from utilities.styling import initialize_sidebar, apply_custom_styling, set_dark_mode
from utilities.icon import page_icon

def setup_page(page_title, icon_emoji, subtitle=None, skip_header=False):
    """
    Common page setup function for task pages
    
    Args:
        page_title (str): The title of the page
        icon_emoji (str): The emoji to use as the page icon
        subtitle (str, optional): Subtitle to display under the header. Defaults to None.
        skip_header (bool, optional): If True, don't add the automatic page header. Defaults to False.
    """
    st.set_page_config(
        page_title=page_title,
        page_icon=icon_emoji,
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://www.cyberguide.com/help',
            'Report a bug': 'https://www.cyberguide.com/bug',
            'About': 'CyberGuide - Your interactive security training tool'
        }
    )
    
    # Initialize theme if not set
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = 'Light'
    
    # NUCLEAR APPROACH: Combine all techniques to completely remove Streamlit navigation
    st.markdown("""
    <style>
    /* NUCLEAR APPROACH TO HIDING STREAMLIT UI ELEMENTS */
    
    /* Target ALL header elements, top bar, menu, etc with multiple techniques */
    header, 
    header[data-testid="stHeader"],
    header.css-18ni7ap,
    header.css-18ni7ap.ezrtsby2,
    header.st-emotion-cache-18ni7ap,
    header.st-emotion-cache-18ni7ap.ezrtsby2,
    div.css-14xtw13.e8zbici0,
    div.css-z5fcl4,
    div.css-z5fcl4.ezrtsby0,
    div.st-emotion-cache-z5fcl4,
    div.st-emotion-cache-z5fcl4.ezrtsby0,
    div[data-testid="stDecoration"],
    div[data-testid="stToolbar"],
    div.stToolbar,
    div.st-emotion-cache-1or543r.e1ewe7hr3,
    div.st-emotion-cache-1to1120.e1f1d6gn0,
    button[data-testid="baseButton-headerNoPadding"],
    button[kind="header"],
    section[data-testid="stSidebar"] > div.st-emotion-cache-16idsys.e1nzilvr5,
    [data-testid="collapsedControl"],
    .main-menu-button,
    .st-emotion-cache-19rxjzo,
    .st-emotion-cache-1erivf3,
    .viewerBadge_container,
    .stDeployButton,
    [data-testid^="st"] header
    {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
        width: 0 !important;
        position: absolute !important;
        top: -9999px !important;
        left: -9999px !important;
        z-index: -9999 !important;
        pointer-events: none !important;
        clip: rect(0,0,0,0) !important;
        overflow: hidden !important;
        max-height: 0 !important;
        max-width: 0 !important;
        transform: scale(0) !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Hide EVERY Streamlit native element that might contain navigation or controls */
    *[data-testid*="stHeader"],
    *[class*="st-emotion"][role="banner"],
    *[class*="st-emotion"][data-testid*="stHeader"],
    *[class*="css-"][role="banner"],
    *[class*="css-"][data-testid*="stHeader"]
    {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
    
    /* Fix sidebar stacking by ensuring there's only one active sidebar */
    [data-testid="stSidebar"] > div > div:nth-child(2) {
        display: none !important;
    }
    
    /* Ensure sidebar has proper spacing with main content */
    [data-testid="stSidebar"] {
        padding-right: 1rem !important;
        margin-right: 1rem !important;
    }
    
    </style>
    """, unsafe_allow_html=True)
    
    # Enhanced JavaScript to forcibly remove elements
    st.markdown("""
    <script>
    const REMOVE_ELEMENTS = () => {
      // Comprehensive list of selectors to target
      const selectors = [
        'header',
        'header[data-testid="stHeader"]',
        'div[data-testid="stToolbar"]',
        'div[data-testid="stDecoration"]',
        'div[role="banner"]',
        'button[kind="header"]',
        'button[data-testid="baseButton-headerNoPadding"]',
        '[data-testid="collapsedControl"]',
        '[data-baseweb="popover"]',
        'div[class*="st-emotion"][role="banner"]',
        'div[class*="css-"][role="banner"]',
        '.main-menu-button',
        '.stDeployButton',
        '.viewerBadge_container',
        'div.stToolbar',
        'div.st-emotion-cache-19rxjzo',
        'div.st-emotion-cache-1erivf3',
        'div.st-emotion-cache-1to1120',
        'section[data-testid="stSidebar"] > div.st-emotion-cache-16idsys.e1nzilvr5'
      ];
      
      // Apply multiple removal techniques to each element
      selectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(element => {
          if (element) {
            // Hide with CSS first
            element.style.cssText = `
              display: none !important;
              visibility: hidden !important;
              opacity: 0 !important;
              height: 0 !important;
              width: 0 !important;
              position: absolute !important;
              top: -9999px !important;
              left: -9999px !important;
              z-index: -9999 !important;
              pointer-events: none !important;
              overflow: hidden !important;
              max-height: 0 !important;
              max-width: 0 !important;
            `;
            
            // Try to remove from DOM
            try {
              element.remove();
            } catch (e) {
              console.log('Could not remove element directly:', e);
              // Fallback: try parent removal
              if (element.parentNode) {
                try {
                  element.parentNode.removeChild(element);
                } catch (e) {
                  console.log('Could not remove via parent:', e);
                  // Final fallback: empty the element
                  try {
                    element.innerHTML = '';
                  } catch (e) {
                    console.log('Could not empty element:', e);
                  }
                }
              }
            }
          }
        });
      });
      
      // Fix double sidebar issue
      const sidebars = document.querySelectorAll('[data-testid="stSidebar"] > div > div');
      if (sidebars.length > 1) {
        for (let i = 1; i < sidebars.length; i++) {
          sidebars[i].style.display = 'none';
        }
      }
    };

    // Run immediately
    REMOVE_ELEMENTS();
    
    // Run on DOMContentLoaded
    document.addEventListener('DOMContentLoaded', REMOVE_ELEMENTS);
    
    // Run on load
    window.addEventListener('load', REMOVE_ELEMENTS);
    
    // Run periodically to catch dynamically added elements
    setInterval(REMOVE_ELEMENTS, 300);
    
    // Run on any DOM changes using MutationObserver
    const observer = new MutationObserver((mutations) => {
      REMOVE_ELEMENTS();
    });
    
    // Start observing once the DOM is fully loaded
    document.addEventListener('DOMContentLoaded', () => {
      observer.observe(document.body, { 
        childList: true, 
        subtree: true 
      });
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Apply base styling
    apply_custom_styling()
    
    # Directly check and apply dark mode if needed
    current_theme = st.session_state.get('theme_mode', 'Light')
    if current_theme == 'Dark':
        set_dark_mode()
    
    # Initialize the sidebar with our custom styling
    # IMPORTANT: Only initialize sidebar once, here in the setup function
    initialize_sidebar()
    
    # Page header (only if not skipped)
    page_icon(icon_emoji)
    if not skip_header:
        st.header(page_title, divider="red", anchor=False)
        
        if subtitle:
            st.subheader(subtitle, anchor=False)
    
    return

def mark_task_complete(task_number):
    """
    Mark a task as complete in the session state
    
    Args:
        task_number (int): The task number (1-4)
    """
    task_key = f"task{task_number}_completed"
    st.session_state[task_key] = True
    
    # Check if all tasks are completed
    all_completed = all(st.session_state.get(f"task{i}_completed", False) for i in range(1, 5))
    
    if all_completed:
        st.session_state["all_tasks_completed"] = True
        
    return all_completed

def show_task_completion_status(task_id=None):
    """
    Display a summary of task completion status
    
    Args:
        task_id (int, optional): The specific task ID to highlight (1-4). If None, shows general summary.
    """
    task1 = st.session_state.get("task1_completed", False)  # Password Creation
    task2 = st.session_state.get("task2_completed", False)  # Phishing Awareness
    task3 = st.session_state.get("task3_completed", False)  # Phishing
    task4 = st.session_state.get("task4_completed", False)  # Security Protocols
    
    total_completed = sum([task1, task2, task3, task4])
    
    # If a specific task_id is provided, show status for that task
    if task_id is not None:
        if task_id == 1:
            is_completed = task1
            task_name = "Password Creation"
        elif task_id == 2:
            is_completed = task2
            task_name = "Phishing Awareness"
        elif task_id == 3:
            is_completed = task3
            task_name = "Security Protocols"
        elif task_id == 4:
            is_completed = task4
            task_name = "Model Management"
        else:
            st.warning(f"Invalid task ID: {task_id}")
            return
            
        status = "✅ Completed" if is_completed else "⏳ In Progress"
        st.info(f"Task {task_id} Status: {status}")
        return
        
    # Otherwise, show the overall summary (original behavior)
    progress_text = f"Tasks completed: {total_completed}/4"
    progress_percentage = total_completed / 4
    
    st.progress(progress_percentage, text=progress_text)
    
    if total_completed == 4:
        st.success("Congratulations! You've completed all security tasks!", icon="🎉")
    elif total_completed == 0:
        st.info("Get started with your security training by completing the tasks")
    
    # Check if role is selected, which is now a prerequisite rather than a task
    has_role = 'selected_role' in st.session_state and st.session_state.selected_role is not None
    if not has_role:
        st.warning("Don't forget to select your role on the Welcome page!")
    
    return total_completed

def create_next_task_buttons():
    """
    Create buttons to navigate to the next incomplete task
    """
    # Get task completion status
    task1 = st.session_state.get('task1_completed', False)
    task2 = st.session_state.get('task2_completed', False)
    task3 = st.session_state.get('task3_completed', False)
    task4 = st.session_state.get('task4_completed', False)
    has_role = 'selected_role' in st.session_state and st.session_state.selected_role
    
    # Calculate remaining tasks
    incomplete_tasks = []
    
    if not has_role:
        incomplete_tasks.append(("Set Your Role", "/00_Welcome"))
    
    if not task1:
        incomplete_tasks.append(("Password Creation", "/03_Password Creation"))
    
    if not task2:
        incomplete_tasks.append(("Phishing Awareness", "/05_Phishing"))
    
    if not task3:
        incomplete_tasks.append(("Security Protocols", "/04_Task 4"))
    
    if not task4:
        incomplete_tasks.append(("Model Management", "/06_Model Management"))
        
    if incomplete_tasks:
        st.markdown("### Next Tasks")
        cols = st.columns(min(3, len(incomplete_tasks)))
        
        for i, (task_name, task_path) in enumerate(incomplete_tasks[:3]):
            with cols[i % 3]:
                if st.button(f"Go to {task_name}", key=f"next_{i}", use_container_width=True):
                    try:
                        st.switch_page(f"pages{task_path}.py")
                    except Exception as e:
                        st.error(f"Navigation error: {e}")
                        st.warning(f"Alternative path: Try clicking on pages{task_path}")
    
    # If all tasks are complete, show dashboard button
    if task1 and task2 and task3 and task4 and has_role:
        st.success("All tasks completed! 🎉")
        if st.button("View Your Dashboard", use_container_width=True):
            try:
                st.switch_page("pages/07_Your Dashboard.py")
            except Exception as e:
                st.error(f"Navigation error: {e}")
                st.warning("Alternative path: Try clicking on pages/07_Your Dashboard") 