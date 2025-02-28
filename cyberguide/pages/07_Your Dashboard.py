import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
from datetime import datetime
import time
import ollama
import json
from utilities.template import setup_page

# Use setup_page for consistent styling and sidebar
setup_page(
    page_title="Security Dashboard",
    icon_emoji="🛡️",
    subtitle="Your personalized cybersecurity performance overview"
)

# Additional custom CSS for dashboard-specific styling
st.markdown("""
<style>
    .main {
        padding: 2rem 3rem;
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
    .dashboard-header {
        padding: 20px;
        background: linear-gradient(to right, #1E3A8A, #3B82F6);
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        height: 100%;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-title {
        font-size: 16px;
        color: #666;
        margin-bottom: 15px;
    }
    .scenario-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
        border-left: 5px solid #3B82F6;
    }
    .scenario-title {
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 5px;
    }
    .score-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
        color: white;
        font-size: 14px;
    }
    .score-high {
        background-color: #10B981;
    }
    .score-medium {
        background-color: #F59E0B;
    }
    .score-low {
        background-color: #EF4444;
    }
    .strength-item {
        background-color: #ECFDF5;
        padding: 10px 15px;
        border-radius: 5px;
        margin-bottom: 10px;
        border-left: 3px solid #10B981;
    }
    .weakness-item {
        background-color: #FEF2F2;
        padding: 10px 15px;
        border-radius: 5px;
        margin-bottom: 10px;
        border-left: 3px solid #EF4444;
    }
    .recommendation-item {
        background-color: #EFF6FF;
        padding: 10px 15px;
        border-radius: 5px;
        margin-bottom: 10px;
        border-left: 3px solid #3B82F6;
    }
    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .section-title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 15px;
        color: #1E3A8A;
        padding-bottom: 5px;
        border-bottom: 2px solid #E5E7EB;
    }
    .area-score {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        color: white;
        margin-right: 5px;
    }
    .badge-phishing {
        background-color: #3B82F6;
    }
    .badge-password {
        background-color: #8B5CF6;
    }
    .badge-social {
        background-color: #EC4899;
    }
    .progress-wrapper {
        height: 10px;
        background-color: #E5E7EB;
        border-radius: 5px;
        overflow: hidden;
        margin-bottom: 15px;
    }
    .progress-bar {
        height: 100%;
        border-radius: 5px;
    }
    .insight-card {
        background-color: #f8fafc;
        border-radius: 10px;
        padding: 15px;
        margin-top: 15px;
        border-left: 3px solid #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if "selected_role" not in st.session_state:
    st.session_state.selected_role = "Accountant Department"  # Set a default value
    
if "completed_number" not in st.session_state:
    st.session_state.completed_number = 0  # Set a default value

if "scenario_scores" not in st.session_state:
    # Default scores if none are available yet
    st.session_state.scenario_scores = {
        "phishing": {"score": 0, "completed": False},
        "password": {"score": 0, "completed": False},
        "social": {"score": 0, "completed": False}
    }

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

# Ensure we have default strengths, weaknesses and recommendations
if "strengths" not in st.session_state:
    st.session_state.strengths = [
        "Complete a scenario to see your strengths",
        "Strengths will be identified based on your responses",
        "Each completed scenario improves your security profile"
    ]

if "weaknesses" not in st.session_state:
    st.session_state.weaknesses = [
        "Complete a scenario to see areas for improvement",
        "Weaknesses will be identified based on your responses",
        "Focus on these areas to strengthen your security posture"
    ]

if "recommendations" not in st.session_state:
    st.session_state.recommendations = [
        "Complete a scenario to receive personalized recommendations",
        "Recommendations will address your specific security needs",
        "Follow these suggestions to enhance your security practices"
    ]

# Track the number of completed scenarios for analysis purposes
if "last_analyzed_count" not in st.session_state:
    st.session_state.last_analyzed_count = 0

# Calculate overall score based on completed scenarios
def calculate_overall_score():
    scores = []
    for scenario, data in st.session_state.scenario_scores.items():
        if data["completed"]:
            scores.append(data["score"])
    
    if not scores:
        return 0
    return int(sum(scores) / len(scores))

# Helper function to analyze chat history using LLM
def analyze_chats_with_llm():
    if len(st.session_state.all_chats) == 0:
        return False
    
    # Prepare chat history for analysis
    chat_summary = ""
    for scenario, messages in st.session_state.all_chats.items():
        chat_summary += f"\n\n--- {scenario} SCENARIO ---\n"
        
        # Extract only relevant messages (user responses and AI feedback)
        for msg in messages:
            if msg["role"] == "user" and not "Let's start" in msg["content"]:
                chat_summary += f"User: {msg['content']}\n"
            elif msg["role"] == "assistant" and ("score" in msg["content"].lower() or "assessment" in msg["content"].lower()):
                chat_summary += f"Assessment: {msg['content']}\n"
    
    # Prepare prompt for LLM analysis
    system_prompt = """
    You are a cybersecurity training analyst. Analyze the user's responses to cybersecurity scenarios and provide:
    1. Three specific strengths demonstrated by the user
    2. Three specific areas for improvement 
    3. Three personalized recommendations
    
    Format your response EXACTLY as a JSON object with three arrays:
    {
        "strengths": ["strength 1", "strength 2", "strength 3"],
        "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
        "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"]
    }
    
    Each entry should be a complete sentence that is specific, actionable, and based on evidence from the user's responses.
    """
    
    user_prompt = f"Here is the chat history from security training scenarios. Please analyze it and provide strengths, weaknesses, and recommendations:\n\n{chat_summary}"
    
    try:
        # Call the LLM for analysis
        response = ollama.chat(model="llava:latest", messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        # Extract and parse the JSON response
        content = response["message"]["content"]
        # Find JSON content within the response
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_content = content[json_start:json_end]
            analysis = json.loads(json_content)
            
            # Update session state with the analysis
            st.session_state.strengths = analysis.get("strengths", st.session_state.strengths)
            st.session_state.weaknesses = analysis.get("weaknesses", st.session_state.weaknesses)
            st.session_state.recommendations = analysis.get("recommendations", st.session_state.recommendations)
            
            return True
        else:
            return False
    except Exception as e:
        print(f"Error analyzing chats: {e}")
        return False

# Get the user data from session state
def get_user_data():
    # Analyze chats if completed scenarios > 0 AND either:
    # 1. We haven't analyzed yet (analysis_performed doesn't exist), OR
    # 2. The number of completed scenarios has increased since last analysis
    if (st.session_state.completed_number > 0 and 
        (("analysis_performed" not in st.session_state) or 
         (st.session_state.completed_number > st.session_state.last_analyzed_count))):
        
        success = analyze_chats_with_llm()
        if success:
            st.session_state.analysis_performed = True
            st.session_state.last_analyzed_count = st.session_state.completed_number
    
    # Calculate overall score
    overall_score = calculate_overall_score()
    
    # Prepare scenario data
    scenarios = []
    scenario_map = {
        "phishing": {
            "name": "Phishing Awareness",
            "badge": "badge-phishing",
            "color": "#3B82F6",
            "areas": {
                "Identification": 0,
                "Response": 0,
                "Prevention": 0
            }
        },
        "password": {
            "name": "Password Security",
            "badge": "badge-password",
            "color": "#8B5CF6",
            "areas": {
                "Password Strength": 0,
                "Password Management": 0,
                "Multi-Factor Authentication": 0
            }
        },
        "social": {
            "name": "Social Engineering",
            "badge": "badge-social",
            "color": "#EC4899",
            "areas": {
                "Awareness": 0,
                "Detection": 0,
                "Response": 0
            }
        }
    }
    
    # Populate scenario data with actual scores
    for key, details in scenario_map.items():
        data = st.session_state.scenario_scores.get(key, {"score": 0, "completed": False})
        score = data.get("score", 0)
        completed = data.get("completed", False)
        
        # Generate random area scores based on overall scenario score if completed
        if completed:
            areas = {}
            for area_key in details["areas"].keys():
                # Randomize a bit while keeping close to overall score
                area_score = max(min(score + np.random.randint(-15, 15), 100), 0)
                areas[area_key] = area_score
        else:
            areas = details["areas"]
        
        scenarios.append({
            "name": details["name"],
            "score": score,
            "badge": details["badge"],
            "areas": areas,
            "color": details["color"],
            "completed": completed
        })
    
    # Sort scenarios by score for determining strongest/weakest
    completed_scenarios = [s for s in scenarios if s["completed"]]
    if completed_scenarios:
        strongest_scenario = max(completed_scenarios, key=lambda x: x["score"])
        weakest_scenario = min(completed_scenarios, key=lambda x: x["score"])
    else:
        strongest_scenario = {"name": "Not available", "score": 0}
        weakest_scenario = {"name": "Not available", "score": 0}
    
    return {
        "name": "User",
        "email": "michael.schmidt@example.com",
        "department": st.session_state.selected_role,
        "completed_date": datetime.now().strftime("%B %d, %Y"),
        "overall_score": overall_score,
        "scenarios": scenarios,
        "strongest_scenario": strongest_scenario,
        "weakest_scenario": weakest_scenario,
        "strengths": st.session_state.strengths,
        "weaknesses": st.session_state.weaknesses,
        "recommendations": st.session_state.recommendations
    }

# Helper functions
def get_score_class(score):
    if score >= 80:
        return "score-high"
    elif score >= 60:
        return "score-medium"
    else:
        return "score-low"

def create_radar_chart(scenario_data):
    # Extract area names and scores
    areas = list(scenario_data["areas"].keys())
    scores = list(scenario_data["areas"].values())
    
    # Set up the radar chart
    angles = np.linspace(0, 2*np.pi, len(areas), endpoint=False).tolist()
    scores += scores[:1]  # Close the circle
    angles += angles[:1]  # Close the circle
    areas += areas[:1]    # Close the circle
    
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.plot(angles, scores, color=scenario_data["color"], linewidth=2)
    ax.fill(angles, scores, color=scenario_data["color"], alpha=0.25)
    
    # Set the labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(areas[:-1], size=8)
    
    # Set y limits
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], size=7)
    
    # Add title
    plt.title(scenario_data["name"], size=12, color='#333', pad=15)
    
    # Set background color to transparent
    ax.set_facecolor('white')
    fig.patch.set_alpha(0.0)
    
    return fig

# Get user data
user_data = get_user_data()

# Display dashboard header
#st.markdown('<div class="big-title">🛡️ CyberGuard Security Dashboard</div>', unsafe_allow_html=True)
#st.markdown('<div class="subtitle">Your personalized cybersecurity performance overview</div>', unsafe_allow_html=True)

# User information header
with st.container():
    st.markdown(f"""
    <div class="dashboard-header">
        <h2>Welcome back, {user_data["name"]}!</h2>
        <p>{user_data["department"]} Department • Assessment completed on {user_data["completed_date"]}</p>
    </div>
    """, unsafe_allow_html=True)

# Top metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">OVERALL SECURITY SCORE</div>
        <div class="metric-value" style="color: {"#10B981" if user_data["overall_score"] >= 80 else "#F59E0B" if user_data["overall_score"] >= 60 else "#EF4444"}">
            {user_data["overall_score"]}/100
        </div>
        <div class="progress-wrapper">
            <div class="progress-bar" style="width: {user_data["overall_score"]}%; background-color: {"#10B981" if user_data["overall_score"] >= 80 else "#F59E0B" if user_data["overall_score"] >= 60 else "#EF4444"};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">STRONGEST AREA</div>
        <div class="metric-value" style="color: #10B981;">
            {user_data["strongest_scenario"]["name"]}
        </div>
        <span class="score-badge score-high">{user_data["strongest_scenario"]["score"]}/100</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">NEEDS IMPROVEMENT</div>
        <div class="metric-value" style="color: #EF4444;">
            {user_data["weakest_scenario"]["name"]}
        </div>
        <span class="score-badge score-low">{user_data["weakest_scenario"]["score"]}/100</span>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">SCENARIOS COMPLETED</div>
        <div class="metric-value" style="color: #3B82F6;">
            {st.session_state.completed_number}/3
        </div>
        <span style="color: {'#10B981' if st.session_state.completed_number == 3 else '#F59E0B'}; font-weight: bold;">
            {'✓ All Complete' if st.session_state.completed_number == 3 else f'{3 - st.session_state.completed_number} Remaining'}
        </span>
    </div>
    """, unsafe_allow_html=True)

# Main content
st.write("")  # Spacer
col1, col2 = st.columns([2, 1])

# Left column - Scenario performance
with col1:
    st.markdown('<div class="section-title">Scenario Performance</div>', unsafe_allow_html=True)
    
    # Create a DataFrame for the scenarios
    completed_scenarios = [s for s in user_data["scenarios"] if s["completed"]]
    if completed_scenarios:
        scenario_df = pd.DataFrame({
            'Scenario': [s['name'] for s in completed_scenarios],
            'Score': [s['score'] for s in completed_scenarios],
            'Color': [s['color'] for s in completed_scenarios]
        })
        
        # Create a horizontal bar chart
        chart = alt.Chart(scenario_df).mark_bar().encode(
            x=alt.X('Score:Q', scale=alt.Scale(domain=[0, 100])),
            y=alt.Y('Scenario:N', sort='-x'),
            color=alt.Color('Color:N', scale=None),
            tooltip=['Scenario', 'Score']
        ).properties(
            height=200
        )
        
        # Add text labels
        text = chart.mark_text(
            align='left',
            baseline='middle',
            dx=3,
            color='white',
            fontSize=14,
            fontWeight='bold'
        ).encode(
            text='Score:Q'
        )
        
        # Combine chart and text
        st.altair_chart(chart + text, use_container_width=True)
    else:
        st.info("Complete scenarios to see your performance. Each scenario assesses different cybersecurity skills.")
    
    # Individual scenario details
    st.markdown('<div class="section-title">Detailed Analysis</div>', unsafe_allow_html=True)
    
    # Create two columns for the radar charts
    radar_col1, radar_col2 = st.columns(2)
    
    # Check which scenarios are completed
    completed_scenarios_dict = {s["name"]: s for s in user_data["scenarios"] if s["completed"]}
    
    # Show radar charts for completed scenarios
    if len(completed_scenarios_dict) > 0:
        scenario_count = 0
        for scenario in user_data["scenarios"]:
            if scenario["completed"]:
                col = radar_col1 if scenario_count % 2 == 0 else radar_col2
                with col:
                    st.pyplot(create_radar_chart(scenario))
                    if scenario_count < len(completed_scenarios_dict) - 1:
                        st.write("")  # Spacer
                scenario_count += 1
    else:
        with radar_col1:
            st.info("Complete scenarios to see detailed analysis of your performance in specific security areas.")
        
        with radar_col2:
            st.markdown("""
            <div class="insight-card">
                <h4>What does this measure?</h4>
                <p>Each scenario evaluates different aspects of cybersecurity awareness:</p>
                <ul>
                    <li><b>Phishing Awareness:</b> Identifying and responding to phishing attempts</li>
                    <li><b>Password Security:</b> Creating and managing secure passwords</li>
                    <li><b>Social Engineering:</b> Recognizing and handling social engineering tactics</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

# Right column - Strengths, Weaknesses, Recommendations
with col2:
    # Strengths section
    st.markdown('<div class="section-title">Your Strengths</div>', unsafe_allow_html=True)
    for strength in user_data["strengths"]:
        st.markdown(f'<div class="strength-item">✓ {strength}</div>', unsafe_allow_html=True)
    
    # Weaknesses section
    st.markdown('<div class="section-title">Areas for Improvement</div>', unsafe_allow_html=True)
    for weakness in user_data["weaknesses"]:
        st.markdown(f'<div class="weakness-item">⚠ {weakness}</div>', unsafe_allow_html=True)
    
    # Recommendations section
    st.markdown('<div class="section-title">Personalized Recommendations</div>', unsafe_allow_html=True)
    for recommendation in user_data["recommendations"]:
        st.markdown(f'<div class="recommendation-item">→ {recommendation}</div>', unsafe_allow_html=True)
    
    # Security insights section to replace training history
    st.markdown('<div class="section-title">Security Insights</div>', unsafe_allow_html=True)
    
    # Check if any scenarios are completed
    if st.session_state.completed_number > 0:
        # Create a simple gauge chart
        score = user_data["overall_score"]
        fig, ax = plt.subplots(figsize=(6, 2))
        
        # Define the gauge
        ax.barh([0], [100], height=0.5, color='#EFF6FF')
        ax.barh([0], [score], height=0.5, color='#10B981' if score >= 80 else '#F59E0B' if score >= 60 else '#EF4444')
        
        # Add labels
        ax.text(0, 0, '0', ha='center', va='center', fontsize=10)
        ax.text(50, 0, '50', ha='center', va='center', fontsize=10)
        ax.text(100, 0, '100', ha='center', va='center', fontsize=10)
        ax.text(score, -0.5, f'{score}', ha='center', va='center', fontsize=12, fontweight='bold')
        
        # Clean up the chart
        ax.set_xlim(0, 100)
        ax.set_ylim(-1, 1)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_frame_on(False)
        
        st.pyplot(fig)
        
        # Add interpretation
        if score >= 80:
            status = "Strong"
            color = "#10B981"
            interpretation = "You demonstrate excellent security awareness. Continue practicing these skills."
        elif score >= 60:
            status = "Moderate"
            color = "#F59E0B"
            interpretation = "You have a good foundation but could benefit from additional training in certain areas."
        else:
            status = "Needs Improvement"
            color = "#EF4444"
            interpretation = "Your security awareness requires significant development. Focus on the recommendations provided."
        
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 15px;">
            <span style="font-size: 18px; font-weight: bold; color: {color};">Security Status: {status}</span>
        </div>
        <p>{interpretation}</p>
        """, unsafe_allow_html=True)
        
    else:
        st.info("Complete at least one security scenario to see your performance insights and security status.")

# Call to action section
st.write("")  # Spacer
st.markdown('<div class="section-title">Next Steps</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #3B82F6;">📚 Continue Learning</h3>
        <p>Explore additional security modules to further enhance your skills.</p>
        <button style="background-color: #3B82F6; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
            View Courses
        </button>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #10B981;">📊 Download Report</h3>
        <p>Get a detailed PDF report of your security performance.</p>
        <button style="background-color: #10B981; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
            Download PDF
        </button>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #F59E0B;">👨‍💼 Schedule Consultation</h3>
        <p>Book a 1:1 session with our security team for personalized guidance.</p>
        <button style="background-color: #F59E0B; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
            Book Session
        </button>
    </div>
    """, unsafe_allow_html=True)

# Add a security certification badge at the bottom
st.write("")  # Spacer
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.session_state.completed_number == 3:
        st.markdown("""
        <div style="text-align: center; padding: 20px; border: 2px dashed #3B82F6; border-radius: 10px; margin-top: 20px;">
            <h3 style="color: #1E3A8A;">🏆 CyberGuard Security Certified</h3>
            <p>You've completed all required security training modules. Your certification is valid until March 2025.</p>
            <button style="background-color: #1E3A8A; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
                View Certificate
            </button>
        </div>
        """, unsafe_allow_html=True)
    else:
        remaining = 3 - st.session_state.completed_number
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 2px dashed #6B7280; border-radius: 10px; margin-top: 20px;">
            <h3 style="color: #6B7280;">🏆 CyberGuard Security Certification</h3>
            <p>Complete {remaining} more scenario{'s' if remaining > 1 else ''} to earn your security certification.</p>
            <div style="background-color: #F3F4F6; padding: 8px 16px; border-radius: 5px; display: inline-block;">
                {st.session_state.completed_number}/3 Scenarios Completed
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer with last update info
st.markdown("""
<div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
    Dashboard last updated: February 26, 2025 • Next assessment due: May 26, 2025
</div>
""", unsafe_allow_html=True)