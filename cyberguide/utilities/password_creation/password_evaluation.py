"""
password_evaluation.py - LLM-based password strength evaluation module
"""

import re
import math
import ollama
import json
from typing import Dict, List, Any, Optional

# Character set definitions for fallback evaluation
CHARSETS = [
    {"name": "ASCII Lowercase", "regex": r"[a-z]", "size": 26},
    {"name": "ASCII Uppercase", "regex": r"[A-Z]", "size": 26},
    {"name": "ASCII Numbers", "regex": r"[0-9]", "size": 10},
    {"name": "ASCII Symbols", "regex": r"[ !\"#$%&'()*+,-./:;<=>?@[\\\]^_`{|}~]", "size": 33}
]

# Reference scoring function for the LLM to use as a guideline
PASSWORD_SCORING_FUNCTION = """
def evaluate_password_strength(password):
    # Initialize component scores
    total_score = 0
    
    # 1. Length evaluation (40 points max)
    # 3 points per character up to 40 points max
    length_score = min(40, len(password) * 3)
    
    # 2. Character diversity (40 points max)
    diversity_score = 0
    has_lowercase = any(c.islower() for c in password)
    has_uppercase = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    # 10 points for each character type
    if has_lowercase: diversity_score += 10
    if has_uppercase: diversity_score += 10
    if has_digit: diversity_score += 10
    if has_special: diversity_score += 10
    
    # 3. Pattern analysis (20 points max)
    pattern_score = 20
    
    # Check for common patterns and deduct points
    common_patterns = ['123', 'abc', 'qwerty', 'password', 'admin']
    if any(pattern in password.lower() for pattern in common_patterns):
        pattern_score -= 10
    
    # Check for repeated sequences
    repeated_chars = False
    for i in range(len(password)-2):
        if password[i] == password[i+1] == password[i+2]:
            repeated_chars = True
            break
    if repeated_chars:
        pattern_score -= 5
    
    # Check for sequential characters
    sequential_chars = False
    for i in range(len(password)-2):
        if (ord(password[i]) + 1 == ord(password[i+1]) and 
            ord(password[i+1]) + 1 == ord(password[i+2])):
            sequential_chars = True
            break
    if sequential_chars:
        pattern_score -= 5
    
    # Ensure pattern score doesn't go below 0
    pattern_score = max(0, pattern_score)
    
    # Calculate total score (0-100)
    total_score = length_score + diversity_score + pattern_score
    
    return total_score
"""

# Basic fallback function if LLM is unavailable
def fallback_evaluate_password_strength(password: str) -> Dict[str, Any]:
    """
    Basic local password evaluation function.
    Used when LLM evaluation is unavailable.
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
    
    # Simple scoring logic
    length_score = min(40, len(password) * 3)
    
    # Check character types
    has_lowercase = bool(re.search(r'[a-z]', password))
    has_uppercase = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'[0-9]', password))
    has_special = bool(re.search(r'[^a-zA-Z0-9]', password))
    
    char_type_count = sum([has_lowercase, has_uppercase, has_digit, has_special])
    
    # Diversity score based on character types (10 points per type)
    diversity_score = char_type_count * 10
    
    # Basic pattern check (simplified)
    pattern_score = 20  # Start with full points
    common_patterns = ['123', 'abc', 'qwerty', 'password', 'admin']
    has_pattern = any(p in password.lower() for p in common_patterns)
    if has_pattern:
        pattern_score -= 10
    
    # Check for repeated chars
    for i in range(len(password)-2):
        if password[i] == password[i+1] == password[i+2]:
            pattern_score -= 5
            break
    
    pattern_score = max(0, pattern_score)  # Ensure non-negative
    
    # Calculate total score
    total_score = length_score + diversity_score + pattern_score
    
    # Format crack time estimate
    if total_score < 20:
        crack_time = "instantly"
    elif total_score < 40:
        crack_time = "a few minutes"
    elif total_score < 60:
        crack_time = "a few hours"
    elif total_score < 80:
        crack_time = "a few weeks"
    else:
        crack_time = "years"
    
    # Generate feedback
    feedback = {
        "warning": "",
        "suggestions": []
    }
    
    if len(password) < 12:
        feedback["suggestions"].append("Use at least 12 characters")
    
    if char_type_count < 3:
        feedback["suggestions"].append("Use a mix of character types")
    
    if has_pattern:
        feedback["suggestions"].append("Avoid common patterns and sequences")
    
    return {
        "score": int(total_score),
        "crack_time_display": crack_time,
        "feedback": feedback
    }

def llm_evaluate_password_strength(password: str, model: str = "llava:latest") -> Dict[str, Any]:
    """
    Evaluates password strength using LLM-based analysis.
    Returns a simplified output with just the essential information.
    """
    if not password:
        return fallback_evaluate_password_strength(password)
    
    try:
        # Construct the prompt for LLM password evaluation
        prompt = f"""
        ## PASSWORD STRENGTH EVALUATION
        
        Please evaluate this password: `{password}`
        
        Use the following scoring function as a reference:
        
        {PASSWORD_SCORING_FUNCTION}
        
        Your evaluation should output a JSON object with EXACTLY this structure:
        ```json
        {{
          "score": <overall_score_0_to_100>,
          "crack_time_display": "<human_readable_time_estimate>",
          "feedback": {{
            "warning": "<warning_if_any>",
            "suggestions": [
              "<suggestion_1>",
              "<suggestion_2>"
            ]
          }}
        }}
        ```
        
        Guidelines:
        - Score should be between 0-100 following the reference function's methodology
        - Provide 1-3 specific and actionable suggestions
        - DO NOT include the actual password in your response
        - Respond ONLY with the valid JSON object, no explanations or additional text
        """
        
        # Call the LLM for evaluation
        response = ollama.chat(model=model, messages=[
            {"role": "system", "content": prompt}
        ])
        
        # Extract the JSON response
        evaluation_text = response["message"]["content"].strip()
        
        # Clean up the response to extract just the JSON
        if "```json" in evaluation_text:
            evaluation_text = evaluation_text.split("```json")[1].split("```")[0].strip()
        elif "```" in evaluation_text:
            evaluation_text = evaluation_text.split("```")[1].strip()
            
        # Parse the JSON
        evaluation = json.loads(evaluation_text)
        
        # Basic validation of required fields
        required_fields = ["score", "crack_time_display", "feedback"]
        
        missing_fields = []
        for field in required_fields:
            if field not in evaluation:
                missing_fields.append(field)
                
        if missing_fields:
            print(f"Missing fields in LLM evaluation: {missing_fields}")
            return fallback_evaluate_password_strength(password)
        
        # Ensure score is an integer between 0-100
        evaluation["score"] = max(0, min(100, int(float(evaluation["score"]))))
        
        # Ensure feedback structure is correct
        if not isinstance(evaluation["feedback"], dict):
            evaluation["feedback"] = {"warning": "", "suggestions": []}
            
        if "suggestions" not in evaluation["feedback"]:
            evaluation["feedback"]["suggestions"] = []
            
        if "warning" not in evaluation["feedback"]:
            evaluation["feedback"]["warning"] = ""
        
        return evaluation
        
    except Exception as e:
        print(f"Error in LLM password evaluation: {e}")
        # Fallback to local evaluation if LLM fails
        return fallback_evaluate_password_strength(password)

def llm_final_password_assessment(password: str, model: str = "llava:latest") -> Dict[str, Any]:
    """
    Provides a final assessment of a password using LLM with improved explanations.
    The assessment includes a final score on a scale of 0-100 and detailed feedback.
    Uses the reference scoring function to guide the assessment.
    """
    try:
        # Construct the prompt for LLM final password assessment with improved requirements
        prompt = f"""
        ## COMPREHENSIVE PASSWORD ASSESSMENT
        
        Evaluate this password: `{password}`
        
        Use the following password scoring function as a strict guideline for your assessment:
        
        {PASSWORD_SCORING_FUNCTION}
        
        Provide a comprehensive assessment based EXACTLY on the scoring principles in the function:
        
        1. Length (40 points maximum): 
           - 3 points per character up to 40 points maximum
           - 12+ characters is recommended
        
        2. Character Mix (40 points maximum):
           - Lowercase letters: 10 points
           - Uppercase letters: 10 points
           - Numbers: 10 points
           - Special characters: 10 points
        
        3. Pattern Avoidance (20 points maximum):
           - Absence of common patterns/words (10 points)
           - No repeated sequences (5 points)
           - No sequential characters (5 points)
        
        Your assessment must output a JSON object with EXACTLY this structure:
        ```json
        {{
          "final_score": <score_0_to_100>,
          "assessment": "<detailed_assessment_text>",
          "perfect_score_requirements": "<what_would_make_this_100_out_of_100>",
          "strengths": [
            "<strength_1>",
            "<strength_2>"
          ],
          "weaknesses": [
            "<weakness_1>",
            "<weakness_2>"
          ],
          "improvement_suggestions": [
            "<actionable_suggestion_1>",
            "<actionable_suggestion_2>"
          ]
        }}
        ```
        
        Guidelines:
        - Final score must STRICTLY follow the scoring function above
        - Assessment should CLEARLY EXPLAIN why the password received this specific score
        - Perfect score requirements should explain specifically what would make this a 100/100 password
        - List 2-3 specific strengths of the password
        - List 2-3 specific weaknesses or areas for improvement
        - Provide 2-3 CONCRETE, ACTIONABLE suggestions for improving this password
        - DO NOT include the actual password in your response
        - Respond ONLY with the valid JSON object
        """
        
        # Call the LLM for assessment
        response = ollama.chat(model=model, messages=[
            {"role": "system", "content": prompt}
        ])
        
        # Extract the JSON response
        assessment_text = response["message"]["content"].strip()
        
        # Clean up the response to extract just the JSON
        if "```json" in assessment_text:
            assessment_text = assessment_text.split("```json")[1].split("```")[0].strip()
        elif "```" in assessment_text:
            assessment_text = assessment_text.split("```")[1].strip()
            
        # Parse the JSON
        assessment = json.loads(assessment_text)
        
        # Basic validation
        if "final_score" not in assessment:
            assessment["final_score"] = 0
        else:
            assessment["final_score"] = max(0, min(100, int(float(assessment["final_score"]))))
            
        if "assessment" not in assessment:
            assessment["assessment"] = "No assessment provided."
            
        if "perfect_score_requirements" not in assessment:
            assessment["perfect_score_requirements"] = "No requirements provided."
            
        if "strengths" not in assessment or not isinstance(assessment["strengths"], list):
            assessment["strengths"] = []
            
        if "weaknesses" not in assessment or not isinstance(assessment["weaknesses"], list):
            assessment["weaknesses"] = []
            
        if "improvement_suggestions" not in assessment or not isinstance(assessment["improvement_suggestions"], list):
            assessment["improvement_suggestions"] = []
        
        return assessment
    
    except Exception as e:
        print(f"Error in LLM final password assessment: {e}")
        # Return a basic structure on error
        return {
            "final_score": 0,
            "assessment": "Error occurred during assessment.",
            "perfect_score_requirements": "Cannot determine requirements due to error.",
            "strengths": [],
            "weaknesses": [],
            "improvement_suggestions": []
        }

def generate_password_options(model: str = "llava:latest") -> List[Dict[str, str]]:
    """
    Generates multiple choice password options using LLM.
    Returns a list of dictionaries with letter, password, and description.
    """
    try:
        # Prompt to generate password options
        prompt = """
        Generate four example passwords for a multiple-choice question where the user must identify the most secure password. 
        
        Requirements:
        1. Option A - Extremely weak password (like 'password123')
        2. Option B - Slightly better but still insecure password
        3. Option C - Moderately strong password
        4. Option D - Highly secure password (the correct answer)
        
        For each password, provide:
        - The password itself
        - A brief description of why it's weak/strong
        
        Format your response as a JSON array:
        ```json
        [
          {
            "letter": "A",
            "password": "password123",
            "description": "Common word with predictable numbers",
            "security_level": "Very Weak"
          },
          {
            "letter": "B",
            "password": "...",
            "description": "...",
            "security_level": "Weak"
          },
          {
            "letter": "C",
            "password": "...",
            "description": "...",
            "security_level": "Moderate"
          },
          {
            "letter": "D",
            "password": "...",
            "description": "...",
            "security_level": "Strong"
          }
        ]
        ```
        
        Make it very obvious which password is the most secure. Respond ONLY with the JSON array.
        """
        
        # Call the LLM
        response = ollama.chat(model=model, messages=[
            {"role": "system", "content": prompt}
        ])
        
        # Extract the JSON response
        options_text = response["message"]["content"].strip()
        
        # Clean up to get just the JSON
        if "```json" in options_text:
            options_text = options_text.split("```json")[1].split("```")[0].strip()
        elif "```" in options_text:
            options_text = options_text.split("```")[1].strip()
            
        # Parse JSON
        options = json.loads(options_text)
        
        return options
    
    except Exception as e:
        print(f"Error generating password options: {e}")
        # Return fallback options if LLM fails
        return [
            {"letter": "A", "password": "password123", "description": "Common word with predictable numbers", "security_level": "Very Weak"},
            {"letter": "B", "password": "P@55word", "description": "Simple substitutions of letters with symbols", "security_level": "Weak"},
            {"letter": "C", "password": "BlueHorse42!", "description": "Contains words but with mixed case and symbols", "security_level": "Moderate"},
            {"letter": "D", "password": "j8K#p3vR!2sT&9qZ", "description": "Long, random mix of characters, numbers and symbols", "security_level": "Strong"}
        ]

def format_password_for_display(password: str) -> str:
    """
    Masks password characters for secure display.
    Shows first and last character, masks the rest.
    """
    if not password:
        return ""
    
    if len(password) <= 2:
        return "*" * len(password)
    
    # Show first and last character, mask the rest
    return password[0] + "*" * (len(password) - 2) + password[-1]

# Set default evaluation function
evaluate_password_strength = llm_evaluate_password_strength