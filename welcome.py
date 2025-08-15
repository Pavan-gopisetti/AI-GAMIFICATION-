import streamlit as st

# Page Configuration
st.set_page_config(page_title="AI Gamification", page_icon="🎮", layout="centered")

# Welcome Page
st.title("🎮 AI-Driven Gamification in Teaching & Learning")
st.markdown("""
### Welcome to the AI Gamification Learning Experience! 🚀  
Enhance your AI knowledge through **interactive lessons, quizzes, and badges**.
- 📖 Learn AI concepts in a **structured** way.
- 🏆 Take quizzes and **earn badges**.
- 🎯 Test your skills and track your **progress**.

Click **Start Learning** to begin!
""")

# Start Button
if st.button("🚀 Start Learning"):
    st.switch_page("pages/app.py")  # ✅ Correct way to navigate to app.py
