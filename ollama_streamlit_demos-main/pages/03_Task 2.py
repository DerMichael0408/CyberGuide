import streamlit as st
import ollama
import openai

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

# Improved System Prompt with clear structure
SYSTEM_PROMPT = """
# PHISHING AWARENESS TRAINING - STRICT INSTRUCTIONS

## CORE RULES (FOLLOW EXACTLY)
- Present ONLY ONE question at a time
- Provide BRIEF feedback after user answers (max 2 sentences)
- ALWAYS proceed to the next question immediately after feedback
- NEVER show multiple questions at once
- Format each question as "Question X/5: [question text]"

## STARTING SEQUENCE
Begin with: "This is a phishing awareness exercise. I will ask you 5 questions about phishing detection. Let's begin."
IMMEDIATELY ask Question 1/5.

## QUESTIONS (ASK IN EXACT ORDER)
Question 1/5: "How can you recognize that this is a phishing email?" 
""" + email_text + """

Question 2/5: "Which of these links is most suspicious?
A) https://yourcompany-support.com/reset-password
B) https://secure-yourcompany.com/login
C) https://gogle.com/security-update
D) https://yourcompany.com/hr-portal"

Question 3/5: "You accidentally clicked the link. What is the safest next step?"

Question 4/5: "Why do attackers create a sense of urgency in phishing emails?"

Question 5/5: "What steps can your organization take to prevent phishing attacks?"

## CRITICAL BEHAVIORS
- After user answers Question 1: Give brief feedback, THEN IMMEDIATELY ask Question 2
- After user answers Question 2: Give brief feedback, THEN IMMEDIATELY ask Question 3
- After user answers Question 3: Give brief feedback, THEN IMMEDIATELY ask Question 4
- After user answers Question 4: Give brief feedback, THEN IMMEDIATELY ask Question 5
- After user answers Question 5: Give brief feedback, THEN END with "Thank you for completing the training."
"""

# Fixed scoring prompt with proper format
SCORING_INSTRUCTIONS = """
# PHISHING AWARENESS SCORING - STRICT OUTPUT FORMAT

You are evaluating the user's phishing awareness based on their 5 responses.

## SCORING SCALE
- 90-100: Expert 🚀
- 70-89: Proficient ✅
- 50-69: Basic Awareness ⚠️
- 30-49: Limited Understanding ❗
- 0-29: High Risk 🚨

## OUTPUT FORMAT REQUIREMENTS
You MUST use EXACTLY this format with actual numeric scores:

```
Thank you for completing the phishing awareness training. Your final score is: [SCORE]/100.


Feedback: [1-2 sentence summary of strengths and improvement areas]
```

IMPORTANT: Replace all [SCORE] placeholders with actual numbers. DO NOT keep brackets or placeholder text.
"""

# Initialize Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Initialize question counter
if "counter" not in st.session_state:
    st.session_state.counter = 0

# Display the email at the start
with st.chat_message("assistant"):
    st.markdown(email_text)

# Ensure AI starts the conversation
if len(st.session_state.messages) == 1:  # If only the system message exists
    response = ollama.chat(model="llava:latest", messages=st.session_state.messages)
    first_question = response["message"]["content"]
    st.session_state.messages.append({"role": "assistant", "content": first_question})

# Display message history (except system message)
for message in st.session_state.messages:
    if message["role"] != "system":  # Hide system message
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User input field
user_input = st.chat_input("Your response...")

if user_input:
    # Append user input to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Increment counter
    st.session_state.counter += 1

    # Check if this was the 5th answer
    if st.session_state.counter == 5:
        # Generate final score after 5th answer
        final_score_messages = st.session_state.messages + [{"role": "system", "content": SCORING_INSTRUCTIONS}]
        final_score_response = ollama.chat(model="llava:latest", messages=final_score_messages)
        final_score = final_score_response["message"]["content"]
        
        # Display final score
        with st.chat_message("assistant"):
            st.markdown(final_score)
            
        # Add to message history
        st.session_state.messages.append({"role": "assistant", "content": final_score})
    else:
        # Generate AI response using Ollama (LLaVA)
        response = ollama.chat(model="llava:latest", messages=st.session_state.messages)
        ai_message = response["message"]["content"]
        
        # Display response
        with st.chat_message("assistant"):
            st.markdown(ai_message)
            
        # Add to message history
        st.session_state.messages.append({"role": "assistant", "content": ai_message})