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
st.markdown(" #### 🔲 Click squares to toggle between black (1) and white (0)")
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

