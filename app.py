import streamlit as st
from openai import OpenAI
import os
import pandas as pd

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI Communication Lab", layout="wide")

# =========================
# ESCENARIOS
# =========================
SCENARIOS = {
    "Campus Life": {
        "context": "You and your classmates disagree about the deadline for a group assignment.",
        "keywords": ["deadline", "assignment", "group", "time"],
    },
    "Workplace": {
        "context": "Your team disagrees about how to divide responsibilities in a project.",
        "keywords": ["responsibilities", "team", "project", "roles"],
    },
    "Global": {
        "context": "Your international partners think your communication style is too direct.",
        "keywords": ["culture", "communication", "style", "message"],
    }
}

# =========================
# ESTADO
# =========================
if "users" not in st.session_state:
    st.session_state.users = {}

# =========================
# FUNCIONES
# =========================

def tts(text):
    audio = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )
    return audio.read()

def ai_eval(text):
    prompt = f"""
    Evaluate this student response:
    "{text}"

    Give:
    - clarity (1-4)
    - negotiation (1-4)
    - appropriateness (1-4)

    Return JSON only.
    """

    response = client.responses.create(
        model="gpt-5.2",
        input=prompt
    )

    return response.output_text

def is_question(text):
    return "?" in text or text.lower().startswith(("what", "why", "how"))

def is_relevant(text, keywords):
    return any(k in text.lower() for k in keywords)

def level(score):
    if score <= 5:
        return "Explorer"
    elif score <= 10:
        return "Negotiator"
    elif score <= 15:
        return "Strategist"
    return "Global Communicator"

# =========================
# SIDEBAR DOCENTE
# =========================
st.sidebar.title("📊 Teacher Dashboard")

if st.session_state.users:
    df = pd.DataFrame(st.session_state.users).T
    st.sidebar.dataframe(df)

# =========================
# LOGIN SIMPLE
# =========================
student = st.text_input("Enter your name")

if student:
    if student not in st.session_state.users:
        st.session_state.users[student] = {
            "score": 0,
            "level": "Explorer"
        }

    scenario_name = st.selectbox("Choose your program", list(SCENARIOS.keys()))
    scenario = SCENARIOS[scenario_name]

    st.info(scenario["context"])

    # 🔊 VOZ IA
    if st.button("🔊 Listen to scenario"):
        audio_bytes = tts(scenario["context"])
        st.audio(audio_bytes)

    # =========================
    # INTERACCIÓN
    # =========================
    response = st.text_area("Your response")

    if st.button("Submit"):
        score = st.session_state.users[student]["score"]

        # evaluación básica
        if len(response.split()) > 4:
            score += 2

        if is_question(response):
            score += 2

        if is_relevant(response, scenario["keywords"]):
            score += 3
        else:
            st.warning("Not relevant to the scenario")

        # evaluación IA (rúbrica)
        eval_result = ai_eval(response)

        st.write("📄 AI Feedback:")
        st.code(eval_result)

        st.session_state.users[student]["score"] = score
        st.session_state.users[student]["level"] = level(score)

        st.success(f"Score: {score} | Level: {level(score)}")