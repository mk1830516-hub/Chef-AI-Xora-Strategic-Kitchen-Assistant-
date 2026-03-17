import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# --- CONFIGURATION & SETUP ---
load_dotenv()

# Get API Key from Environment
api_key = os.environ.get("GEMINI_API_KEY")

FILE_NAME = "chef_memory.json"

st.set_page_config(page_title="Chef AI-Xora", page_icon="👩‍🍳", layout="centered")

# --- DATA PERSISTENCE LOGIC (The Memory) ---
def load_data():
    if os.path.exists(FILE_NAME) and os.path.getsize(FILE_NAME) > 0:
        try:
            with open(FILE_NAME, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_data(chat_history):
    new_memory = []
    for message in chat_history:
        role_to_save = "model" if message["role"] == "assistant" else "user"
        new_memory.append({
            "role": role_to_save,
            "parts": [{"text": message["content"]}]
        })
    with open(FILE_NAME, "w") as diary:
        json.dump(new_memory, diary, indent=4)

# --- GEMINI AI SETUP ---
genai.configure(api_key=api_key)

# OFFICIAL CHALLENGE SYSTEM INSTRUCTIONS
instructions = """
Role:
You are 'Chef AI-Xora', a Strategic Kitchen Assistant. You are professional, helpful, and efficient.

Core Logic:
1. RESCUE MISSION: You are obsessed with 'Rescue Ingredients'. If the user mentions items about to expire, build the recipe around those VIP items.
2. MEMORY: Remember lifestyle (Keto, Vegan, etc.), health goals, and allergies mentioned in the chat.
3. BUDGET: Always consider the user's budget (Rs). Identify missing ingredients and suggest a shopping list within that budget.
4. FORMAT: All recipes MUST be displayed in a Markdown Table with columns: Ingredients | Time | Calories.
"""

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=instructions
)

# --- STREAMLIT UI ---

# Sidebar
with st.sidebar:
    # Kitchen/Chef Icon
    st.image("https://cdn-icons-png.flaticon.com/512/1830/1830839.png", width=100)
    st.title("Chef AI-Xora")
    st.subheader("Strategic Kitchen Assistant")
    
    st.markdown("---")
    # MANDATORY DEVELOPER CREDIT
    st.write("### Developed & Deployed by:")
    st.info("**Ammara M.Nadeem**")
    st.markdown("---")

    if st.button("🗑️ Reset Kitchen Memory"):
        if os.path.exists(FILE_NAME):
            os.remove(FILE_NAME)
        st.session_state.messages = []
        st.success("Memory Cleared!")
        st.rerun()

st.title("👨‍🍳 Chef AI-Xora: Manage Your Kitchen")
st.caption("A smart, waste-aware, and budget-conscious cooking expert.")

# --- SESSION INITIALIZATION ---
if "messages" not in st.session_state:
    saved_history = load_data()
    st.session_state.messages = []

    if saved_history:
        for msg in saved_history:
            st.session_state.messages.append({
                "role": "assistant" if msg["role"] == "model" else "user",
                "content": msg["parts"][0]["text"]
            })
    else:
        # Welcome message in English
        welcome_text = "Assalamu Alaikum! I am Chef AI-Xora. I'm here to help you manage your kitchen. Which ingredients are about to expire? Let's rescue them!"
        st.session_state.messages.append({"role": "assistant", "content": welcome_text})

# Display Chat History with Kitchen Icons
CHEF_ICON = "👨‍🍳"
USER_ICON = "👤"

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT LOGIC ---
if prompt := st.chat_input("I have some bread and tomatoes about to go bad..."):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):
        # Mandatory Spinner
        with st.spinner("Chef AI-Xora is preparing your strategy..."):
            history_for_gemini = []
            for m in st.session_state.messages[:-1]:
                history_for_gemini.append({
                    "role": "model" if m["role"] == "assistant" else "user",
                    "parts": [{"text": m["content"]}]
                })

            try:
                chat_session = model.start_chat(history=history_for_gemini)
                response = chat_session.send_message(prompt)

                st.markdown(response.text)

                # Save to session and file
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                save_data(st.session_state.messages)

            except Exception as e:
                st.error(f"Something went wrong: {e}")
