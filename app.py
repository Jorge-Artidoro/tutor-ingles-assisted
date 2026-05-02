import os
import json
import random
import re
from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Copilot | AI Lab", layout="wide")

# -----------------------------------------------------------------------------
# Visual design
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle, #111111 0%, #050505 100%);
        color: #ffffff;
    }
    .stButton > button {
        border-radius: 999px;
        background-color: #D4FF48 !important;
        color: #000000 !important;
        font-weight: 700;
        border: 0;
        padding: 0.6rem 1.4rem;
        box-shadow: 0 0 12px rgba(212, 255, 72, 0.18);
        transition: all .2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 0 18px rgba(212, 255, 72, 0.28);
    }
    .metric-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 16px;
        padding: 18px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .program-badge {
        background: #D4FF48;
        color: #000000;
        padding: 8px 16px;
        border-radius: 999px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 12px;
    }
    .scenario-box {
        background: rgba(212,255,72,0.05);
        border: 1px solid rgba(212,255,72,0.28);
        border-radius: 14px;
        padding: 18px;
        color: #ffffff;
        font-size: 1.02rem;
        line-height: 1.6;
    }
    .section-title {
        color: #D4FF48;
        font-size: 1.02rem;
        font-weight: 700;
        margin: 18px 0 10px 0;
        border-bottom: 1px solid rgba(212,255,72,0.25);
        padding-bottom: 8px;
    }
    .feedback-box {
        background: rgba(212,255,72,0.08);
        border-left: 4px solid #D4FF48;
        border-radius: 10px;
        padding: 14px;
        color: #ffffff;
        margin: 12px 0;
    }
    .competency-report {
        background: rgba(212,255,72,0.06);
        border: 1px solid rgba(212,255,72,0.20);
        border-radius: 12px;
        padding: 14px;
        margin: 10px 0;
    }
    .competency-bar {
        width: 100%;
        height: 8px;
        background: rgba(255,255,255,0.10);
        border-radius: 999px;
        overflow: hidden;
        margin-top: 6px;
    }
    .competency-fill {
        height: 100%;
        background: linear-gradient(90deg, #D4FF48, #a8cc24);
        border-radius: 999px;
    }
    .improvement-box {
        background: rgba(255,100,100,0.08);
        border: 1px solid rgba(255,100,100,0.25);
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
    }
    .strategy-box {
        background: rgba(100,200,255,0.08);
        border: 1px solid rgba(100,200,255,0.25);
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
    }
    .scorecard-box {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 16px;
        padding: 16px;
        margin: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Scenario bank: preserved structure and wording from the original file
# -----------------------------------------------------------------------------
SCENARIOS: Dict[str, List[Dict[str, str]]] = {
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
        "fallback_improve": "Use more varied vocabulary and more precise sentence structures.",
        "fallback_strategies": ["Use connectors: however, therefore, consequently", "Rewrite one sentence with stronger grammar and clearer wording"]
    },
    "Citizenship": {
        "icon": "🏛️",
        "fallback_improve": "Consider fairness, respect, and the collective impact of your decision.",
        "fallback_strategies": ["Use inclusive language such as 'we' and 'our team'", "Mention ethical consequences before deciding"]
    },
    "Intercultural": {
        "icon": "🌍",
        "fallback_improve": "Show a more explicit awareness of cultural differences and perspectives.",
        "fallback_strategies": ["Acknowledge alternative cultural expectations", "Use a clarifying question before judging the situation"]
    },
    "Negotiation": {
        "icon": "🤝",
        "fallback_improve": "Propose a concrete solution and seek common ground.",
        "fallback_strategies": ["Offer at least two options", "Ask what would be acceptable for all parties"]
    },
    "Soft Skills": {
        "icon": "💼",
        "fallback_improve": "Demonstrate empathy, assertiveness, and calm tone.",
        "fallback_strategies": ["Use 'I' statements", "Acknowledge the other person's viewpoint before disagreeing"]
    }
}

LEVELS = [
    (4.5, "Master Negotiator", "Outstanding performance."),
    (3.8, "Global Communicator", "Very strong performance."),
    (3.0, "Strategist", "Solid performance with room to refine."),
    (2.0, "Negotiator", "Developing performance."),
    (0.0, "Explorer", "Beginning stage.")
]

SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "follow_up_questions": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 2,
            "description": "One or two Socratic follow-up questions in English."
        },
        "overall_summary": {"type": "string"},
        "dimensions": {
            "type": "object",
            "properties": {
                "English Language": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer", "minimum": 1, "maximum": 5},
                        "evidence": {"type": "string"},
                        "strengths": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 2},
                        "improve": {"type": "string"},
                        "rewrite_example": {"type": "string"},
                        "strategies": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 3}
                    },
                    "required": ["score", "evidence", "strengths", "improve", "rewrite_example", "strategies"],
                    "additionalProperties": False
                },
                "Citizenship": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer", "minimum": 1, "maximum": 5},
                        "evidence": {"type": "string"},
                        "strengths": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 2},
                        "improve": {"type": "string"},
                        "rewrite_example": {"type": "string"},
                        "strategies": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 3}
                    },
                    "required": ["score", "evidence", "strengths", "improve", "rewrite_example", "strategies"],
                    "additionalProperties": False
                },
                "Intercultural": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer", "minimum": 1, "maximum": 5},
                        "evidence": {"type": "string"},
                        "strengths": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 2},
                        "improve": {"type": "string"},
                        "rewrite_example": {"type": "string"},
                        "strategies": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 3}
                    },
                    "required": ["score", "evidence", "strengths", "improve", "rewrite_example", "strategies"],
                    "additionalProperties": False
                },
                "Negotiation": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer", "minimum": 1, "maximum": 5},
                        "evidence": {"type": "string"},
                        "strengths": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 2},
                        "improve": {"type": "string"},
                        "rewrite_example": {"type": "string"},
                        "strategies": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 3}
                    },
                    "required": ["score", "evidence", "strengths", "improve", "rewrite_example", "strategies"],
                    "additionalProperties": False
                },
                "Soft Skills": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer", "minimum": 1, "maximum": 5},
                        "evidence": {"type": "string"},
                        "strengths": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 2},
                        "improve": {"type": "string"},
                        "rewrite_example": {"type": "string"},
                        "strategies": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 3}
                    },
                    "required": ["score", "evidence", "strengths", "improve", "rewrite_example", "strategies"],
                    "additionalProperties": False
                },
            },
            "required": ["English Language", "Citizenship", "Intercultural", "Negotiation", "Soft Skills"],
            "additionalProperties": False
        },
        "metacognition": {
            "type": "object",
            "properties": {
                "thinking_quality": {"type": "string"},
                "decision_logic": {"type": "string"},
                "transfer_skill": {"type": "string"}
            },
            "required": ["thinking_quality", "decision_logic", "transfer_skill"],
            "additionalProperties": False
        },
        "ethical_note": {"type": "string"}
    },
    "required": ["follow_up_questions", "overall_summary", "dimensions", "metacognition", "ethical_note"],
    "additionalProperties": False
}

# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------
def init_state() -> None:
    defaults = {
        "messages": [],
        "competencies": {c: 0 for c in COMPETENCIES},
        "level": "Explorer",
        "program_selected": None,
        "mission_started": False,
        "current_scenario": None,
        "total_score": 0,
        "response_count": 0,
        "pending_feedback": None,
        "pending_followup": None,
        "pending_summary": None,
        "pending_ethical_note": None,
        "pending_metacognition": None,
        "show_feedback": False,
        "score_history": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def get_level_info(avg: float) -> Tuple[str, str]:
    for threshold, name, msg in LEVELS:
        if avg >= threshold:
            return name, msg
    return "Explorer", LEVELS[-1][1]

def update_level() -> str:
    avg = sum(st.session_state.competencies.values()) / len(st.session_state.competencies)
    level_name, msg = get_level_info(avg)
    st.session_state.level = level_name
    return msg

def start_mission(program: str) -> None:
    st.session_state.program_selected = program
    st.session_state.mission_started = True
    st.session_state.current_scenario = random.choice(SCENARIOS[program])
    st.session_state.messages = []
    st.session_state.competencies = {c: 0 for c in COMPETENCIES}
    st.session_state.total_score = 0
    st.session_state.response_count = 0
    st.session_state.pending_feedback = None
    st.session_state.pending_followup = None
    st.session_state.pending_summary = None
    st.session_state.pending_ethical_note = None
    st.session_state.pending_metacognition = None
    st.session_state.show_feedback = False
    st.session_state.score_history = []
    st.session_state.level = "Explorer"

def parse_json_response(raw: str) -> Dict[str, Any]:
    """Try to parse JSON returned by Gemini. Fallback to extracting the last JSON object."""
    raw = raw.strip()
    try:
        return json.loads(raw)
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}\s*$", raw)
    if match:
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except Exception:
            pass
    raise ValueError("Model response is not valid JSON")

def build_system_instruction(program: str, scenario_title: str, scenario_text: str) -> str:
    return f"""
You are an EFL Copilot for university students.

Context:
- Program: {program}
- Scenario title: {scenario_title}
- Scenario text: {scenario_text}

Pedagogical role:
- Mediate, do not replace, the teacher.
- Force the learner to answer in English.
- Prioritize meaning and communicative success over perfect grammar.
- At B1 level, reward clear main points, simple organization, and understandable language.
- Penalize only errors that block communication.
- Promote negotiation of meaning, pragmatic appropriateness, intercultural awareness, citizenship, and functional writing.
- Use the student's actual wording as evidence.
- Never give a generic response.
- Never provide the full solution as the main answer.
- Ask Socratic questions that deepen reasoning.

Evaluation standards:
1. Linguistic (CEFR B1 Threshold)
   - Coherence: links short ideas into a linear sequence.
   - Lexical range: enough vocabulary for daily and personal topics.
   - Grammar: reasonable control of predictable structures.
   - Fluency: understandable even with pauses or simple phrasing.

2. Citizenship / Global Citizenship
   - Respect others' rights and dignity.
   - Consider the community or group impact.
   - Identify bias, unfairness, or prejudice in the conflict.

3. Soft Skills / 21st Century Skills
   - Critical Thinking: root cause analysis, not only symptoms.
   - Communication: clear purpose and calm expression.
   - Collaboration: willingness to compromise and cooperate.
   - Creativity: non-obvious, constructive solutions.

4. Professional Skills
   - Professionalism: appropriate register for boss, colleague, or client.
   - Work ethic: responsibility, integrity, and ownership.
   - Leadership: organize, delegate, and coordinate fairly when relevant.

5. Negotiation (Harvard Principled Negotiation)
   - Separate people from the problem.
   - Focus on interests, not positions.
   - Generate win-win options.
   - Use objective criteria when possible.

6. Life & Career Skills
   - Adaptability: respond well to change or constraints.
   - Initiative: proactive, self-directed action.
   - Cross-cultural awareness: respectful diplomacy across cultures.

7. Digital / Media Literacy
   - Netiquette: respectful and composed behavior in chat or online conflict.

Feedback style:
- Highlight evidence of 21st century skills explicitly.
- Reward strong reasoning even when English is simple.
- If the response mixes Spanish and English, say so explicitly and request a full English reformulation.
- Use B1 standards: message first, polish second.
- Example:
  "Your English is simple, but your compromise shows strong Collaboration and Negotiation."

Output requirements:
- Return strictly one JSON object.
- Must follow the provided schema.
- Every criterion must include evidence taken from the student's response.
- If the response is incomplete, mention exactly what is missing.
- The rewrite_example must be natural English, specific to the student's answer, and shorter than 120 words.
- The ethical_note must remind the student that the AI is support, not a substitute for their own work.
- Ask 1-2 Socratic follow-up questions.
""".strip()

def build_user_prompt(student_response: str, history_text: str) -> str:
    return f"""
Evaluate the student's latest response with the highest possible specificity.

Student latest response:
\"\"\"{student_response}\"\"\"

Conversation history:
{history_text}

Rules for analysis:
1. Quote or closely paraphrase at least one fragment from the student's response in each criterion.
2. Distinguish strengths from weaknesses.
3. Focus on observable evidence only.
4. Score each dimension from 1 to 5.
5. Keep the overall tone constructive and criterial.
6. Produce 1-2 Socratic follow-up questions.
7. If the answer is incomplete, mention exactly what is missing.
8. If the answer is generic, explain why and how to improve it.
9. If the answer is strong, identify what makes it strong.
10. The response must be in English except for labels in the JSON keys.
11. For B1, value clarity and communicative success over perfect accuracy.
""".strip()

def get_client() -> genai.Client:
    api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY", "")).strip()
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY in Streamlit secrets or environment.")
    return genai.Client(api_key=api_key)

def call_gemini(student_response: str) -> Dict[str, Any]:
    client = get_client()

    history_text = "\n".join(
        [f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages]
    )

    system_instruction = build_system_instruction(
        st.session_state.program_selected,
        st.session_state.current_scenario["title"],
        st.session_state.current_scenario["scenario"],
    )
    user_prompt = build_user_prompt(student_response, history_text)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            response_mime_type="application/json",
            response_json_schema=SCHEMA,
        ),
    )
    return parse_json_response(response.text)

def build_feedback(payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    result: Dict[str, Dict[str, Any]] = {}
    dimensions = payload.get("dimensions", {})
    for comp, meta in COMPETENCIES.items():
        entry = dimensions.get(comp, {})
        score = int(entry.get("score", 2))
        score = max(1, min(5, score))
        strategies = entry.get("strategies", meta["fallback_strategies"])
        if isinstance(strategies, str):
            strategies = [strategies]
        result[comp] = {
            "score": score,
            "evidence": entry.get("evidence", ""),
            "strengths": entry.get("strengths", []),
            "improve": entry.get("improve", meta["fallback_improve"]),
            "rewrite_example": entry.get("rewrite_example", ""),
            "strategies": strategies or meta["fallback_strategies"],
            "badge": "🟢 Excellent" if score >= 4 else ("🟡 Developing" if score >= 2 else "🔴 Needs work"),
            "needs": score < 4,
        }
    return result

def build_radar_chart(competencies: Dict[str, int]):
    labels = list(competencies.keys())
    values = list(competencies.values())

    if not labels:
        return None

    values_closed = values + [values[0]]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles_closed = angles + [angles[0]]

    fig = plt.figure(figsize=(7.0, 7.0))
    ax = plt.subplot(111, polar=True)
    ax.plot(angles_closed, values_closed, linewidth=2)
    ax.fill(angles_closed, values_closed, alpha=0.15)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=8)
    ax.set_ylim(0, 5)
    ax.set_title("Competency Scorecard", pad=20)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig

def render_scorecard() -> None:
    st.markdown("<div class='section-title'>Scorecard & Progress</div>", unsafe_allow_html=True)

    cols = st.columns([1.2, 1])
    with cols[0]:
        st.markdown("<div class='scorecard-box'>", unsafe_allow_html=True)
        rows = []
        for comp, score in st.session_state.competencies.items():
            pct = int((score / 5) * 100)
            rows.append(
                {
                    "Skill": comp,
                    "Score": f"{score}/5",
                    "Progress": f"{pct}%",
                }
            )
        st.table(pd.DataFrame(rows))
        st.markdown("</div>", unsafe_allow_html=True)

    with cols[1]:
        fig = build_radar_chart(st.session_state.competencies)
        if fig is not None:
            st.pyplot(fig, clear_figure=True)

    if st.session_state.score_history:
        with st.expander("Progress over responses", expanded=False):
            hist_df = pd.DataFrame(st.session_state.score_history)
            cols_to_show = ["response", "total_score", "level"]
            skill_cols = list(COMPETENCIES.keys())
            existing = [c for c in cols_to_show + skill_cols if c in hist_df.columns]
            st.dataframe(hist_df[existing], use_container_width=True, hide_index=True)

def render_feedback() -> None:
    fb = st.session_state.pending_feedback
    if not fb:
        return

    st.markdown("<div class='section-title'>Feedback on the last response</div>", unsafe_allow_html=True)

    if st.session_state.pending_summary:
        st.markdown(
            f"<div class='feedback-box'><strong>Overall:</strong> {st.session_state.pending_summary}</div>",
            unsafe_allow_html=True,
        )

    for comp, data in fb.items():
        icon = COMPETENCIES[comp]["icon"]
        pct = int((data["score"] / 5) * 100)
        strengths_html = "".join([f"<li>{s}</li>" for s in data.get("strengths", [])])

        st.markdown(
            f"""
            <div class="competency-report">
                <div style="display:flex; justify-content:space-between; gap:12px; align-items:center;">
                    <div style="font-size:1rem;"><strong>{icon} {comp}</strong></div>
                    <div style="font-size:0.85rem; color:#ccc;">{data['badge']} | Score: {data['score']}/5</div>
                </div>
                <div class="competency-bar"><div class="competency-fill" style="width:{pct}%;"></div></div>
                <div style="margin-top:10px; color:#ffffff;"><strong>Evidence:</strong> {data['evidence']}</div>
                <div style="margin-top:8px; color:#ffffff;"><strong>Strengths:</strong><ul>{strengths_html}</ul></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if data["needs"]:
            strategies_html = "".join([f"<li>{s}</li>" for s in data["strategies"]])
            st.markdown(
                f"""
                <div class="improvement-box">
                    <strong>What to improve:</strong>
                    <div style="margin-top:6px;">{data['improve']}</div>
                </div>
                <div class="strategy-box">
                    <strong>Strategies:</strong>
                    <ul style="margin-top:6px;">{strategies_html}</ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if data.get("rewrite_example"):
                st.markdown(
                    f"<div class='feedback-box'><strong>English reformulation:</strong> {data['rewrite_example']}</div>",
                    unsafe_allow_html=True,
                )

    if st.session_state.pending_metacognition:
        meta = st.session_state.pending_metacognition
        st.markdown(
            f"""
            <div class='feedback-box'>
                <strong>Metacognition:</strong><br>
                <strong>Thinking quality:</strong> {meta.get("thinking_quality", "")}<br>
                <strong>Decision logic:</strong> {meta.get("decision_logic", "")}<br>
                <strong>Transfer skill:</strong> {meta.get("transfer_skill", "")}
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.pending_ethical_note:
        st.markdown(
            f"<div class='feedback-box'><strong>Ethical note:</strong> {st.session_state.pending_ethical_note}</div>",
            unsafe_allow_html=True,
        )

def record_progress() -> None:
    snapshot = {
        "response": st.session_state.response_count,
        "total_score": st.session_state.total_score,
        "level": st.session_state.level,
    }
    for comp, score in st.session_state.competencies.items():
        snapshot[comp] = score
    st.session_state.score_history.append(snapshot)

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<h3 style='color:#D4FF48;'>Navigation</h3>", unsafe_allow_html=True)
    st.markdown("---")

    if st.session_state.mission_started:
        st.markdown(f"**Program:** {st.session_state.program_selected}")
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("New Scenario"):
                st.session_state.current_scenario = random.choice(SCENARIOS[st.session_state.program_selected])
                st.session_state.messages = []
                st.session_state.pending_feedback = None
                st.session_state.pending_followup = None
                st.session_state.pending_summary = None
                st.session_state.pending_ethical_note = None
                st.session_state.pending_metacognition = None
                st.session_state.show_feedback = False
                st.rerun()
        with c2:
            if st.button("Programs"):
                st.session_state.mission_started = False
                st.session_state.program_selected = None
                st.rerun()

        st.markdown("---")
        st.metric("Responses", st.session_state.response_count)
        st.metric("Level", st.session_state.level)
        st.metric("Total score", st.session_state.total_score)

        with st.expander("Quality criteria", expanded=False):
            for comp, meta in COMPETENCIES.items():
                st.write(f"{meta['icon']} {comp}")
    else:
        st.info("Select a program to start.")
    st.markdown("---")
    st.caption("Streamlit + Google AI Studio (Gemini API)")

# -----------------------------------------------------------------------------
# Home
# -----------------------------------------------------------------------------
col_nav1, col_nav2 = st.columns([8, 2])
with col_nav1:
    st.markdown("<h2 style='color:#D4FF48; margin:0;'>COPILOT</h2>", unsafe_allow_html=True)
with col_nav2:
    st.button("Login", key="login_btn")

if not st.session_state.mission_started:
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown(
            """
            <h1 style='font-size:3rem; line-height:1.05;'>
            AI-Driven<br><span style='color:#D4FF48;'>Communication Lab</span>
            </h1>
            <p style='font-size:1.1rem; color:#aaa;'>
            Solve contextualized English scenarios, justify decisions, and receive criterial feedback.
            </p>
            """,
            unsafe_allow_html=True,
        )
        program = st.selectbox("Choose your program", list(SCENARIOS.keys()))
        b1, b2 = st.columns(2)
        with b1:
            if st.button("Start mission"):
                start_mission(program)
                st.rerun()
        with b2:
            if st.button("Learn more"):
                st.info("Each program contains six scenarios designed for negotiation, ethics, and intercultural communication.")

    with col2:
        st.markdown(
            """
            <div class="metric-card">
                <h4 style="color:#D4FF48;">Mission focus</h4>
                <p>Real-time English response + personalized feedback + metacognitive refinement.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="metric-card" style="margin-top:12px;">
                <div>Total score</div>
                <h2 style="color:#D4FF48;">{st.session_state.total_score}</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="metric-card" style="margin-top:12px;">
                <div>Level</div>
                <h4 style="color:#D4FF48;">{st.session_state.level}</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------------------------------------------------------
# Mission mode
# -----------------------------------------------------------------------------
else:
    hc1, hc2 = st.columns([2, 3])
    with hc1:
        st.markdown(f'<div class="program-badge">{st.session_state.program_selected}</div>', unsafe_allow_html=True)
    with hc2:
        st.markdown(f"<h3 style='color:#D4FF48;'>{st.session_state.current_scenario['title']}</h3>", unsafe_allow_html=True)

    st.markdown(f'<div class="scenario-box">{st.session_state.current_scenario["scenario"]}</div>', unsafe_allow_html=True)
    st.markdown("---")

    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown(f'<div class="metric-card">Responses<br><h2 style="color:#D4FF48;">{st.session_state.response_count}</h2></div>', unsafe_allow_html=True)
    with d2:
        st.markdown(f'<div class="metric-card">Score<br><h2 style="color:#D4FF48;">{st.session_state.total_score}</h2></div>', unsafe_allow_html=True)
    with d3:
        st.markdown(f'<div class="metric-card">Level<br><h4 style="color:#D4FF48;">{st.session_state.level}</h4></div>', unsafe_allow_html=True)

    st.markdown("---")

    render_scorecard()

    st.markdown("---")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if st.session_state.show_feedback and st.session_state.pending_feedback:
        st.markdown("---")
        render_feedback()
        st.markdown("---")

    with st.expander("Instructions", expanded=False):
        st.write("Answer in English only.")
        st.write("Resolve the case, justify your decision, and keep a respectful tone.")
        st.write("The AI will give feedback by criterion, with evidence and a rewrite suggestion.")
        st.write("At B1, clarity and successful meaning matter more than perfect grammar.")

    if prompt := st.chat_input("Write your response here...", key="chat_input"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.response_count += 1

        try:
            with st.spinner("Analyzing response..."):
                result = call_gemini(prompt)

            socratic = result.get("follow_up_questions", [])
            summary = result.get("overall_summary", "")
            ethical_note = result.get("ethical_note", "")
            metacognition = result.get("metacognition", {})

            st.session_state.messages.append({
                "role": "assistant",
                "content": "\n".join([f"- {q}" for q in socratic]) if socratic else "Please answer again in English with more detail."
            })

            feedback_built = build_feedback(result)
            for comp, data in feedback_built.items():
                st.session_state.competencies[comp] = max(st.session_state.competencies[comp], data["score"])

            st.session_state.total_score = sum(st.session_state.competencies.values())
            st.session_state.pending_feedback = feedback_built
            st.session_state.pending_followup = socratic
            st.session_state.pending_summary = summary
            st.session_state.pending_ethical_note = ethical_note
            st.session_state.pending_metacognition = metacognition
            st.session_state.show_feedback = True
            update_level()
            record_progress()

        except Exception as e:
            st.error(f"API error: {e}")

        st.rerun()
