import streamlit as st
from openai import OpenAI

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILO (NO SE TOCA LA GRÁFICA) ---
st.set_page_config(page_title="English Negotiator | AI Lab", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle, #1a1a1a 0%, #050505 100%);
        color: #ffffff;
    }
    .stButton>button {
        border-radius: 50px;
        background-color: #D4FF48 !important;
        color: #000000 !important;
        font-weight: bold;
        border: none;
        padding: 0.6rem 2.5rem;
        box-shadow: 0 0 15px rgba(212, 255, 72, 0.3);
    }
    /* Forzar texto blanco en los mensajes de chat */
    .stChatMessage p, .stChatMessage span {
        color: white !important;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
    }
    /* Waveform Animado */
    .waveform-container { display: flex; align-items: center; justify-content: center; gap: 4px; height: 100px; }
    .bar { width: 8px; background: linear-gradient(180deg, #D4FF48 0%, #4a5a1a 100%); border-radius: 4px; animation: pulse 1.2s infinite ease-in-out; }
    @keyframes pulse { 0%, 100% { height: 20px; } 50% { height: 80px; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXIÓN API ---
client = OpenAI(
    api_key=st.secrets["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# --- 3. LÓGICA DE ESTADO ---
if "messages" not in st.session_state: st.session_state.messages = []
if "score" not in st.session_state: st.session_state.score = 0
if "level" not in st.session_state: st.session_state.level = "Explorer"

# --- 4. HEADER Y HERO SECTION ---
st.markdown("<h2 style='color:#D4FF48; margin:0;'>TREASURIE</h2>", unsafe_allow_html=True)

col_hero_left, col_hero_right = st.columns([1.2, 1])

with col_hero_left:
    st.markdown("<h1 style='font-size: 3.5rem; line-height: 1.1;'>AI-Driven <br><span style='color:#D4FF48;'>Communication Lab</span></h1>", unsafe_allow_html=True)
    
    program = st.selectbox("CHOOSE YOUR PROGRAM:", 
                         ["Campus Life", "Workplace Communication", "Intercultural Negotiation"])
    
    if st.button("START MISSION"):
        st.session_state.messages = []
        st.session_state.score = 0
        
        # Generación de escenario único (Anti-plagio)
        with st.spinner("Generating unique conflict..."):
            prompt_gen = f"Create a unique, brief (max 50 words) conflict scenario for a {program} program. Must be highly argumentative but concise. End with a Socratic question."
            res = client.chat.completions.create(
                model="gemini-1.5-flash",
                messages=[{"role": "system", "content": "You are a creative scenario generator. Create diverse and non-repetitive English negotiation cases."},
                          {"role": "user", "content": prompt_gen}]
            )
            scenario = res.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": scenario})
        st.rerun()

with col_hero_right:
    # Waveform dinámico
    st.markdown('<div class="waveform-container">' + 
                '<div class="bar" style="animation-delay: 0.1s"></div>' * 7 + 
                '</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1: st.markdown(f'<div class="metric-card">SCORE<br><h2 style="color:#D4FF48;">{st.session_state.score}</h2></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card">LEVEL<br><h4 style="color:#D4FF48;">{st.session_state.level}</h4></div>', unsafe_allow_html=True)

st.markdown("---")

# --- 5. ÁREA DE CHAT (LETRAS BLANCAS) ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(f"<span style='color: white;'>{msg['content']}</span>", unsafe_allow_html=True)

if prompt := st.chat_input("Negotiate here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Lógica de puntos básica
    st.session_state.score += 2
    
    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[{"role": "system", "content": "Socratic Tutor. White text only. Be concise (60 words max). Never give the answer."},
                      *st.session_state.messages]
        )
        tutor_reply = response.choices[0].message.content
        st.markdown(f"<span style='color: white;'>{tutor_reply}</span>", unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": tutor_reply})
    st.rerun()
