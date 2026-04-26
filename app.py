import streamlit as st
from openai import OpenAI
import time

# --- CONFIGURACIÓN DE MARCA Y ESTILO (FINTECH DARK) ---
st.set_page_config(page_title="English Negotiator | AI Lab", layout="wide")

# Inyección de CSS para estética Dark Mode + Neon Lime
st.markdown("""
    <style>
    /* Fondo y tipografía general */
    .stApp {
        background: radial-gradient(circle, #1a1a1a 0%, #050505 100%);
        color: #ffffff;
    }
    
    /* Botones estilo Pill y Neón */
    .stButton>button {
        border-radius: 50px;
        background-color: #D4FF48 !important;
        color: #000000 !important;
        font-weight: bold;
        border: none;
        padding: 0.6rem 2.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(212, 255, 72, 0.3);
    }
    .stButton>button:hover {
        box-shadow: 0 0 25px rgba(212, 255, 72, 0.6);
        transform: scale(1.02);
    }

    /* Tarjetas de Dashboard */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        backdrop-filter: blur(10px);
    }

    /* Waveform Simulado (Animación) */
    .waveform-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
        height: 150px;
    }
    .bar {
        width: 8px;
        background: linear-gradient(180deg, #D4FF48 0%, #4a5a1a 100%);
        border-radius: 4px;
        animation: pulse 1.2s infinite ease-in-out;
    }
    @keyframes pulse {
        0%, 100% { height: 20px; }
        50% { height: 80px; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NEGOCIO Y GAMIFICACIÓN ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "score" not in st.session_state:
    st.session_state.score = 0
if "level" not in st.session_state:
    st.session_state.level = "Explorer"

def update_gamification(text):
    # Lógica simple de detección para sumar puntos
    points = 0
    if "?" in text: points += 3  # Pregunta relevante
    if "because" in text or "reason" in text: points += 2 # Justificación
    if len(text.split()) > 10: points += 1 # Opinión clara
    
    st.session_state.score += points
    if st.session_state.score > 15: st.session_state.level = "Global Communicator"
    elif st.session_state.score > 10: st.session_state.level = "Strategist"
    elif st.session_state.score > 5: st.session_state.level = "Negotiator"

# --- INTERFAZ SUPERIOR (NAVBAR) ---
col_nav1, col_nav2 = st.columns([8, 2])
with col_nav1:
    st.markdown("<h2 style='color:#D4FF48; margin:0;'>TREASURIE </h2>", unsafe_allow_html=True)
with col_nav2:
    st.button("Login", key="login")

# --- HERO SECTION ---
col_hero_left, col_hero_right = st.columns([1.2, 1])

with col_hero_left:
    st.markdown(f"""
        <h1 style='font-size: 3.5rem; line-height: 1.1;'>AI-Driven <br><span style='color:#D4FF48;'>Communication Lab</span></h1>
        <p style='font-size: 1.2rem; color: #aaa; margin-bottom: 2rem;'>
        Empower your professional English through Socratic negotiation. 
        Analyze, justify, and resolve intercultural conflicts in real-time.
        </p>
    """, unsafe_allow_html=True)
    
    program = st.selectbox("CHOOSE YOUR PROGRAM:", 
                         ["Campus Life (Foundation)", 
                          "Workplace (Professional)", 
                          "Intercultural (Global)"])
    
    if st.button("START MISSION"):
        st.session_state.messages = []
        st.session_state.score = 0
        st.success("Scenario Loaded. Initializing Voice System...")

with col_hero_right:
    # ELEMENTO DINÁMICO: Waveform Neón
    st.markdown('<div class="waveform-container">' + 
                '<div class="bar" style="animation-delay: 0.1s"></div>' +
                '<div class="bar" style="animation-delay: 0.2s"></div>' +
                '<div class="bar" style="animation-delay: 0.3s"></div>' +
                '<div class="bar" style="animation-delay: 0.4s"></div>' +
                '<div class="bar" style="animation-delay: 0.5s"></div>' +
                '<div class="bar" style="animation-delay: 0.4s"></div>' +
                '<div class="bar" style="animation-delay: 0.3s"></div>' +
                '</div>', unsafe_allow_html=True)
    
    # DASHBOARD DE PUNTOS
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="metric-card">SCORE<br><h2 style="color:#D4FF48;">{st.session_state.score}</h2></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card">LEVEL<br><h4 style="color:#D4FF48;">{st.session_state.level}</h4></div>', unsafe_allow_html=True)

st.markdown("---")

# --- ÁREA DE CHAT (NEGOCIACIÓN SOCRÁTICA) ---
client = OpenAI(
    api_key=st.secrets["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Mostrar historial
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada de usuario
if prompt := st.chat_input("Negotiate here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    update_gamification(prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[
                {"role": "system", "content": f"You are a Socratic Fintech Tutor. Program: {program}. Rules: Ask 1-2 questions only. Never give answers. Force the student to justify. Tone: Professional and corporate."},
                *st.session_state.messages
            ]
        )
        full_response = response.choices[0].message.content
        st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    st.rerun()

# --- FOOTER / SERVICIOS ---
st.markdown("<br><br>", unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns(4)
services = [("Transfer", "→"), ("Payment", "→"), ("Online Shopping", "→"), ("Investment", "→")]
for col, (name, icon) in zip([f1, f2, f3, f4], services):
    with col:
        st.markdown(f"<p style='color:#D4FF48;'>{icon} {name}</p><p style='font-size:0.8rem;'>Learn more</p>", unsafe_allow_html=True)
