
import streamlit as st
import time
import random
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import aus components.password_training.password_training_utils
from components.password_training.password_training_utils import (
    evaluate_password_strength, generate_score_message, check_challenge_met,
    QUESTIONS, PASSWORD_CREATION_OPTIONS, PASSWORD_COMPARISON_OPTIONS,
    CORRECT_ANSWERS, PASSWORD_CHALLENGES, PASSWORD_FACTS,
    get_achievements, calculate_points,
    format_message, format_multiple_choice, generate_score_html,
    generate_certificate_html, generate_question_feedback,
    get_custom_css
)


# Page configuration
st.set_page_config(
    page_title="Password Creation Training",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Load custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

st.markdown('<div class="big-title">🔐 Password Creation Training</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Complete this interactive training to learn how to create strong, secure passwords</div>', unsafe_allow_html=True)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "question_index" not in st.session_state:
    st.session_state.question_index = 0

if "started" not in st.session_state:
    st.session_state.started = False

if "training_complete" not in st.session_state:
    st.session_state.training_complete = False
    
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
    
if "points" not in st.session_state:
    st.session_state.points = 0
    
if "correct_answers" not in st.session_state:
    st.session_state.correct_answers = 0
    
if "password_challenge" not in st.session_state:
    st.session_state.password_challenge = random.choice(PASSWORD_CHALLENGES)
    
# Randomize questions for this session
if "randomized_questions" not in st.session_state:
    # Create a copy of the base questions
    randomized_questions = QUESTIONS.copy()
    
    # Replace question 2 with a random version
    creation_options = random.choice(PASSWORD_CREATION_OPTIONS)
    randomized_questions[1] = f"Which of these is the most secure way to create a password?\nA) {creation_options[0]}\nB) {creation_options[1]}\nC) {creation_options[2]}\nD) {creation_options[3]}"
    
    # Replace question 4 with a random version
    comparison_options = random.choice(PASSWORD_COMPARISON_OPTIONS)
    randomized_questions[3] = f"Which of these passwords is the most secure?\nA) {comparison_options[0]}\nB) {comparison_options[1]}\nC) {comparison_options[2]}\nD) {comparison_options[3]}"
    
    st.session_state.randomized_questions = randomized_questions

# Layout columns
col1, col2 = st.columns([3, 1])

# Sidebar content
with col2:
    st.info("**About this training**\n\n"
            "This interactive password security course will test your knowledge with 5 key questions.\n\n"
            "Learn how to create strong passwords that protect your accounts from unauthorized access.")
    
    # Show progress
    if st.session_state.question_index > 0:
        st.write(f"**Progress: {st.session_state.question_index}/5 questions**")
        progress = st.progress(min(st.session_state.question_index * 20, 100))
    
    # Show a random password fact
    with st.expander("💡 Did you know?", expanded=False):
        st.write(random.choice(PASSWORD_FACTS))
        
    # Password Tips sidebar
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
    
    # Password Challenge
    if st.session_state.question_index >= 3 and not st.session_state.training_complete:
        st.markdown(f"""
        <div class="password-challenge">
            <strong>🎯 Password Challenge:</strong><br>
            {st.session_state.password_challenge}
        </div>
        """, unsafe_allow_html=True)

# Main content area
with col1:
    st.write("---")

    # Start training when the app loads
    if not st.session_state.started:
        # Present first question - EXACTLY as defined
        first_message = f"Welcome to password creation training! Learn how to create stronger, more secure passwords.\n\nQuestion 1/5: {st.session_state.randomized_questions[0]}"
        st.session_state.messages.append({"role": "assistant", "content": first_message})
        st.session_state.started = True
        st.session_state.question_index = 1
        st.session_state.start_time = time.time()

    # Message History
    for message in st.session_state.messages:
        st.markdown(format_message(message["content"], message["role"]), unsafe_allow_html=True)

    # User entry field
    if not st.session_state.training_complete:
        user_input = st.chat_input("Type your answer here...")
        
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Check for correct answers to multiple choice questions
            if st.session_state.question_index in CORRECT_ANSWERS:
                # Extract the first letter from the answer which should be the option (A, B, C, D)
                user_answer_option = user_input.strip()[0].upper() if user_input.strip() else ""
                if user_answer_option == CORRECT_ANSWERS[st.session_state.question_index]:
                    st.session_state.correct_answers += 1
            
            st.rerun()

    # Process user response after rerun
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and not st.session_state.training_complete:
        with st.spinner("Processing your answer..."):
            # Visual delay effect
            time.sleep(0.5)
            
            # Get user input
            user_answer = st.session_state.messages[-1]["content"]
            
            # Process final question (password evaluation)
            if st.session_state.question_index == 5:
                # Calculate total time taken
                time_taken = time.time() - st.session_state.start_time
                
                # Evaluate the password
                password_details = evaluate_password_strength(user_answer)
                final_score = generate_score_message(password_details)
                
                # Check if the password challenge was met
                challenge_met = check_challenge_met(st.session_state.password_challenge, user_answer)
                
                # Calculate final points
                password_score = password_details['score']
                points = calculate_points(password_score, st.session_state.correct_answers)
                
                # Add bonus points for meeting the challenge
                if challenge_met:
                    points += 50
                
                # Get achievements
                achievements = get_achievements(password_details, time_taken, st.session_state.correct_answers)
                
                # Generate HTML for score visualization and certificate
                score_html = generate_score_html(password_details, points, challenge_met, achievements)
                certificate_html = generate_certificate_html(password_score, points, time_taken)
                
                # Display both visualizations
                st.markdown(score_html, unsafe_allow_html=True)
                st.markdown(certificate_html, unsafe_allow_html=True)
                
                # Add to message history
                st.session_state.messages.append({"role": "assistant", "content": final_score})
                st.session_state.training_complete = True
                
                # Update progress to 100%
                if "progress" in locals():
                    progress.progress(100)
                
                # Success message and download option
                st.success("🎓 Training completed successfully! Remember to apply these principles to all your accounts.")
                
                st.download_button(
                    label="📜 Download Password Security Cheat Sheet",
                    data="# Password Security Cheat Sheet\n\n- Use a mix of uppercase, lowercase, numbers, and special characters\n- Don't reuse passwords across accounts\n- Avoid dictionary words and personal information\n- Consider using a password manager\n- Minimum 12 characters for strong passwords\n- Use passphrases for enhanced security and memorability\n- Enable multi-factor authentication when available\n- Change passwords regularly, especially for important accounts",
                    file_name="password_security_cheatsheet.md"
                )
                
                st.rerun()
            
            # Process regular questions (1-4)
            else:
                # Generate feedback for this question
                feedback = generate_question_feedback(st.session_state.question_index, user_answer)
                
                # Get the next question from our randomized questions list
                next_question_text = st.session_state.randomized_questions[st.session_state.question_index]
                next_question_num = st.session_state.question_index + 1
                
                # Construct the next message with the exact next question
                ai_message = f"{feedback}\n\nQuestion {next_question_num}/5: {next_question_text}"
                
                # Add to message history
                st.session_state.messages.append({"role": "assistant", "content": ai_message})
                
                # Increment question counter
                st.session_state.question_index += 1
                
                st.rerun()

# Reset button (only show in completed state)
if st.session_state.training_complete:
    if st.button("Start New Training"):
        # Reset all session state variables
        st.session_state.messages = []
        st.session_state.question_index = 0
        st.session_state.started = False
        st.session_state.training_complete = False
        st.session_state.start_time = time.time()
        st.session_state.points = 0
        st.session_state.correct_answers = 0
        st.session_state.password_challenge = random.choice(PASSWORD_CHALLENGES)
        
        # Clear randomized questions to get a new set
        if "randomized_questions" in st.session_state:
            del st.session_state.randomized_questions
            
        st.rerun()