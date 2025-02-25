import streamlit as st
from utilities.icon import page_icon

st.set_page_config(
    page_title="Your Results",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    page_icon("📊")
    st.subheader("Your Training Results", divider="red", anchor=False)
    st.write("Your cybersecurity training results and progress will be displayed here.")

if __name__ == "__main__":
    main() 