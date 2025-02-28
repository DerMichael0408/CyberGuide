"""
03_Password Creation.py - Password security training module

An interactive Streamlit application for password security training
with LLM-driven evaluation and feedback.
"""

import streamlit as st
import ollama
import re
import time
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from utilities.template import setup_page

# Paths definition
BASE_DIR = Path(__file__).parent.parent  # Goes one level up from pages/
UTILITIES_DIR = BASE_DIR / "utilities" / "password_creation"

# Add path to Python path
sys.path.append(str(BASE_DIR))

# Import functions from the module
try:
    from utilities.password_creation.password_evaluation import (
        llm_evaluate_password_strength,
        llm_final_password_assessment,
        format_password_for_display,
        generate_password_options
    )
except ImportError as e:
    st.error(f"Error importing Password Evaluation module: {e}")
    
    # Define fallback functions if module import fails
    def llm_evaluate_password_strength(password):
        """Simple fallback implementation"""
        score = min(100, len(password) * 5)
        return {
            "score": score,
            "crack_time_display": "unknown",
            "feedback": {"warning": "", "suggestions": []}
        }
    
    def llm_final_password_assessment(password):
        """Simple fallback implementation"""
        score = min(100, len(password) * 5)
        return {
            "final_score": score,
            "assessment": "Password assessment unavailable.",
            "perfect_score_requirements": "Cannot determine requirements.",
            "strengths": [],
            "weaknesses": [],
            "improvement_suggestions": []
        }
    
    def format_password_for_display(password):
        """Mask password for display"""
        return "*" * len(password)
        
    def generate_password_options():
        """Password options with clear security levels"""
        return [
            {"letter": "A", "password": "password123", "description": "Common word with predictable numbers", "security_level": "Very Weak"},
            {"letter": "B", "password": "Summer2025!", "description": "Predictable pattern with season and year", "security_level": "Weak"},
            {"letter": "C", "password": "BlueHorse42!", "description": "Common words with numbers and symbols", "security_level": "Moderate"},
            {"letter": "D", "password": "j8K#p3vR!2sT&9qZ", "description": "Random mix of characters, numbers and symbols", "security_level": "Strong"}
        ]

# Set the evaluate_password_strength function
evaluate_password_strength = llm_evaluate_password_strength

# Load CSS file
def load_css():
    """Load CSS styling for the application"""
    css_file = UTILITIES_DIR / "password_styles.css"
    try:
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Minimal essential CSS only as fallback
        st.markdown("""
        <style>
        .main { padding: 2rem 3rem; }
        .big-title { font-size: 42px; font-weight: 700; margin-bottom: 10px; color: #1E3A8A; text-align: center; }
        .subtitle { font-size: 18px; margin-bottom: 30px; text-align: center; color: #666; }
        .user-message { background-color: #e6f3ff; border-radius: 10px; padding: 15px; margin: 5px 0; }
        .assistant-message { background-color: #f0f0f0; border-radius: 10px; padding: 15px; margin: 5px 0; }
        .question-number { font-weight: bold; color: #1E3A8A; }
        .feedback { padding: 10px; background-color: #f0f7ff; border-left: 3px solid #2196F3; margin-bottom: 10px; }
        .security-warning { background-color: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 15px 0; font-weight: bold; color: #c62828; }
        .security-fact { background-color: #fffde7; border-left: 4px solid #ffc107; padding: 15px; margin: 15px 0; font-style: italic; }
        .mc-option { display: block; padding: 10px; margin: 8px 0; background-color: #f5f5f5; border-radius: 5px; border-left: 3px solid #ccc; }
        
        /* Enhanced final assessment styling */
        .final-assessment { background-color: #f0f7ff; padding: 20px; border-radius: 10px; margin-top: 20px; border-left: 5px solid #2196F3; }
        .final-assessment h2 { text-align: center; margin-bottom: 20px; }
        .final-assessment h3 { margin-top: 20px; }
        .perfect-score { background-color: #e8f5e9; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4CAF50; }
        
        /* New enhanced score container similar to phishing training */
        .score-container {
            background: linear-gradient(to right, #4CAF50, #2196F3);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
        }
        
        /* Password options styling */
        .password-option { 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 8px; 
            border-left: 5px solid #ccc; 
        }
        .password-option-very-weak { 
            background-color: #ffebee; 
            border-left-color: #f44336; 
        }
        .password-option-weak { 
            background-color: #fff8e1; 
            border-left-color: #ffc107; 
        }
        .password-option-moderate { 
            background-color: #e8f5e9; 
            border-left-color: #4caf50; 
        }
        .password-option-strong { 
            background-color: #e3f2fd; 
            border-left-color: #2196f3; 
        }
        
        /* Password requirements box */
        .password-requirements {
            background-color: #e3f2fd;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        .password-requirements h4 {
            margin-top: 0;
            margin-bottom: 10px;
            color: #1565C0;
        }
        .password-requirements ul {
            margin-bottom: 0;
            padding-left: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

# Setup page
setup_page(
    page_title="Password Security Training",
    icon_emoji="🔒",
    subtitle="Learn how to create strong, secure passwords"
)

# Load CSS for additional styling specific to this module
load_css()

# Get the current page name from the file name
def get_current_page():
    """Get the current page name from the file name"""
    current_file = os.path.basename(__file__)
    page_name = os.path.splitext(current_file)[0]
    return page_name

# Get current page identifier
current_page = get_current_page()

# Function to get page-specific session state keys
def get_page_key(base_key):
    """Create page-specific session state keys to avoid conflicts"""
    return f"{current_page}_{base_key}"

# Create page-specific session keys
messages_key = get_page_key("messages")
question_number_key = get_page_key("question_number")
started_key = get_page_key("started")
first_password_key = get_page_key("first_password")
final_password_key = get_page_key("final_password")
security_fact_key = get_page_key("security_fact")
password_options_key = get_page_key("password_options")

# Questions list for password training with placeholder for question 2
questions = [
    "Imagine you need to set a secure password for a company system. Please enter your new password.",
    "Which of these passwords is the MOST secure?\n[PASSWORD_OPTIONS_PLACEHOLDER]",
    "What are three key factors that make a password strong and difficult to crack?",
    "What strategies can you use to create passwords that are both secure and memorable?",
    "Based on what you've learned, create a new secure password. We'll evaluate how much you've improved."
]

# System Prompt for password training
SYSTEM_PROMPT = """
## PASSWORD SECURITY TRAINING PROTOCOL
You are a Cybersecurity Training Assistant delivering an interactive 5-question password security training.

## QUESTION SEQUENCE (MUST FOLLOW EXACTLY)
The training consists of exactly these 5 questions in this order:

1. "Imagine you need to set a secure password for a company system. Please enter your new password."

2. "Which of these passwords is the MOST secure?"
   [The multiple choice options will be dynamically generated]

3. "What are three key factors that make a password strong and difficult to crack?"

4. "What strategies can you use to create passwords that are both secure and memorable?"

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

# First question - password training
FIRST_QUESTION = "This is a password security training exercise. I will guide you through 5 questions about creating and managing secure passwords.\n\nQuestion 1/5: Imagine you need to set a secure password for a company system. Please enter your new password."

# Function to generate security fact using LLM
def generate_security_fact(model="llava:latest"):
    """Generate a random security fact about passwords using LLM"""
    fact_prompt = """
    Generate ONE interesting and educational fact about password security. The fact should be:
    
    1. Accurate and informative
    2. Concise (under 150 characters)
    3. Focused on password creation, strength, or management
    
    EXAMPLES OF GOOD SECURITY FACTS:
    - "A longer password isn't always stronger. A 16-character password with only lowercase letters has as much entropy as a 4-character password with all character types."
    - "Using passphrases made up of unrelated words can be more secure than a short complex password."
    - "Password crackers use dictionaries of common words, so substituting letters with similar symbols provides little additional security."
    
    Respond with ONLY the fact - no introduction, explanation, or conclusion.
    """
    
    try:
        response = ollama.chat(model=model, messages=[{"role": "system", "content": fact_prompt}])
        fact = response["message"]["content"].strip()
        
        # Clean up the response to ensure it's just a single fact
        fact = fact.split('\n')[0]  # Take just the first line if multiple lines
        fact = re.sub(r'^["\']|["\']$', '', fact)  # Remove quotes if present
        
        return fact
    except Exception as e:
        # Fallback security fact if LLM generation fails
        return "Using a combination of uppercase, lowercase, numbers, and symbols increases password strength exponentially compared to using just one character type."

# Function to construct Question 2 with dynamically generated password options
def construct_question_2():
    """
    Generates multiple choice password options and constructs Question 2
    with these options.
    """
    # Generate or retrieve password options
    if password_options_key not in st.session_state:
        st.session_state[password_options_key] = generate_password_options()
    
    # Include options in the question with all passwords fully displayed
    options = st.session_state[password_options_key]
    
    # Construct the question
    question = "Which of these passwords is the MOST secure?\n\n"
    
    # Add all options as plain text, ensuring no placeholders
    for option in options:
        question += f"{option['letter']}) {option['password']}\n"
    
    return question

# Function to format messages
def format_message(message, role):
    """Format chat messages with simple styling"""
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
                
                # For all multiple choice questions (including password question)
                if "A)" in question_text and "B)" in question_text:
                    # Show the full question text with options for all multiple choice questions
                    formatted += f'<div>{formatted_question} {question_text}</div>'
                    
                    # Store the question number in session state
                    current_q_num = int(re.search(r'Question (\d+)/5:', message).group(1))
                    st.session_state["current_mc_question"] = current_q_num
                else:
                    formatted += f'<div>{formatted_question} {question_text}</div>'
                
                return f'<div class="assistant-message">{formatted}</div>'
        
        # Default formatting for other assistant messages
        return f'<div class="assistant-message">{message}</div>'

# Function to ensure correct question sequencing
def force_next_question(response, current_question_num):
    """
    Extracts feedback from AI response and adds the next correct question.
    Dynamically handles the password options for Question 2.
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
    
    # Remove any lettered or numbered points 
    cleaned_text = re.sub(r'[a-z]\)\s+', '', cleaned_text)
    cleaned_text = re.sub(r'[A-Z]\)\s+', '', cleaned_text)
    cleaned_text = re.sub(r'\d+\.\s+', '', cleaned_text)
    cleaned_text = re.sub(r'•\s+', '', cleaned_text)
    
    # Ensure we get at least one complete sentence of feedback
    sentences = re.split(r'(?<=[.!?])\s+', cleaned_text.strip())
    
    # Make sure we have at least one sentence but not more than 3
    feedback = ' '.join(sentences[:min(3, len(sentences))]).strip()
    
    # For Question 2, use dynamically generated password options
    if next_question_idx == 1:  # Going to question 2
        next_question = f"Question {next_question_idx+1}/5: {construct_question_2()}"
    else:
        next_question = f"Question {next_question_idx+1}/5: {questions[next_question_idx]}"
    
    # Combine feedback with next question, ensuring there's a proper break between them
    if feedback:
        return f"{feedback}\n\n{next_question}"
    else:
        # Fallback feedback if none was extracted
        return f"I understand your response.\n\n{next_question}"

# Extract multiple choice options
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

# Process user answers and move to next question
def process_answer(user_input):
    """Process the user's answer and move to the next question"""
    # Generate AI response for the next question
    with st.spinner("Analyzing your response..."):
        # Get response from LLM
        response = ollama.chat(model="llava:latest", messages=st.session_state[messages_key])
        ai_message = response["message"]["content"]
        
        # Force the correct next question and include feedback
        fixed_message = force_next_question(ai_message, st.session_state[question_number_key])
        
        # Display the fixed message with formatting
        st.markdown(format_message(fixed_message, "assistant"), unsafe_allow_html=True)
        
        # Add to message history
        st.session_state[messages_key].append({"role": "assistant", "content": fixed_message})
        
        # Increment question counter
        st.session_state[question_number_key] += 1

# Function to process multiple choice password answer
def process_mc_password_answer(selected_letter):
    """Process the multiple choice password answer with immediate LLM feedback"""
    # Get the options from session state
    options = st.session_state[password_options_key]
    
    # Find the selected option
    selected_option = None
    correct_option = None
    
    for option in options:
        if option["letter"] == selected_letter:
            selected_option = option
        if option["security_level"] == "Strong":
            correct_option = option
    
    # If no option was found (shouldn't happen), use fallback
    if not selected_option:
        selected_option = {"letter": selected_letter, "password": "Unknown", "security_level": "Unknown"}
    
    if not correct_option:
        correct_option = {"letter": "D", "password": options[-1]["password"], "security_level": "Strong"}
    
    # Construct prompt for LLM analysis
    analysis_prompt = f"""
    Analyze this password selection from a multiple choice question:
    
    Question: Which of these passwords is the MOST secure?
    
    Options:
    {', '.join([f"{opt['letter']}) {opt['password']} ({opt['security_level']})" for opt in options])}
    
    User selected: {selected_letter}) {selected_option['password']}
    
    Correct answer: {correct_option['letter']}) {correct_option['password']}
    
    Provide brief feedback (2-3 sentences) explaining:
    1. Whether the user's choice was correct or incorrect
    2. Why the selected password is strong/weak
    3. What makes the most secure password better
    
    Keep your response under 100 words and focus on educational value.
    DO NOT include the actual passwords in your response.
    """
    
    # Get LLM analysis
    with st.spinner("Analyzing your selection..."):
        analysis_response = ollama.chat(model="llava:latest", messages=[
            {"role": "system", "content": analysis_prompt}
        ])
        feedback = analysis_response["message"]["content"].strip()
    
    # Add user selection to chat history
    user_message = f"My answer is {selected_letter}."
    st.session_state[messages_key].append({"role": "user", "content": user_message})
    
    # Add the feedback to session state for next question
    mc_feedback = feedback
    
    # Force next question with our custom feedback
    next_question_idx = st.session_state[question_number_key] + 1
    next_question = f"Question {next_question_idx+1}/5: {questions[next_question_idx]}"
    ai_response = f"{mc_feedback}\n\n{next_question}"
    
    # Add to message history
    st.session_state[messages_key].append({"role": "assistant", "content": ai_response})
    
    # Display messages
    st.markdown(format_message(user_message, "user"), unsafe_allow_html=True)
    st.markdown(format_message(ai_response, "assistant"), unsafe_allow_html=True)
    
    # Increment question counter
    st.session_state[question_number_key] += 1

# Handle the first password submission
def handle_first_password(password_input):
    """Process the first password submission (Question 1) without showing analysis"""
    # Store the password
    st.session_state[first_password_key] = password_input
    
    # Mask the password for display in chat
    masked_password = format_password_for_display(password_input)
    
    # Add to chat history with masked password
    st.session_state[messages_key].append({"role": "user", "content": f"Password: {masked_password}"})
    
    # Simple evaluation for LLM to provide brief feedback (no UI display)
    brief_eval_prompt = f"""
    Provide a VERY BRIEF evaluation of this password (1-2 sentences only).
    
    Password to evaluate: `{password_input}`
    
    DO NOT mention the actual password itself in your response.
    Keep your response to 1-2 short sentences.
    Just give brief general feedback.
    """
    
    # Get LLM feedback without displaying the evaluation UI
    with st.spinner("Getting feedback..."):
        evaluation_response = ollama.chat(model="llava:latest", messages=[
            {"role": "system", "content": brief_eval_prompt}
        ])
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
    """Process the final password submission (Question 5) with LLM-driven final score"""
    # Store the final password
    st.session_state[final_password_key] = password_input
    
    # Mask the password for display in chat
    masked_password = format_password_for_display(password_input)
    
    # Add to chat history with masked password
    st.session_state[messages_key].append({"role": "user", "content": f"Final Password: {masked_password}"})
    
    # Get comprehensive final assessment from LLM
    with st.spinner("Analyzing your password..."):
        # Make sure to handle possible errors
        try:
            final_assessment = llm_final_password_assessment(password_input)
        except Exception as e:
            # Use fallback assessment if there's an error
            final_assessment = {
                "final_score": min(len(password_input) * 5, 100),
                "assessment": f"Password assessment encountered an error: {str(e)[:50]}. Using basic scoring.",
                "perfect_score_requirements": "Use a long, random mix of characters, numbers, and symbols.",
                "strengths": ["Your effort to create a stronger password is appreciated."],
                "weaknesses": ["Unable to perform detailed analysis."],
                "improvement_suggestions": ["Consider using a password manager."]
            }
        
        # --- STORE RESULTS IN SESSION STATE ---
        # Store chat history in all_chats
        if "all_chats" not in st.session_state:
            st.session_state["all_chats"] = {}
        st.session_state["all_chats"][current_page] = st.session_state[messages_key]
        
        # Initialize scenario scores if needed
        if "scenario_scores" not in st.session_state:
            st.session_state.scenario_scores = {
                "phishing": {"score": 0, "completed": False},
                "password": {"score": 0, "completed": False},
                "social": {"score": 0, "completed": False}
            }
        
        # Only increment completed_number if not previously completed
        if not st.session_state.scenario_scores["password"]["completed"]:
            if "completed_number" not in st.session_state:
                st.session_state.completed_number = 0
            st.session_state.completed_number += 1
        
        # Update the scenario score
        st.session_state.scenario_scores["password"] = {
            "score": final_assessment["final_score"],
            "completed": True
        }
    
    # Create a container to ensure score and assessment stay visible
    result_container = st.container()
    
    with result_container:
        # Display the enhanced score visualization with more pronounced styling
        score_num = final_assessment["final_score"]
        assessment_text = final_assessment["assessment"]
        
        # Create enhanced visual score display with more prominence
        score_html = f"""
        <div class="score-container" style="margin-bottom: 30px;">
            <h2>Password Training Complete! 🎉</h2>
            <h1 style="font-size: 52px; margin: 20px 0; font-weight: bold;">{score_num}/100</h1>
            <p style="font-size: 18px; margin: 15px 0;">{assessment_text}</p>
        </div>
        """
        result_container.markdown(score_html, unsafe_allow_html=True)
        
        # Display the detailed analysis below the score in the same container
        result_container.markdown("""
        <div class="final-assessment">
        <h2>Detailed Password Analysis</h2>
        """, unsafe_allow_html=True)
        
        # Display strengths
        result_container.markdown("<h3>Strengths:</h3>", unsafe_allow_html=True)
        
        strengths_list = "<ul>"
        for strength in final_assessment['strengths']:
            strengths_list += f"<li>{strength}</li>"
        strengths_list += "</ul>"
        result_container.markdown(strengths_list, unsafe_allow_html=True)
        
        # Display areas for improvement
        result_container.markdown("<h3>Areas for Improvement:</h3>", unsafe_allow_html=True)
        
        weaknesses_list = "<ul>"
        for weakness in final_assessment['weaknesses']:
            weaknesses_list += f"<li>{weakness}</li>"
        weaknesses_list += "</ul>"
        result_container.markdown(weaknesses_list, unsafe_allow_html=True)
        
        # Display actionable suggestions
        result_container.markdown("<h3>How to Improve Your Password:</h3>", unsafe_allow_html=True)
        
        suggestions_list = "<ul>"
        for suggestion in final_assessment['improvement_suggestions']:
            suggestions_list += f"<li>{suggestion}</li>"
        suggestions_list += "</ul>"
        result_container.markdown(suggestions_list, unsafe_allow_html=True)
        
        # Display perfect score requirements
        result_container.markdown(f"""
        <div class="perfect-score">
        <strong>To achieve a perfect 100/100 score:</strong> {final_assessment['perfect_score_requirements']}
        </div>
        """, unsafe_allow_html=True)
        
        result_container.markdown("</div>", unsafe_allow_html=True)
    
    # Create text version of assessment for message history
    assessment_text = (
        f"Final Password Score: {final_assessment['final_score']}/100\n\n"
        f"{final_assessment['assessment']}\n\n"
        f"Strengths:\n"
    )
    
    for strength in final_assessment['strengths']:
        assessment_text += f"- {strength}\n"
    
    assessment_text += "\nAreas for Improvement:\n"
    
    for weakness in final_assessment['weaknesses']:
        assessment_text += f"- {weakness}\n"
    
    assessment_text += "\nHow to Improve Your Password:\n"
    
    for suggestion in final_assessment['improvement_suggestions']:
        assessment_text += f"- {suggestion}\n"
    
    assessment_text += f"\nTo achieve a perfect 100/100 score: {final_assessment['perfect_score_requirements']}"
    
    # Add to message history
    st.session_state[messages_key].append({"role": "assistant", "content": assessment_text})
    
    # Complete the training
    st.session_state[question_number_key] += 1
    
    # Show completion message and certificate button - outside the container to remain visible
    st.success("🎉 Congratulations on completing the Password Security Training!")
    
    if st.button("📜 Download Certificate of Completion", type="primary"):
        st.info("Certificate generation would be implemented here in a production environment.")

# Display interface elements
def display_interface():
    """
    Display the appropriate interface elements based on the current question.
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
    
    # Display appropriate input method based on question type
    if is_mc:
        if st.session_state[question_number_key] == 1:  # Password options question (Q2)
            # Get password options from session state
            password_options = st.session_state[password_options_key]
            
            # Verify we have all four options properly populated
            if len(password_options) != 4 or any(not opt.get("password") for opt in password_options):
                # In case of missing options, use fallback options
                password_options = [
                    {"letter": "A", "password": "password123", "description": "Common word with predictable numbers", "security_level": "Very Weak"},
                    {"letter": "B", "password": "Summer2025!", "description": "Predictable pattern with season and year", "security_level": "Weak"},
                    {"letter": "C", "password": "BlueHorse42!", "description": "Common words with numbers and symbols", "security_level": "Moderate"},
                    {"letter": "D", "password": "j8K#p3vR!2sT&9qZ", "description": "Random mix of characters, numbers and symbols", "security_level": "Strong"}
                ]
                st.session_state[password_options_key] = password_options
            
            # Display password options clearly
            st.write("### Select the most secure password:")
            
            # Create fully visible options for radio buttons
            options = [(opt["letter"], opt["password"]) for opt in password_options]
            option_display = [f"{letter}) {password}" for letter, password in options]
            
            # Display the radio buttons in a vertical layout for better readability
            selected_option = st.radio(
                "Choose one option:",
                option_display,
                label_visibility="collapsed",
                key=f"radio_q{st.session_state[question_number_key]+1}",
                horizontal=False
            )
            
            # Extract just the letter (A, B, C, D) from the selection
            if selected_option:
                selected_letter = selected_option.split(")")[0].strip()
            else:
                selected_letter = ""
            
            # Submit button for password selection
            if st.button("Submit Selection", key=f"submit_q{st.session_state[question_number_key]+1}", type="primary"):
                if selected_letter:
                    # Use our custom multiple choice processor for immediate feedback
                    process_mc_password_answer(selected_letter)
                    st.rerun()
                else:
                    st.error("Please select an option.")
        else:
            # For other multiple choice questions
            options = extract_multiple_choice_options(current_question)
            
            if options:
                # Use radio buttons for multiple choice
                st.write("### Select your answer:")
                
                # Create radio buttons with the letter only for selection
                option_texts = [f"{letter}) {text}" for letter, text in options]
                selected_option = st.radio(
                    "Choose one option:",
                    option_texts,
                    label_visibility="collapsed",
                    key=f"radio_q{st.session_state[question_number_key]+1}"
                )
                
                # Extract just the letter (A, B, C, D) from the selection
                selected_letter = selected_option.split(")")[0].strip() if selected_option else ""
                
                # Submit button for other multiple choice questions
                if st.button("Submit Answer", key=f"submit_q{st.session_state[question_number_key]+1}", type="primary"):
                    if selected_letter:
                        # Process the selected answer
                        answer_text = f"My answer is {selected_letter}."
                        st.session_state[messages_key].append({"role": "user", "content": answer_text})
                        process_answer(answer_text)
                        st.rerun()
                    else:
                        st.error("Please select an option.")
    elif st.session_state[question_number_key] == 0:
        # Question 1: Password input
        password_input = st.text_input("Enter your password:", type="password", key="password_q1")
        
        if st.button("Submit Password", key="submit_q1", type="primary"):
            if password_input:
                # Process first password without showing analysis
                handle_first_password(password_input)
                st.rerun()
            else:
                st.error("Please enter a password.")
    elif st.session_state[question_number_key] == 4:
        # Question 5: Final password creation without showing requirements
        
        # Password input field - no requirements displayed to avoid giving hints
        password_input = st.text_input("Enter your improved password:", type="password", key="password_q5")
        
        if st.button("Submit Final Password", key="submit_q5", type="primary"):
            if password_input:
                # Process final password
                handle_final_password(password_input)
                st.rerun()
            else:
                st.error("Please enter a password.")
    else:
        # Regular text input for other questions
        user_input = st.text_input("Your answer:", key=f"input_q{st.session_state[question_number_key]+1}")
        
        if st.button("Submit", key=f"submit_q{st.session_state[question_number_key]+1}", type="primary"):
            if user_input:
                st.session_state[messages_key].append({"role": "user", "content": user_input})
                process_answer(user_input)
                st.rerun()
            else:
                st.error("Please enter an answer.")

# Main function to run the app
def main():
    """Main function to initialize the password creation training app"""
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
    
    # Generate or retrieve security fact
    if security_fact_key not in st.session_state:
        st.session_state[security_fact_key] = generate_security_fact()
    
    # Generate password options for Question 2 if not already generated
    if password_options_key not in st.session_state:
        with st.spinner("Preparing training..."):
            st.session_state[password_options_key] = generate_password_options()
    
    # Display the training title
    st.markdown('<div class="big-title">🔒 Password Security Training</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Learn how to create strong, secure passwords in this interactive training</div>', unsafe_allow_html=True)
    
    # Display security fact
    st.markdown(f"""
    <div class="security-fact">
        <strong>💡 Security Fact:</strong> {st.session_state[security_fact_key]}
    </div>
    """, unsafe_allow_html=True)
    
    # Display security warning (no animations)
    st.markdown("""
    <div class="security-warning">
        ⚠️ For security reasons, please do not enter your real passwords in this training exercise. 
        Create example passwords that follow security best practices instead.
    </div>
    """, unsafe_allow_html=True)
    
    # Add columns for layout
    col1, col2 = st.columns([3, 1])
    
    # Display training info in sidebar
    with col2:
        st.info("**About this training**\n\n"
                "This interactive password security course will test your knowledge with 5 key questions.\n\n"
                "You'll create passwords, learn best practices, and receive expert feedback on your password strength.")
        
        # Show progress
        if st.session_state[question_number_key] > 0:
            # Calculate progress percentage
            progress_percent = min((st.session_state[question_number_key]) * 20, 100)
            question_display = min(st.session_state[question_number_key], 5)
            
            st.write(f"**Progress: {question_display}/5 questions**")
            st.progress(progress_percent)
    
    # Use the main column for the chat interface
    with col1:
        st.write("---")

        # Initialize the training with fixed approach
        if not st.session_state[started_key]:
            # Set the initial system prompt
            st.session_state[messages_key] = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            # Add context
            st.session_state[messages_key].append({"role": "user", "content": "Let's start the password security training."})
            
            # Use our predefined first question to ensure consistency
            first_message = FIRST_QUESTION
            
            # Add to message history
            st.session_state[messages_key].append({"role": "assistant", "content": first_message})
            st.session_state[started_key] = True

        # Display message history
        for idx, message in enumerate(st.session_state[messages_key]):
            # Skip system messages and the initial context message
            if message["role"] == "system":
                continue
            if idx == 1 and message["role"] == "user" and "Let's start the password security training" in message["content"]:
                continue
            
            # Display the message with formatting
            st.markdown(format_message(message["content"], message["role"]), unsafe_allow_html=True)
        
        # Display the appropriate interface based on current question
        display_interface()

# Execute main function when script is run
if __name__ == "__main__":
    main()