import streamlit as st
from openai import OpenAI
import time
import random

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
    
    /* Mensajes del Chat - Texto BLANCO para IA */
    .stChatMessage [data-testid="chatAvatarIcon-assistant"] ~ div [data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }
    
    .stChatMessage [data-testid="chatAvatarIcon-assistant"] ~ div {
        color: #ffffff !important;
    }
    
    div[data-testid="stChatMessageContent"] {
        color: #ffffff !important;
    }
    
    /* Contenedor de chat con fondo oscuro */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 10px;
    }
    
    /* Badge de programa activo */
    .program-badge {
        background: #D4FF48;
        color: #000000;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 20px;
    }
    
    /* Escenario en caja */
    .scenario-box {
        background: rgba(212, 255, 72, 0.05);
        border: 2px solid rgba(212, 255, 72, 0.3);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        color: #ffffff;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DICCIONARIO DE ESCENARIOS POR PROGRAMA ---
SCENARIOS = {
    "Campus Life (Foundation)": [
        {
            "title": "Conflict Resolution - Study Group",
            "scenario": "You're in a study group project. Your partner hasn't contributed anything in 2 weeks, and the presentation is in 3 days. When you bring it up, they get defensive and blame their other courses. How do you negotiate a fair resolution while keeping the relationship intact?"
        },
        {
            "title": "Accommodation Disagreement",
            "scenario": "You share an apartment with 3 roommates. One roommate constantly uses shared kitchen items without replacing them, creating tension. You need to address this without escalating the conflict. What's your approach?"
        },
        {
            "title": "Misunderstanding with Classmate",
            "scenario": "A classmate misunderstood something you said in group chat and thinks you were disrespectful. They've posted about it publicly. How do you handle this communication crisis?"
        }
    ],
    "Workplace (Professional)": [
        {
            "title": "Budget Cut Negotiation",
            "scenario": "Your department faces a 20% budget reduction. Your manager suggests cutting your professional development budget entirely. You believe this will hurt team morale and productivity. How do you present an alternative proposal?"
        },
        {
            "title": "Deadline Conflict",
            "scenario": "Two senior stakeholders have given you conflicting deadlines. Manager A wants deliverables by Friday, Manager B by next Wednesday. Both claim their deadline is critical. How do you navigate this without damaging relationships?"
        },
        {
            "title": "Salary Review Discussion",
            "scenario": "During your performance review, you were told there's 'no budget' for salary increases this year, despite exceeding all targets. How do you address compensation fairly without threatening your position?"
        }
    ],
    "Intercultural (Global)": [
        {
            "title": "Cross-Cultural Business Misunderstanding",
            "scenario": "In a video call with your international team, a German colleague made a blunt critique of your proposal, perceived as rude by US colleagues. Now there's tension. How do you bridge the cultural gap and refocus on the goal?"
        },
        {
            "title": "Time Zone Collaboration Issue",
            "scenario": "Your Asian team feels excluded because all meetings are scheduled during US hours. They're considering not participating, which affects project quality. How do you propose a fair solution for a global team?"
        },
        {
            "title": "Communication Style Conflict",
            "scenario": "Your Indian team prefers indirect, context-rich communication, while your UK team wants direct, concise messages. This is causing friction. How do you align communication without dismissing either culture?"
        }
    ]
}

# --- INICIALIZACIÓN DE ESTADO DE SESIÓN ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "score" not in st.session_state:
    st.session_state.score = 0
if "level" not in st.session_state:
    st.session_state.level = "Explorer"
if "program_selected" not in st.session_state:
    st.session_state.program_selected = None
if "mission_started" not in st.session_state:
    st.session_state.mission_started = False
if "current_scenario" not in st.session_state:
    st.session_state.current_scenario = None

# --- LÓGICA DE NEGOCIO Y GAMIFICACIÓN ---
def update_gamification(text):
    """Actualiza puntuación basada en calidad de respuesta"""
    points = 0
    if "?" in text: 
        points += 3  # Pregunta relevante
    if "because" in text or "reason" in text or "since" in text: 
        points += 2  # Justificación clara
    if len(text.split()) > 15: 
        points += 1  # Respuesta elaborada
    
    st.session_state.score += points
    
    # Actualizar nivel
    if st.session_state.score > 30: 
        st.session_state.level = "Master Negotiator"
    elif st.session_state.score > 20: 
        st.session_state.level = "Global Communicator"
    elif st.session_state.score > 15: 
        st.session_state.level = "Strategist"
    elif st.session_state.score > 10: 
        st.session_state.level = "Negotiator"

def generate_random_scenario(program):
    """Genera un escenario aleatorio para el programa seleccionado"""
    scenarios = SCENARIOS.get(program, [])
    if scenarios:
        return random.choice(scenarios)
    return None

def start_mission(program):
    """Inicia la misión con el programa seleccionado"""
    st.session_state.program_selected = program
    st.session_state.mission_started = True
    st.session_state.current_scenario = generate_random_scenario(program)
    st.session_state.messages = []
    st.session_state.score = 0

# --- INTERFAZ SUPERIOR (NAVBAR) ---
col_nav1, col_nav2 = st.columns([8, 2])
with col_nav1:
    st.markdown("<h2 style='color:#D4FF48; margin:0;'>TREASURIE</h2>", unsafe_allow_html=True)
with col_nav2:
    st.button("Login", key="login")

# --- FLUJO CONDICIONAL PRINCIPAL ---

# SECCIÓN 1: SELECCIONAR PROGRAMA (Si no ha iniciado misión)
if not st.session_state.mission_started:
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
                              "Intercultural (Global)"],
                             key="program_select")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("START MISSION", key="start_mission_btn"):
                start_mission(program)
                st.rerun()
        
        with col_btn2:
            if st.button("LEARN MORE", key="learn_more"):
                st.info("📚 Each program offers unique scenarios tailored to improve your negotiation skills in different contexts.")

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

# SECCIÓN 2: MISIÓN EN PROGRESO (Si la misión ha iniciado)
else:
    # Header de misión activa
    col_mission1, col_mission2, col_mission3 = st.columns([2, 3, 1])
    
    with col_mission1:
        st.markdown(f'<div class="program-badge">🎯 {st.session_state.program_selected}</div>', unsafe_allow_html=True)
    
    with col_mission2:
        st.markdown(f'<h3 style="color:#D4FF48; margin:0;">{st.session_state.current_scenario["title"]}</h3>', unsafe_allow_html=True)
    
    with col_mission3:
        if st.button("🔄 New Scenario", key="new_scenario"):
            st.session_state.current_scenario = generate_random_scenario(st.session_state.program_selected)
            st.session_state.messages = []
            st.rerun()
    
    # Mostrar escenario conflictivo
    st.markdown(f'<div class="scenario-box">{st.session_state.current_scenario["scenario"]}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Dashboard lateral
    col_dash1, col_dash2 = st.columns(2)
    with col_dash1:
        st.markdown(f'<div class="metric-card">SCORE<br><h2 style="color:#D4FF48;">{st.session_state.score}</h2></div>', unsafe_allow_html=True)
    with col_dash2:
        st.markdown(f'<div class="metric-card">LEVEL<br><h4 style="color:#D4FF48;">{st.session_state.level}</h4></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- ÁREA DE CHAT (NEGOCIACIÓN SOCRÁTICA) ---
    client = OpenAI(
        api_key=st.secrets["GEMINI_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    # Mostrar historial de chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Entrada de usuario
    if prompt := st.chat_input("Negotiate here...", key="chat_input"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        update_gamification(prompt)

        # Respuesta de IA
        with st.chat_message("assistant"):
            system_message = f"""You are a Socratic Fintech Tutor specializing in {st.session_state.program_selected}.

Current Scenario: {st.session_state.current_scenario["title"]}

Your role:
1. Ask ONLY 1-2 targeted questions to deepen their thinking
2. NEVER provide direct answers or solutions
3. Force the student to justify their reasoning
4. Maintain a professional, corporate tone
5. Keep responses concise (max 3-4 sentences)
6. Challenge their assumptions gently but firmly
7. Reference the scenario context in your questions

Remember: Your goal is Socratic dialogue, not instruction."""

            response = client.chat.completions.create(
                model="gemini-1.5-flash",
                messages=[
                    {"role": "system", "content": system_message},
                    *st.session_state.messages
                ]
            )
            full_response = response.choices[0].message.content
            st.markdown(f'<span style="color: #ffffff;">{full_response}</span>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        st.rerun()
    
    # Botón para volver al menú
    st.markdown("---")
    if st.button("← Back to Programs", key="back_to_programs"):
        st.session_state.mission_started = False
        st.session_state.program_selected = None
        st.session_state.messages = []
        st.rerun()

# --- FOOTER / SERVICIOS (Solo si no está en misión) ---
if not st.session_state.mission_started:
    st.markdown("<br><br>", unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    services = [("Transfer", "→"), ("Payment", "→"), ("Online Shopping", "→"), ("Investment", "→")]
    for col, (name, icon) in zip([f1, f2, f3, f4], services):
        with col:
            st.markdown(f"<p style='color:#D4FF48;'>{icon} {name}</p><p style='font-size:0.8rem;'>Learn more</p>", unsafe_allow_html=True)
