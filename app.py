import streamlit as st
from openai import OpenAI
import time
import random

# --- CONFIGURACIÓN DE MARCA Y ESTILO (FINTECH DARK) ---
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
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(212, 255, 72, 0.3);
    }
    .stButton>button:hover {
        box-shadow: 0 0 25px rgba(212, 255, 72, 0.6);
        transform: scale(1.02);
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        backdrop-filter: blur(10px);
    }

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

    .stChatMessage [data-testid="chatAvatarIcon-assistant"] ~ div [data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }

    .stChatMessage [data-testid="chatAvatarIcon-assistant"] ~ div {
        color: #ffffff !important;
    }

    div[data-testid="stChatMessageContent"] {
        color: #ffffff !important;
    }

    .stChatMessage {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 10px;
    }

    .program-badge {
        background: #D4FF48;
        color: #000000;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 20px;
    }

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

    .feedback-box {
        background: rgba(212, 255, 72, 0.1);
        border-left: 4px solid #D4FF48;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        color: #D4FF48;
        font-weight: bold;
        font-size: 0.95rem;
        animation: fadeIn 0.5s ease-in;
    }

    .competency-report {
        background: rgba(212, 255, 72, 0.08);
        border: 1px solid rgba(212, 255, 72, 0.3);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }

    .competency-item {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid rgba(212, 255, 72, 0.1);
    }

    .competency-bar {
        width: 100%;
        height: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        margin: 5px 0;
        overflow: hidden;
    }

    .competency-fill {
        height: 100%;
        background: linear-gradient(90deg, #D4FF48, #a8cc24);
        transition: width 0.3s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .sidebar-button {
        width: 100%;
        margin: 5px 0;
        text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ESCENARIOS EXPANDIDOS (6 por programa) ---
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
        },
        {
            "title": "Scheduling Conflict - Group Project",
            "scenario": "Your group needs to meet for a project, but everyone has different schedules. Some prefer morning, others evening. People are getting frustrated. How do you find a solution that works for everyone?"
        },
        {
            "title": "Library Noise Dispute",
            "scenario": "A student next to you at the library is talking loudly on the phone, disrupting your study. You've tried ignoring it, but it's getting worse. How do you address this politely but firmly?"
        },
        {
            "title": "Grade Appeal Discussion",
            "scenario": "You believe your exam was graded unfairly. Your professor seems dismissive initially. How do you present your case respectfully and persuasively?"
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
        },
        {
            "title": "Remote Work Policy Change",
            "scenario": "Your company is mandating return to office 5 days a week, but remote work dramatically improved your productivity. Your team is upset. How do you advocate for a hybrid model?"
        },
        {
            "title": "Unrealistic Project Scope",
            "scenario": "A client has increased the project scope by 40% without adjusting timeline or budget. Your team is overwhelmed. How do you renegotiate without losing the client?"
        },
        {
            "title": "Colleague Credit Dispute",
            "scenario": "A colleague presented your ideas in a meeting and got credit for them. The manager now thinks those ideas were theirs. How do you address this professionally?"
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
        },
        {
            "title": "Religious Holiday Scheduling",
            "scenario": "A Muslim team member requested a day off for Eid, but it conflicts with a critical deadline. Other team members are frustrated about coverage. How do you handle this with cultural sensitivity?"
        },
        {
            "title": "Hierarchical vs. Flat Culture Clash",
            "scenario": "Your Japanese team expects decisions from the top, but your company operates on consensus. This is causing decision paralysis. How do you bridge this organizational culture gap?"
        },
        {
            "title": "Language Barrier in Meetings",
            "scenario": "A non-native English speaker is struggling to keep up in fast-paced meetings and is withdrawing from discussions. Productivity is suffering. How do you create an inclusive environment?"
        }
    ]
}

# --- SISTEMA DE COMPETENCIAS ---
COMPETENCIES = {
    "English Language": {
        "icon": "🇬🇧",
        "description": "Grammar, vocabulary, fluency, and pronunciation",
        "indicators": ["uses correct grammar", "varied vocabulary", "clear pronunciation", "speaks fluently"]
    },
    "Citizenship": {
        "icon": "🏛️",
        "description": "Civic responsibility, ethical reasoning, respect for diversity",
        "indicators": ["respects others", "considers collective good", "ethical thinking", "inclusive approach"]
    },
    "Intercultural": {
        "icon": "🌍",
        "description": "Cultural awareness, empathy, adaptability across cultures",
        "indicators": ["cultural awareness", "shows empathy", "respects differences", "adapts communication"]
    },
    "Negotiation": {
        "icon": "🤝",
        "description": "Finding win-win solutions, active listening, problem-solving",
        "indicators": ["asks questions", "listens actively", "proposes solutions", "seeks common ground"]
    },
    "Soft Skills": {
        "icon": "💼",
        "description": "Communication, emotional intelligence, collaboration, leadership",
        "indicators": ["clear communication", "emotional control", "collaborative tone", "shows leadership"]
    }
}

# --- INICIALIZACIÓN DE ESTADO DE SESIÓN ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "competencies" not in st.session_state:
    st.session_state.competencies = {comp: 0 for comp in COMPETENCIES}
if "level" not in st.session_state:
    st.session_state.level = "Explorer"
if "program_selected" not in st.session_state:
    st.session_state.program_selected = None
if "mission_started" not in st.session_state:
    st.session_state.mission_started = False
if "current_scenario" not in st.session_state:
    st.session_state.current_scenario = None
if "total_score" not in st.session_state:
    st.session_state.total_score = 0
if "response_count" not in st.session_state:
    st.session_state.response_count = 0

# --- FUNCIONES ---
def evaluate_competencies(text):
    """Evalúa el texto del usuario contra las 5 competencias"""
    scores = {comp: 0 for comp in COMPETENCIES}

    # Análisis simple basado en patrones
    text_lower = text.lower()

    # English Language
    if len(text.split()) > 15 and "?" in text:
        scores["English Language"] = 3
    elif len(text.split()) > 10:
        scores["English Language"] = 2
    else:
        scores["English Language"] = 1

    # Citizenship (respeto, ética)
    citizenship_keywords = ["respect", "fair", "everyone", "together", "community", "ethical", "responsibility"]
    if any(kw in text_lower for kw in citizenship_keywords):
        scores["Citizenship"] = 3

    # Intercultural (empatía, sensibilidad)
    intercultural_keywords = ["understand", "perspective", "different", "culture", "appreciate", "empathy"]
    if any(kw in text_lower for kw in intercultural_keywords):
        scores["Intercultural"] = 3

    # Negotiation (preguntas, soluciones)
    negotiation_keywords = ["?" , "solution", "propose", "suggest", "agree", "compromise", "win-win"]
    negotiation_score = sum(1 for kw in negotiation_keywords if kw in text_lower)
    scores["Negotiation"] = min(negotiation_score * 2, 5)

    # Soft Skills (comunicación clara, tono positivo)
    if "I think" in text or "I believe" in text or "I suggest" in text:
        scores["Soft Skills"] = 3
    elif "because" in text_lower or "reason" in text_lower:
        scores["Soft Skills"] = 2

    return scores

def generate_detailed_feedback(competency_scores):
    """Genera retroalimentación detallada por competencia"""
    feedback = {}

    for comp, score in competency_scores.items():
        if score >= 4:
            level = "🟢 Excellent"
            message = f"You demonstrated strong {comp.lower()}!"
            advice = ""
        elif score >= 2:
            level = "🟡 Good"
            message = f"You showed {comp.lower()} skills, but there's room for improvement."
            advice = f"Tip: Focus on {COMPETENCIES[comp]['description'].lower()}"
        else:
            level = "🔴 Developing"
            message = f"Work on your {comp.lower()} skills."
            advice = f"Next time: {COMPETENCIES[comp]['indicators'][0]}"

        feedback[comp] = {
            "level": level,
            "message": message,
            "advice": advice,
            "score": score
        }

    return feedback

def get_motivational_message(level):
    """Mensaje motivador según el nivel del usuario"""
    messages = {
        "Explorer": "🌟 Great start, Explorer! You're beginning your negotiation journey.",
        "Negotiator": "💪 Well done, Negotiator! Your skills are growing.",
        "Strategist": "🎯 Impressive, Strategist! You're thinking strategically.",
        "Global Communicator": "🌍 Excellent, Global Communicator! You're bridging cultures effectively.",
        "Master Negotiator": "🏆 Outstanding, Master Negotiator! You're at the top of your game!"
    }
    return messages.get(level, "Keep up the great work!")

def update_level():
    """Actualiza nivel según competencias"""
    avg_score = sum(st.session_state.competencies.values()) / len(st.session_state.competencies)

    if avg_score >= 4.5:
        st.session_state.level = "Master Negotiator"
    elif avg_score >= 3.8:
        st.session_state.level = "Global Communicator"
    elif avg_score >= 3:
        st.session_state.level = "Strategist"
    elif avg_score >= 2:
        st.session_state.level = "Negotiator"
    else:
        st.session_state.level = "Explorer"

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
    st.session_state.competencies = {comp: 0 for comp in COMPETENCIES}
    st.session_state.total_score = 0
    st.session_state.response_count = 0

# --- SIDEBAR PERMANENTE (DISPONIBLE SIEMPRE) ---
with st.sidebar:
    st.markdown("<h3 style='color:#D4FF48;'>⚙️ NAVIGATION</h3>", unsafe_allow_html=True)
    st.markdown("---")

    if st.session_state.mission_started:
        st.markdown(f"**Current Program:** {st.session_state.program_selected}")
        st.markdown("---")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("🔄 New Scenario", key="side_new_scenario"):
                st.session_state.current_scenario = generate_random_scenario(st.session_state.program_selected)
                st.session_state.messages = []
                st.rerun()

        with col_s2:
            if st.button("← Back to Programs", key="side_back"):
                st.session_state.mission_started = False
                st.session_state.program_selected = None
                st.rerun()

        st.markdown("---")
        st.markdown("**Quick Stats:**")
        col_s3, col_s4 = st.columns(2)
        with col_s3:
            st.metric("Responses", st.session_state.response_count)
        with col_s4:
            st.metric("Level", st.session_state.level)
    else:
        st.info("👈 Select a program to start a mission!")

    st.markdown("---")
    st.markdown("<small style='color:#aaa;'>English Negotiator © 2024</small>", unsafe_allow_html=True)

# --- INTERFAZ SUPERIOR (NAVBAR) ---
col_nav1, col_nav2 = st.columns([8, 2])
with col_nav1:
    st.markdown("<h2 style='color:#D4FF48; margin:0;'>TREASURIE</h2>", unsafe_allow_html=True)
with col_nav2:
    st.button("Login", key="login")

# --- FLUJO CONDICIONAL PRINCIPAL ---

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
                st.info("📚 Each program offers 6 unique scenarios tailored to improve your negotiation skills in different contexts.")

    with col_hero_right:
        st.markdown('<div class="waveform-container">' + 
                    '<div class="bar" style="animation-delay: 0.1s"></div>' +
                    '<div class="bar" style="animation-delay: 0.2s"></div>' +
                    '<div class="bar" style="animation-delay: 0.3s"></div>' +
                    '<div class="bar" style="animation-delay: 0.4s"></div>' +
                    '<div class="bar" style="animation-delay: 0.5s"></div>' +
                    '<div class="bar" style="animation-delay: 0.4s"></div>' +
                    '<div class="bar" style="animation-delay: 0.3s"></div>' +
                    '</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="metric-card">TOTAL SCORE<br><h2 style="color:#D4FF48;">{st.session_state.total_score}</h2></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card">LEVEL<br><h4 style="color:#D4FF48;">{st.session_state.level}</h4></div>', unsafe_allow_html=True)

else:
    # SECCIÓN 2: MISIÓN EN PROGRESO
    col_mission1, col_mission2 = st.columns([2, 3])

    with col_mission1:
        st.markdown(f'<div class="program-badge">🎯 {st.session_state.program_selected}</div>', unsafe_allow_html=True)

    with col_mission2:
        st.markdown(f'<h3 style="color:#D4FF48; margin:0;">{st.session_state.current_scenario["title"]}</h3>', unsafe_allow_html=True)

    st.markdown(f'<div class="scenario-box">{st.session_state.current_scenario["scenario"]}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Dashboard de competencias
    col_dash1, col_dash2, col_dash3 = st.columns(3)
    with col_dash1:
        st.markdown(f'<div class="metric-card">RESPONSES<br><h2 style="color:#D4FF48;">{st.session_state.response_count}</h2></div>', unsafe_allow_html=True)
    with col_dash2:
        st.markdown(f'<div class="metric-card">SCORE<br><h2 style="color:#D4FF48;">{st.session_state.total_score}</h2></div>', unsafe_allow_html=True)
    with col_dash3:
        st.markdown(f'<div class="metric-card">LEVEL<br><h4 style="color:#D4FF48;">{st.session_state.level}</h4></div>', unsafe_allow_html=True)

    st.markdown("---")

    # --- ÁREA DE CHAT (NEGOCIACIÓN SOCRÁTICA) ---
    client = OpenAI(
        api_key=st.secrets.get("GOOGLE_API_KEY", ""),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Negotiate here...", key="chat_input"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.response_count += 1

        with st.chat_message("user"):
            st.markdown(prompt)

        # Evaluar competencias
        comp_scores = evaluate_competencies(prompt)
        for comp, score in comp_scores.items():
            st.session_state.competencies[comp] = max(st.session_state.competencies[comp], score)

        st.session_state.total_score = sum(st.session_state.competencies.values())
        update_level()

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

            try:
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

            except Exception as e:
                st.error(f"⚠️ API Error: Please check your GOOGLE_API_KEY in Streamlit secrets")

        st.markdown("---")

        # RETROALIMENTACIÓN DETALLADA DE COMPETENCIAS
        st.markdown("<h4 style='color:#D4FF48;'>📊 Competency Analysis</h4>", unsafe_allow_html=True)

        feedback_data = generate_detailed_feedback(comp_scores)

        for comp, feedback in feedback_data.items():
            with st.container():
                st.markdown(f"""
                <div class="competency-report">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span>{COMPETENCIES[comp]['icon']} <strong>{comp}</strong></span>
                        <span>{feedback['level']}</span>
                    </div>
                    <div class="competency-bar">
                        <div class="competency-fill" style="width: {(feedback['score'] / 5) * 100}%"></div>
                    </div>
                    <p style="margin: 8px 0; font-size: 0.9rem;">{feedback['message']}</p>
                    {f'<p style="margin: 5px 0; font-size: 0.85rem; color: #aaa;">💡 {feedback["advice"]}</p>' if feedback['advice'] else ''}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # MENSAJE MOTIVADOR
        motivational = get_motivational_message(st.session_state.level)
        st.markdown(f'<div class="feedback-box">{motivational}</div>', unsafe_allow_html=True)

        st.rerun()
