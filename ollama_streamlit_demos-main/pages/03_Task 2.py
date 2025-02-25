import streamlit as st
import ollama
import openai
# ✅ Hidden system prompt (invisible to user, but guides the AI)
email = """
    Subject: "Action Required: Payroll Update to Avoid Salary Delay!"

    The email body contains the following message:

    From: payroll@yourcompany-support.com \n
    To: You \n
    Subject: Urgent: Payroll System Update Required \n

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

SYSTEM_PROMPT = """
### SYSTEM PROMPT: Phishing Awareness Training AI  

You are an AI-powered **Cybersecurity Training Assistant**.  
Your role is to **train users to recognize phishing attacks** by **asking structured security-related questions** and **evaluating their responses**.  

🚨 **STRICT RULES YOU MUST FOLLOW:**  

1.**Start the training by stating:**  
   **"This is a phishing awareness exercise. I will ask you 5 questions and evaluate your responses. Let's begin."**  

2.**Ask this first question (Question 1):**  
   ❓ **"How can you recognize that this is a phishing email?"**  
   - Do NOT display the email itself. The user has already seen it.  

3.**Wait for the user’s response. Then, evaluate their answer dynamically:**  
   - ✅ **If the answer is strong**, acknowledge it and confirm its importance.  
   - ⚠️ **If the answer is incomplete**, guide the user toward missing details.  
   - ❌ **If the answer is incorrect or vague**, provide a brief correction.  

   🚨 **DO NOT use predefined responses. Instead, generate feedback based on the user’s exact answer.**  

4.**Ask a follow-up question and number it explicitly:**  
   - Example: **"Question 2: What should you do before clicking any links in this email?"**  
   - Example: **"Question 3: How can you verify the sender’s email address?"**  
   - Example: **"Question 4: Why do attackers create fake urgency?"**  
   - Example: **"Question 5: What should you do if you suspect an email is a phishing attempt?"**  

   - **ALWAYS include 'Question X:' at the beginning of each new question.**  
---

🚨 **ENFORCEMENT RULES:** 
- **ALWAYS answer and state the next question in the same response.**
- **ALWAYS number your questions (Question 1, Question 2, etc.).**  
- **NEVER provide full answers—only give short feedback.**  
- **NEVER use predefined feedback. Always analyze the user’s actual response.**  
- **Follow this structure EXACTLY.**  

"""

# ✅ Initialize Streamlit session state (Ensures messages exist)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
with st.chat_message("assistant"):
    st.markdown(email)
# ✅ Ensure AI starts the conversation
if len(st.session_state.messages) == 1:  # If only the system message exists
    response = ollama.chat(model="llava:latest", messages=st.session_state.messages)
    first_question = response["message"]["content"]
    st.session_state.messages.append({"role": "assistant", "content": first_question})



for message in st.session_state.messages:
    if message["role"] != "system":  # Hide system message
        with st.chat_message(message["role"]):
            st.markdown(message["content"])



# ✅ User input field
user_input = st.chat_input("Your response...")
counter = 0

if counter == 2:
    final_score = ollama.chat(model="llava:latest", messages=st.session_state.messages ++ "Create a final score based on the interaction. Output the format Your Score is: [Insert score here]/100")
    st.markdown(final_score)
    
if user_input:
    # Append user input to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    
    # Generate AI response using Ollama (LLaVA)
    response = ollama.chat(model="llava:latest", messages=st.session_state.messages)

    # Extract AI's next question
    ai_message = response["message"]["content"]
    
    st.session_state.messages.append({"role": "assistant", "content": ai_message})

    # Display AI response
    counter = counter + 1
    with st.chat_message("assistant"):
        st.markdown(ai_message)
        

