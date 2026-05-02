import os
import json
import random
import re
import math
from typing import Any, Dict, List, Tuple

import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Copilot | AI Lab", layout="wide")

# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top, #101010 0%, #050505 100%);
        color: #ffffff;
    }
    .hero-title {
        font-size: 3rem;
        line-height: 1.02;
        font-weight: 800;
        margin: 0.2rem 0 0.5rem 0;
    }
    .hero-subtitle {
        color: #bdbdbd;
        font-size: 1.05rem;
        line-height: 1.55;
        margin-bottom: 0.8rem;
    }
    .glow-badge {
        display: inline-block;
        background: #D4FF48;
        color: #000000;
        border-radius: 999px;
        padding: 0.45rem 1rem;
        font-weight: 800;
        margin-bottom: 0.9rem;
    }
    .panel {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(212,255,72,0.20);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.02) inset;
    }
    .scenario-box {
        background: rgba(212,255,72,0.04);
        border: 1px solid rgba(212,255,72,0.28);
        border-radius: 16px;
        padding: 18px;
        line-height: 1.6;
        font-size: 1.02rem;
        color: #ffffff;
    }
    .instruction-box {
        background: rgba(212,255,72,0.10);
        border: 1px solid rgba(212,255,72,0.35);
        border-radius: 14px;
        padding: 14px 16px;
        color: #ffffff;
        margin: 10px 0 16px 0;
    }
    .section-title {
        color: #D4FF48;
        font-size: 1.02rem;
        font-weight: 800;
        margin: 18px 0 10px 0;
        border-bottom: 1px solid rgba(212,255,72,0.18);
        padding-bottom: 8px;
    }
    .metric-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        padding: 18px;
        text-align: center;
        backdrop-filter: blur(8px);
        min-height: 118px;
    }
    .feedback-box {
        background: rgba(212,255,72,0.07);
        border-left: 4px solid #D4FF48;
        border-radius: 12px;
        padding: 14px 16px;
        color: #ffffff;
        margin: 10px 0;
    }
    .soft-box {
        background: rgba(100,200,255,0.08);
        border: 1px solid rgba(100,200,255,0.22);
        border-radius: 12px;
        padding: 12px 14px;
        margin: 8px 0;
        color: #ffffff;
    }
    .improvement-box {
        background: rgba(255,120,120,0.08);
        border: 1px solid rgba(255,120,120,0.25);
        border-radius: 12px;
        padding: 12px 14px;
        margin: 8px 0;
        color: #ffffff;
    }
    .scorecard-wrap {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        padding: 14px;
    }
    .scenario-chip {
        display: inline-block;
        background: #D4FF48;
        color: #000000;
        border-radius: 999px;
        padding: 0.55rem 1rem;
        font-weight: 800;
        margin-bottom: 0.8rem;
    }
    .hint-chip {
        display: inline-block;
        background: rgba(212,255,72,0.08);
        border: 1px solid rgba(212,255,72,0.24);
        color: #ffffff;
        border-radius: 999px;
        padding: 0.35rem 0.75rem;
        margin: 0.2rem 0.35rem 0.2rem 0;
        font-size: 0.92rem;
    }
    .small-muted {
        color: #b4b4b4;
        font-size: 0.92rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Scenario bank
# -----------------------------------------------------------------------------
SCENARIOS: Dict[str, List[Dict[str, str]]] = {
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

SCENARIO_SUPPORT = {
    "Campus Life (Foundation)": [
        "Use polite, direct language",
        "Focus on fairness and shared responsibility",
        "Mention respectful tone in group chat or face-to-face"
    ],
    "Workplace (Professional)": [
        "Use a professional or semi-formal register",
        "Offer practical alternatives and objective criteria",
        "Show responsibility and integrity"
    ],
    "Intercultural (Global)": [
        "Avoid stereotypes",
        "Acknowledge different communication styles",
        "Use diplomatic language"
    ]
}

COMPETENCIES = {
    "English Language": {"icon": "🇬🇧", "fallback_improve": "Make your English clearer and more structured.", "fallback_strategies": ["Use connectors like however, because, therefore", "Rewrite one idea with simpler, clearer grammar"]},
    "Citizenship": {"icon": "🏛️", "fallback_improve": "Show more respect, fairness, and attention to the group.", "fallback_strategies": ["Mention how your choice affects others", "Use inclusive language such as we or our team"]},
    "Intercultural": {"icon": "🌍", "fallback_improve": "Show stronger awareness of different perspectives and cultural expectations.", "fallback_strategies": ["Acknowledge another viewpoint before disagreeing", "Use a diplomatic phrase to reduce tension"]},
    "Negotiation": {"icon": "🤝", "fallback_improve": "Move from position to interest and propose a workable compromise.", "fallback_strategies": ["Offer a win-win option", "Ask a clarifying question before deciding"]},
    "Soft Skills": {"icon": "💼", "fallback_improve": "Show more empathy, calm tone, and problem-solving.", "fallback_strategies": ["Use an I-statement", "Name the root cause before proposing a solution"]},
}

LEVELS = [
    (4.5, "Master Negotiator", "Outstanding performance."),
    (3.8, "Global Communicator", "Very strong performance."),
    (3.0, "Strategist", "Solid performance with room to refine."),
    (2.0, "Negotiator", "Developing performance."),
    (0.0, "Explorer", "Beginning stage."),
]

SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "follow_up": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 2,
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
        "next_step": {"type": "string"},
        "metacognition": {
            "type": "object",
            "properties": {
                "thinking_quality": {"type": "string"},
                "decision_logic": {"type": "string"},
                "transfer_skill": {"type": "string"},
            },
            "required": ["thinking_quality", "decision_logic", "transfer_skill"],
            "additionalProperties": False
        },
        "ethical_note": {"type": "string"}
    },
    "required": ["follow_up", "overall_summary", "dimensions", "next_step", "metacognition", "ethical_note"],
    "additionalProperties": False
}

COMPARE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "change_summary": {"type": "string"},
        "what_improved": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 4},
        "what_to_keep": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 3},
        "next_reflection_prompt": {"type": "string"}
    },
    "required": ["change_summary", "what_improved", "what_to_keep", "next_reflection_prompt"],
    "additionalProperties": False
}

# -----------------------------------------------------------------------------
# State helpers
# -----------------------------------------------------------------------------
def init_state() -> None:
    defaults = {
        "messages": [],
        "mission_started": False,
        "selected_program": None,
        "current_scenario": None,
        "stage": "choose_program",  # choose_program -> answering -> feedback -> revision -> revision_feedback
        "original_response": "",
        "revised_response": "",
        "response_count": 0,
        "competencies": {c: 0 for c in COMPETENCIES},
        "level": "Explorer",
        "total_score": 0,
        "pending_feedback": None,
        "pending_summary": None,
        "pending_follow_up": None,
        "pending_next_step": None,
        "pending_ethical_note": None,
        "pending_metacognition": None,
        "pending_rewrite_examples": {},
        "pending_revision_compare": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# -----------------------------------------------------------------------------
# Core helpers
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
    st.session_state.total_score = sum(st.session_state.competencies.values())
    return msg

def parse_json_response(raw: str) -> Dict[str, Any]:
    raw = raw.strip()
    try:
        return json.loads(raw)
    except Exception:
        pass
    match = re.search(r"\{[\s\S]*\}\s*$", raw)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    raise ValueError("Model response is not valid JSON")

def get_client() -> genai.Client:
    api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY", "")).strip()
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY in Streamlit secrets or environment.")
    return genai.Client(api_key=api_key)

def start_mission(program: str) -> None:
    st.session_state.mission_started = True
    st.session_state.selected_program = program
    st.session_state.current_scenario = random.choice(SCENARIOS[program])
    st.session_state.stage = "answering"
    st.session_state.messages = []
    st.session_state.original_response = ""
    st.session_state.revised_response = ""
    st.session_state.response_count = 0
    st.session_state.competencies = {c: 0 for c in COMPETENCIES}
    st.session_state.level = "Explorer"
    st.session_state.total_score = 0
    st.session_state.pending_feedback = None
    st.session_state.pending_summary = None
    st.session_state.pending_follow_up = None
    st.session_state.pending_next_step = None
    st.session_state.pending_ethical_note = None
    st.session_state.pending_metacognition = None
    st.session_state.pending_rewrite_examples = {}
    st.session_state.pending_revision_compare = None

def reset_current_case() -> None:
    st.session_state.current_scenario = random.choice(SCENARIOS[st.session_state.selected_program])
    st.session_state.stage = "answering"
    st.session_state.messages = []
    st.session_state.original_response = ""
    st.session_state.revised_response = ""
    st.session_state.response_count = 0
    st.session_state.competencies = {c: 0 for c in COMPETENCIES}
    st.session_state.level = "Explorer"
    st.session_state.total_score = 0
    st.session_state.pending_feedback = None
    st.session_state.pending_summary = None
    st.session_state.pending_follow_up = None
    st.session_state.pending_next_step = None
    st.session_state.pending_ethical_note = None
    st.session_state.pending_metacognition = None
    st.session_state.pending_rewrite_examples = {}
    st.session_state.pending_revision_compare = None

def build_system_instruction(program: str, scenario_title: str, scenario_text: str) -> str:
    return f"""
You are an EFL Copilot for university students at CEFR B1 level.

Context:
- Program: {program}
- Scenario title: {scenario_title}
- Scenario text: {scenario_text}

Pedagogical role:
- Mediate, do not replace, the teacher.
- Force the learner to answer in English.
- Reward clear message quality over perfect grammar.
- Use observable evidence from the student's text only.
- Never give a generic response.
- Never provide the full solution as the main answer.
- Ask Socratic questions that deepen reasoning.

Evaluation standards:
1. English Language (CEFR B1)
   - Coherence: link short, simple ideas in a logical sequence.
   - Range: enough vocabulary for everyday and personal topics, with some circumlocution.
   - Grammar: reasonable control of familiar structures in predictable situations.
   - Fluency: understandable even with pauses and minor lapses.

2. Citizenship / Global Citizenship
   - Respect others' rights.
   - Consider the group or community impact.
   - Notice bias, unfairness, or ethical consequences.

3. Soft Skills / 21st Century Skills
   - Critical Thinking: identify root cause before responding.
   - Communication: clear purpose and calm tone.
   - Collaboration: willingness to compromise and co-create.
   - Creativity: propose non-obvious solutions.

4. Professional Skills
   - Use the appropriate register.
   - Show responsibility and integrity.
   - Demonstrate leadership when the scenario requires coordination.

5. Negotiation (Harvard Principled Negotiation)
   - Separate people from the problem.
   - Focus on interests, not positions.
   - Generate win-win options.
   - Use objective criteria when justifying decisions.

6. Life & Career Skills
   - Adaptability: propose a Plan B when constraints change.
   - Initiative: show proactive action.
   - Cross-cultural awareness: avoid stereotypes and use diplomatic language.

7. Digital / Media Literacy
   - Keep netiquette in digital conflict.
   - Maintain professional composure in chat or online exchanges.

Feedback rules:
- Quote or closely paraphrase at least one fragment from the student's response in every criterion.
- Distinguish strengths from weaknesses.
- If the response is incomplete, say exactly what is missing.
- If the student mixes Spanish and English, identify it and request a full English response.
- Align feedback strictly to observable evidence.
- Never replace the teacher's role.
- Do not give the full solution as the main answer.
- Reward simple but effective reasoning, even if vocabulary is basic.

Output rules:
- Return only valid JSON.
- Follow the provided schema exactly.
- Include 1-2 Socratic follow-up questions.
- Include one short next_step sentence that helps the learner rewrite.
- Include an ethical_note reminding the student that the AI supports, not substitutes, their own work.
- Keep rewrite examples natural, specific to the student's text, and under 120 words.
""".strip()

def build_user_prompt(student_response: str, history_text: str) -> str:
    return f"""
Evaluate the student's latest response with high specificity.

Student response:
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
""".strip()

def build_revision_prompt(initial_response: str, revised_response: str, previous_summary: str, feedback: Dict[str, Any]) -> str:
    return f"""
Compare the student's initial and revised responses.

Initial response:
\"\"\"{initial_response}\"\"\"

Revised response:
\"\"\"{revised_response}\"\"\"

Previous summary:
{previous_summary}

Selected feedback indicators:
{json.dumps(feedback, ensure_ascii=False)}

Return only JSON using this schema:
{json.dumps(COMPARE_SCHEMA, ensure_ascii=False)}

Rules:
- Focus on what changed.
- Mention what improved concretely.
- Mention what the student should keep doing.
- Use English.
- Be specific and grounded in the actual text.
""".strip()

def call_gemini_evaluate(student_response: str) -> Dict[str, Any]:
    client = get_client()
    history_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=build_user_prompt(student_response, history_text),
        config=types.GenerateContentConfig(
            system_instruction=build_system_instruction(
                st.session_state.selected_program,
                st.session_state.current_scenario["title"],
                st.session_state.current_scenario["scenario"],
            ),
            temperature=0.2,
            response_mime_type="application/json",
            response_json_schema=SCHEMA,
        ),
    )
    return parse_json_response(response.text)

def call_gemini_revision_compare(initial_response: str, revised_response: str) -> Dict[str, Any]:
    client = get_client()
    prompt = build_revision_prompt(
        initial_response,
        revised_response,
        st.session_state.pending_summary or "",
        st.session_state.pending_feedback or {},
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
            response_json_schema=COMPARE_SCHEMA,
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
            "badge": "🟢 Strong" if score >= 4 else ("🟡 Developing" if score >= 2 else "🔴 Needs work"),
            "needs": score < 4,
        }
    return result

# -----------------------------------------------------------------------------
# Visualization helpers
# -----------------------------------------------------------------------------
def render_scorecard_table(feedback: Dict[str, Dict[str, Any]]) -> None:
    rows = []
    for comp, meta in COMPETENCIES.items():
        item = feedback.get(comp, {})
        score = int(item.get("score", 0))
        pct = int(score / 5 * 100)
        rows.append((meta["icon"], comp, score, pct))
    html = """
    <div class="scorecard-wrap">
      <div style="font-weight:800; font-size:1rem; margin-bottom:12px; color:#D4FF48;">Competency Scorecard</div>
      <table style="width:100%; border-collapse:collapse;">
        <thead>
          <tr style="text-align:left; color:#bdbdbd;">
            <th style="padding:8px 6px;">Skill</th>
            <th style="padding:8px 6px;">Score</th>
            <th style="padding:8px 6px;">Progress</th>
          </tr>
        </thead>
        <tbody>
    """
    for icon, comp, score, pct in rows:
        html += f"""
          <tr style="border-top:1px solid rgba(255,255,255,0.08);">
            <td style="padding:10px 6px;">{icon} {comp}</td>
            <td style="padding:10px 6px;">{score}/5</td>
            <td style="padding:10px 6px;">
              <div style="width:100%; height:10px; background:rgba(255,255,255,0.10); border-radius:999px; overflow:hidden;">
                <div style="width:{pct}%; height:10px; background:linear-gradient(90deg, #D4FF48, #a6c93f); border-radius:999px;"></div>
              </div>
            </td>
          </tr>
        """
    html += """
        </tbody>
      </table>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def radar_svg(scores: List[float], labels: List[str], width: int = 460, height: int = 360) -> str:
    cx = width / 2
    cy = height / 2 + 10
    radius = 120
    n = len(scores)
    # polygon points
    pts = []
    for i, s in enumerate(scores):
        angle = -math.pi / 2 + (2 * math.pi * i / n)
        r = radius * (s / 5)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        pts.append((x, y))
    poly_points = " ".join([f"{x:.1f},{y:.1f}" for x, y in pts])

    # axis labels
    label_elems = []
    for i, label in enumerate(labels):
        angle = -math.pi / 2 + (2 * math.pi * i / n)
        x = cx + (radius + 30) * math.cos(angle)
        y = cy + (radius + 30) * math.sin(angle)
        anchor = "middle"
        if -math.pi / 2 < angle < math.pi / 2:
            anchor = "start"
        elif angle > math.pi / 2 or angle < -math.pi / 2:
            anchor = "end"
        label_elems.append(
            f'<text x="{x:.1f}" y="{y:.1f}" fill="#111" font-size="13" text-anchor="{anchor}" font-family="Arial">{label}</text>'
        )

    circles = []
    for level in [1, 2, 3, 4, 5]:
        r = radius * (level / 5)
        circles.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="rgba(0,0,0,0.15)" stroke-width="1" />')

    axes = []
    for i in range(n):
        angle = -math.pi / 2 + (2 * math.pi * i / n)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        axes.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="rgba(0,0,0,0.18)" stroke-width="1" />')

    points = "".join([f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="#111"/>' for x, y in pts])

    svg = f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background:white; border-radius:16px;">
      <text x="{cx:.1f}" y="28" text-anchor="middle" font-size="17" font-family="Arial" fill="#111">Competency Scorecard</text>
      {''.join(circles)}
      {''.join(axes)}
      <polygon points="{poly_points}" fill="rgba(212,255,72,0.28)" stroke="#111" stroke-width="2"/>
      {points}
      {''.join(label_elems)}
    </svg>
    """
    return svg

def render_radar_chart(feedback: Dict[str, Dict[str, Any]]) -> None:
    labels = list(COMPETENCIES.keys())
    scores = [float(feedback.get(label, {}).get("score", 0)) for label in labels]
    svg = radar_svg(scores, labels)
    st.markdown(
        f'<div class="scorecard-wrap">{svg}</div>',
        unsafe_allow_html=True,
    )

def render_case_support(program: str) -> None:
    hints = SCENARIO_SUPPORT.get(program, [])
    if not hints:
        return
    chips = "".join([f'<span class="hint-chip">{h}</span>' for h in hints])
    st.markdown(f"<div>{chips}</div>", unsafe_allow_html=True)

def render_student_prompt() -> None:
    st.markdown(
        """
        <div class="instruction-box">
        <strong>Answer only in English.</strong> Solve the problem, justify your decision, and mention at least one ethical or interpersonal consideration.
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_feedback() -> None:
    fb = st.session_state.pending_feedback
    if not fb:
        return

    st.markdown("<div class='section-title'>Feedback</div>", unsafe_allow_html=True)

    if st.session_state.pending_follow_up:
        st.markdown(
            "<div class='feedback-box'><strong>Socratic follow-up</strong><br>"
            + "<br>".join([f"• {q}" for q in st.session_state.pending_follow_up])
            + "</div>",
            unsafe_allow_html=True,
        )

    if st.session_state.pending_summary:
        st.markdown(
            f"<div class='feedback-box'><strong>Overall summary</strong><br>{st.session_state.pending_summary}</div>",
            unsafe_allow_html=True,
        )

    col_left, col_right = st.columns([1.1, 1])
    with col_left:
        render_scorecard_table(fb)
    with col_right:
        render_radar_chart(fb)

    st.markdown("<div class='section-title'>Criterion-by-criterion analysis</div>", unsafe_allow_html=True)

    for comp, data in fb.items():
        icon = COMPETENCIES[comp]["icon"]
        pct = int((data["score"] / 5) * 100)
        strengths_html = "".join([f"<li>{s}</li>" for s in data.get("strengths", [])])

        st.markdown(
            f"""
            <div class="panel" style="margin: 10px 0;">
                <div style="display:flex; justify-content:space-between; gap:12px; align-items:center;">
                    <div style="font-size:1rem; font-weight:800;">{icon} {comp}</div>
                    <div style="font-size:0.9rem; color:#cfcfcf;">{data['badge']} | Score: {data['score']}/5</div>
                </div>
                <div style="width:100%; height:8px; background:rgba(255,255,255,0.10); border-radius:999px; overflow:hidden; margin-top:10px;">
                    <div style="width:{pct}%; height:8px; background:linear-gradient(90deg, #D4FF48, #8fb52b); border-radius:999px;"></div>
                </div>
                <div style="margin-top:12px;"><strong>Evidence:</strong> {data['evidence']}</div>
                <div style="margin-top:8px;"><strong>Strengths:</strong><ul>{strengths_html}</ul></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="improvement-box">
                <strong>Improve:</strong>
                <div style="margin-top:6px;">{data['improve']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if data.get("rewrite_example"):
            st.markdown(
                f"<div class='feedback-box'><strong>Model reformulation:</strong> {data['rewrite_example']}</div>",
                unsafe_allow_html=True,
            )

        strategies_html = "".join([f"<li>{s}</li>" for s in data.get("strategies", [])])
        st.markdown(
            f"""
            <div class="soft-box">
                <strong>Strategies:</strong>
                <ul style="margin-top:6px;">{strategies_html}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.pending_next_step:
        st.markdown(
            f"<div class='feedback-box'><strong>Next step</strong><br>{st.session_state.pending_next_step}</div>",
            unsafe_allow_html=True,
        )

    if st.session_state.pending_metacognition:
        meta = st.session_state.pending_metacognition
        st.markdown(
            f"""
            <div class='panel'>
                <div style='font-weight:800; color:#D4FF48; margin-bottom:8px;'>Metacognition</div>
                <div><strong>Thinking quality:</strong> {meta.get("thinking_quality","")}</div>
                <div style="margin-top:6px;"><strong>Decision logic:</strong> {meta.get("decision_logic","")}</div>
                <div style="margin-top:6px;"><strong>Transfer skill:</strong> {meta.get("transfer_skill","")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.pending_ethical_note:
        st.markdown(
            f"<div class='feedback-box'><strong>Ethical note:</strong> {st.session_state.pending_ethical_note}</div>",
            unsafe_allow_html=True,
        )

def render_revision_feedback() -> None:
    compare = st.session_state.pending_revision_compare
    if not compare:
        return
    st.markdown("<div class='section-title'>Revision comparison</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='feedback-box'><strong>What changed:</strong><br>{compare.get('change_summary','')}</div>", unsafe_allow_html=True)

    improved_html = "".join([f"<li>{x}</li>" for x in compare.get("what_improved", [])])
    keep_html = "".join([f"<li>{x}</li>" for x in compare.get("what_to_keep", [])])

    st.markdown(
        f"""
        <div class="soft-box">
            <strong>What improved</strong>
            <ul style="margin-top:6px;">{improved_html}</ul>
        </div>
        <div class="soft-box">
            <strong>What to keep</strong>
            <ul style="margin-top:6px;">{keep_html}</ul>
        </div>
        <div class="feedback-box"><strong>Reflection prompt:</strong><br>{compare.get('next_reflection_prompt','What changed? What did you improve? What will you do next time?')}</div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<h3 style='color:#D4FF48;'>Navigation</h3>", unsafe_allow_html=True)
    st.markdown("---")
    if st.session_state.mission_started:
        st.markdown(f"**Program:** {st.session_state.selected_program}")
        st.markdown(f"**Stage:** {st.session_state.stage}")
        st.markdown("---")
        if st.button("New scenario", use_container_width=True):
            reset_current_case()
            st.rerun()
        if st.button("Back to program selection", use_container_width=True):
            st.session_state.mission_started = False
            st.session_state.stage = "choose_program"
            st.session_state.selected_program = None
            st.session_state.current_scenario = None
            st.session_state.messages = []
            st.session_state.pending_feedback = None
            st.session_state.pending_summary = None
            st.session_state.pending_follow_up = None
            st.session_state.pending_next_step = None
            st.session_state.pending_ethical_note = None
            st.session_state.pending_metacognition = None
            st.session_state.pending_revision_compare = None
            st.session_state.original_response = ""
            st.session_state.revised_response = ""
            st.rerun()

        st.markdown("---")
        st.metric("Responses", st.session_state.response_count)
        st.metric("Total score", st.session_state.total_score)
        st.metric("Level", st.session_state.level)

        with st.expander("Criteria", expanded=False):
            for comp, meta in COMPETENCIES.items():
                st.write(f"{meta['icon']} {comp}")
    else:
        st.info("Choose a scenario track to start.")
    st.markdown("---")
    st.caption("Streamlit + Google Gemini API")

# -----------------------------------------------------------------------------
# Home / Program selection
# -----------------------------------------------------------------------------
col_nav1, col_nav2 = st.columns([8, 2])
with col_nav1:
    st.markdown("<h2 style='color:#D4FF48; margin:0;'>COPILOT</h2>", unsafe_allow_html=True)
with col_nav2:
    st.button("Login", key="login_btn")

if not st.session_state.mission_started:
    c1, c2 = st.columns([1.15, 1])

    with c1:
        st.markdown(
            """
            <div class="hero-title">AI-Driven<br><span style="color:#D4FF48;">Communication Lab</span></div>
            <div class="hero-subtitle">
            Choose one scenario track, solve a contextualized case in English, and receive evidence-based feedback on communication, negotiation, citizenship, and soft skills.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div class='section-title'>Choose one scenario track</div>", unsafe_allow_html=True)
        program = st.radio(
            label="Program",
            options=list(SCENARIOS.keys()),
            index=0,
            label_visibility="collapsed",
            horizontal=False,
        )

        st.markdown(
            """
            <div class="instruction-box">
            <strong>Answer only in English.</strong> Solve the problem, justify your decision, and mention at least one ethical or interpersonal consideration.
            </div>
            """,
            unsafe_allow_html=True,
        )

        b1, b2 = st.columns(2)
        with b1:
            if st.button("Start mission", use_container_width=True):
                start_mission(program)
                st.rerun()
        with b2:
            if st.button("Learn more", use_container_width=True):
                st.info("Each track includes contextual cases designed for negotiation, ethics, and intercultural communication.")

    with c2:
        st.markdown(
            """
            <div class="metric-card">
                <h4 style="color:#D4FF48;">Mission focus</h4>
                <p>Real-time English response + individualized feedback + guided rewrite.</p>
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
        st.markdown(
            """
            <div class="metric-card" style="margin-top:12px;">
                <div style="font-weight:700; margin-bottom:6px;">Support cues</div>
                <div class="small-muted">• B1 clarity over perfection</div>
                <div class="small-muted">• Evidence-based scoring</div>
                <div class="small-muted">• Feedback after response</div>
                <div class="small-muted">• Rewrite + reflection</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

else:
    # Mission header
    hc1, hc2 = st.columns([2, 3])
    with hc1:
        st.markdown(f'<div class="scenario-chip">{st.session_state.selected_program}</div>', unsafe_allow_html=True)
    with hc2:
        st.markdown(f"<h3 style='color:#D4FF48; margin-bottom:0.2rem;'>{st.session_state.current_scenario['title']}</h3>", unsafe_allow_html=True)

    st.markdown(f"<div class='scenario-box'>{st.session_state.current_scenario['scenario']}</div>", unsafe_allow_html=True)
    st.markdown("---")
    render_student_prompt()
    render_case_support(st.session_state.selected_program)

    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown(f'<div class="metric-card">Responses<br><h2 style="color:#D4FF48;">{st.session_state.response_count}</h2></div>', unsafe_allow_html=True)
    with d2:
        st.markdown(f'<div class="metric-card">Score<br><h2 style="color:#D4FF48;">{st.session_state.total_score}</h2></div>', unsafe_allow_html=True)
    with d3:
        st.markdown(f'<div class="metric-card">Level<br><h4 style="color:#D4FF48;">{st.session_state.level}</h4></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Conversation history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Feedback after first answer
    if st.session_state.stage == "feedback" and st.session_state.pending_feedback:
        render_feedback()
        st.markdown("---")
        st.markdown(
            """
            <div class="instruction-box">
            <strong>Now rewrite your answer in English.</strong> Keep the useful ideas, improve clarity, and make the response more complete.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Feedback after revision
    if st.session_state.stage == "revision_feedback" and st.session_state.pending_feedback:
        render_feedback()
        st.markdown("---")
        render_revision_feedback()
        st.markdown("---")
        st.markdown(
            """
            <div class="instruction-box">
            <strong>Final step:</strong> answer the reflection prompt in one short paragraph:
            What changed? What did you improve? What will you do next time?
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Input behavior by stage
    if st.session_state.stage == "answering":
        user_prompt = st.chat_input("Write your response in English...", key="chat_input_1")
        if user_prompt:
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            st.session_state.original_response = user_prompt
            st.session_state.response_count += 1

            try:
                with st.spinner("Analyzing response..."):
                    result = call_gemini_evaluate(user_prompt)

                follow_up = result.get("follow_up", [])
                summary = result.get("overall_summary", "")
                next_step = result.get("next_step", "")
                ethical_note = result.get("ethical_note", "")
                metacognition = result.get("metacognition", {})

                assistant_text = "Follow-up questions:\n" + "\n".join([f"- {q}" for q in follow_up]) if follow_up else "Please answer again in English with more detail."
                st.session_state.messages.append({"role": "assistant", "content": assistant_text})

                feedback_built = build_feedback(result)
                for comp, data in feedback_built.items():
                    st.session_state.competencies[comp] = max(st.session_state.competencies[comp], data["score"])

                update_level()
                st.session_state.pending_feedback = feedback_built
                st.session_state.pending_follow_up = follow_up
                st.session_state.pending_summary = summary
                st.session_state.pending_next_step = next_step
                st.session_state.pending_ethical_note = ethical_note
                st.session_state.pending_metacognition = metacognition
                st.session_state.stage = "feedback"

            except Exception as e:
                st.error(f"API error: {e}")

            st.rerun()

    elif st.session_state.stage == "feedback":
        revised = st.chat_input("Rewrite your response in English...", key="chat_input_2")
        if revised:
            st.session_state.messages.append({"role": "user", "content": revised})
            st.session_state.revised_response = revised
            st.session_state.response_count += 1

            try:
                with st.spinner("Comparing original and revised response..."):
                    compare = call_gemini_revision_compare(st.session_state.original_response, revised)

                st.session_state.pending_revision_compare = compare

                # Optional: show a concise final assistant message prompting reflection
                reflection_prompt = compare.get("next_reflection_prompt", "What changed? What did you improve? What will you do next time?")
                st.session_state.messages.append({"role": "assistant", "content": reflection_prompt})

                st.session_state.stage = "revision_feedback"

            except Exception as e:
                st.error(f"Revision comparison error: {e}")

            st.rerun()

    elif st.session_state.stage == "revision_feedback":
        reflection = st.chat_input("Write your reflection in English...", key="chat_input_3")
        if reflection:
            st.session_state.messages.append({"role": "user", "content": reflection})
            st.session_state.response_count += 1
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Reflection received. You improved the response by making your reasoning clearer, more explicit, and more aligned with the scenario."
            })
            st.rerun()

    with st.expander("Instructions", expanded=False):
        st.write("Answer in English only.")
        st.write("Solve the case, justify your decision, and keep a respectful tone.")
        st.write("The AI will give feedback by criterion, with evidence, a rewrite suggestion, and a final reflection step.")
