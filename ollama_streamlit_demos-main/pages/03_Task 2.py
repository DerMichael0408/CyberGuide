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

# Enhanced phishing email content
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

# Improved System Prompt with better questions and formatting guidelines
SYSTEM_PROMPT = """
You are an AI-powered **Cybersecurity Training Assistant**.  
Your role is to **engage users in an interactive phishing awareness training** by asking structured cybersecurity-related questions.  

🚨 **You MUST primarily ask questions—but you can provide brief explanations** before moving to the next question.  
🚨 **Your goal is to help users think critically about phishing threats.**  
🚨 **This is an educational training scenario, not a real security incident.**  

---

## **📌 Phishing Scenario (Starting Point)**  
📩 The Setup
You receive an urgent email from what appears to be your company’s HR department. The subject line reads:
"🚨 Action Required: Payroll Update to Avoid Salary Delay!"

The email body contains the following message:

From: payroll@yourcompany-support.com
To: You
Subject: 🚨 Urgent: Payroll System Update Required

Dear [Your Name],

We have recently updated our payroll system to enhance security and ensure compliance with the latest regulations. To prevent any delays in your upcoming salary payment, please log in to confirm your account details.

Click the secure link below to verify your account before 5:00 PM today:

🔗 Update Payroll Information

Failure to complete this verification may result in a delay or disruption in salary disbursement.

Thank you for your prompt attention.

Best regards,
HR & Payroll Team
YourCompany Inc.

🚨 Red Flags in the Email
Fake Sense of Urgency – The email pressures you to act immediately or face a consequence (salary delay).
Slight Email Spoofing – The sender’s email looks like it’s from HR but is actually payroll@yourcompany-support.com instead of hr@yourcompany.com.
Suspicious Link – The URL yourcompany.payroll-update.com is not an official company domain. A real payroll link would be something like payroll.yourcompany.com.
No Personalized Details – Legitimate HR emails usually include personal identifiers like your full name or employee ID.
Grammatical & Formatting Issues – Words like "Failure to complete this verification may result in a delay" sound slightly unnatural and overly formal.
🔍 How to Handle This Situation
DO NOT Click the Link – Hover over the link to inspect the real URL without clicking it.
Verify with HR Directly – Contact HR through official company channels to confirm if they sent the email.
Report the Email – Forward the email to your IT/security team.
Check for Spoofing – Look at the actual email address behind the display name.
Stay Alert for Similar Attempts – Phishing scams evolve and may use different wording or sender addresses in future attempts.
❓ Follow-Up Questions for Training
First, you AI, present the scenario to the user!!
What would be your first reaction after receiving this email?
How can you check if the sender is legitimate?
What should you do if you accidentally clicked the link?
Why do attackers use urgency as a tactic in phishing emails?
How can a company train employees to spot phishing scams effectively?
This type of phishing attack preys on employees’ trust in HR-related emails, making it a common and dangerous tactic. 🚨

Would you like another example focused on a different attack vector, such as spear phishing, voice phishing (vishing), or SMS phishing (smishing)?

---

## **📌 Dynamic Cybersecurity Training**  
🔹 **Start by asking the user how they would react to the phishing scenario.**  
🔹 **Based on their response, provide a short evaluation and ask follow-up questions.**  
🔹 **The questions should evolve naturally, always staying within the topic of phishing and cybersecurity.**  

### **🔍 Example Interaction Flow**
1️⃣ **(User Response)** → "I would check the email sender."  
   ✅ **(AI Response)** → "Good thinking! Checking the sender is a key step.  
   🔹 How can you verify whether an email sender is authentic?"  

2️⃣ **(User Response)** → "I would hover over the link before clicking."  
   ✅ **(AI Response)** → "Great! Hovering over links can reveal misleading URLs.  
   🔹 What signs in a URL might indicate a phishing attempt?"  

3️⃣ **(User Response)** → "I would report the email to IT."  
   ✅ **(AI Response)** → "That’s a safe approach! Reporting helps prevent future attacks.  
   🔹 Why is it important to report phishing attempts instead of just deleting them?"  

---

## **🚨 Rules for AI**  
✅ **Always ask open-ended questions—never provide full answers.**  
✅ **Briefly acknowledge correct responses before asking the next question.**  
✅ **Dynamically generate follow-up questions based on the user’s input.**  
✅ **If the user asks for an answer, remind them that this is an interactive training exercise.**  
✅ **Begin the conversation by presenting the scenario in short to the user and retelling it.**  

"""

# ✅ Initialize Streamlit session state (Ensures messages exist)
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Initialize question counter 
if "question_number" not in st.session_state:
    st.session_state.question_number = 0
    
# Initialize start flag
if "started" not in st.session_state:
    st.session_state.started = False

# Display the training title with better styling
st.markdown('<div class="big-title">🛡️ Phishing Awareness Training</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Complete this interactive training to strengthen your defenses against phishing attacks</div>', unsafe_allow_html=True)

# Add columns for layout
col1, col2 = st.columns([2, 1])

# Display phishing email for reference with custom styling
with col1:
    with st.expander("📧 Sample Phishing Email", expanded=True):
        st.markdown(f'<div class="email-container">{email_text}</div>', unsafe_allow_html=True)

# Display training info in sidebar - FIXED: Only show one progress bar
with col2:
    st.info("**About this training**\n\n"
            "This interactive phishing awareness course will test your knowledge with 5 key questions.\n\n"
            "Answer carefully! Each response affects your final score.")
    
    # Show progress with custom styling in the sidebar only
    if st.session_state.question_number > 0:
        # Calculate progress percentage
        progress_percent = min((st.session_state.question_number) * 20, 100)
        question_display = min(st.session_state.question_number, 5)
        
        st.write(f"**Progress: {question_display}/5 questions**")
        st.progress(progress_percent)

# Use the full width for the chat interface
st.write("---")

# Initialize the training with fixed approach
if not st.session_state.started:
    # Set the initial system prompt
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# ✅ Ensure AI starts the conversation
if len(st.session_state.messages) == 1:  # If only the system message exists
    response = ollama.chat(model="llava:latest", messages=st.session_state.messages)
    first_question = response["message"]["content"]
    st.session_state.messages.append({"role": "assistant", "content": first_question})

# ✅ Display chat history (but hide system prompt)
st.title("🛡️ Cybersecurity Phishing Awareness Chatbot")

for message in st.session_state.messages:
    if message["role"] != "system":  # Hide system message
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User input field with custom prompt
user_input = st.chat_input("Type your answer here...")

if user_input:
    # Append user input to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(format_message(user_input, "user"), unsafe_allow_html=True)
    
    # If we've completed all 5 questions, generate final score
    if st.session_state.question_number == 4:  # This is the answer to Question 5
        with st.spinner("Conducting scientific assessment of your phishing awareness..."):
            # For visual effect, add a short delay
            time.sleep(1.5)
            
            # Generate final score with scientific assessment
            final_score_messages = st.session_state.messages + [{"role": "system", "content": SCORING_INSTRUCTIONS}]
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
            st.session_state.messages.append({"role": "assistant", "content": final_score})
            
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
            time.sleep(0.5)
            
            # Get response from LLM
            response = ollama.chat(model="llava:latest", messages=st.session_state.messages)
            ai_message = response["message"]["content"]
            
            # Force the correct next question and include feedback
            fixed_message = force_next_question(ai_message, st.session_state.question_number)
            
            # Display the fixed message with enhanced formatting
            st.markdown(format_message(fixed_message, "assistant"), unsafe_allow_html=True)
            
            # Add to message history
            st.session_state.messages.append({"role": "assistant", "content": fixed_message})
            
            # Increment question counter
            st.session_state.question_number += 1
            
            # Update progress in the sidebar
            with col2:
                question_display = min(st.session_state.question_number, 5)
                progress_percent = min(st.session_state.question_number * 20, 100)
                st.write(f"**Progress: {question_display}/5 questions**")
                st.progress(progress_percent)