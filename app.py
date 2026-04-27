import streamlit as st
import google.generativeai as genai
import random

st.set_page_config(page_title="Copilot | AI Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #1a1a1a 0%, #050505 100%); color: #ffffff; }
    .stButton>button {
        border-radius: 50px; background-color: #D4FF48 !important; color: #000000 !important;
        font-weight: bold; border: none; padding: 0.6rem 2.5rem;
        transition: all 0.3s ease; box-shadow: 0 0 15px rgba(212, 255, 72, 0.3);
    }
    .stButton>button:hover { box-shadow: 0 0 25px rgba(212, 255, 72, 0.6); transform: scale(1.02); }
    .metric-card {
        background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 15px; padding: 20px; text-align: center; backdrop-filter: blur(10px);
    }
    .waveform-container { display: flex; align-items: center; justify-content: center; gap: 4px; height: 150px; }
    .bar { width: 8px; background: linear-gradient(180deg, #D4FF48 0%, #4a5a1a 100%); border-radius: 4px; animation: pulse 1.2s infinite ease-in-out; }
    @keyframes pulse { 0%, 100% { height: 20px; } 50% { height: 80px; } }
    .program-badge { background: #D4FF48; color: #000000; padding: 8px 16px; border-radius: 20px; font-weight: bold; display: inline-block; margin-bottom: 20px; }
    .scenario-box { background: rgba(212,255,72,0.05); border: 2px solid rgba(212,255,72,0.3); border-radius: 10px; padding: 20px; margin-bottom: 20px; color: #ffffff; font-size: 1.1rem; line-height: 1.6; }
    .feedback-box { background: rgba(212,255,72,0.1); border-left: 4px solid #D4FF48; border-radius: 8px; padding: 15px; margin: 15px 0; color: #D4FF48; font-weight: bold; font-size: 0.95rem; }
    .competency-report { background: rgba(212,255,72,0.08); border: 1px solid rgba(212,255,72,0.3); border-radius: 10px; padding: 15px; margin: 10px 0; }
    .competency-bar { width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; margin: 5px 0; overflow: hidden; }
    .competency-fill { height: 100%; background: linear-gradient(90deg, #D4FF48, #a8cc24); }
    .improvement-box { background: rgba(255,100,100,0.08); border: 1px solid rgba(255,100,100,0.3); border-radius: 10px; padding: 15px; margin: 10px 0; }
    .strategy-box { background: rgba(100,200,255,0.08); border: 1px solid rgba(100,200,255,0.3); border-radius: 10px; padding: 15px; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

SCENARIOS = {
    "Campus Life (Foundation)": [
        {"title": "Conflict Resolution - Study Group", "scenario": "You're in a study group project. Your partner hasn't contributed anything in 2 weeks, and the presentation is in 3 days. When you bring it up, they get defensive and blame their other courses. How do you negotiate a fair resolution while keeping the relationship intact?"},
        {"title": "Accommodation Disagreement", "scenario": "You share an apartment with 3 roommates. One roommate constantly uses shared kitchen items without replacing them, creating tension. You need to address this without escalating the conflict. What's your approach?"},
        {"title": "Misunderstanding with Classmate", "scenario": "A classmate misunderstood something you said in group chat and thinks you were disrespectful. They've posted about it publicly. How do you handle this communication crisis?"},
        {"title": "Scheduling Conflict - Group Project", "scenario": "Your group needs to meet for a project, but everyone has different schedules. Some prefer morning, others evening. People are getting frustrated. How do you find a solution that works for everyone?"},
        {"title": "Library Noise Dispute", "scenario": "A student next to you at the library is talking loudly on the phone, disrupting your study. You've tried ignoring it, but it's getting worse. How do you address this politely but firmly?"},
        {"title": "Grade Appeal Discussion", "scenario": "You believe your exam was graded unfairly. Your professor seems dismissive initially. How do you present your case respectfully and persuasively?"}
    ],
    "Workplace (Professional)": [
        {"title": "Budget Cut Negotiation", "scenario": "Your department faces a 20% budget reduction. Your manager suggests cutting your professional development budget entirely. You believe this will hurt team morale and productivity. How do you present an alternative proposal?"},
        {"title": "Deadline Conflict", "scenario": "Two senior stakeholders have given you conflicting deadlines. Manager A wants deliverables by Friday, Manager B by next Wednesday. Both claim their deadline is critical. How do you navigate this without damaging relationships?"},
        {"title": "Salary Review Discussion", "scenario": "During your performance review, you were told there's 'no budget' for salary increases this year, despite exceeding all targets. How do you address compensation fairly without threatening your position?"},
        {"title": "Remote Work Policy Change", "scenario": "Your company is mandating return to office 5 days a week, but remote work dramatically improved your productivity. Your team is upset. How do you advocate for a hybrid model?"},
        {"title": "Unrealistic Project Scope", "scenario": "A client has increased the project scope by 40% without adjusting timeline or budget. Your team is overwhelmed. How do you renegotiate without losing the client?"},
        {"title": "Colleague Credit Dispute", "scenario": "A colleague presented your ideas in a meeting and got credit for them. The manager now thinks those ideas were theirs. How do you address this professionally?"}
    ],
    "Intercultural (Global)": [
        {"title": "Cross-Cultural Business Misunderstanding", "scenario": "In a video call with your international team, a German colleague made a blunt critique of your proposal, perceived as rude by US colleagues. Now there's tension. How do you bridge the cultural gap and refocus on the goal?"},
        {"title": "Time Zone Collaboration Issue", "scenario": "Your Asian team feels excluded because all meetings are scheduled during US hours. They're considering not participating, which affects project quality. How do you propose a fair solution for a global team?"},
        {"title": "Communication Style Conflict", "scenario": "Your Indian team prefers indirect, context-rich communication, while your UK team wants direct, concise messages. This is causing friction. How do you align communication without dismissing either culture?"},
        {"title": "Religious Holiday Scheduling", "scenario": "A Muslim team member requested a day off for Eid, but it conflicts with a critical deadline. Other team members are frustrated about coverage. How do you handle this with cultural sensitivity?"},
        {"title": "Hierarchical vs. Flat Culture Clash", "scenario": "Your Japanese team expects decisions from the top, but your company operates on consensus. This is causing decision paralysis. How do you bridge this organizational culture gap?"},
        {"title": "Language Barrier in Meetings", "scenario": "A non-native English speaker is struggling to keep up in fast-paced meetings and is withdrawing from discussions. Productivity is suffering. How do you create an inclusive environment?"}
    ]
}

COMPETENCIES = {
    "English Language": {
        "icon": "🇬🇧",
        "description": "Grammar, vocabulary, fluency, and clarity of expression",
        "what_to_improve": "Use more varied vocabulary, complex sentence structures, and precise academic language.",
        "strategies": [
            "Read 1 article in English daily and note 5 new words",
            "Practice using connectors: however, therefore, consequently",
            "Record yourself speaking and review for grammar errors"
        ]
    },
    "Citizenship": {
        "icon": "🏛️",
        "description": "Civic responsibility, ethical reasoning, respect for diversity",
        "what_to_improve": "Consider the collective impact of decisions and demonstrate ethical reasoning.",
        "strategies": [
            "Ask yourself: 'How does this affect everyone involved?'",
            "Use inclusive language: 'we', 'our team', 'together'",
            "Reference shared values and common goals in your arguments"
        ]
    },
    "Intercultural": {
        "icon": "🌍",
        "description": "Cultural awareness, empathy, adaptability across cultures",
        "what_to_improve": "Show deeper awareness of cultural differences and adapt your communication style.",
        "strategies": [
            "Acknowledge cultural perspectives explicitly: 'I understand that in your culture...'",
            "Avoid assumptions — ask clarifying questions about preferences",
            "Research communication norms of the cultures involved"
        ]
    },
    "Negotiation": {
        "icon": "🤝",
        "description": "Finding win-win solutions, active listening, problem-solving",
        "what_to_improve": "Focus on proposing concrete solutions and seeking common ground.",
        "strategies": [
            "Use the BATNA framework: identify your best alternative",
            "Ask open-ended questions: 'What would work best for you?'",
            "Summarize the other party's position before responding"
        ]
    },
    "Soft Skills": {
        "icon": "💼",
        "description": "Communication, emotional intelligence, collaboration, leadership",
        "what_to_improve": "Demonstrate emotional control, empathy, and clear assertive communication.",
        "strategies": [
            "Use 'I' statements: 'I feel...', 'I believe...', 'I suggest...'",
            "Pause before responding to show you're listening",
            "Acknowledge emotions: 'I understand this is frustrating...'"
        ]
    }
}

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
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = None
if "last_motivational" not in st.session_state:
    st.session_state.last_motivational = None

def evaluate_competencies(text):
    scores = {comp: 0 for comp in COMPETENCIES}
    text_lower = text.lower()
    words = text.split()

    # English Language
    if len(words) > 20 and "?" in text:
        scores["English Language"] = 4
    elif len(words) > 15:
        scores["English Language"] = 3
    elif len(words) > 8:
        scores["English Language"] = 2
    else:
        scores["English Language"] = 1

    # Citizenship
    citizenship_kw = ["respect", "fair", "everyone", "together", "community", "ethical", "responsibility", "inclusive", "rights"]
    scores["Citizenship"] = min(sum(1 for kw in citizenship_kw if kw in text_lower) * 2, 5)

    # Intercultural
    intercultural_kw = ["understand", "perspective", "different", "culture", "appreciate", "empathy", "background", "diversity", "aware"]
    scores["Intercultural"] = min(sum(1 for kw in intercultural_kw if kw in text_lower) * 2, 5)

    # Negotiation
    negotiation_kw = ["solution", "propose", "suggest", "agree", "compromise", "win-win", "alternative", "option", "resolve", "?"]
    scores["Negotiation"] = min(sum(1 for kw in negotiation_kw if kw in text_lower) * 1, 5)

    # Soft Skills
    soft_kw = ["i think", "i believe", "i suggest", "i feel", "i understand", "because", "reason", "therefore", "however"]
    scores["Soft Skills"] = min(sum(1 for kw in soft_kw if kw in text_lower) * 2, 5)

    return scores

def generate_detailed_feedback(competency_scores):
    feedback = {}
    for comp, score in competency_scores.items():
        comp_data = COMPETENCIES[comp]
        if score >= 4:
            level = "🟢 Excellent"
            message = f"Strong performance in {comp}! You demonstrated clear mastery."
            needs_improvement = False
        elif score >= 2:
            level = "🟡 Developing"
            message = f"You showed some {comp} skills, but there's clear room to grow."
            needs_improvement = True
        else:
            level = "🔴 Needs Work"
            message = f"Your {comp} needs significant attention in this response."
            needs_improvement = True

        feedback[comp] = {
            "level": level,
            "message": message,
            "score": score,
            "needs_improvement": needs_improvement,
            "what_to_improve": comp_data["what_to_improve"] if needs_improvement else None,
            "strategies": comp_data["strategies"] if needs_improvement else []
        }
    return feedback

def get_motivational_message(level):
    messages = {
        "Explorer": "🌟 Great start, Explorer! Every expert was once a beginner. Keep pushing!",
        "Negotiator": "💪 Well done, Negotiator! Your communication skills are growing stronger.",
        "Strategist": "🎯 Impressive, Strategist! You're thinking several steps ahead.",
        "Global Communicator": "🌍 Excellent, Global Communicator! You're bridging cultures effectively.",
        "Master Negotiator": "🏆 Outstanding, Master Negotiator! You're at the pinnacle of your game!"
    }
    return messages.get(level, "Keep up the great work!")

def update_level():
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

def start_mission(program):
    st.session_state.program_selected = program
    st.session_state.mission_started = True
    st.session_state.current_scenario = random.choice(SCENARIOS[program])
    st.session_state.messages = []
    st.session_state.competencies = {comp: 0 for comp in COMPETENCIES}
    st.session_state.total_score = 0
    st.session_state.response_count = 0
    st.session_state.last_feedback = None
    st.session_state.last_motivational = None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h3 style='color:#D4FF48;'>⚙️ NAVIGATION</h3>", unsafe_allow_html=True)
    st.markdown("---")
    if st.session_state.mission_started:
        st.markdown(f"**Program:** {st.session_state.program_selected}")
        st.markdown("---")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("🔄 New Scenario"):
                st.session_state.current_scenario = random.choice(SCENARIOS[st.session_state.program_selected])
                st.session_state.messages = []
                st.session_state.last_feedback = None
                st.rerun()
        with col_s2:
            if st.button("← Programs"):
                st.session_state.mission_started = False
                st.session_state.program_selected = None
                st.rerun()
        st.markdown("---")
        st.metric("Responses", st.session_state.response_count)
        st.metric("Level", st.session_state.level)
    else:
        st.info("👈 Select a program to start!")
    st.markdown("---")
    st.markdown("<small style='color:#aaa;'>Copilot © 2024</small>", unsafe_allow_html=True)

# --- NAVBAR ---
col_nav1, col_nav2 = st.columns([8, 2])
with col_nav1:
    st.markdown("<h2 style='color:#D4FF48; margin:0; font-weight:bold; letter-spacing:2px;'>COPILOT</h2>", unsafe_allow_html=True)
with col_nav2:
    st.button("Login", key="login")

# --- MAIN FLOW ---
if not st.session_state.mission_started:
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown("""
            <h1 style='font-size:3.5rem; line-height:1.1;'>AI-Driven <br><span style='color:#D4FF48;'>Communication Lab</span></h1>
            <p style='font-size:1.2rem; color:#aaa; margin-bottom:2rem;'>
            Empower your professional English through Socratic negotiation.
            Analyze, justify, and resolve intercultural conflicts in real-time.
            </p>
        """, unsafe_allow_html=True)
        program = st.selectbox("CHOOSE YOUR PROGRAM:", list(SCENARIOS.keys()), key="program_select")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("START MISSION"):
                start_mission(program)
                st.rerun()
        with col_btn2:
            if st.button("LEARN MORE"):
                st.info("📚 Each program offers 6 unique scenarios to improve your negotiation skills.")
    with col2:
        st.markdown('<div class="waveform-container">' + ''.join([f'<div class="bar" style="animation-delay:{i*0.1}s"></div>' for i in range(7)]) + '</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="metric-card">TOTAL SCORE<br><h2 style="color:#D4FF48;">{st.session_state.total_score}</h2></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card">LEVEL<br><h4 style="color:#D4FF48;">{st.session_state.level}</h4></div>', unsafe_allow_html=True)

else:
    # MISSION IN PROGRESS
    col_m1, col_m2 = st.columns([2, 3])
    with col_m1:
        st.markdown(f'<div class="program-badge">🎯 {st.session_state.program_selected}</div>', unsafe_allow_html=True)
    with col_m2:
        st.markdown(f'<h3 style="color:#D4FF48;">{st.session_state.current_scenario["title"]}</h3>', unsafe_allow_html=True)

    st.markdown(f'<div class="scenario-box">{st.session_state.current_scenario["scenario"]}</div>', unsafe_allow_html=True)
    st.markdown("---")

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.markdown(f'<div class="metric-card">RESPONSES<br><h2 style="color:#D4FF48;">{st.session_state.response_count}</h2></div>', unsafe_allow_html=True)
    with col_d2:
        st.markdown(f'<div class="metric-card">SCORE<br><h2 style="color:#D4FF48;">{st.session_state.total_score}</h2></div>', unsafe_allow_html=True)
    with col_d3:
        st.markdown(f'<div class="metric-card">LEVEL<br><h4 style="color:#D4FF48;">{st.session_state.level}</h4></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Configure Google AI
    genai.configure(api_key=st.secrets.get("GOOGLE_API_KEY", ""))

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(f'<span style="color:#ffffff;">{msg["content"]}</span>', unsafe_allow_html=True)

    # ── SHOW PERSISTENT FEEDBACK AFTER LAST RESPONSE ──
    if st.session_state.last_feedback:
        st.markdown("---")
        st.markdown("<h4 style='color:#D4FF48;'>📊 Competency Feedback — Your Last Response</h4>", unsafe_allow_html=True)

        for comp, fb in st.session_state.last_feedback.items():
            st.markdown(f"""
            <div class="competency-report">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span>{COMPETENCIES[comp]['icon']} <strong style="color:#D4FF48;">{comp}</strong></span>
                    <span style="font-size:0.9rem;">{fb['level']}</span>
                </div>
                <div class="competency-bar"><div class="competency-fill" style="width:{(fb['score']/5)*100}%"></div></div>
                <p style="margin:8px 0; font-size:0.9rem; color:#fff;">{fb['message']}</p>
            </div>
            """, unsafe_allow_html=True)

            if fb["needs_improvement"]:
                st.markdown(f"""
                <div class="improvement-box">
                    <strong style="color:#ff9999;">🎯 What to improve:</strong>
                    <p style="color:#ffcccc; margin:5px 0;">{fb['what_to_improve']}</p>
                </div>
                <div class="strategy-box">
                    <strong style="color:#99ccff;">💡 Strategies:</strong>
                    <ul style="color:#cce5ff; margin:5px 0;">
                        {''.join([f"<li>{s}</li>" for s in fb['strategies']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f'<div class="feedback-box">{st.session_state.last_motivational}</div>', unsafe_allow_html=True)

    # ── CHAT INPUT ──
    if prompt := st.chat_input("Negotiate here...", key="chat_input"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.response_count += 1

        with st.chat_message("user"):
            st.markdown(f'<span style="color:#ffffff;">{prompt}</span>', unsafe_allow_html=True)

        # Evaluate competencies
        comp_scores = evaluate_competencies(prompt)
        for comp, score in comp_scores.items():
            st.session_state.competencies[comp] = max(st.session_state.competencies[comp], score)
        st.session_state.total_score = sum(st.session_state.competencies.values())
        update_level()

        # Generate AI Socratic response
        system_message = f"""You are a Socratic English Communication Tutor specializing in {st.session_state.program_selected}.
Current Scenario: {st.session_state.current_scenario['title']}
Your role:
1. Ask ONLY 1-2 targeted Socratic questions to deepen the student's thinking
2. NEVER provide direct answers or solutions
3. Challenge their assumptions gently but firmly
4. Keep responses concise (max 3-4 sentences)
5. Reference the scenario context in your questions
Goal: Guide the student to discover better negotiation strategies themselves."""

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            full_prompt = system_message + "\n\nConversation:\n" + "\n".join(
                [f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages]
            )
            response = model.generate_content(full_prompt)
            ai_reply = response.text

            with st.chat_message("assistant"):
                st.markdown(f'<span style="color:#ffffff;">{ai_reply}</span>', unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": ai_reply})

        except Exception as e:
            st.error(f"⚠️ API Error: {e}")
            ai_reply = "Error generating response."

        # Save feedback to session_state so it persists after rerun
        st.session_state.last_feedback = generate_detailed_feedback(comp_scores)
        st.session_state.last_motivational = get_motivational_message(st.session_state.level)

        st.rerun()
