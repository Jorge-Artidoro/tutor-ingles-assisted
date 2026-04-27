import streamlit as st
import google.generativeai as genai
import random
import json
import re

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
    .competency-fill { height: 100%; background: linear-gradient(90deg, #D4FF48, #a8cc24); border-radius: 4px; }
    .improvement-box { background: rgba(255,100,100,0.08); border: 1px solid rgba(255,100,100,0.3); border-radius: 10px; padding: 15px; margin: 8px 0; }
    .strategy-box { background: rgba(100,200,255,0.08); border: 1px solid rgba(100,200,255,0.3); border-radius: 10px; padding: 15px; margin: 8px 0; }
    .section-title { color: #D4FF48; font-size: 1.1rem; font-weight: bold; margin: 20px 0 10px 0; border-bottom: 1px solid rgba(212,255,72,0.3); padding-bottom: 8px; }
    </style>
""", unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────────────────────

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
    "English Language": {"icon": "🇬🇧", "fallback_improve": "Use more varied vocabulary and complex sentence structures.", "fallback_strategies": ["Use connectors: however, therefore, consequently", "Record yourself and review for grammar errors"]},
    "Citizenship":      {"icon": "🏛️", "fallback_improve": "Consider the collective impact and demonstrate ethical reasoning.", "fallback_strategies": ["Use inclusive language: 'we', 'our team'", "Reference shared values in your arguments"]},
    "Intercultural":    {"icon": "🌍", "fallback_improve": "Show deeper awareness of cultural differences.", "fallback_strategies": ["Acknowledge cultural perspectives explicitly", "Ask clarifying questions about preferences"]},
    "Negotiation":      {"icon": "🤝", "fallback_improve": "Propose concrete solutions and seek common ground.", "fallback_strategies": ["Use BATNA: identify your best alternative", "Ask open-ended questions: 'What would work best for you?'"]},
    "Soft Skills":      {"icon": "💼", "fallback_improve": "Demonstrate empathy and assertive communication.", "fallback_strategies": ["Use 'I' statements: 'I feel...', 'I believe...'", "Acknowledge emotions: 'I understand this is frustrating...'"]}
}

LEVELS = [
    (4.5, "Master Negotiator", "🏆 Outstanding, Master Negotiator! You're at the pinnacle of your game!"),
    (3.8, "Global Communicator", "🌍 Excellent, Global Communicator! You're bridging cultures effectively."),
    (3.0, "Strategist", "🎯 Impressive, Strategist! You're thinking several steps ahead."),
    (2.0, "Negotiator", "💪 Well done, Negotiator! Your communication skills are growing stronger."),
    (0.0, "Explorer", "🌟 Great start, Explorer! Every expert was once a beginner. Keep pushing!")
]

# ── SESSION STATE ─────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "messages": [],
        "competencies": {c: 0 for c in COMPETENCIES},
        "level": "Explorer",
        "program_selected": None,
        "mission_started": False,
        "current_scenario": None,
        "total_score": 0,
        "response_count": 0,
        # KEY: feedback stored here persists across reruns
        "pending_feedback": None,   # dict with full AI feedback
        "pending_motivational": None,
        "show_feedback": False,     # flag: True = render feedback section
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── HELPERS ───────────────────────────────────────────────────────────────────

def get_level_info(avg):
    for threshold, name, msg in LEVELS:
        if avg >= threshold:
            return name, msg
    return "Explorer", LEVELS[-1][2]

def update_level():
    avg = sum(st.session_state.competencies.values()) / len(st.session_state.competencies)
    name, msg = get_level_info(avg)
    st.session_state.level = name
    return msg

def start_mission(program):
    st.session_state.program_selected = program
    st.session_state.mission_started = True
    st.session_state.current_scenario = random.choice(SCENARIOS[program])
    st.session_state.messages = []
    st.session_state.competencies = {c: 0 for c in COMPETENCIES}
    st.session_state.total_score = 0
    st.session_state.response_count = 0
    st.session_state.pending_feedback = None
    st.session_state.pending_motivational = None
    st.session_state.show_feedback = False

def parse_combined_response(raw):
    """Extract Socratic text and JSON feedback from a single Gemini response."""
    socratic = raw.strip()
    feedback_data = None
    match = re.search(r'```json\s*([\s\S]*?)\s*```', raw)
    if match:
        socratic = raw[:match.start()].strip()
        try:
            feedback_data = json.loads(match.group(1))
        except Exception:
            pass
    else:
        brace = re.search(r'(\{[\s\S]*\})\s*$', raw)
        if brace:
            socratic = raw[:brace.start()].strip()
            try:
                feedback_data = json.loads(brace.group(1))
            except Exception:
                pass
    return socratic, feedback_data

def build_feedback(ai_json):
    """Turn AI JSON into structured feedback dict."""
    result = {}
    for comp, meta in COMPETENCIES.items():
        entry = ai_json.get(comp, {}) if ai_json else {}
        score = max(1, min(5, int(entry.get("score", 2))))
        comment = entry.get("comment", "No specific comment available.")
        improve = entry.get("improve", meta["fallback_improve"])
        strategies = entry.get("strategies", meta["fallback_strategies"])
        if isinstance(strategies, str):
            strategies = [strategies]
        if score >= 4:
            badge = "🟢 Excellent"
            needs = False
        elif score >= 2:
            badge = "🟡 Developing"
            needs = True
        else:
            badge = "🔴 Needs Work"
            needs = True
        result[comp] = {
            "score": score, "badge": badge, "comment": comment,
            "needs": needs, "improve": improve, "strategies": strategies
        }
    return result

def render_feedback_section():
    """Render the full competency feedback block — called every cycle when show_feedback=True."""
    fb = st.session_state.pending_feedback
    mot = st.session_state.pending_motivational
    if not fb:
        return

    st.markdown("<div class='section-title'>📊 Feedback on Your Last Response</div>", unsafe_allow_html=True)

    for comp, data in fb.items():
        icon = COMPETENCIES[comp]["icon"]
        pct = int((data["score"] / 5) * 100)
        st.markdown(f"""
        <div class="competency-report">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <span style="font-size:1rem;">{icon} <strong style="color:#D4FF48;">{comp}</strong></span>
                <span style="font-size:0.85rem; color:#ccc;">{data['badge']} &nbsp; Score: {data['score']}/5</span>
            </div>
            <div class="competency-bar"><div class="competency-fill" style="width:{pct}%;"></div></div>
            <p style="margin:8px 0 4px 0; font-size:0.9rem; color:#ffffff;">{data['comment']}</p>
        </div>
        """, unsafe_allow_html=True)

        if data["needs"]:
            strategies_html = "".join([f"<li style='margin:4px 0;'>{s}</li>" for s in data["strategies"]])
            st.markdown(f"""
            <div class="improvement-box">
                <strong style="color:#ff9999;">🎯 What to improve:</strong>
                <p style="color:#ffcccc; margin:6px 0 0 0; font-size:0.9rem;">{data['improve']}</p>
            </div>
            <div class="strategy-box">
                <strong style="color:#99ccff;">💡 Strategies:</strong>
                <ul style="color:#cce5ff; margin:6px 0 0 0; font-size:0.9rem; padding-left:18px;">
                    {strategies_html}
                </ul>
            </div>
            """, unsafe_allow_html=True)

    if mot:
        st.markdown(f'<div class="feedback-box">{mot}</div>', unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("<h3 style='color:#D4FF48;'>⚙️ NAVIGATION</h3>", unsafe_allow_html=True)
    st.markdown("---")
    if st.session_state.mission_started:
        st.markdown(f"**Program:** {st.session_state.program_selected}")
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 New Scenario"):
                st.session_state.current_scenario = random.choice(SCENARIOS[st.session_state.program_selected])
                st.session_state.messages = []
                st.session_state.pending_feedback = None
                st.session_state.show_feedback = False
                st.rerun()
        with c2:
            if st.button("← Programs"):
                st.session_state.mission_started = False
                st.session_state.program_selected = None
                st.rerun()
        st.markdown("---")
        st.metric("Responses", st.session_state.response_count)
        st.metric("Level", st.session_state.level)
        st.metric("Score", st.session_state.total_score)
    else:
        st.info("👈 Select a program to start!")
    st.markdown("---")
    st.markdown("<small style='color:#aaa;'>Copilot © 2024</small>", unsafe_allow_html=True)

# ── NAVBAR ────────────────────────────────────────────────────────────────────

col_nav1, col_nav2 = st.columns([8, 2])
with col_nav1:
    st.markdown("<h2 style='color:#D4FF48; margin:0; font-weight:bold; letter-spacing:2px;'>COPILOT</h2>", unsafe_allow_html=True)
with col_nav2:
    st.button("Login", key="login_btn")

# ── HOME ──────────────────────────────────────────────────────────────────────

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
        b1, b2 = st.columns(2)
        with b1:
            if st.button("START MISSION"):
                start_mission(program)
                st.rerun()
        with b2:
            if st.button("LEARN MORE"):
                st.info("📚 Each program offers 6 unique scenarios to improve your negotiation skills.")
    with col2:
        st.markdown('<div class="waveform-container">' + ''.join([f'<div class="bar" style="animation-delay:{i*0.1}s"></div>' for i in range(7)]) + '</div>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f'<div class="metric-card">TOTAL SCORE<br><h2 style="color:#D4FF48;">{st.session_state.total_score}</h2></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card">LEVEL<br><h4 style="color:#D4FF48;">{st.session_state.level}</h4></div>', unsafe_allow_html=True)

# ── MISSION ───────────────────────────────────────────────────────────────────

else:
    genai.configure(api_key=st.secrets.get("GOOGLE_API_KEY", ""))

    # Header
    hc1, hc2 = st.columns([2, 3])
    with hc1:
        st.markdown(f'<div class="program-badge">🎯 {st.session_state.program_selected}</div>', unsafe_allow_html=True)
    with hc2:
        st.markdown(f'<h3 style="color:#D4FF48;">{st.session_state.current_scenario["title"]}</h3>', unsafe_allow_html=True)

    st.markdown(f'<div class="scenario-box">{st.session_state.current_scenario["scenario"]}</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Stats
    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown(f'<div class="metric-card">RESPONSES<br><h2 style="color:#D4FF48;">{st.session_state.response_count}</h2></div>', unsafe_allow_html=True)
    with d2:
        st.markdown(f'<div class="metric-card">SCORE<br><h2 style="color:#D4FF48;">{st.session_state.total_score}</h2></div>', unsafe_allow_html=True)
    with d3:
        st.markdown(f'<div class="metric-card">LEVEL<br><h4 style="color:#D4FF48;">{st.session_state.level}</h4></div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── CHAT HISTORY ──
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── FEEDBACK BLOCK (renders AFTER chat, persists across reruns) ──
    if st.session_state.show_feedback and st.session_state.pending_feedback:
        st.markdown("---")
        render_feedback_section()
        st.markdown("---")

    # ── CHAT INPUT ──
    if prompt := st.chat_input("Write your response here...", key="chat_input"):

        # 1. Add user message and display it immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.response_count += 1

        # 2. Build single combined prompt for Gemini
        history_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])

        combined_prompt = f"""You are a Socratic English Communication Tutor for the program: {st.session_state.program_selected}.
Scenario title: {st.session_state.current_scenario['title']}
Scenario: {st.session_state.current_scenario['scenario']}

STUDENT'S LATEST RESPONSE:
\"\"\"{prompt}\"\"\"

CONVERSATION HISTORY:
{history_text}

YOUR TASK — respond in exactly TWO parts with no extra text between them:

PART 1 — SOCRATIC FOLLOW-UP:
Write 1-2 Socratic questions (2-3 sentences max) that challenge the student's reasoning based on what they JUST said. Never give direct answers. Be specific to their words.

PART 2 — COMPETENCY EVALUATION:
Immediately after Part 1, output a JSON block evaluating the student's LATEST response.
Reference specific words or phrases they actually used. Be honest and constructive.

```json
{{
  "English Language": {{
    "score": <integer 1-5>,
    "comment": "<specific observation about grammar, vocabulary, sentence structure in their response>",
    "improve": "<one concrete improvement based on what they wrote>",
    "strategies": ["<tip 1>", "<tip 2>"]
  }},
  "Citizenship": {{
    "score": <integer 1-5>,
    "comment": "<specific observation about ethical reasoning or collective thinking>",
    "improve": "<one concrete improvement>",
    "strategies": ["<tip 1>", "<tip 2>"]
  }},
  "Intercultural": {{
    "score": <integer 1-5>,
    "comment": "<specific observation about cultural awareness shown or missing>",
    "improve": "<one concrete improvement>",
    "strategies": ["<tip 1>", "<tip 2>"]
  }},
  "Negotiation": {{
    "score": <integer 1-5>,
    "comment": "<specific observation about negotiation approach, proposals, or listening>",
    "improve": "<one concrete improvement>",
    "strategies": ["<tip 1>", "<tip 2>"]
  }},
  "Soft Skills": {{
    "score": <integer 1-5>,
    "comment": "<specific observation about tone, empathy, assertiveness, or emotional intelligence>",
    "improve": "<one concrete improvement>",
    "strategies": ["<tip 1>", "<tip 2>"]
  }}
}}
```"""

        # 3. Call Gemini (single call)
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(combined_prompt)
            raw = response.text

            # 4. Parse Socratic reply and JSON feedback
            socratic_reply, feedback_json = parse_combined_response(raw)

            # 5. Store AI reply in messages
            st.session_state.messages.append({"role": "assistant", "content": socratic_reply})

            # 6. Build and STORE feedback in session_state
            feedback_built = build_feedback(feedback_json)
            for comp, data in feedback_built.items():
                st.session_state.competencies[comp] = max(st.session_state.competencies[comp], data["score"])

            st.session_state.total_score = sum(st.session_state.competencies.values())
            motivational = update_level()

            # 7. Save to session_state so it survives rerun
            st.session_state.pending_feedback = feedback_built
            st.session_state.pending_motivational = motivational
            st.session_state.show_feedback = True  # ← THIS FLAG makes feedback appear after rerun

        except Exception as e:
            st.error(f"⚠️ API Error: {e}")

        # 8. Rerun — feedback will now render because show_feedback=True
        st.rerun()
