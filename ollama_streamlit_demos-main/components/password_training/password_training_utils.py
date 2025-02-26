# password_training_utils.py
import re
import time
import string
import math
import random

# ===== PART 1: PASSWORD EVALUATION =====

# Common words to check for in passwords
COMMON_WORDS = [
    "password", "123456", "qwerty", "admin", "welcome", "login", "abc123", 
    "letmein", "monkey", "dragon", "baseball", "football", "superman", "batman",
    "trustno1", "sunshine", "iloveyou", "princess", "admin123", "welcome123", 
    "password123", "12345678", "1234", "123123", "qwertyuiop", "master", "hello",
    "test", "company", "secret", "shadow", "asdfgh", "zxcvbn", "jordan", "hunter",
    "harley", "ranger", "tigger", "charlie", "robert", "thomas", "hockey", "killer",
    "george", "andrew", "charlie", "summer", "winter", "spring", "autumn", "january",
    "february", "march", "april", "june", "july", "august", "september", "october",
    "november", "december"
]

# Common keyboard patterns
KEYBOARD_SEQUENCES = [
    "qwerty", "asdfgh", "zxcvbn", "qazwsx", "1qaz2wsx", "qwertz", "poiuyt", 
    "lkjhgf", "mnbvcx", "asdf", "wasd", "zxcv", "qwe"
]

# Sequential characters
SEQUENCES = [
    "abcdefghijklmnopqrstuvwxyz",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "0123456789",
    "!@#$%^&*()"
]

def evaluate_password_strength(password):
    """Evaluates the strength of a password and returns a detailed assessment."""
    if not password:
        return {
            'score': 0,
            'raw_score': 0,
            'feedback': "Empty password",
            'crack_time': "Instant",
            'char_types': 0,
            'length': 0,
            'suggestions': ["Please enter a password"],
            'strength': "Very Weak"
        }
    
    # Calculate length score (0-40 points)
    length = len(password)
    length_score = min(length * 4, 40)  # Max 40 points for length
    
    # Calculate character variety score (0-25 points)
    has_lowercase = any(c in string.ascii_lowercase for c in password)
    has_uppercase = any(c in string.ascii_uppercase for c in password)
    has_digit = any(c in string.digits for c in password)
    has_special = any(c in string.punctuation for c in password)
    char_types = sum([has_lowercase, has_uppercase, has_digit, has_special])
    variety_score = char_types * 6.25  # Max 25 points for variety (4 types)
    
    # Check for common words and patterns (0-25 points deduction)
    pattern_deduction = 0
    pattern_feedback = []
    
    # Check for common words
    lower_password = password.lower()
    for word in COMMON_WORDS:
        if word in lower_password:
            pattern_deduction += 10
            pattern_feedback.append(f"Contains common word: '{word}'")
            break
    
    # Check for keyboard sequences
    for seq in KEYBOARD_SEQUENCES:
        if seq in lower_password:
            pattern_deduction += 10
            pattern_feedback.append("Contains keyboard pattern")
            break
    
    # Check for sequential characters
    for seq in SEQUENCES:
        for i in range(len(seq) - 2):  # Look for 3+ character sequences
            if seq[i:i+3] in lower_password:
                pattern_deduction += 5
                pattern_feedback.append("Contains sequential characters")
                break
        if len(pattern_feedback) > 0:
            break
    
    # Check for repeating characters
    if re.search(r'(.)\1{2,}', password):  # Same character 3+ times
        pattern_deduction += 5
        pattern_feedback.append("Contains repeating characters")
    
    # Check for only one character type
    if char_types == 1:
        pattern_deduction += 15
        if has_lowercase:
            pattern_feedback.append("Only lowercase letters")
        elif has_uppercase:
            pattern_feedback.append("Only uppercase letters")
        elif has_digit:
            pattern_feedback.append("Only digits")
        else:
            pattern_feedback.append("Only special characters")
    
    # Ensure pattern_deduction is at most 25
    pattern_deduction = min(pattern_deduction, 25)
    
    # Calculate entropy score (0-35 points)
    pool_size = 0
    if has_lowercase:
        pool_size += 26
    if has_uppercase:
        pool_size += 26
    if has_digit:
        pool_size += 10
    if has_special:
        pool_size += 33  # Approx number of special chars
        
    # Entropy formula: log2(pool_size^length)
    if pool_size > 0:
        entropy = length * math.log2(pool_size)
        entropy_score = min(entropy / 3, 35)  # Max 35 points, scaling factor of 3
    else:
        entropy_score = 0
    
    # Calculate total score (0-100)
    total_score = length_score + variety_score + entropy_score - pattern_deduction
    total_score = max(0, min(total_score, 100))  # Ensure score is between 0-100
    
    # Determine strength category
    if total_score < 20:
        strength = "Very Weak"
        crack_time = "Instant"
    elif total_score < 40:
        strength = "Weak"
        crack_time = "Minutes to Hours"
    elif total_score < 60:
        strength = "Moderate"
        crack_time = "Days to Weeks"
    elif total_score < 80:
        strength = "Strong"
        crack_time = "Months to Years"
    else:
        strength = "Very Strong"
        crack_time = "Many Years"
    
    # Generate feedback
    feedback = []
    feedback.append(f"Strength: {strength}")
    
    if length < 8:
        feedback.append("Too short")
    elif length >= 12:
        feedback.append("Good length")
    else:
        feedback.append("Acceptable length")
    
    if char_types < 3:
        feedback.append("Limited character variety")
    elif char_types == 4:
        feedback.append("Excellent character variety")
    
    # Add any pattern feedback
    feedback.extend(pattern_feedback)
    
    # Generate suggestions
    suggestions = []
    if length < 12:
        suggestions.append("Use at least 12 characters")
    if char_types < 4:
        missing = []
        if not has_lowercase:
            missing.append("lowercase letters")
        if not has_uppercase:
            missing.append("uppercase letters")
        if not has_digit:
            missing.append("numbers")
        if not has_special:
            missing.append("special characters")
        suggestions.append(f"Add {', '.join(missing)}")
    if pattern_feedback:
        suggestions.append("Avoid common words, sequences, and patterns")
    
    if not suggestions:
        suggestions = ["Consider using a password manager to generate and store complex passwords"]
    
    # Create result
    result = {
        'score': round(total_score),
        'raw_score': min(int(total_score / 20), 4),  # 0-4 scale for display
        'feedback': ". ".join(feedback),
        'crack_time': crack_time,
        'char_types': char_types,
        'length': length,
        'suggestions': suggestions,
        'strength': strength
    }
    
    return result

def generate_score_message(password_details):
    """Generates a user-friendly message based on password evaluation."""
    score = password_details['score']
    feedback = password_details['feedback']
    suggestions = ". ".join(password_details['suggestions']) if password_details['suggestions'] else ""
    
    message = f"""
Your final password score is: {score}/100.

Feedback: {feedback}

{suggestions}
"""
    return message

def check_challenge_met(challenge, password):
    """Checks if a password meets a specific challenge."""
    if challenge == "Create a password that includes at least one number, uppercase letter, and symbol":
        return (any(c.isdigit() for c in password) and 
                any(c.isupper() for c in password) and 
                any(c in string.punctuation for c in password))
                
    elif challenge == "Create a memorable password that uses a phrase with substitutions":
        substitutions = {'a': '@', 'i': '1', 'e': '3', 'o': '0', 's': '$', 't': '+'}
        for char, sub in substitutions.items():
            if char in password.lower() and sub in password:
                return True
        return False
                
    elif challenge == "Create a password that is at least 12 characters long":
        return len(password) >= 12
        
    elif challenge == "Create a password that doesn't contain any dictionary words":
        has_common_word = False
        for word in COMMON_WORDS:
            if word in password.lower():
                has_common_word = True
                break
        return not has_common_word
        
    elif challenge == "Create a password that tells a tiny story":
        return len(password) >= 15
        
    return False

# ===== PART 2: TRAINING DATA =====

# The 5 questions for the training with examples
QUESTIONS = [
    "❓ Enter a new password for your company's network, and I will evaluate its security.",
    "Which of these is the most secure way to create a password?\nA) Using a single dictionary word (e.g., \"sunshine\")\nB) Using a mix of uppercase, lowercase, numbers, and special characters (e.g., \"P@s$w0rd!2023\")\nC) Using a birth date or pet's name\nD) Reusing an old password",
    "Why should you never use the same password for multiple accounts?",
    "Which of these passwords is the most secure?\nA) Password123!\nB) Tr0ub4dor&3\nC) S3cureP@ssw0rd!\nD) company2024",
    "Now that you have completed this training, create a new secure password for your company's network based on what you have learned."
]

# Password creation options for question 2
PASSWORD_CREATION_OPTIONS = [
    [
        "Using a single dictionary word (e.g., \"sunshine\")",
        "Using a mix of uppercase, lowercase, numbers, and special characters (e.g., \"P@s$w0rd!2023\")",
        "Using a birth date or pet's name",
        "Reusing an old password"
    ],
    [
        "Using a phrase with no special characters (e.g., \"ilovemydog\")",
        "Creating a complex password with various character types (e.g., \"Tr4v3l#2023!\")",
        "Using personally identifiable information like your phone number",
        "Using the same password you use for other sites"
    ],
    [
        "Using sequential patterns like \"abcdef\" or \"123456\"",
        "Using a mixture of random characters, numbers, and symbols (e.g., \"xK5&pL9@zT\")",
        "Using your username as your password",
        "Using a password shared by a colleague"
    ]
]

# Password comparison options for question 4
PASSWORD_COMPARISON_OPTIONS = [
    [
        "Password123!",
        "Tr0ub4dor&3",
        "S3cureP@ssw0rd!",
        "company2024"
    ],
    [
        "welcome2023!",
        "7$Butterfly@Garden^9",
        "letmein$1",
        "Admin#1234"
    ],
    [
        "Summer2023!",
        "R4nd0m-Ch@r@cterz",
        "MyL0g!n#27",
        "1q2w3e4r!"
    ]
]

# Correct answers for multiple choice questions
CORRECT_ANSWERS = {
    1: "B",  # Question 2 (index 1): Using a mix of uppercase, lowercase, numbers, and special characters
    3: "C"   # Question 4 (index 3): S3cureP@ssw0rd!
}

# Password challenges
PASSWORD_CHALLENGES = [
    "Create a password that includes at least one number, uppercase letter, and symbol",
    "Create a memorable password that uses a phrase with substitutions",
    "Create a password that is at least 12 characters long",
    "Create a password that doesn't contain any dictionary words",
    "Create a password that tells a tiny story"
]

# Password facts
PASSWORD_FACTS = [
    "The most common password is still '123456', used by millions of accounts.",
    "It would take a computer about 34,000 years to crack a 12-character password that uses numbers, symbols, and upper and lower-case letters.",
    "The average person has 100 passwords across different accounts.",
    "25% of people forget their passwords at least once a day.",
    "Over 80% of data breaches are caused by password-related issues.",
    "The word 'password' is still used as a password by millions of people.",
    "Adding just one capital letter, number and symbol to an 8-character password increases the possible combinations from 41 billion to 94 trillion!",
    "Password crackers often try substitutions like '@' for 'a' and '3' for 'E' first, because they're so common.",
    "A truly random 8-character password takes about 57 days to crack, but a 10-character one would take 12 years."
]

# Achievements and their criteria
ACHIEVEMENTS = {
    "strong_password": {"name": "🏆 Password Master", "description": "Created a password with score above 80"},
    "quick_learner": {"name": "🚀 Quick Learner", "description": "Completed training in under 3 minutes"},
    "full_marks": {"name": "🌟 Perfect Score", "description": "Got 100% on the final password"},
    "character_mix": {"name": "🔤 Character Wizard", "description": "Used all 4 character types in your password"},
    "password_expert": {"name": "🧠 Security Expert", "description": "Demonstrated excellent password knowledge"},
}

def get_achievements(password_details, time_taken, correct_answers):
    """Determines which achievements were earned based on performance."""
    earned = []
    
    # Strong password achievement
    if password_details['score'] >= 80:
        earned.append(ACHIEVEMENTS["strong_password"])
    
    # Quick learner achievement
    if time_taken < 180:  # Less than 3 minutes
        earned.append(ACHIEVEMENTS["quick_learner"])
    
    # Perfect score achievement
    if password_details['score'] == 100:
        earned.append(ACHIEVEMENTS["full_marks"])
    
    # Character mix achievement
    if password_details['char_types'] == 4:
        earned.append(ACHIEVEMENTS["character_mix"])
    
    # Password expert achievement
    if correct_answers == 2 and password_details['score'] >= 70:
        earned.append(ACHIEVEMENTS["password_expert"])
    
    return earned

def calculate_points(password_score, correct_answers):
    """Calculates total points based on password score and correct answers."""
    # Base points for completing the training
    points = 100
    
    # Add points based on final password score
    points += password_score // 2
    
    # Add points for correct multiple choice answers (25 points each)
    points += correct_answers * 25
    
    return points

# ===== PART 3: UI COMPONENTS =====

def format_multiple_choice(question_text):
    """Formats multiple-choice questions for better display."""
    if "A)" in question_text and "B)" in question_text:
        parts = question_text.split("\n", 1)
        if len(parts) > 1:
            main_question = parts[0]
            options = parts[1]
            
            formatted_options = ""
            for option in options.split("\n"):
                formatted_options += f'<div class="option-item">{option}</div>'
                
            return f'{main_question}<div class="option-list">{formatted_options}</div>'
    
    return question_text

def format_message(message, role):
    """Formats chat messages based on their role."""
    if role == "user":
        return f'<div class="user-message">{message}</div>'
    else:
        # Remove any system notes that shouldn't be displayed
        message = re.sub(r'\(Note: This question should be asked.*?\)', '', message)
        message = re.sub(r'\(Use this exact question.*?\)', '', message)
        
        # Format assistant messages with highlighted question number
        if "Question" in message and "/5:" in message:
            parts = re.split(r'(Question \d/5:)', message, 1)
            if len(parts) > 1:
                feedback = parts[0].strip()
                question_part = parts[1]
                rest = parts[2] if len(parts) > 2 else ""
                
                rest = format_multiple_choice(rest)
                
                formatted = ""
                if feedback:
                    formatted += f'<div class="feedback">{feedback}</div>'
                formatted += f'<div><span class="question-number">{question_part}</span>{rest}</div>'
                return f'<div class="assistant-message">{formatted}</div>'
        
        return f'<div class="assistant-message">{message}</div>'

def generate_score_html(password_details, points=None, challenge_met=False, achievements=None):
    """Generates HTML for the final password score display."""
    password_score = password_details['score']
    
    # Start with the container
    html = f"""
    <div class="score-container celebrate">
        <h2>Training Complete! 🎉</h2>
        <h1 style="font-size: 48px; margin: 20px 0;">{password_score}/100</h1>
        <div>Password Strength: {password_details['strength']}</div>
        <div class="strength-meter">
            <div style="width: {password_score}%; height: 100%; background: linear-gradient(90deg, #ff4d4d, #ffba00, #4CAF50); border-radius: 5px;"></div>
        </div>
        <p style="margin-top: 15px;">{password_details['feedback']}</p>
        <div class="strength-details">
            <div class="strength-factor">Length<br>{password_details['length']} chars</div>
            <div class="strength-factor">Character Types<br>{password_details['char_types']}/4</div>
            <div class="strength-factor">Crack Time<br>{password_details['crack_time']}</div>
        </div>
    """
    
    # Add points if provided
    if points is not None:
        html += f"""
        <div style="margin-top: 20px;">
            <span class="badge">Total Points: {points}</span>
        </div>
        """
    
    # Add challenge result if applicable
    if challenge_met:
        html += """
        <div style="margin-top: 15px; padding: 10px; background-color: #FFF9C4; border-radius: 10px; color: #FF6F00;">
            <strong>🎯 Challenge Completed!</strong> +50 bonus points
        </div>
        """
    
    # Add achievements
    if achievements:
        html += '<div style="margin-top: 20px;"><strong>🏆 Achievements Unlocked:</strong></div>'
        for achievement in achievements:
            html += f'<div class="achievement"><span class="achievement-icon">🏆</span> {achievement["name"]}: {achievement["description"]}</div>'
    
    # Close container
    html += "</div>"
    
    return html

def generate_certificate_html(password_score, points=None, time_taken=0):
    """Generates HTML for the completion certificate."""
    minutes, seconds = divmod(int(time_taken), 60)
    
    html = f"""
    <div class="final-certificate">
        <div class="certificate-title">Certificate of Completion</div>
        <p>This certifies that you have successfully completed the</p>
        <h3>Password Security Training</h3>
        <p>With a final score of <strong>{password_score}/100</strong></p>
    """
    
    if points is not None:
        html += f'<p>Total points earned: <strong>{points}</strong></p>'
    
    html += f"""
        <p>Time to complete: <strong>{minutes}m {seconds}s</strong></p>
        <p>Date: {time.strftime("%B %d, %Y")}</p>
    </div>
    """
    
    return html

def generate_question_feedback(question_index, user_answer):
    """Generates feedback for a given question and answer."""
    # First question - password evaluation
    if question_index == 1:
        password_details = evaluate_password_strength(user_answer)
        score = password_details['score']
        
        if score < 40:
            return f"Your password scored {score}/100. It's quite weak and could be easily compromised. {password_details['feedback']}"
        elif score < 70:
            return f"Your password scored {score}/100. It's moderately secure but could be improved. {password_details['feedback']}"
        else:
            return f"Your password scored {score}/100. That's a strong password! {password_details['feedback']}"
    
    # Second question - secure password creation principles
    elif question_index == 2:
        user_answer_option = user_answer.strip()[0].upper() if user_answer.strip() else ""
        correct_option = CORRECT_ANSWERS.get(1)
        
        if user_answer_option == correct_option:
            return "Correct! Using a mix of character types significantly increases password strength."
        else:
            return "Actually, option B is the most secure approach. A diverse mix of characters creates much stronger passwords."
    
    # Third question - password reuse
    elif question_index == 3:
        if "breach" in user_answer.lower() or "compromise" in user_answer.lower() or "hack" in user_answer.lower():
            return "Great point about security breaches! When one account is compromised, unique passwords protect your other accounts."
        else:
            return "That's right! Using the same password across multiple accounts creates a single point of failure."
    
    # Fourth question - most secure password
    elif question_index == 4:
        user_answer_option = user_answer.strip()[0].upper() if user_answer.strip() else ""
        correct_option = CORRECT_ANSWERS.get(3)
        
        if user_answer_option == correct_option:
            return "Correct! S3cureP@ssw0rd! has the best combination of length and character diversity."
        else:
            return "Actually, option C (S3cureP@ssw0rd!) is the most secure due to its length and variety of character types."
    
    return "Thank you for your response."

# ===== PART 4: CSS STYLES =====

def get_custom_css():
    """Returns all custom CSS styles for the password training app."""
    return """
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
            cursor: pointer;
            padding: 10px;
            border-radius: 5px;
            transition: background-color 0.3s;
        }
        .option-item:hover {
            background-color: #f0f0f0;
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
        .strength-meter {
            height: 10px;
            border-radius: 5px;
            margin: 10px 0;
            background-color: #e0e0e0;
        }
        .strength-details {
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
        }
        .strength-factor {
            flex: 1;
            padding: 8px;
            margin: 0 5px;
            border-radius: 5px;
            background-color: #f5f5f5;
            text-align: center;
            font-size: 14px;
        }
        .badge {
            display: inline-block;
            background-color: #673AB7;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin: 5px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        .game-points {
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
            text-align: center;
            padding: 10px;
            background-color: #f5f5f5;
            border-radius: 10px;
            margin: 10px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .achievement {
            background-color: #FFD700;
            color: #333;
            padding: 10px 15px;
            border-radius: 10px;
            margin: 10px 0;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .achievement-icon {
            font-size: 24px;
            margin-right: 10px;
        }
        .final-certificate {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
            border: 2px solid #1E3A8A;
        }
        .certificate-title {
            font-size: 28px;
            font-weight: bold;
            color: #1E3A8A;
            margin-bottom: 20px;
        }
        .password-feedback {
            padding: 15px;
            background-color: #f0f8ff;
            border-radius: 10px;
            margin: 15px 0;
            animation: fadeIn 1s;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .level-badge {
            display: inline-block;
            background-color: #FF5722;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-weight: bold;
            font-size: 14px;
            margin-left: 10px;
        }
        .password-challenge {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            border-left: 5px solid #FF9800;
        }
        .timer {
            font-size: 18px;
            font-weight: bold;
            color: #F44336;
            text-align: center;
        }
        .celebrate {
            animation: celebrate 1s ease-in-out;
        }
        @keyframes celebrate {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
    </style>
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """