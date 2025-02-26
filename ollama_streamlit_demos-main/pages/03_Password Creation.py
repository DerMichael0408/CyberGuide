import streamlit as st
import ollama
import re
import time
import os
from utilities.template import setup_page, mark_task_complete, show_task_completion_status
from utilities.icon import page_icon

# Function to get the current page name
def get_current_page():
    # Get the filename of the current script
    current_file = os.path.basename(__file__)
    # Remove the extension
    page_name = os.path.splitext(current_file)[0]
    return page_name

# Get current page identifier
current_page = get_current_page()

# Function to get page-specific session state keys
def get_page_key(base_key):
    return f"{current_page}_{base_key}"

# Create page-specific session keys
messages_key = get_page_key("messages")
question_index_key = get_page_key("question_index")
started_key = get_page_key("started")
training_complete_key = get_page_key("training_complete")

# Use the common setup_page function instead of manual configuration
setup_page(
    page_title="Password Creation Training",
    icon_emoji="🔐",
    subtitle="Learn to create strong, secure passwords"
)

# Custom styling specific to this page
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .stAlert {
        border-radius: 10px;
    }
    .stExpander {
        border-radius: 10px;
        border: 1px solid #ddd;
    }
    .big-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 10px;
        color: #1E3A8A;
        text-align: center;
    }
    .subtitle {
        font-size: 18px;
        margin-bottom: 30px;
        text-align: center;
        color: #666;
    }
    .user-message {
        background-color: #e6f3ff;
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
    }
    .assistant-message {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
    }
    .score-container {
        background: linear-gradient(to right, #4CAF50, #2196F3);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
    }
    .question-number {
        font-weight: bold;
        color: #1E3A8A;
    }
    .feedback {
        padding: 10px;
        background-color: #f0f7ff;
        border-left: 3px solid #2196F3;
        margin-bottom: 10px;
    }
    .option-list {
        margin-left: 20px;
    }
    .option-item {
        margin: 5px 0;
    }
    .password-tips {
        background-color: #f8f9fa;
        border-left: 4px solid #4CAF50;
        padding: 10px 15px;
        margin: 15px 0;
        border-radius: 0 10px 10px 0;
    }
    .tip-title {
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 5px;
    }
    .page-indicator {
        font-size: 12px;
        color: #888;
        text-align: center;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# The 5 questions for the training
QUESTIONS = [
    "❓ Enter a new password for your company's network, and I will evaluate its security.",
    "Which of these is the most secure way to create a password?\nA) Using a single dictionary word\nB) Using a mix of uppercase, lowercase, numbers, and special characters\nC) Using a birth date or pet's name\nD) Reusing an old password",
    "Why should you never use the same password for multiple accounts?",
    "Which of these passwords is the most secure?\nA) Password123!\nB) Tr0ub4dor&3\nC) S3cureP@ssw0rd!\nD) company2024",
    "Now that you have completed this training, create a new secure password for your company's network based on what you have learned."
]

# System prompt with stronger instructions
SYSTEM_PROMPT = """
## PASSWORD CREATION TRAINING PROCEDURE
You are a Password Security Training Assistant delivering a 5-question password creation training.
You MUST follow the EXACT questions provided to you in order.

## CRITICAL RESPONSE FORMAT
YOU MUST:
1. For each user response, provide brief feedback (1-2 sentences)
2. After giving feedback, present the NEXT question exactly as provided
3. Always include the correct question number (e.g., "Question 2/5:", "Question 3/5:", etc.)
4. Do NOT modify the questions - use them exactly as provided
5. Do NOT include any meta notes or instructions in your responses - only provide the feedback and next question

IMPORTANT: Present each question separately and wait for the user's response before moving to the next question.
"""

# Instructions for password evaluation
SCORING_INSTRUCTIONS = """
## PASSWORD CREATION EVALUATION
Evaluate ONLY the user's final password creation (response to Question 5) and provide a numerical score using EXACTLY this format:

```
Your final password score is: [X]/100.

Feedback: [1-2 sentences explaining the strengths and weaknesses of their password]
```

Use actual numbers, not placeholders. The score should reflect password strength based on:
- Length (longer is better, at least 12 characters recommended)
- Complexity (mix of character types)
- Unpredictability (not based on common words or patterns)
- Memorability balanced with security
"""

# Function to format multiple-choice questions
def format_multiple_choice(question_text):
    if "A)" in question_text and "B)" in question_text:
        # Split the question into main question and options
        parts = question_text.split("\n", 1)
        if len(parts) > 1:
            main_question = parts[0]
            options = parts[1]
            
            # Format options with HTML
            formatted_options = ""
            for option in options.split("\n"):
                formatted_options += f'<div class="option-item">{option}</div>'
                
            return f'{main_question}<div class="option-list">{formatted_options}</div>'
    
    return question_text

# Function to format messages with custom styling
def format_message(message, role):
    if role == "user":
        return f'<div class="user-message">{message}</div>'
    else:
        # Remove any system notes that shouldn't be displayed
        message = re.sub(r'\(Note: This question should be asked.*?\)', '', message)
        
        # Format assistant messages with highlighted question number
        if "Question" in message and "/5:" in message:
            # Split by question marker to highlight it
            parts = re.split(r'(Question \d/5:)', message, 1)
            if len(parts) > 1:
                feedback = parts[0].strip()
                question_part = parts[1]
                rest = parts[2] if len(parts) > 2 else ""
                
                # Format multiple-choice questions
                rest = format_multiple_choice(rest)
                
                formatted = ""
                if feedback:
                    formatted += f'<div class="feedback">{feedback}</div>'
                formatted += f'<div><span class="question-number">{question_part}</span>{rest}</div>'
                return f'<div class="assistant-message">{formatted}</div>'
        
        # Default formatting for other assistant messages
        return f'<div class="assistant-message">{message}</div>'

# Display the training title with better styling
st.markdown('<div class="big-title">🔐 Password Creation Training</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Complete this interactive training to learn how to create strong, secure passwords</div>', unsafe_allow_html=True)
st.markdown(f'<div class="page-indicator">Page: {current_page}</div>', unsafe_allow_html=True)

# Initialize page-specific session state variables
if messages_key not in st.session_state:
    st.session_state[messages_key] = []

if question_index_key not in st.session_state:
    st.session_state[question_index_key] = 0

if started_key not in st.session_state:
    st.session_state[started_key] = False

if training_complete_key not in st.session_state:
    st.session_state[training_complete_key] = False

# Add columns for layout
col1, col2 = st.columns([3, 1])

# Display training info in sidebar
with col2:
    st.info("**About this training**\n\n"
            "This interactive password security course will test your knowledge with 5 key questions.\n\n"
            "Learn how to create strong passwords that protect your accounts from unauthorized access.")
    
    # Show progress with custom styling
    if st.session_state[question_index_key] > 0:
        st.write(f"**Progress: {st.session_state[question_index_key]}/5 questions**")
        progress = st.progress(min(st.session_state[question_index_key] * 20, 100))
        
    # Password Tips in the sidebar
    with st.expander("📌 Password Security Tips", expanded=False):
        st.markdown("""
        <div class="password-tips">
            <div class="tip-title">Length Matters</div>
            <p>Longer passwords are generally more secure. Aim for at least 12 characters.</p>
        </div>
        
        <div class="password-tips">
            <div class="tip-title">Mix Character Types</div>
            <p>Use a combination of uppercase, lowercase, numbers, and special characters.</p>
        </div>
        
        <div class="password-tips">
            <div class="tip-title">Avoid Common Patterns</div>
            <p>Don't use sequential numbers, repeated characters, or keyboard patterns like "qwerty".</p>
        </div>
        
        <div class="password-tips">
            <div class="tip-title">Consider Passphrases</div>
            <p>A sequence of random words with special characters can be both secure and memorable.</p>
        </div>
        """, unsafe_allow_html=True)

with col1:
    st.write("---")

    # Start training when the app loads
    if not st.session_state[started_key]:
        # Present first question
        first_message = f"Welcome to password creation training. I will help you learn how to create stronger, more secure passwords.\n\nQuestion 1/5: {QUESTIONS[0]}"
        st.session_state[messages_key].append({"role": "assistant", "content": first_message})
        st.session_state[started_key] = True
        st.session_state[question_index_key] = 1

    # Display message history from page-specific chat
    for message in st.session_state[messages_key]:
        st.markdown(format_message(message["content"], message["role"]), unsafe_allow_html=True)

    # User input field
    if not st.session_state[training_complete_key]:
        user_input = st.chat_input("Type your answer here...")
        
        if user_input:
            # Add to page-specific message history
            st.session_state[messages_key].append({"role": "user", "content": user_input})
            
            # IMPORTANT: rerun to update UI
            st.rerun()

    # After rerun: Check if there's a new user response and generate AI response
    if st.session_state[messages_key] and st.session_state[messages_key][-1]["role"] == "user" and not st.session_state[training_complete_key]:
        with st.spinner("Processing your answer..."):
            # Add a short delay for visual effect
            time.sleep(0.5)
            
            # Get user input
            user_answer = st.session_state[messages_key][-1]["content"]
            
            if st.session_state[question_index_key] == 5:
                # Generate final score
                final_score_messages = [
                    {"role": "system", "content": SCORING_INSTRUCTIONS},
                    {"role": "user", "content": f"Evaluate this password: {user_answer}"}
                ]
                
                final_score_response = ollama.chat(model="llava:latest", messages=final_score_messages)
                final_score = final_score_response["message"]["content"]
                
                score_match = re.search(r'(\d+)/100', final_score)
                if score_match:
                    score_num = int(score_match.group(1))
                    
                    # Create score display
                    score_html = f"""
                    <div class="score-container">
                        <h2>Training Complete! 🎉</h2>
                        <h1 style="font-size: 48px; margin: 20px 0;">{score_num}/100</h1>
                        <p>{final_score.split('Feedback:')[1].strip() if 'Feedback:' in final_score else ''}</p>
                    </div>
                    """
                    st.markdown(score_html, unsafe_allow_html=True)
                    
                    # Add to page-specific message history
                    st.session_state[messages_key].append({"role": "assistant", "content": final_score})
                    
                    st.session_state[training_complete_key] = True
                    
                    if "progress" in locals():
                        progress.progress(100)
                    
                    # Mark Task 1 as complete
                    mark_task_complete(1)
                    
                    st.success("🎓 Training completed successfully! Remember to apply these principles to all your accounts.")
                    
                    # Show task completion status
                    show_task_completion_status(1)
                    
                    st.download_button(
                        label="📜 Download Password Security Cheat Sheet",
                        data="# Password Security Cheat Sheet\n\n- Use a mix of uppercase, lowercase, numbers, and special characters\n- Don't reuse passwords across accounts\n- Avoid dictionary words and personal information\n- Consider using a password manager\n- Minimum 12 characters for strong passwords",
                        file_name="password_security_cheatsheet.md"
                    )
                    
                    st.rerun()
            else:
                system_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                
                context_message = f"The user has answered question {st.session_state[question_index_key]}. Give brief feedback and then ask question {st.session_state[question_index_key] + 1}."
                system_messages.append({"role": "user", "content": context_message})
                
                feedback_messages = system_messages + [
                    {"role": "user", "content": f"Question {st.session_state[question_index_key]}: {QUESTIONS[st.session_state[question_index_key] - 1]}"},
                    {"role": "user", "content": f"User's answer: {user_answer}"}
                ]
                
                response = ollama.chat(model="llava:latest", messages=feedback_messages)
                ai_message = response["message"]["content"]
                
                if f"Question {st.session_state[question_index_key] + 1}/5:" not in ai_message:
                    feedback = ai_message.strip()
                    ai_message = f"{feedback}\n\nQuestion {st.session_state[question_index_key] + 1}/5: {QUESTIONS[st.session_state[question_index_key]]}"

                # Add to page-specific message history
                st.session_state[messages_key].append({"role": "assistant", "content": ai_message})
                
                # Increment page-specific question counter
                st.session_state[question_index_key] += 1
                
                st.rerun()

# Reset button (only show in completed state)
if st.session_state[training_complete_key]:
    if st.button("Start New Training"):
        # Reset all page-specific session state variables
        st.session_state[messages_key] = []
        st.session_state[question_index_key] = 0
        st.session_state[started_key] = False
        st.session_state[training_complete_key] = False
        st.rerun()