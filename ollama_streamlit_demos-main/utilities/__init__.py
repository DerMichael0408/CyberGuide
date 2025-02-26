# This makes the directory a Python package

# Utilities module
from .icon import page_icon
from .styling import (
    initialize_sidebar, 
    apply_custom_styling, 
    set_dark_mode, 
    create_sidebar_header, 
    create_sidebar_tasks, 
    create_theme_toggle, 
    create_chat_history, 
    create_sidebar_resources
)
from .template import (
    setup_page, 
    mark_task_complete, 
    show_task_completion_status, 
    create_next_task_buttons
)
