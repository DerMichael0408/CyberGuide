import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
from datetime import datetime
import time
from utilities.template import setup_page

# Use the common setup_page function instead of manual configuration
setup_page(
    page_title="CyberGuide - Security Dashboard",
    icon_emoji="🛡️", 
    subtitle="Track your security training progress"
)

# Custom CSS for better styling
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
    .badge-incident {
        background-color: #F59E0B;
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
</style>
""", unsafe_allow_html=True)

# Mock data for demonstration - In a real app, this would come from a database
def get_user_data():
    return {
        "name": "Michael Schmidt",
        "email": "michael.schmidt@example.com",
        "department": "Finance",
        "completed_date": datetime.now().strftime("%B %d, %Y"),
        "overall_score": 76,
        "scenarios": [
            {
                "name": "Phishing Awareness",
                "score": 82,
                "badge": "badge-phishing",
                "areas": {
                    "Identification": 85,
                    "Response": 80,
                    "Prevention": 70
                },
                "color": "#3B82F6"
            },
            {
                "name": "Password Security",
                "score": 65,
                "badge": "badge-password",
                "areas": {
                    "Password Strength": 60,
                    "Password Management": 75,
                    "Multi-Factor Authentication": 55
                },
                "color": "#8B5CF6"
            },
            {
                "name": "Social Engineering",
                "score": 90,
                "badge": "badge-social",
                "areas": {
                    "Awareness": 95,
                    "Detection": 85,
                    "Response": 90
                },
                "color": "#EC4899"
            },
            {
                "name": "Incident Response",
                "score": 70,
                "badge": "badge-incident",
                "areas": {
                    "Identification": 65,
                    "Containment": 75,
                    "Recovery": 70,
                    "Reporting": 60
                },
                "color": "#F59E0B"
            }
        ],
        "strengths": [
            "Strong ability to recognize social engineering attempts",
            "Good understanding of phishing email indicators",
            "Effective knowledge of security incident escalation procedures"
        ],
        "weaknesses": [
            "Password management practices need improvement",
            "Limited understanding of multi-factor authentication benefits",
            "Incident reporting procedures need more attention"
        ],
        "recommendations": [
            "Enroll in the password management workshop next month",
            "Enable MFA on all company accounts as soon as possible",
            "Review the incident response protocol documentation",
            "Schedule a 1:1 session with the security team for personalized guidance"
        ],
        "training_history": [
            {"date": "2023-10-15", "name": "Security Basics", "score": 72},
            {"date": "2023-11-20", "name": "Email Security", "score": 78},
            {"date": "2024-01-10", "name": "Data Protection", "score": 81},
            {"date": "2024-02-25", "name": "Cyber Threats", "score": 76}
        ]
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

def main():
    # Remove the duplicate title since setup_page already adds one
    st.markdown('<div class="subtitle">Your personal security training overview</div>', unsafe_allow_html=True)
    
    # Get sample user data
    user_data = get_user_data()
    
    # Role display
    if 'selected_role' in st.session_state and st.session_state.selected_role:
        st.markdown(f"**Current Role:** {st.session_state.selected_role}", unsafe_allow_html=True)
    
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
                {max(user_data["scenarios"], key=lambda x: x["score"])["name"]}
            </div>
            <span class="score-badge score-high">{max(user_data["scenarios"], key=lambda x: x["score"])["score"]}/100</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">NEEDS IMPROVEMENT</div>
            <div class="metric-value" style="color: #EF4444;">
                {min(user_data["scenarios"], key=lambda x: x["score"])["name"]}
            </div>
            <span class="score-badge score-low">{min(user_data["scenarios"], key=lambda x: x["score"])["score"]}/100</span>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">SCENARIOS COMPLETED</div>
            <div class="metric-value" style="color: #3B82F6;">
                4/4
            </div>
            <span style="color: #10B981; font-weight: bold;">✓ All Complete</span>
        </div>
        """, unsafe_allow_html=True)

    # Main content
    st.write("")  # Spacer
    col1, col2 = st.columns([2, 1])

    # Left column - Scenario performance
    with col1:
        st.markdown('<div class="section-title">Scenario Performance</div>', unsafe_allow_html=True)
        
        # Create a DataFrame for the scenarios
        scenario_df = pd.DataFrame({
            'Scenario': [s['name'] for s in user_data['scenarios']],
            'Score': [s['score'] for s in user_data['scenarios']],
            'Color': [s['color'] for s in user_data['scenarios']]
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
        
        # Individual scenario details
        st.markdown('<div class="section-title">Detailed Analysis</div>', unsafe_allow_html=True)
        
        # Create two columns for the radar charts
        radar_col1, radar_col2 = st.columns(2)
        
        with radar_col1:
            # First radar chart
            st.pyplot(create_radar_chart(user_data["scenarios"][0]))
            st.write("")  # Spacer
            # Third radar chart
            st.pyplot(create_radar_chart(user_data["scenarios"][2]))
            
        with radar_col2:
            # Second radar chart
            st.pyplot(create_radar_chart(user_data["scenarios"][1]))
            st.write("")  # Spacer
            # Fourth radar chart
            st.pyplot(create_radar_chart(user_data["scenarios"][3]))

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
        
        # Training history
        st.markdown('<div class="section-title">Training History</div>', unsafe_allow_html=True)
        
        # Create a DataFrame for training history
        history_df = pd.DataFrame(user_data["training_history"])
        history_df['date'] = pd.to_datetime(history_df['date'])
        history_df = history_df.sort_values('date')
        
        # Create a line chart for training progress
        line_chart = alt.Chart(history_df).mark_line(point=True).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('score:Q', scale=alt.Scale(domain=[50, 100]), title='Score'),
            tooltip=['name', 'date', 'score']
        ).properties(
            height=200
        )
        
        st.altair_chart(line_chart, use_container_width=True)

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
        st.markdown("""
        <div style="text-align: center; padding: 20px; border: 2px dashed #3B82F6; border-radius: 10px; margin-top: 20px;">
            <h3 style="color: #1E3A8A;">🏆 CyberGuard Security Certified</h3>
            <p>You've completed all required security training modules. Your certification is valid until March 2025.</p>
            <button style="background-color: #1E3A8A; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
                View Certificate
            </button>
        </div>
        """, unsafe_allow_html=True)

    # Footer with last update info
    st.markdown("""
    <div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
        Dashboard last updated: February 25, 2025 • Next assessment due: May 25, 2025
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()