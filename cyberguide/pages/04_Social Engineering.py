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
    page_title="Social Engineering Training",
    page_icon="🕵️",
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
    .scenario-container {
        background-color: #f9f9f9;
        border-radius: 10px;
        border-left: 5px solid #6366F1;
        padding: 20px;
        margin-bottom: 25px;
        font-family: sans-serif;
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
    .conversation-bubble {
        margin: 8px 0;
        padding: 10px 15px;
        border-radius: 18px;
        max-width: 80%;
        position: relative;
    }
    .visitor-bubble {
        background-color: #6366F1;
        color: white;
        border-bottom-left-radius: 5px;
        margin-right: auto;
    }
    .employee-bubble {
        background-color: #E5E7EB;
        color: #333;
        border-bottom-right-radius: 5px;
        margin-left: auto;
    }
    .bubble-name {
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 4px;
    }
    /* Fix for input field positioning */
    .chat-input-container {
        position: sticky;
        bottom: 0;
        background-color: white;
        padding-top: 20px;
        margin-top: 10px;
        z-index: 100;
        border-top: 1px solid #eee;
    }
    /* Hide default Streamlit components that may interfere with layout */
    .block-container {
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Social engineering scenario content
scenario_text = """
<div class="scenario-title">Office Building Visitor Scenario</div>

<p>You work at a tech company called SecureTech Solutions, handling sensitive customer data and product information. You're at your desk when an unfamiliar person approaches you:</p>

<div class="conversation-bubble visitor-bubble">
    <div class="bubble-name">Visitor:</div>
    Hi there! I'm David from IT support. We've detected some unusual activity on the network affecting this floor. I need to check your workstation quickly. It'll just take a minute - I need to install a security patch before the vulnerability spreads.
</div>

<div class="conversation-bubble employee-bubble">
    <div class="bubble-name">You:</div>
    Oh, I didn't get any notification about this.
</div>

<div class="conversation-bubble visitor-bubble">
    <div class="bubble-name">Visitor:</div>
    Yeah, we're just going around in person - it was faster than sending emails to everyone. It's pretty urgent. Several machines are already affected. I just need your login credentials to run the patch without triggering the security alerts.
</div>

<div class="conversation-bubble employee-bubble">
    <div class="bubble-name">You:</div>
    Hmm, I see. You need my credentials?
</div>

<div class="conversation-bubble visitor-bubble">
    <div class="bubble-name">Visitor:</div>
    Yes, or you can step away and I'll type them in if you're more comfortable with that. I just need to run the patch as an admin user. The CTO authorized this - you can call him if you want, but he's in meetings all day. Several people on this floor have already done it.
</div>

<p>The visitor is wearing casual clothes with no visible company ID badge. He has a laptop and seems to be in a hurry.</p>
"""

# The 5 questions for the training
QUESTIONS = [
    "Based on the scenario described, what are three red flags that suggest this might be a social engineering attempt?",
    
    "What is the most appropriate first response to this situation?\nA) Give the visitor your credentials since the CTO approved it\nB) Ask to see identification and verify with IT department\nC) Step away and let the visitor use your computer\nD) Tell the visitor to come back later when you're less busy",
    
    "Which principle of social engineering is the visitor using when they say 'Several people on this floor have already done it'?",
    
    "What should you do if you've already shared sensitive information with a suspected social engineer?",
    
    "What security protocols should your organization implement to prevent this type of social engineering attack?"
]

# System prompt with structured instructions and explicit question tracking
SYSTEM_PROMPT = """
## SOCIAL ENGINEERING AWARENESS TRAINING PROTOCOL
You are a Cybersecurity Training Assistant delivering an interactive 5-question social engineering awareness training.

## QUESTION SEQUENCE (MUST FOLLOW EXACTLY)
The training consists of exactly these 5 questions in this order:

1. "Based on the scenario described, what are three red flags that suggest this might be a social engineering attempt?"

2. "What is the most appropriate first response to this situation?
   A) Give the visitor your credentials since the CTO approved it
   B) Ask to see identification and verify with IT department
   C) Step away and let the visitor use your computer
   D) Tell the visitor to come back later when you're less busy"

3. "Which principle of social engineering is the visitor using when they say 'Several people on this floor have already done it'?"

4. "What should you do if you've already shared sensitive information with a suspected social engineer?"

5. "What security protocols should your organization implement to prevent this type of social engineering attack?"

## CRITICAL RESPONSE FORMAT
YOU MUST:
1. Start with "This is a social engineering awareness exercise" and ask Question 1
2. For each user response:
   a. FIRST provide informative feedback on their answer to the CURRENT question only (1-2 sentences)
   b. THEN immediately ask the next question in sequence
3. Format multiple choice options in a clean, visually appealing way
4. ALWAYS include the correct question number (e.g., "Question 2/5:", "Question 3/5:", etc.)
5. NEVER repeat a question
6. NEVER use lettered points (a), b), etc.) in your feedback - use plain text only
7. NEVER skip ahead - always provide feedback for the current question number

## QUESTION TRACKING
YOU MUST TRACK WHICH QUESTION NUMBER THE USER IS CURRENTLY ANSWERING:
- If the last question in the conversation was "Question 1/5", then provide feedback on Question 1 and ask Question 2/5
- If the last question in the conversation was "Question 2/5", then provide feedback on Question 2 and ask Question 3/5
- And so on

## FEEDBACK GUIDELINES
For each question, evaluate the user's response and provide appropriate feedback:

Question 1: Highlight key red flags they identified correctly or missed, such as:
- No visible ID badge
- Requesting login credentials (against standard security protocols)
- Creating urgency to pressure a decision
- Claiming authority (CTO approval) without verification
- Mentioning others have complied (social proof)

Question 2: The correct answer is B. Explain briefly why verification is crucial.

Question 3: The principle is "social proof" - the tendency to follow what others are doing.

Question 4: Good responses include immediately reporting the incident, changing passwords, and following incident response protocols.

Question 5: Look for mentions of visitor management systems, ID verification, security awareness training, clear protocols for system maintenance, etc.

## FORMATTING GUIDELINES
- For Question 2 (multiple choice), format the options in a clean, visually appealing way
- Make questions visually distinct by using proper spacing
- Keep feedback concise and focused on key learning points
- Use clear language that's easy to understand
"""

# Scoring instructions
SCORING_INSTRUCTIONS = """
## SOCIAL ENGINEERING ASSESSMENT

Conduct a rigorous and scientific evaluation of the user's social engineering awareness based on their 5 responses.

### Assessment Framework:
When calculating the final score, consider these key areas (but do NOT include separate scores for each in your output):

1. **Threat Detection**: Ability to identify social engineering tactics and red flags (25%)
2. **Response Knowledge**: Understanding of appropriate responses to potential attacks (25%)
3. **Principle Recognition**: Awareness of psychological principles used in social engineering (15%) 
4. **Incident Handling**: Knowledge of proper procedures after a security incident (15%)
5. **Preventative Measures**: Understanding of organizational controls against social engineering (20%)

### Output Format Requirements:
You MUST use EXACTLY this format:

```
Thank you for completing the social engineering awareness training. Your final score is: [X]/100.

Security Assessment: [3-4 sentences providing evidence-based evaluation of their social engineering awareness, including strengths, areas for improvement, and specific recommendations]
```

The score should be a precise reflection of their demonstrated knowledge, not an arbitrary number. Use the assessment framework internally to calculate it, but only output the final score.
"""

# First question
FIRST_QUESTION = "This is a social engineering awareness exercise. I will ask you 5 questions about recognizing and responding to social engineering attempts.\n\nQuestion 1/5: Based on the scenario described, what are three red flags that suggest this might be a social engineering attempt?"

# Function to format multiple choice options with improved regex pattern
def format_multiple_choice(question_text):
    """Format multiple choice options with better styling"""
    if "A)" in question_text and "B)" in question_text:
        # Split the question into the prompt and options
        parts = question_text.split("A)", 1)
        main_text = parts[0]
        options_text = "A)" + parts[1] if len(parts) > 1 else ""
        
        # Use a more robust regex pattern to correctly capture all options
        option_pattern = r'([A-D]\))(.*?)(?=[A-D]\)|$)'
        options = re.findall(option_pattern, options_text, re.DOTALL)
        
        formatted_options = ""
        for opt_letter, opt_text in options:
            formatted_options += f'<div class="multiple-choice-option">{opt_letter}{opt_text.strip()}</div>'
        
        # Combine with styled question text
        return f'<div class="question-text">{main_text}</div><div class="multiple-choice">{formatted_options}</div>'
    else:
        # For non-multiple choice, just add basic styling
        return f'<div class="question-text">{question_text}</div>'

# Helper function to get next question response with explicit question tracking
def get_next_question_response(messages, current_question_num):
    """
    Gets response from LLM with explicit instruction about current question
    """
    # Create a copy of messages to modify for this specific request
    request_messages = messages.copy()
    
    # Add explicit instruction about which question we're on
    instruction = {
        "role": "system", 
        "content": f"IMPORTANT: The user is currently answering Question {current_question_num}/5. " +
                  f"Provide feedback ONLY for Question {current_question_num}/5 and then ask Question {current_question_num + 1}/5."
    }
    
    # Add the instruction to the request
    request_messages.append(instruction)
    
    # Get response from LLM
    response = ollama.chat(model="llava:latest", messages=request_messages)
    return response["message"]["content"]

# Function to ensure correct question sequencing
def force_next_question(response, current_question_num):
    """
    Extracts feedback from AI response and adds the next correct question.
    Removes any lettered points (a), b), etc.) and ensures clean formatting.
    """
    # Get the next question number (0-indexed internally, 1-indexed for display)
    next_question_idx = current_question_num
    
    # If we're done with questions, just return the response
    if next_question_idx >= 5:
        return response
    
    # Process AI feedback
    # First, let's check if the AI has already included the correct next question
    next_question_marker = f"Question {next_question_idx + 1}/5:"
    
    if next_question_marker in response:
        # The AI included the correct next question, so just clean up the response if needed
        cleaned_text = response
    else:
        # The AI did not include the correct next question or included the wrong one
        # Remove any existing questions
        question_patterns = [
            "Question 1/5:", "Question 2/5:", "Question 3/5:", "Question 4/5:", "Question 5/5:",
            "Based on the scenario", "What is the most appropriate", "Which principle of social", 
            "What should you do if", "What security protocols"
        ]
        
        # Get the feedback portion by removing question text
        cleaned_text = response
        for pattern in question_patterns:
            if pattern in cleaned_text:
                parts = cleaned_text.split(pattern, 1)
                cleaned_text = parts[0]
        
        # Remove any lettered or numbered points
        cleaned_text = re.sub(r'[a-z]\)\s+', '', cleaned_text)
        cleaned_text = re.sub(r'[A-Z]\)\s+', '', cleaned_text)
        cleaned_text = re.sub(r'\d+\.\s+', '', cleaned_text)
        cleaned_text = re.sub(r'•\s+', '', cleaned_text)
        
        # Remove "Progress: X/5 questions" text if it appears
        cleaned_text = re.sub(r'Progress: \d/5 questions', '', cleaned_text)
    
    # Ensure we get at least one complete sentence of feedback
    sentences = re.split(r'(?<=[.!?])\s+', cleaned_text.strip())
    
    # Make sure we have at least one sentence but not more than 3
    feedback = ' '.join(sentences[:min(3, len(sentences))]).strip()
    
    # Build the correct next question text with proper numbering
    display_num = next_question_idx + 1
    next_question = f"Question {display_num}/5: {QUESTIONS[next_question_idx]}"
    
    # If the AI already included the correct next question, return as is
    if next_question_marker in response:
        return response
    
    # Combine feedback with next question, ensuring there's a proper break between them
    if feedback:
        return f"{feedback}\n\n{next_question}"
    else:
        # Fallback feedback if none was extracted
        return f"I understand your response.\n\n{next_question}"

# Function to format messages with custom styling
def format_message(message, role):
    if role == "user":
        return f'<div class="user-message">{message}</div>'
    else:
        # Format assistant messages with highlighted question number
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

# Display the training title with better styling
st.markdown('<div class="big-title">🕵️ Social Engineering Awareness Training</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Complete this interactive training to recognize and respond to social engineering attempts</div>', unsafe_allow_html=True)

# Add columns for layout
col1, col2 = st.columns([2, 1])

# Display scenario 
with col1:
    st.markdown(f'<div class="scenario-container">{scenario_text}</div>', unsafe_allow_html=True)

# Display training info in sidebar
with col2:
    st.info("**About this training**\n\n"
            "This interactive social engineering awareness course will test your knowledge with 5 key questions.\n\n"
            "Learn how to recognize and respond to social engineering attempts in the workplace.")
    
    # Show progress with custom styling in the sidebar only
    if st.session_state[question_number_key] > 0:
        # Calculate progress percentage
        progress_percent = min((st.session_state[question_number_key]) * 20, 100)
        question_display = min(st.session_state[question_number_key], 5)
        
        st.write(f"**Progress: {question_display}/5 questions**")
        st.progress(progress_percent)

# Create a dedicated container for messages (history)
message_container = st.container()

# Use the full width for the chat interface
with col1:
    st.write("---")

    # Initialize the training with fixed approach - using page-specific keys
    if not st.session_state[started_key]:
        # Set the initial system prompt
        st.session_state[messages_key] = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add the scenario as context (but don't display this)
        st.session_state[messages_key].append({"role": "user", "content": f"Let's start the social engineering training. The user can see the scenario in the UI already."})
        
        # Use our predefined first question to ensure consistency
        first_message = FIRST_QUESTION
        
        # Add to message history
        st.session_state[messages_key].append({"role": "assistant", "content": first_message})
        st.session_state[started_key] = True
        st.session_state[question_number_key] = 1

    # Create a container for the chat input at the bottom
    chat_input_container = st.container()

    # Display message history with custom styling - using page-specific keys
    with message_container:
        for idx, message in enumerate(st.session_state[messages_key]):
            # Skip system messages and the initial context message
            if message["role"] == "system":
                continue
            if idx == 1 and message["role"] == "user" and "Let's start the social engineering training" in message["content"]:
                continue
            
            # Display the message with enhanced formatting
            st.markdown(format_message(message["content"], message["role"]), unsafe_allow_html=True)

    # Create a spacer to ensure there's room before the input field
    st.write("")
    st.write("")
    
    # Wrap the chat input in its own container and custom HTML to pin it to bottom
    with chat_input_container:
        st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
        user_input = st.chat_input("Type your answer here...")
        st.markdown('</div>', unsafe_allow_html=True)

    if user_input:
        # Append user input to page-specific chat history
        st.session_state[messages_key].append({"role": "user", "content": user_input})
        
        # If we've completed all 5 questions, generate final score
        if st.session_state[question_number_key] == 5:  # This is the answer to Question 5
            with st.spinner("Conducting scientific assessment of your social engineering awareness..."):
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
                    if "Security Assessment:" in final_score:
                        assessment_text = final_score.split("Security Assessment:")[1].strip()
                    
                    # Create enhanced visual score display
                    score_html = f"""
                    <div class="score-container">
                        <h2>Training Complete! 🎉</h2>
                        <h1 style="font-size: 48px; margin: 20px 0;">{score_num}/100</h1>
                        <p>{assessment_text}</p>
                    </div>
                    """
                    
                    # Add to message history and rerun to update the display
                    st.session_state[messages_key].append({"role": "assistant", "content": final_score})
                    
                    # Update all_chat with local chat history
                    if "all_chats" not in st.session_state:
                        st.session_state["all_chats"] = {}
                    st.session_state["all_chats"][current_page] = st.session_state[messages_key]
                    
                    # Initialize scenario_scores if it doesn't exist
                    if "scenario_scores" not in st.session_state:
                        st.session_state.scenario_scores = {
                            "phishing": {"score": 0, "completed": False},
                            "password": {"score": 0, "completed": False},
                            "social": {"score": 0, "completed": False}
                        }
                    
                    # Only increment completed_number if social scenario wasn't already completed
                    if not st.session_state.scenario_scores["social"]["completed"]:
                        # Initialize completed_number if it doesn't exist
                        if "completed_number" not in st.session_state:
                            st.session_state.completed_number = 0
                        
                        # Increment the completed scenarios counter
                        st.session_state.completed_number += 1
                    
                    # Update the score and mark as completed
                    st.session_state.scenario_scores["social"] = {
                        "score": score_num,
                        "completed": True
                    }
                    
                    # Rerun to display updated state
                    st.rerun()
                
                else:
                    # Fallback if score parsing fails
                    st.session_state[messages_key].append({"role": "assistant", "content": final_score})
                    st.rerun()
        else:
            # Generate AI response for the next question - using the enhanced function
            with st.spinner("Analyzing your response..."):
                # Get response from LLM with explicit question tracking
                ai_message = get_next_question_response(
                    st.session_state[messages_key], 
                    st.session_state[question_number_key]
                )
                
                # Force the correct next question and include feedback
                fixed_message = force_next_question(ai_message, st.session_state[question_number_key])
                
                # Add to message history
                st.session_state[messages_key].append({"role": "assistant", "content": fixed_message})
                
                # Increment question counter
                st.session_state[question_number_key] += 1
                
                # Rerun to update the display with the new message
                st.rerun()

# Reset button (only show in completed state)
if st.session_state.get(question_number_key, 0) == 5 and len(st.session_state[messages_key]) > 7:  # At least 7 messages means training is completed
    with col1:
        # Display the final score after rerun
        for message in st.session_state[messages_key]:
            if message["role"] == "assistant" and "Thank you for completing" in message["content"]:
                score_match = re.search(r'(\d+)/100', message["content"])
                if score_match:
                    score_num = int(score_match.group(1))
                    assessment_text = ""
                    if "Security Assessment:" in message["content"]:
                        assessment_text = message["content"].split("Security Assessment:")[1].strip()
                    
                    score_html = f"""
                    <div class="score-container">
                        <h2>Training Complete! 🎉</h2>
                        <h1 style="font-size: 48px; margin: 20px 0;">{score_num}/100</h1>
                        <p>{assessment_text}</p>
                    </div>
                    """
                    st.markdown(score_html, unsafe_allow_html=True)
        
        # Show success message and certificate button
        st.success("🎓 Training completed successfully! Your results have been recorded.")
        if st.button("🔄 Start New Training"):
            # Reset all page-specific session state variables
            st.session_state[messages_key] = []
            st.session_state[question_number_key] = 0
            st.session_state[started_key] = False
            st.rerun()