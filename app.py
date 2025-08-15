import streamlit as st
import json
import random
import os
import pandas as pd
import requests

# API URL for the generative language model
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Function to send API request and get hint or explanation
def chatbot_response(question):
    try:
        response = requests.post(f"{API_URL}?key=AIzaSyD_ySnDcymZXVzViLi0GULdkVDexk0hqCY", json={
            "contents": [{"parts": [{"text": question}]}]
        })
        response.raise_for_status()
        result = response.json()

        if 'candidates' in result and len(result['candidates']) > 0:
            content = result['candidates'][0].get('content', {})
            if 'parts' in content and len(content['parts']) > 0:
                hint_text = content['parts'][0].get('text', "No explanation available.")
                return hint_text.strip()
        return "No explanation available."

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching explanation: {e}")
        return "No explanation available."

# Function to load questions from JSON files
def load_data(filename):
    file_path = os.path.join("data", filename)
    if not os.path.exists(file_path):
        st.error(f"⚠️ File not found: {file_path}. Please check if the file exists.")
        return []
    with open(file_path, "r") as file:
        return json.load(file)

# Initialize session state
for key, default in {
    "score": 0,
    "badges": [],
    "answers": {},
    "current_question": 0,
    "quiz_finished": False,
    "username": "",
    "quiz_started": False,
    "page": "Home",
    "current_blank": 0,
    "blank_answers": {},
    "blank_finished": False,
    "easy_count": 0,
    "medium_count": 0,
    "difficult_count": 0,
    "unit": 1  # Default to unit 1
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# UI Design
st.set_page_config(page_title="AI Gamification", layout="wide")
st.title("🎮 AI-Driven Gamification in Teaching & Learning")

# Sidebar Navigation
st.sidebar.title("Navigation")
page_selection = st.sidebar.radio("Go to", ["Home", "Quiz", "Fill in the Blank", "Leaderboard", "Doubt"])

if page_selection:
    st.session_state["page"] = page_selection

# Home Page
if st.session_state["page"] == "Home":
    st.header("Welcome to AI Gamification Platform!")
    st.write("This platform enhances learning using AI-driven quizzes, fill-in-the-blanks, and gamification elements like badges and leaderboards.")

    st.subheader("Enter Your Name to Start the Quiz")
    username = st.text_input("Name:", key="username_input")

    if st.button("Submit"):
        if username.strip():
            st.session_state["username"] = username.strip()
            st.session_state["quiz_started"] = True
            st.session_state["page"] = "Quiz"
            st.rerun()
        else:
            st.error("Please enter a valid name.")

# Quiz Page
# Quiz Page
if st.session_state["page"] == "Quiz":
    st.header(f"📝 Quiz Time! Welcome, {st.session_state['username']}!")
    st.subheader("Choose a Unit for the Quiz")
    unit = st.selectbox("Select Unit", [1, 2, 3, 4, 5], key="unit_selection")

    # Load the selected unit's questions
    questions = load_data(f"unit{unit}.json")

    if not questions:
        st.warning("No questions available for this unit.")
    else:
        st.session_state["unit"] = unit  # Save selected unit
        total_questions = len(questions)
        question_idx = st.session_state["current_question"]

        if not st.session_state["quiz_finished"]:
            q = questions[question_idx]
            st.write(f"**Question {question_idx + 1} of {total_questions}:** {q['question']}")
            answer = st.radio("Select an answer:", [""] + q["options"], key=f"unit{unit}_q{question_idx}")

            if st.button("Hint"):
                hint = chatbot_response(q['question'])
                st.info(f"💡 Hint: {hint}")

            if st.button("Next Question"):
                if answer and answer != "":
                    st.session_state["answers"][question_idx] = answer
                    if answer == q['answer']:
                        # Track correct answers by difficulty
                        if q['difficulty'] == 'easy':
                            st.session_state['easy_count'] += 1
                        elif q['difficulty'] == 'medium':
                            st.session_state['medium_count'] += 1
                        elif q['difficulty'] == 'difficult':
                            st.session_state['difficult_count'] += 1
                    if question_idx < total_questions - 1:
                        st.session_state["current_question"] += 1
                    else:
                        st.session_state["quiz_finished"] = True
                st.rerun()

        else:
            correct_answers = sum(1 for i, q in enumerate(questions) if st.session_state["answers"].get(i) == q["answer"])
            st.session_state["score"] = correct_answers * 10
            st.success(f"🎉 Quiz Completed! Your final score: {st.session_state['score']}")

            # Check and compare with previous score
            previous_score = st.session_state.get("previous_score", 0)
            if previous_score > 0:
                if st.session_state["score"] > previous_score:
                    st.success("🌟 Great job! You've improved your score!")
                elif st.session_state["score"] == previous_score:
                    st.info("You maintained your score. Keep it up!")
                else:
                    st.warning("Don't be discouraged! Try to improve your score next time.")
            else:
                st.info("This is your first quiz! Keep it up!")

            # Save to leaderboard
            leaderboard_file = "quiz_leaderboard.xlsx"
            if os.path.exists(leaderboard_file):
                leaderboard_df = pd.read_excel(leaderboard_file)
            else:
                leaderboard_df = pd.DataFrame(columns=["Name", "Score", "Quiz", "Easy", "Medium", "Difficult"])
            new_entry = pd.DataFrame({
                "Name": [st.session_state["username"]],
                "Score": [st.session_state["score"]],
                "Quiz": [f"Quiz {unit}"],
                "Easy": [st.session_state['easy_count']],
                "Medium": [st.session_state['medium_count']],
                "Difficult": [st.session_state['difficult_count']]
            })
            leaderboard_df = pd.concat([leaderboard_df, new_entry], ignore_index=True)
            leaderboard_df.to_excel(leaderboard_file, index=False)

            # Update previous score for next comparison
            st.session_state["previous_score"] = st.session_state["score"]

            st.session_state["quiz_finished"] = False
            st.session_state["current_question"] = 0  # Reset the question index for the next quiz

#fill in the blank
if st.session_state["page"] == "Fill in the Blank":
    import random
    import os
    import pandas as pd

    st.header("✍️ Fill in the Blank!")

    total_questions = 10
    question_idx = st.session_state["current_blank"]

    if question_idx < total_questions:
        # Check if question is already generated
        if f"blank_q{question_idx}" not in st.session_state:
            topics = ["Operating System", "Artificial Intelligence", "Python Programming"]
            topic = random.choice(topics)
            difficulty = random.choice(["easy", "medium", "difficult"])

            prompt = f"Generate a {difficulty} fill-in-the-blank question with a single blank and answer for the topic: {topic}. Respond in the format: Question: ... Answer: ..."

            ai_response = chatbot_response(prompt)

            if "Question:" in ai_response and "Answer:" in ai_response:
                question_text = ai_response.split("Question:")[1].split("Answer:")[0].strip()
                answer_text = ai_response.split("Answer:")[1].strip()

                st.session_state[f"blank_q{question_idx}"] = question_text
                st.session_state[f"blank_a{question_idx}"] = answer_text
                st.session_state[f"blank_difficulty{question_idx}"] = difficulty
            else:
                st.warning("⚠️ Couldn't parse the AI's question format correctly.")
                st.stop()

        # Get stored question/answer/difficulty
        question_text = st.session_state[f"blank_q{question_idx}"]
        answer_text = st.session_state[f"blank_a{question_idx}"]
        difficulty = st.session_state[f"blank_difficulty{question_idx}"]

        st.subheader(f"Difficulty Level: :blue[{difficulty.capitalize()}]")
        st.write(f"**Question {question_idx + 1} of {total_questions}:** {question_text}")

        user_answer = st.text_input("Your Answer:", key=f"blank_{question_idx}_input")

        hint_col, submit_col = st.columns(2)

        with hint_col:
            if st.button("Hint", key=f"hint_button_{question_idx}"):
                hint = chatbot_response(f"Give me a hint for this fill-in-the-blank question: {question_text}")
                st.info(f"💡 Hint: {hint}")

        with submit_col:
            if st.button("Submit Answer", key=f"submit_button_{question_idx}"):
                if user_answer.strip().lower() == answer_text.lower():
                    st.success("✅ Correct!")
                    st.session_state["score"] += 10

                    # Count based on difficulty
                    if difficulty == 'easy':
                        st.session_state['easy_count'] += 1
                    elif difficulty == 'medium':
                        st.session_state['medium_count'] += 1
                    elif difficulty == 'difficult':
                        st.session_state['difficult_count'] += 1
                else:
                    st.error("❌ Incorrect.")
                    st.info(f"✅ Correct Answer: {answer_text}")
                    explanation = chatbot_response(f"Explain why the correct answer to this fill-in-the-blank question is: {answer_text}")
                    st.write(f"🧠 Explanation: {explanation}")

                # Move to next question after feedback
                st.session_state["current_blank"] += 1
                st.rerun()

    else:
        st.success("🎉 You've completed all 10 fill-in-the-blank questions!")

        # Save to leaderboard
        leaderboard_file = "fill_leaderboard.xlsx"
        if os.path.exists(leaderboard_file):
            leaderboard_df = pd.read_excel(leaderboard_file)
        else:
            leaderboard_df = pd.DataFrame(columns=["Name", "Score", "Easy", "Medium", "Difficult"])

        prev_scores = leaderboard_df[leaderboard_df["Name"] == st.session_state["username"]]["Score"]
        previous_score = prev_scores.iloc[-1] if not prev_scores.empty else None

        new_entry = pd.DataFrame({
            "Name": [st.session_state["username"]],
            "Score": [st.session_state["score"]],
            "Easy": [st.session_state['easy_count']],
            "Medium": [st.session_state['medium_count']],
            "Difficult": [st.session_state['difficult_count']]
        })
        leaderboard_df = pd.concat([leaderboard_df, new_entry], ignore_index=True)
        leaderboard_df.to_excel(leaderboard_file, index=False)

        # Final Feedback
        st.subheader("📊 Final Feedback:")
        final_score = st.session_state["score"]

        if final_score >= 90:
            st.success(f"🌟 Outstanding! You scored {final_score}/100. Truly exceptional work!")
        elif 70 <= final_score < 90:
            st.success(f"👍 Great Job! You scored {final_score}/100. Keep aiming higher!")
        elif 50 <= final_score < 70:
            st.info(f"📈 Fair Attempt! You scored {final_score}/100. Keep practicing and you'll improve!")
        elif 30 <= final_score < 50:
            st.warning(f"⚡ Needs More Practice. You scored {final_score}/100. Don't give up!")
        else:
            st.error(f"🛠️ Try Again. You scored {final_score}/100. Failure is part of success!")
 # Compare with previous
        if previous_score is not None:
            score_diff = final_score - previous_score
            if score_diff > 0:
                st.info(f"📈 You improved by {score_diff} points compared to your last attempt!")
            elif score_diff < 0:
                st.info(f"📉 Your score decreased by {abs(score_diff)} points. Reflect and bounce back!")
            else:
                st.info("⚡ You matched your previous score! Consistency is impressive!")
        else:
            st.info(f"This was your first attempt! 🎉 Well done scoring {final_score}/100!")


# Leaderboard Page
if st.session_state["page"] == "Leaderboard":
    st.header("🏆 Leaderboard")

    leaderboard_type = st.selectbox("Select Leaderboard", ["Quiz", "Fill in the Blank"])
    leaderboard_file = "quiz_leaderboard.xlsx" if leaderboard_type == "Quiz" else "fill_leaderboard.xlsx"

    if os.path.exists(leaderboard_file):
        leaderboard_df = pd.read_excel(leaderboard_file)
        if leaderboard_type == "Quiz" and "Quiz" in leaderboard_df.columns:
            leaderboard_df = leaderboard_df[["Name", "Score", "Quiz", "Easy", "Medium", "Difficult"]]
        st.dataframe(leaderboard_df.sort_values(by="Score", ascending=False).reset_index(drop=True))
    else:
        st.write("No leaderboard data available for this section.")

    st.subheader(f"Your Score: {st.session_state['score']}")
    st.write(f"Your Badges: {', '.join(st.session_state['badges']) if st.session_state['badges'] else 'No badges yet'}")
    st.progress(min(st.session_state['score'] / 100, 1.0))


# Doubt Page
if st.session_state["page"] == "Doubt":
    st.header("❓ Ask Your Doubt")
    st.write("Have a question or doubt related to your subject? Ask below and let the AI help you out!")

    user_question = st.text_area("Type your question here...", key="doubt_input")

    if st.button("Get Answer"):
        if user_question.strip():
            with st.spinner("Getting your answer..."):
                answer = chatbot_response(user_question)
            st.success("Here's the AI's response:")
            st.info(answer)
        else:
            st.warning("Please enter a question before submitting.")
