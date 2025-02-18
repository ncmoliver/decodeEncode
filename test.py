import streamlit as st
import numpy as np
import os
from openai import OpenAI
from dotenv import load_dotenv

# Configure Streamlit Page
st.set_page_config(
    page_title="🔢📝 Interactive Binary Encoding Grid",
    layout="wide",
    initial_sidebar_state="auto",
)

st.title("Binary Transformer")

# Constants
GRID_ROWS = 1
GRID_COLS = 8

# Initialize session state
if "grid" not in st.session_state:
    st.session_state["grid"] = np.zeros((GRID_ROWS, GRID_COLS), dtype=int)
if "data_type" not in st.session_state:
    st.session_state["data_type"] = ["Number"] * GRID_ROWS
if "decoded_labels" not in st.session_state:
    st.session_state["decoded_labels"] = [""] * GRID_ROWS
if "quiz_questions" not in st.session_state:  # Store quiz questions
    st.session_state["quiz_questions"] = None  # Initialize to None

# Functions (no changes needed)
def toggle_square(row, col):
    st.session_state["grid"][row, col] = 1 - st.session_state["grid"][row, col]

def reset_grid():
    st.session_state["grid"] = np.zeros((GRID_ROWS, GRID_COLS), dtype=int)
    st.session_state["decoded_labels"] = [""] * GRID_ROWS
    st.rerun()

def calculate_number_value(binary_row):
    values = [2 ** i for i in range(len(binary_row))][::-1]
    return sum(v for v, b in zip(values, binary_row) if b == 1)

def binary_to_ascii(binary_row):
    binary_string = "".join(map(str, binary_row))
    try:
        ascii_value = int(binary_string, 2) if "1" in binary_string else 0
        return chr(ascii_value) if 32 <= ascii_value <= 126 else "?"
    except ValueError:  # Catch specific error
        return "?"

# Create the interactive grid (no changes needed)
st.subheader("🔲 Click squares to toggle between black (1) and white (0)")
for row in range(GRID_ROWS):
    cols = st.columns(GRID_COLS + 2)

    with cols[0]:
        st.session_state["data_type"][row] = st.selectbox(
            f"Row {row+1} Type", ["Number", "Text"], index=0 if st.session_state["data_type"][row] == "Number" else 1
        )

    binary_values = []

    for col in range(GRID_COLS):
        color = "black" if st.session_state["grid"][row, col] else "white"
        button_key = f"button_{row}_{col}"

        with cols[col + 1]:
            if st.button("⬛" if color == "black" else "⬜", key=button_key):
                toggle_square(row, col)
                st.rerun()

        binary_values.append(st.session_state["grid"][row, col])

# Display computed value (no changes needed)
st.markdown("---")
st.subheader("🔍 Output Interpretation")
col1, col2 = st.columns(2)
with col1:
    if st.session_state["data_type"][0] == "Number":
        st.info(f"**Total Value:** `{calculate_number_value(binary_values)}`")
    else:
        st.info(f"**ASCII Character:** `{binary_to_ascii(binary_values)}`")

with col2:
    if st.button("🔄 Reset Grid"):
        reset_grid()

##########################################----------------- Quiz -----------------------##########################################
import json

load_dotenv('.env')

def generate_quiz(prompt):
    api_key = os.getenv('.env')
    client = OpenAI(api_key=api_key)

    try:
        completion = client.chat.completions.create(
            model="gpt-4",  # Use GPT-4 or any compatible model
            messages=[
            {"role": "developer", "content": (
                "You are an expert quiz creator who specializes in designing engaging and educational multiple-choice "
                "quizzes for middle school students. Your goal is to help students learn by solving real world problems "
                "Each question should be age-appropriate, interactive, and thought-provoking. "
                " Provide clear instructions, a question, and four multiple-choice "
                "answers (A, B, C, D), ensuring that one is correct while the others serve as reasonable distractors. "
                "At the end of each question, provide a short explanation for the correct answer."
            )},
            {"role": "user", "content": (
                "Create a multiple choice quiz challenging students to find like terms when solving a quadratic equation."
            )}, 
            {"role": "developer", "content": (
                """
                1. A racecar(r), a bicycle(b), scooter(s) are all variables in a quadratic equation. However you can only combine or add those with the same variable. 
                Take a look at this example:
                2r + 4b+ 5b + 2s = 5s + 7b + 1s - 5b
                On both sides of the equation you have sets of racecars or bicycles, or scooters that are alike that you can combine. 
                Try to simplify this equation. 

                A. 5r + 3b + 5s = 7b + 6s
                B. 2r + 9b + 2s = 6s + 2b
                C. 2b + 7r + 1s = 3s + 8b
                D. 4b + 5r + 1s = 3s + 3b

                correct_answer: B
                """
            )},
            {"role": "user", "content": (prompt)}
        ])

        quiz_text = completion.choices[0].message.content

        # Parse the quiz string into a list of dictionaries
        try:
            quiz_data = json.loads(quiz_text)  # Try parsing as JSON first
        except json.JSONDecodeError:  # If JSON fails, try custom parsing
            quiz_data = []
            questions = quiz_text.split('\n\n')  # Split into individual questions
            for q_block in questions:
                if q_block.strip():  # Skip empty blocks
                    lines = q_block.strip().split('\n')
                    question = lines[0]
                    options = {}
                    correct_answer = None
                    explanation = None
                    for line in lines[1:]:
                        if line.startswith(('A.', 'B.', 'C.', 'D.')):
                            option_letter = line[0]
                            options[option_letter] = line[3:].strip()
                        elif line.startswith("Correct Answer:"):
                            correct_answer = line.split("Correct Answer:")[1].strip()
                        elif line.startswith("Explanation:"):
                            explanation = line.split("Explanation:")[1].strip()

                    if question and options and correct_answer: # Check if all parts are present
                        quiz_data.append({
                            "question": question,
                            "options": options,
                            "correct_answer": correct_answer,
                            "explanation": explanation
                        })

        return quiz_data  # Return the list of dictionaries

    except Exception as e:
        st.error(f"Error generating quiz: {e}")
        return None


if "quiz_questions" not in st.session_state:
    st.session_state["quiz_questions"] = None
if "user_answers" not in st.session_state:
    st.session_state["user_answers"] = {}
if "quiz_submitted" not in st.session_state:
    st.session_state["quiz_submitted"] = False
if "current_question" not in st.session_state:
    st.session_state["current_question"] = 0  # Start at the first question

prompt = st.text_area("Describe Quiz")
start_button = st.button("Start Quiz")

if start_button:
    if st.session_state["quiz_questions"] is None:
        st.session_state["quiz_questions"] = generate_quiz(prompt)
        st.session_state["current_question"] = 0  # Reset to the first question
        st.session_state["user_answers"] = {} # Reset user answers
        st.session_state["quiz_submitted"] = False # Reset quiz submission status

if st.session_state["quiz_questions"]:
    total_questions = len(st.session_state["quiz_questions"])
    current_question_index = st.session_state["current_question"]

    for i in range(total_questions):  # Iterate through indices directly
        question_data = st.session_state["quiz_questions"][i]
        st.subheader(f"Question {i + 1} of {total_questions}")
        st.write(question_data["question"])
        options = question_data["options"]

        for option_letter, option_text in options.items():
            if i not in st.session_state["user_answers"]:  # Use question index 'i'
                st.session_state["user_answers"][i] = None

            def on_change_callback(question_index=i, answer=option_letter): # Define callback function inside the loop
                st.session_state["user_answers"][question_index] = answer

            st.radio(
                f"Option {option_letter}",
                [option_text],
                key=f"q{i}_{option_letter}",  # Keep the key unique
                horizontal=True,
                on_change=on_change_callback # Now it calls the correct callback
            )
        next_question = st.button("Next Question")

        if next_question:
            st.session_state["current_question"] += 1  # Go to the next question
            st.rerun()  # Force rerun to display the next question
        elif not st.session_state["quiz_submitted"]: # All questions answered, but not submitted
            pass
        submit_quiz_button = st.button("Submit Quiz")
        if submit_quiz_button:
            st.session_state["quiz_submitted"] = True
            st.rerun()  # Rerun to show results
    
    if st.session_state["quiz_submitted"]: # Show results after submission
        # ... (rest of your result display code - no changes needed)
        st.session_state["quiz_submitted"] = False #Reset for next quiz attempt
        st.session_state["user_answers"] = {}  #Reset for next quiz attempt
        st.session_state["quiz_questions"] = None #Reset for next quiz attempt
        st.session_state["current_question"] = 0  # Start at the first question
        st.rerun() # Rerun to start quiz from the beginning