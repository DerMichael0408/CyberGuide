import streamlit as st
import ollama
import re
import time
import os
import string
import random
import math

# Get the current page name from the file name
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
question_number_key = get_page_key("question_number")
started_key = get_page_key("started")
first_password_key = get_page_key("first_password")
final_password_key = get_page_key("final_password")

# Set page config for wider layout and custom title/icon
st.set_page_config(
    page_title="Password Security Training",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem 3rem;
    }
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
    .password-container {
        background-color: #f9f9f9;
        border-radius: 10px;
        border-left: 5px solid #2196F3;
        padding: 20px;
        margin-bottom: 25px;
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
    .multiple-choice {
        padding: 2px 0;
        margin: 2px 0;
    }
    .multiple-choice-option {
        display: block;
        padding: 12px 15px;
        margin: 8px 0;
        background-color: #f8f9fa;
        border-radius: 6px;
        border-left: 3px solid #6c757d;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .multiple-choice-option:hover {
        background-color: #e9ecef;
        border-left-color: #2196F3;
        transform: translateX(2px);
    }
    .question-text {
        font-size: 17px;
        margin-bottom: 15px;
        line-height: 1.5;
    }
    .crack-time {
        font-weight: bold;
        font-size: 18px;
        color: #d32f2f;
    }
    .password-strength-meter {
        height: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .strength-0 {
        background-color: #d32f2f;
        width: 20%;
    }
    .strength-1 {
        background-color: #ff9800;
        width: 40%;
    }
    .strength-2 {
        background-color: #ffc107;
        width: 60%;
    }
    .strength-3 {
        background-color: #8bc34a;
        width: 80%;
    }
    .strength-4 {
        background-color: #4caf50;
        width: 100%;
    }
    .password-tips {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .security-fact {
        background-color: #fffde7;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 15px 0;
        font-style: italic;
    }
    # Add new class for option buttons
    .option-button {
        background-color: #f8f9fa !important;
        color: #333 !important;
        text-align: left !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 6px !important;
        padding: 12px 15px !important;
        margin: 8px 0 !important;
        font-weight: normal !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    .option-button:hover {
        background-color: #e2e6ea !important;
        border-color: #2196F3 !important;
        transform: translateX(3px) !important;
    }
    /* Better button styling */
    .stButton > button {
        border-radius: 4px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .submit-button > button {
        background-color: #4CAF50 !important;
        color: white !important;
        padding: 10px 20px !important;
    }
    .submit-button > button:hover {
        background-color: #45a049 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# Security facts to display randomly
SECURITY_FACTS = [
    "It would take a computer about 1 trillion years to crack a 12-character password with upper and lowercase letters, numbers, and symbols.",
    "The most common password is still '123456', followed by 'password' and '123456789'.",
    "A typical computer can make 1 billion password guesses per second.",
    "Over 80% of data breaches are linked to password-related issues.",
    "Password managers are considered more secure than manually creating and remembering unique passwords.",
    "Two-factor authentication can prevent 99.9% of automated attacks, even if your password is compromised.",
    "The average person has around 100 online accounts requiring passwords.",
    "Many major breaches occur due to password reuse across multiple sites.",
    "The NIST no longer recommends periodic password changes unless there's evidence of compromise.",
    "Using a passphrase (multiple random words) can be more secure and easier to remember than a complex password."
]

# System Prompt for password training
SYSTEM_PROMPT = """
## PASSWORD SECURITY TRAINING PROTOCOL
You are a Cybersecurity Training Assistant delivering an interactive 5-question password security training.

## QUESTION SEQUENCE (MUST FOLLOW EXACTLY)
The training consists of exactly these 5 questions in this order:

1. "Imagine you need to set a secure password for a company system. Please enter your new password."

2. "Which of these passwords is the MOST secure?
   A) Spring2024!
   B) P@55w0rd2024
   C) correct-horse-battery-staple
   D) 7K!9#mLp$2Q"

3. "What are three key factors that make a password strong and difficult to crack?"

4. "Why is using the same password across multiple websites dangerous, and what's a better approach?"

5. "Based on what you've learned, create a new secure password. We'll evaluate how much you've improved."

## CRITICAL RESPONSE FORMAT
YOU MUST:
1. Start with "This is a password security training exercise" and ask Question 1
2. For each user response:
   a. FIRST provide informative feedback on their answer (1-2 sentences)
   b. THEN immediately ask the next question in sequence
3. Format multiple choice options in a clean, visually appealing way
4. ALWAYS include the correct question number (e.g., "Question 2/5:", "Question 3/5:", etc.)
5. NEVER repeat a question
6. NEVER use lettered points (a), b), etc.) in your feedback - use plain text only

## IMPORTANT NOTES FOR PASSWORD EVALUATIONS
For Questions 1 and 5 (password creation):
- Evaluate the password thoroughly, providing a score (0-100)
- Comment on password length, character diversity, common patterns, estimated crack time
- Always provide constructive feedback
- Be encouraging while highlighting security considerations
- For Question 5, compare with their initial password if possible, noting improvements
"""

# Password evaluation instructions
PASSWORD_EVALUATION_INSTRUCTIONS = """
## SCIENTIFIC PASSWORD STRENGTH ASSESSMENT

Conduct a comprehensive and scientific evaluation of the user's password based on modern security standards.

### Assessment Framework:
Evaluate the password based on these key areas:

1. **Length**: Score higher for longer passwords (12+ characters is recommended)
2. **Character Diversity**: Check for a mix of uppercase, lowercase, numbers, and special characters
3. **Patterns**: Look for common substitutions (e.g., 'a' to '@'), keyboard patterns, and sequential characters
4. **Dictionary Words**: Check if the password contains common words or names
5. **Uniqueness**: Evaluate originality and creativity

### Output Format Requirements:
You MUST use EXACTLY this format:

```
Password Strength: [X]/100

Analysis:
- Length: [Comment on the password length and its impact on security]
- Character Diversity: [Evaluate the mix of character types]
- Patterns: [Identify any concerning patterns or strengths]
- Dictionary Vulnerability: [Comment on presence of dictionary words]

Estimated crack time: [Time estimate to crack using current technology]

Improvement suggestions:
- [1-3 specific, actionable suggestions to strengthen the password]
```

### IMPORTANT:
- Make your crack time estimate realistic based on current computing capabilities
- Scoring guidelines:
  * 0-20: Very weak (simple patterns, very short, only one character type)
  * 21-40: Weak (short, limited character types, common words/patterns)
  * 41-60: Moderate (decent length, some character variety, may contain patterns)
  * 61-80: Strong (good length, good character variety, minimal patterns)
  * 81-100: Very strong (excellent length, full character diversity, no patterns)
- Be specific about weaknesses rather than general
- NEVER include the actual password in your response
"""

# Questions list for password training
questions = [
    "Imagine you need to set a secure password for a company system. Please enter your new password.",
    "Which of these passwords is the MOST secure?\nA) Spring2024!\nB) P@55w0rd2024\nC) correct-horse-battery-staple\nD) 7K!9#mLp$2Q",
    "What are three key factors that make a password strong and difficult to crack?",
    "Why is using the same password across multiple websites dangerous, and what's a better approach?",
    "Based on what you've learned, create a new secure password. We'll evaluate how much you've improved."
]

# First question - password training
FIRST_QUESTION = "This is a password security training exercise. I will guide you through 5 questions about creating and managing secure passwords.\n\nQuestion 1/5: Imagine you need to set a secure password for a company system. Please enter your new password."

# Function to evaluate password strength
def evaluate_password_strength(password):
    """
    Custom password strength evaluation function
    Returns a dictionary with score and feedback
    """
    if not password:
        return {
            "score": 0,
            "crack_time_display": "instantly",
            "feedback": {
                "warning": "No password provided",
                "suggestions": ["Please enter a password"]
            }
        }
    
    # Initialize score
    score = 0
    
    # Check length
    length = len(password)
    if length >= 16:
        score += 30
    elif length >= 12:
        score += 25
    elif length >= 8:
        score += 15
    else:
        score += 5
    
    # Check character types
    has_lowercase = any(c.islower() for c in password)
    has_uppercase = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    char_type_count = sum([has_lowercase, has_uppercase, has_digit, has_special])
    score += char_type_count * 10
    
    # Check for common patterns
    common_patterns = [
        '123', '1234', '12345', '123456', 'abc', 'abcd', 'abcde', 'abcdef',
        'qwerty', 'asdfgh', 'zxcvbn', 'password', 'admin', 'welcome',
        '!@#$', '!@#$%', '!@#$%^'
    ]
    
    # Check for sequential characters
    sequential_penalty = 0
    for i in range(len(password) - 2):
        # Check for sequential characters (either ascending or descending)
        if (ord(password[i]) + 1 == ord(password[i+1]) and ord(password[i+1]) + 1 == ord(password[i+2])) or \
           (ord(password[i]) - 1 == ord(password[i+1]) and ord(password[i+1]) - 1 == ord(password[i+2])):
            sequential_penalty += 5
    
    # Check for repeating characters
    repeat_penalty = 0
    for i in range(len(password) - 2):
        if password[i] == password[i+1] and password[i+1] == password[i+2]:
            repeat_penalty += 5
    
    # Apply penalties
    pattern_found = False
    for pattern in common_patterns:
        if pattern.lower() in password.lower():
            pattern_found = True
            break
    
    if pattern_found:
        score -= 10
    
    score -= min(sequential_penalty, 15)
    score -= min(repeat_penalty, 15)
    
    # Ensure score is within 0-100 range
    score = max(0, min(100, score))
    
    # Calculate crack time (simplified estimation)
    entropy = math.log2(95) * length if char_type_count >= 3 else math.log2(26) * length
    crack_attempts = 2 ** entropy
    seconds_to_crack = crack_attempts / (10 ** 9)  # Assuming 1 billion attempts per second
    
    # Determine crack time display
    if seconds_to_crack < 60:
        crack_time = "instantly" if seconds_to_crack < 1 else f"{seconds_to_crack:.1f} seconds"
    elif seconds_to_crack < 3600:
        crack_time = f"{seconds_to_crack / 60:.1f} minutes"
    elif seconds_to_crack < 86400:
        crack_time = f"{seconds_to_crack / 3600:.1f} hours"
    elif seconds_to_crack < 31536000:
        crack_time = f"{seconds_to_crack / 86400:.1f} days"
    elif seconds_to_crack < 31536000 * 100:
        crack_time = f"{seconds_to_crack / 31536000:.1f} years"
    else:
        crack_time = "centuries"
    
    # Generate feedback
    feedback = {
        "warning": "",
        "suggestions": []
    }
    
    if length < 12:
        feedback["suggestions"].append("Use at least 12 characters")
    
    if char_type_count < 3:
        feedback["suggestions"].append("Use a mix of character types (uppercase, lowercase, numbers, symbols)")
    
    if pattern_found:
        feedback["warning"] = "Contains common patterns"
        feedback["suggestions"].append("Avoid common patterns and sequences")
    
    if sequential_penalty > 0:
        feedback["suggestions"].append("Avoid sequential characters")
    
    if repeat_penalty > 0:
        feedback["suggestions"].append("Avoid repeating characters")
    
    return {
        "score": int(score),
        "crack_time_display": crack_time,
        "feedback": feedback
    }

# Function to format multiple choice options
def format_multiple_choice(question_text):
    """Format multiple choice options with better styling"""
    if "A)" in question_text and "B)" in question_text:
        # Split the question into the prompt and options
        main_text, options_text = question_text.split("A)", 1)
        options_text = "A)" + options_text
        
        # Split options and format them
        options = re.findall(r'([A-D]\))([^A-D\)]+)', options_text)
        formatted_options = ""
        for opt_letter, opt_text in options:
            formatted_options += f'<div class="multiple-choice-option">{opt_letter}{opt_text}</div>'
        
        # Combine with styled question text
        return f'<div class="question-text">{main_text}</div><div class="multiple-choice">{formatted_options}</div>'
    else:
        # For non-multiple choice, just add basic styling
        return f'<div class="question-text">{question_text}</div>'

# Extract multiple choice options in a more reliable way
def extract_multiple_choice_options(message):
    """Extract multiple choice options from a message."""
    if not message or "A)" not in message:
        return []
    
    # Use regex to find all options in the format A) text, B) text, etc.
    options = []
    pattern = r'([A-D]\))(.*?)(?=[A-D]\)|$)'
    matches = re.findall(pattern, message, re.DOTALL)
    
    for option_letter, option_text in matches:
        options.append((option_letter.strip(), option_text.strip()))
    
    return options

# Function to ensure correct question sequencing
def force_next_question(response, current_question_num):
    """
    Extracts feedback from AI response and adds the next correct question.
    Removes any lettered points (a), b), etc.) and ensures clean formatting.
    """
    # Get the next question number (0-indexed internally, 1-indexed for display)
    next_question_idx = current_question_num + 1
    
    # If we're done with questions, just return the response
    if next_question_idx >= 5:
        return response
    
    # Process AI feedback
    # Remove any existing questions
    question_patterns = [
        "Question 1/5:", "Question 2/5:", "Question 3/5:", "Question 4/5:", "Question 5/5:"
    ]
    
    # Get the feedback portion by removing question text
    cleaned_text = response
    for pattern in question_patterns:
        if pattern in cleaned_text:
            parts = cleaned_text.split(pattern, 1)
            cleaned_text = parts[0]
    
    # Remove any lettered or numbered points (a), b), 1., 2., etc.)
    cleaned_text = re.sub(r'[a-z]\)\s+', '', cleaned_text)
    cleaned_text = re.sub(r'[A-Z]\)\s+', '', cleaned_text)
    cleaned_text = re.sub(r'\d+\.\s+', '', cleaned_text)
    cleaned_text = re.sub(r'•\s+', '', cleaned_text)
    
    # Remove "Progress: X/5 questions" text if it appears
    cleaned_text = re.sub(r'Progress: \d/5 questions', '', cleaned_text)
    
    # Ensure we get at least one complete sentence of feedback
    # Get sentences but preserve proper formatting
    sentences = re.split(r'(?<=[.!?])\s+', cleaned_text.strip())
    
    # Make sure we have at least one sentence but not more than 3
    feedback = ' '.join(sentences[:min(3, len(sentences))]).strip()
    
    # Build the correct next question text with proper numbering
    next_question = f"Question {next_question_idx+1}/5: {questions[next_question_idx]}"
    
    # Combine feedback with next question, ensuring there's a proper break between them
    if feedback:
        return f"{feedback}\n\n{next_question}"
    else:
        # Fallback feedback if none was extracted
        return f"I understand your response.\n\n{next_question}"

# REVISED APPROACH: Use a different technique for handling messages and UI elements
# Function to format messages - modified to NOT render multiple choice options as HTML
def format_message(message, role):
    if role == "user":
        return f'<div class="user-message">{message}</div>'
    else:
        # Format assistant messages by highlighting the question number
        if "Question" in message and "/5:" in message:
            # Split by question marker to highlight it
            parts = re.split(r'(Question \d+/5:)', message, 1)
            if len(parts) > 1:
                feedback = parts[0].strip()
                question_part = parts[1]
                question_text = parts[2] if len(parts) > 2 else ""
                
                formatted = ""
                if feedback:
                    formatted += f'<div class="feedback">{feedback}</div>'
                
                # Format question number
                formatted_question = f'<span class="question-number">{question_part}</span>'
                
                # For multiple choice questions, DON'T format the options as HTML 
                # We'll handle them with Streamlit components separately
                if "A)" in question_text and "B)" in question_text:
                    # Only format the question text itself, not the options
                    main_text = question_text.split("A)")[0].strip()
                    formatted += f'<div>{formatted_question} {main_text}</div>'
                    
                    # Store the question identifier in session state for reference
                    # This helps us know which question to display interactive elements for
                    current_q_num = int(re.search(r'Question (\d+)/5:', message).group(1))
                    st.session_state["current_mc_question"] = current_q_num
                else:
                    formatted += f'<div>{formatted_question} {question_text}</div>'
                
                return f'<div class="assistant-message">{formatted}</div>'
        
        # Default formatting for other assistant messages
        return f'<div class="assistant-message">{message}</div>'

# Function to display password strength results
def display_password_results(password, is_final=False):
    # Evaluate the password
    evaluation = evaluate_password_strength(password)
    score = evaluation["score"]
    crack_time = evaluation["crack_time_display"]
    feedback = evaluation["feedback"]
    
    # Determine strength level (0-4) for visual indicator
    strength_level = min(4, score // 20)
    
    # Display random security fact
    security_fact = random.choice(SECURITY_FACTS)
    
    # Create strength meter and feedback
    st.markdown(f"""
    <div class="score-container">
        <h2>{"Final " if is_final else ""}Password Strength Assessment</h2>
        <h1 style="font-size: 48px; margin: 20px 0;">{score}/100</h1>
        <div class="password-strength-meter strength-{strength_level}"></div>
        <p>Estimated time to crack: <span class="crack-time">{crack_time}</span></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display feedback
    st.markdown("""
    <div class="password-tips">
        <div class="tip-header">Password Analysis</div>
        <ul>
    """, unsafe_allow_html=True)
    
    # Character analysis
    has_lowercase = any(c.islower() for c in password)
    has_uppercase = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    st.markdown(f"<li><strong>Length:</strong> {len(password)} characters " + 
                f"({'Good' if len(password) >= 12 else 'Consider using 12+ characters'})</li>", 
                unsafe_allow_html=True)
    
    st.markdown(f"<li><strong>Character Types:</strong> " +
                f"{'✓' if has_lowercase else '✗'} Lowercase, " +
                f"{'✓' if has_uppercase else '✗'} Uppercase, " +
                f"{'✓' if has_digit else '✗'} Numbers, " +
                f"{'✓' if has_special else '✗'} Special Characters</li>", 
                unsafe_allow_html=True)
    
    # Add warning if present
    if feedback["warning"]:
        st.markdown(f"<li><strong>Warning:</strong> {feedback['warning']}</li>", unsafe_allow_html=True)
    
    st.markdown("</ul></div>", unsafe_allow_html=True)
    
    # Display improvement suggestions if any
    if feedback["suggestions"]:
        st.markdown("""
        <div class="password-tips">
            <div class="tip-header">Improvement Suggestions</div>
            <ul>
        """, unsafe_allow_html=True)
        
        for suggestion in feedback["suggestions"]:
            st.markdown(f"<li>{suggestion}</li>", unsafe_allow_html=True)
        
        st.markdown("</ul></div>", unsafe_allow_html=True)
    
    # Display random security fact
    st.markdown(f"""
    <div class="security-fact">
        <strong>💡 Security Fact:</strong> {security_fact}
    </div>
    """, unsafe_allow_html=True)
    
    return evaluation

# Helper function to process answers and move to next question
def process_answer(user_input):
    """Process the user's answer and move to the next question"""
    # Generate AI response for the next question
    with st.spinner("Analyzing your response..."):
        # For visual effect, add a short delay
        time.sleep(0.5)
        
        # Get response from LLM
        response = ollama.chat(model="llava:latest", messages=st.session_state[messages_key])
        ai_message = response["message"]["content"]
        
        # Force the correct next question and include feedback
        fixed_message = force_next_question(ai_message, st.session_state[question_number_key])
        
        # Display the fixed message with enhanced formatting
        st.markdown(format_message(fixed_message, "assistant"), unsafe_allow_html=True)
        
        # Add to message history
        st.session_state[messages_key].append({"role": "assistant", "content": fixed_message})
        
        # Increment question counter
        st.session_state[question_number_key] += 1

# Main content area handling function - new approach
def display_interface(col1):
    """
    Display the appropriate interface elements based on the current question.
    This is the main function for handling user input.
    """
    # Find current question in message history
    current_question = None
    for message in reversed(st.session_state[messages_key]):
        if message["role"] == "assistant" and f"Question {st.session_state[question_number_key]+1}/5" in message["content"]:
            current_question = message["content"]
            break
    
    if not current_question:
        return
    
    # Determine if it's a multiple choice question
    is_mc = "A)" in current_question and "B)" in current_question
    
    # Only display ONE input method at a time
    if is_mc:
        # Extract options from the question
        options = extract_multiple_choice_options(current_question)
        if options:
            # Use radio buttons for multiple choice
            st.write("### Select your answer:")
            
            # Create radio buttons with the full text of each option
            option_texts = [f"{letter} {text}" for letter, text in options]
            selected_option = st.radio(
                "Choose one option:",
                option_texts,
                label_visibility="collapsed",
                key=f"radio_q{st.session_state[question_number_key]+1}"
            )
            
            # Extract just the letter (A, B, C, D) from the selection
            selected_letter = selected_option.split(")")[0].strip() if selected_option else ""
            
            # Submit button
            col1, col2, col3 = st.columns([1, 1, 5])
            with col1:
                if st.button("Submit Answer", key=f"submit_q{st.session_state[question_number_key]+1}", type="primary"):
                    # Process the selected answer
                    answer_text = f"My answer is {selected_letter}."
                    st.session_state[messages_key].append({"role": "user", "content": answer_text})
                    process_answer(answer_text)
                    st.rerun()  # Ensure the UI updates
    elif st.session_state[question_number_key] == 0:
        # Question 1: Password input
        password_input = st.text_input("Enter your password:", type="password", key="password_q1")
        
        col1, col2, col3 = st.columns([1, 1, 5])
        with col1:
            if st.button("Submit Password", key="submit_q1", type="primary"):
                # Process first password
                handle_first_password(password_input)
                st.rerun()
    elif st.session_state[question_number_key] == 5:
        # Question 5: Final password
        password_input = st.text_input("Enter your improved password:", type="password", key="password_q5")
        
        col1, col2, col3 = st.columns([1, 1, 5])
        with col1:
            if st.button("Submit Final Password", key="submit_q5", type="primary"):
                # Process final password
                handle_final_password(password_input)
                st.rerun()
    else:
        # Regular text input for other questions
        user_input = st.text_input("Your answer:", key=f"input_q{st.session_state[question_number_key]+1}")
        
        col1, col2, col3 = st.columns([1, 1, 5])
        with col1:
            if st.button("Submit", key=f"submit_q{st.session_state[question_number_key]+1}", type="primary"):
                st.session_state[messages_key].append({"role": "user", "content": user_input})
                process_answer(user_input)
                st.rerun()

# Handle the first password submission
def handle_first_password(password_input):
    """Process the first password submission (Question 1)"""
    # Store the password
    st.session_state[first_password_key] = password_input
    
    # Only do a brief evaluation for the first password
    with st.spinner("Analyzing password..."):
        # Basic password analysis for visual feedback only
        length = len(password_input)
        has_lowercase = any(c.islower() for c in password_input)
        has_uppercase = any(c.isupper() for c in password_input)
        has_digit = any(c.isdigit() for c in password_input)
        has_special = any(not c.isalnum() for c in password_input)
        
        char_types = sum([has_lowercase, has_uppercase, has_digit, has_special])
        
        # Simple visual feedback only - no detailed evaluation
        st.markdown(f"""
        <div class="password-tips">
            <div class="tip-header">Initial Password Analysis</div>
            <p>We'll analyze your password in more detail after you complete the training.</p>
            <ul>
                <li><strong>Length:</strong> {length} characters</li>
                <li><strong>Character Variety:</strong> {char_types} of 4 possible types</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Add to chat history without displaying the placeholder text
        st.session_state[messages_key].append({"role": "user", "content": "I've created my password."})
        
        # Simple evaluation for LLM to provide brief feedback
        brief_eval_prompt = """
        Provide a VERY BRIEF evaluation of this password (1-2 sentences only).
        DO NOT mention the password itself.
        DO NOT provide a detailed analysis or score.
        DO NOT provide cracking time estimates.
        Just give brief general feedback and immediately move to the next question.
        """
        
        # Append to message history with the LLM's brief evaluation
        password_eval_messages = st.session_state[messages_key] + [
            {"role": "system", "content": brief_eval_prompt},
            {"role": "user", "content": f"Briefly evaluate this password: {password_input}"}
        ]
        
        evaluation_response = ollama.chat(model="llava:latest", messages=password_eval_messages)
        ai_evaluation = evaluation_response["message"]["content"]
        
        # Add the evaluation and force the next question
        fixed_message = force_next_question(ai_evaluation, st.session_state[question_number_key])
        st.markdown(format_message(fixed_message, "assistant"), unsafe_allow_html=True)
        
        # Add to message history
        st.session_state[messages_key].append({"role": "assistant", "content": fixed_message})
        
        # Increment question counter
        st.session_state[question_number_key] += 1

# Handle the final password submission
def handle_final_password(password_input):
    """Process the final password submission (Question 5)"""
    # Store the final password
    st.session_state[final_password_key] = password_input
    
    # Compare with initial password
    first_password = st.session_state[first_password_key]
    comparison = ""
    
    if first_password and password_input:
        # Simple comparison to show improvement
        first_eval = evaluate_password_strength(first_password)
        final_eval = evaluate_password_strength(password_input)
        
        score_diff = final_eval["score"] - first_eval["score"]
        
        if score_diff > 0:
            comparison = f"You've improved your password strength by {score_diff} points! Great job!"
        elif score_diff == 0:
            comparison = "Your new password has the same strength score as your initial one."
        else:
            comparison = "Your initial password was actually stronger. Remember to apply the security principles you've learned."
    
    # Show final evaluation
    st.write("### Your Final Password Evaluation")
    final_evaluation = display_password_results(password_input, is_final=True)
    
    if comparison:
        st.info(comparison)
    
    # Final message
    st.success("🎉 You've completed the Password Security Training! Keep applying these principles to stay secure online.")
    
    # Add to chat history
    st.session_state[messages_key].append({"role": "user", "content": "I've created my final password."})
    
    # Final evaluation prompt
    final_eval_prompt = """
    Provide a comprehensive evaluation of this final password, comparing it to the first password if possible.
    Highlight strengths, weaknesses, and areas of improvement.
    End with some final encouragement about password security.
    DO NOT mention the password itself.
    """
    
    # Append to message history with detailed evaluation
    password_eval_messages = st.session_state[messages_key] + [
        {"role": "system", "content": final_eval_prompt},
        {"role": "user", "content": f"Evaluate this final password: {password_input} compared to initial password: {first_password}"}
    ]
    
    final_response = ollama.chat(model="llava:latest", messages=password_eval_messages)
    final_feedback = final_response["message"]["content"]
    
    st.markdown(format_message(final_feedback, "assistant"), unsafe_allow_html=True)
    st.session_state[messages_key].append({"role": "assistant", "content": final_feedback})
    
    # Complete the training
    st.session_state[question_number_key] += 1

# Initialize page-specific session state
if messages_key not in st.session_state:
    st.session_state[messages_key] = []
    
if question_number_key not in st.session_state:
    st.session_state[question_number_key] = 0
    
if started_key not in st.session_state:
    st.session_state[started_key] = False

if first_password_key not in st.session_state:
    st.session_state[first_password_key] = ""

if final_password_key not in st.session_state:
    st.session_state[final_password_key] = ""

# Select a random security fact when the app is first loaded
if "random_fact" not in st.session_state:
    st.session_state.random_fact = random.choice(SECURITY_FACTS)

# Display the training title
st.markdown('<div class="big-title">🔒 Password Security Training</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Learn how to create strong, secure passwords in this interactive training</div>', unsafe_allow_html=True)

# Add columns for layout
col1, col2 = st.columns([3, 1])

# Display training info in sidebar
with col2:
    st.info("**About this training**\n\n"
            "This interactive password security course will test your knowledge with 5 key questions.\n\n"
            "You'll create passwords, learn best practices, and receive expert feedback on your password strength.")
    
    # Show progress with custom styling in the sidebar only
    if st.session_state[question_number_key] > 0:
        # Calculate progress percentage
        progress_percent = min((st.session_state[question_number_key]) * 20, 100)
        question_display = min(st.session_state[question_number_key], 5)
        
        st.write(f"**Progress: {question_display}/5 questions**")
        st.progress(progress_percent)
    
    # Display password tips in the sidebar
    st.markdown("""
    <div class="password-container">
    <h3>Password Security Best Practices</h3>
    <ul>
        <li><strong>Length Matters:</strong> Aim for 12+ characters</li>
        <li><strong>Mix Characters:</strong> Use uppercase, lowercase, numbers, and symbols</li>
        <li><strong>Avoid Patterns:</strong> No keyboard patterns (qwerty) or sequential numbers</li>
        <li><strong>No Personal Info:</strong> Don't use names, birthdays, or personal details</li>
        <li><strong>Use Unique Passwords:</strong> Never reuse passwords across accounts</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Display random security fact
    st.markdown(f"""
    <div class="security-fact">
        <strong>💡 Security Fact:</strong> {st.session_state.random_fact}
    </div>
    """, unsafe_allow_html=True)

# Use the full width for the chat interface
with col1:
    st.write("---")

    # Initialize the training with fixed approach - using page-specific keys
    if not st.session_state[started_key]:
        # Set the initial system prompt
        st.session_state[messages_key] = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add context
        st.session_state[messages_key].append({"role": "user", "content": f"Let's start the password security training."})
        
        # Use our predefined first question to ensure consistency
        first_message = FIRST_QUESTION
        
        # Add to message history
        st.session_state[messages_key].append({"role": "assistant", "content": first_message})
        st.session_state[started_key] = True

    # Display message history with custom styling - using page-specific keys
    for idx, message in enumerate(st.session_state[messages_key]):
        # Skip system messages and the initial context message
        if message["role"] == "system":
            continue
        if idx == 1 and message["role"] == "user" and "Let's start the password security training" in message["content"]:
            continue
        
        # Display the message with enhanced formatting
        st.markdown(format_message(message["content"], message["role"]), unsafe_allow_html=True)
    
    # IMPORTANT CHANGE: Use our new function to display the appropriate interface
    # This replaces all the previous conditional logic for different question types
    display_interface(col1)