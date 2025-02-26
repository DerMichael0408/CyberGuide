import streamlit as st
import ollama
import re
import time
import os

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

# Set page config for wider layout and custom title/icon
st.set_page_config(
    page_title="Phishing Awareness Training",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling - unchanged
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
    .email-container {
        background-color: #f9f9f9;
        border-radius: 10px;
        border-left: 5px solid #ff4757;
        padding: 20px;
        margin-bottom: 25px;
        font-family: monospace;
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
        padding: 8px 12px;
        margin: 5px 0;
        background-color: #f8f9fa;
        border-radius: 6px;
        border-left: 3px solid #6c757d;
    }
    .question-text {
        font-size: 17px;
        margin-bottom: 15px;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced phishing email content - unchanged
email_text = """
From: security-alerts@globalbank-verification.com
To: employee@company.com
Subject: URGENT: Your GlobalBank Account Has Been Compromised

Dear Valued Customer,

We have detected unusual activity on your GlobalBank account that requires immediate attention. Our security systems have flagged multiple suspicious login attempts from an unrecognized location.

To prevent unauthorized transactions, your account access has been temporarily limited. You must verify your identity within 24 hours to avoid account suspension.

✅ Verify Your Account Now: https://globelbank-security-portal.com/verify

Please note:
- This process takes only 2 minutes
- You will need your account credentials and SSN
- Failure to verify will result in immediate account suspension

If you did not initiate these login attempts, please complete the verification immediately to secure your account.

For security reasons, do not reply to this email.

Sincerely,
John Wilson
Head of Security
GlobalBank Customer Protection Team
"""

# System Prompt - unchanged
SYSTEM_PROMPT = """
## PHISHING AWARENESS TRAINING PROTOCOL
You are a Cybersecurity Training Assistant delivering an interactive 5-question phishing awareness training.

## QUESTION SEQUENCE (MUST FOLLOW EXACTLY)
The training consists of exactly these 5 questions in this order:

1. "Looking at the sample email provided, what are three specific red flags that indicate this is a phishing attempt?"

2. "Which of these URLs is most suspicious and why?
   A) https://company-payroll.com/login
   B) https://globelbank-security-portal.com/verify
   C) https://accounts.google.com/signin
   D) https://yourcompany.com/reset-password"

3. "If you accidentally clicked on the phishing link in the email, what immediate steps should you take to minimize potential damage?"

4. "The email creates a false sense of urgency by mentioning a 24-hour deadline. Why is creating urgency a common tactic in phishing attacks?"

5. "What specific security measures can organizations implement to reduce the risk of successful phishing attacks against their employees?"

## CRITICAL RESPONSE FORMAT
YOU MUST:
1. Start with "This is a phishing awareness exercise" and ask Question 1
2. For each user response:
   a. FIRST provide informative feedback on their answer (1-2 sentences)
   b. THEN immediately ask the next question in sequence
3. Format multiple choice options in a clean, visually appealing way
4. ALWAYS include the correct question number (e.g., "Question 2/5:", "Question 3/5:", etc.)
5. NEVER repeat a question
6. NEVER use lettered points (a), b), etc.) in your feedback - use plain text only

## FORMATTING GUIDELINES
- For Question 2 (multiple choice), format the options in a clean, visually appealing way
- Make questions visually distinct by using proper spacing
- Keep feedback concise and focused on key learning points
- Use clear language that's easy to understand
"""

# Scoring Instructions - unchanged
SCORING_INSTRUCTIONS = """
## SCIENTIFIC PHISHING AWARENESS ASSESSMENT

Conduct a rigorous and scientific evaluation of the user's phishing awareness based on their 5 responses.

### Scientific Assessment Framework:
When calculating the final score, consider these key areas (but do NOT include separate scores for each in your output):

1. **Threat Recognition**: Ability to identify phishing indicators (URLs, sender details, urgency tactics)
2. **Technical Knowledge**: Understanding of phishing infrastructure and methodology
3. **Response Protocols**: Knowledge of appropriate actions when encountering potential threats
4. **Preventative Measures**: Awareness of organizational and personal security practices
5. **Critical Thinking**: Application of analytical reasoning to security scenarios

### Output Format Requirements:
You MUST use EXACTLY this format:

```
Thank you for completing the phishing awareness training. Your final score is: [X]/100.

Scientific Assessment: [3-4 sentences providing evidence-based evaluation of their phishing awareness, including strengths, areas for improvement, and specific recommendations]
```

The score should be a precise reflection of their demonstrated knowledge, not an arbitrary number. Use the assessment framework internally to calculate it, but only output the final score.
"""

# Questions list - unchanged
questions = [
    "Looking at the sample email provided, what are three specific red flags that indicate this is a phishing attempt?",
    "Which of these URLs is most suspicious and why?\nA) https://company-payroll.com/login\nB) https://globelbank-security-portal.com/verify\nC) https://accounts.google.com/signin\nD) https://yourcompany.com/reset-password",
    "If you accidentally clicked on the phishing link in the email, what immediate steps should you take to minimize potential damage?",
    "The email creates a false sense of urgency by mentioning a 24-hour deadline. Why is creating urgency a common tactic in phishing attacks?",
    "What specific security measures can organizations implement to reduce the risk of successful phishing attacks against their employees?"
]

# First question - unchanged
FIRST_QUESTION = "This is a phishing awareness exercise. I will ask you 5 questions about phishing detection.\n\nQuestion 1/5: Looking at the sample email provided, what are three specific red flags that indicate this is a phishing attempt?"

# Function to format multiple choice options - unchanged
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

# Function to ensure correct question sequencing - unchanged
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
        "Question 1/5:", "Question 2/5:", "Question 3/5:", "Question 4/5:", "Question 5/5:",
        "Looking at the sample", "Which of these URLs", "If you accidentally", 
        "The email creates", "What specific security"
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

# Function to format messages - unchanged
def format_message(message, role):
    if role == "user":
        return f'<div class="user-message">{message}</div>'
    else:
        # Format assistant messages by highlighting the question number
        if "Question" in message and "/5:" in message:
            # Split by question marker to highlight it
            parts = re.split(r'(Question \d/5:)', message, 1)
            if len(parts) > 1:
                feedback = parts[0].strip()
                question_part = parts[1]
                question_text = parts[2] if len(parts) > 2 else ""
                
                formatted = ""
                if feedback:
                    formatted += f'<div class="feedback">{feedback}</div>'
                
                # Format question number
                formatted_question = f'<span class="question-number">{question_part}</span>'
                
                # Format the question text (with special handling for multiple choice)
                if "A)" in question_text and "B)" in question_text:
                    formatted_content = format_multiple_choice(question_text)
                    formatted += f'<div>{formatted_question} {formatted_content}</div>'
                else:
                    formatted += f'<div>{formatted_question} {question_text}</div>'
                
                return f'<div class="assistant-message">{formatted}</div>'
        
        # Default formatting for other assistant messages
        return f'<div class="assistant-message">{message}</div>'

# Initialize page-specific session state
if messages_key not in st.session_state:
    st.session_state[messages_key] = []
    
if question_number_key not in st.session_state:
    st.session_state[question_number_key] = 0
    
if started_key not in st.session_state:
    st.session_state[started_key] = False

# Display the training title
st.markdown('<div class="big-title">🛡️ Phishing Awareness Training</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Complete this interactive training to strengthen your defenses against phishing attacks</div>', unsafe_allow_html=True)
st.markdown(f"<div style='text-align: center; color: #666;'>Page: {current_page}</div>", unsafe_allow_html=True)

# Add columns for layout
col1, col2 = st.columns([2, 1])

# Display phishing email for reference with custom styling
with col1:
    with st.expander("📧 Sample Phishing Email", expanded=True):
        st.markdown(f'<div class="email-container">{email_text}</div>', unsafe_allow_html=True)

# Display training info in sidebar
with col2:
    st.info("**About this training**\n\n"
            "This interactive phishing awareness course will test your knowledge with 5 key questions.\n\n"
            "Answer carefully! Each response affects your final score.")
    
    # Show progress with custom styling in the sidebar only
    if st.session_state[question_number_key] > 0:
        # Calculate progress percentage
        progress_percent = min((st.session_state[question_number_key]) * 20, 100)
        question_display = min(st.session_state[question_number_key], 5)
        
        st.write(f"**Progress: {question_display}/5 questions**")
        st.progress(progress_percent)

# Use the full width for the chat interface
st.write("---")

# Initialize the training with fixed approach - using page-specific keys
if not st.session_state[started_key]:
    # Set the initial system prompt
    st.session_state[messages_key] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add the email as context (but don't display this)
    st.session_state[messages_key].append({"role": "user", "content": f"Let's start the phishing training. The user can see the email in the UI already."})
    
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
    if idx == 1 and message["role"] == "user" and "Let's start the phishing training" in message["content"]:
        continue
    
    # Display the message with enhanced formatting
    st.markdown(format_message(message["content"], message["role"]), unsafe_allow_html=True)

# User input field with custom prompt
user_input = st.chat_input("Type your answer here...")

if user_input:
    # Append user input to page-specific chat history
    st.session_state[messages_key].append({"role": "user", "content": user_input})
    st.markdown(format_message(user_input, "user"), unsafe_allow_html=True)
    
    # If we've completed all 5 questions, generate final score
    if st.session_state[question_number_key] == 4:  # This is the answer to Question 5
        with st.spinner("Conducting scientific assessment of your phishing awareness..."):
            # For visual effect, add a short delay
            #time.sleep(1.5)
            
            # Generate final score with scientific assessment
            final_score_messages = st.session_state[messages_key] + [{"role": "system", "content": SCORING_INSTRUCTIONS}]
            final_score_response = ollama.chat(model="llava:latest", messages=final_score_messages)
            final_score = final_score_response["message"]["content"]
            
            # Extract score for visual display
            score_match = re.search(r'(\d+)/100', final_score)
            if score_match:
                score_num = int(score_match.group(1))
                
                # Extract assessment text
                assessment_text = ""
                if "Scientific Assessment:" in final_score:
                    assessment_text = final_score.split("Scientific Assessment:")[1].strip()
                
                # Create enhanced visual score display
                score_html = f"""
                <div class="score-container">
                    <h2>Training Complete! 🎉</h2>
                    <h1 style="font-size: 48px; margin: 20px 0;">{score_num}/100</h1>
                    <p>{assessment_text}</p>
                </div>
                """
                st.markdown(score_html, unsafe_allow_html=True)
            else:
                # Fallback if score parsing fails
                st.markdown(format_message(final_score, "assistant"), unsafe_allow_html=True)
                
            # Add to message history
            st.session_state[messages_key].append({"role": "assistant", "content": final_score})
            
            #Update all_chat with local chat history
            if "all_chats" not in st.session_state:
                st.session_state["all_chats"] = {}
            st.session_state["all_chats"][current_page] = st.session_state[messages_key]
            #print(st.session_state["all_chats"])    
            
            # Update progress to show 5/5
            with col2:
                st.write(f"**Progress: 5/5 questions**")
                st.progress(100)
            
            # Show certificate button
            st.success("🎓 Training completed successfully! Your results have been recorded.")
            if st.button("📜 Download Certificate of Completion"):
                st.info("Certificate generation would be implemented here in a production environment.")
    else:
        # Generate AI response for the next question
        with st.spinner("Analyzing your response..."):
            # For visual effect, add a short delay
            #time.sleep(0.5)
            
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
            
            # Update progress in the sidebar
            with col2:
                question_display = min(st.session_state[question_number_key], 5)
                progress_percent = min(st.session_state[question_number_key] * 20, 100)
                st.write(f"**Progress: {question_display}/5 questions**")
                st.progress(progress_percent)

# Debug information (optional) - comment out in production
# st.sidebar.write(f"Current page: {current_page}")
# st.sidebar.write(f"Messages key: {messages_key}")
# st.sidebar.write(f"Question number: {st.session_state[question_number_key]}")