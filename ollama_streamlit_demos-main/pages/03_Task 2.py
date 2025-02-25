import streamlit as st
import ollama
import re
import time

# Set page config for wider layout and custom title/icon
st.set_page_config(
    page_title="Phishing Awareness Training",
    page_icon="🛡️",
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
</style>
""", unsafe_allow_html=True)

# Email content
email_text = """
Subject: "Action Required: Payroll Update to Avoid Salary Delay!"

From: payroll@yourcompany-support.com
To: You
Subject: Urgent: Payroll System Update Required

Dear [Your Name],

We have recently updated our payroll system to enhance security and ensure compliance with the latest regulations. To prevent any delays in your upcoming salary payment, please log in to confirm your account details.

Click the secure link below to verify your account before 5:00 PM today:

🔗 Update Payroll Information

Failure to complete this verification may result in a delay or disruption in salary disbursement.

Thank you for your prompt attention.

Best regards,
HR & Payroll Team
YourCompany Inc.
"""

# Fixed System Prompt with stronger guardrails
SYSTEM_PROMPT = """
## MANDATORY PHISHING TRAINING PROCEDURE
You are a Cybersecurity Training Assistant delivering a 5-question phishing awareness training.
You MUST follow this EXACT question sequence.

## STRICT QUESTION SEQUENCE
The training consists of exactly these 5 questions asked in this order:

1. "How can you recognize that this is a phishing email?"
2. "Which of these links is most suspicious? A) https://yourcompany-support.com/reset-password B) https://secure-yourcompany.com/login C) https://gogle.com/security-update D) https://yourcompany.com/hr-portal"
3. "You accidentally clicked the link. What is the safest next step?"
4. "Why do attackers create a sense of urgency in phishing emails?"
5. "What steps can your organization take to prevent phishing attacks?"

## CRITICAL RESPONSE FORMAT
YOU MUST:
1. Start with "This is a phishing awareness exercise" and ask Question 1
2. For Questions 2-5: ONLY give brief feedback on the previous answer (1-2 sentences), then ask THE NEXT question
3. NEVER repeat a question that has already been asked
4. NEVER ask more than one question at a time
5. ALWAYS include the correct question number (e.g., "Question 2/5:", "Question 3/5:", etc.)

IMPORTANT: When the user answers Question X, your next response MUST contain Question X+1.
"""

# Simplified Scoring Prompt
SCORING_INSTRUCTIONS = """
## PHISHING AWARENESS EVALUATION
Evaluate the user's 5 responses and provide a numerical score using EXACTLY this format:

```
Thank you for completing the phishing awareness training. Your final score is: [X]/100.

Feedback: [1-2 sentences of personalized feedback about their overall performance]
```

Use actual numbers, not placeholders. The score should reflect their overall understanding of phishing threats and preventative measures.
"""

# List of questions to enforce the sequence
questions = [
    "How can you recognize that this is a phishing email?",
    "Which of these links is most suspicious?\nA) https://yourcompany-support.com/reset-password\nB) https://secure-yourcompany.com/login\nC) https://gogle.com/security-update\nD) https://yourcompany.com/hr-portal",
    "You accidentally clicked the link. What is the safest next step?",
    "Why do attackers create a sense of urgency in phishing emails?",
    "What steps can your organization take to prevent phishing attacks?"
]

# Function to forcibly set the next question based on the question number
def force_next_question(response, current_question_num):
    if current_question_num >= 4:  # If we've already asked Question 5, return as is
        return response
    
    # Remove any incorrect numbering or repeated question text
    feedback = re.sub(r'Question \d/5:.*', '', response).strip()
    
    # Keep feedback concise (max 2 sentences)
    sentences = re.split(r'(?<=[.!?])\s+', feedback)
    short_feedback = ' '.join(sentences[:2])
    
    # Enforce correct next question
    next_question_num = current_question_num + 1
    next_question_text = f"Question {next_question_num}/5: {questions[next_question_num]}"
    
    return f"{short_feedback}\n\n{next_question_text}"

# Function to format messages with custom styling
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
                rest = parts[2] if len(parts) > 2 else ""
                
                formatted = ""
                if feedback:
                    formatted += f'<div class="feedback">{feedback}</div>'
                formatted += f'<div><span class="question-number">{question_part}</span>{rest}</div>'
                return f'<div class="assistant-message">{formatted}</div>'
        
        # Default formatting for other assistant messages
        return f'<div class="assistant-message">{message}</div>'

# Initialize Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Initialize question counter 
if "question_number" not in st.session_state:
    st.session_state.question_number = 0
    
# Initialize to track if we've started
if "started" not in st.session_state:
    st.session_state.started = False

# Display the training title with better styling
st.markdown('<div class="big-title">🛡️ Phishing Awareness Training</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Complete this interactive training to strengthen your defenses against phishing attacks</div>', unsafe_allow_html=True)

# Add columns for layout
col1, col2 = st.columns([2, 1])

# Display initial email for reference with custom styling
with col1:
    with st.expander("📧 Sample Phishing Email", expanded=True):
        st.markdown(f'<div class="email-container">{email_text}</div>', unsafe_allow_html=True)

# Display training info in sidebar
with col2:
    st.info("**About this training**\n\n"
            "This interactive phishing awareness course will test your knowledge with 5 key questions.\n\n"
            "Answer carefully! Each response affects your final score.")
    
    # Show progress with custom styling
    if st.session_state.question_number > 0:
        st.write(f"**Progress: {st.session_state.question_number}/5 questions**")
        progress = st.progress(min(st.session_state.question_number * 20, 100))

# Use the full width for the chat interface
st.write("---")

# Start the training when the app loads
if not st.session_state.started:
    # Set the initial system prompt
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add the email as context
    st.session_state.messages.append({"role": "user", "content": f"Let's start the phishing training using this email:\n\n{email_text}"})
    
    # Get first question from LLM
    with st.spinner("Preparing your training..."):
        response = ollama.chat(model="llava:latest", messages=st.session_state.messages)
        first_message = response["message"]["content"]
        
        # Force the first question to be correct
        if "Question 1/5:" not in first_message:
            first_message = "This is a phishing awareness exercise. I will ask you 5 questions about phishing detection.\n\nQuestion 1/5: How can you recognize that this is a phishing email?"
        
        # Add to message history
        st.session_state.messages.append({"role": "assistant", "content": first_message})
        st.session_state.started = True

# Display message history with custom styling
for idx, message in enumerate(st.session_state.messages):
    if message["role"] != "system":  # Skip system messages
        st.markdown(format_message(message["content"], message["role"]), unsafe_allow_html=True)

# User input field with custom prompt
user_input = st.chat_input("Type your answer here...")

if user_input:
    # Append user input to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(format_message(user_input, "user"), unsafe_allow_html=True)
    
    # If we've completed all 5 questions, generate final score
    if st.session_state.question_number == 4:  # This is the answer to Question 5
        with st.spinner("Evaluating your responses..."):
            # For visual effect, add a short delay
            time.sleep(1)
            
            # Generate final score
            final_score_messages = st.session_state.messages + [{"role": "system", "content": SCORING_INSTRUCTIONS}]
            final_score_response = ollama.chat(model="llava:latest", messages=final_score_messages)
            final_score = final_score_response["message"]["content"]
            
            # Extract score for visual display
            score_match = re.search(r'(\d+)/100', final_score)
            if score_match:
                score_num = int(score_match.group(1))
                
                # Create visual score display
                score_html = f"""
                <div class="score-container">
                    <h2>Training Complete! 🎉</h2>
                    <h1 style="font-size: 48px; margin: 20px 0;">{score_num}/100</h1>
                    <p>{final_score.split('Feedback:')[1].strip() if 'Feedback:' in final_score else ''}</p>
                </div>
                """
                st.markdown(score_html, unsafe_allow_html=True)
            else:
                # Fallback if score parsing fails
                st.markdown(format_message(final_score, "assistant"), unsafe_allow_html=True)
                
            # Add to message history
            st.session_state.messages.append({"role": "assistant", "content": final_score})
            
            # Update progress bar to 100%
            progress = st.progress(100)
            
            # Show certificate button
            st.success("🎓 Training completed successfully! Your results have been recorded.")
            if st.button("📜 Download Certificate of Completion"):
                st.info("Certificate generation would be implemented here in a production environment.")
    else:
        # Generate AI response for the next question
        with st.spinner("Processing your answer..."):
            # For visual effect, add a short delay
            time.sleep(0.5)
            
            response = ollama.chat(model="llava:latest", messages=st.session_state.messages)
            ai_message = response["message"]["content"]
            
            # CRITICAL FIX: Force the correct next question regardless of what the LLM returns
            ai_message = force_next_question(ai_message, st.session_state.question_number)
            
            # Display response with custom formatting
            st.markdown(format_message(ai_message, "assistant"), unsafe_allow_html=True)
                
            # Add to message history
            st.session_state.messages.append({"role": "assistant", "content": ai_message})
            
            # Increment question counter
            st.session_state.question_number += 1
            
            # Update progress
            if "progress" in locals():
                progress.progress(st.session_state.question_number * 20)