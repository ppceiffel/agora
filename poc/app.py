import random
import time

import plotly.graph_objects as go
import streamlit as st

from mock_data import ARGUMENTS, PAST_VOTES, QUIZ, REFERENDUM, VOTE_RESULTS

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agora — Le Référendum Intelligent",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Palette automnale ─────────────────────────────────────────────────────────
#   Fond        #080808   Noir
#   Carte       #111111   Gris très foncé
#   Bordure     #222222   Gris foncé
#   Or/Ambre    #c8860a   Accent principal
#   Crème       #ede0c8   Texte principal
#   Sable       #8a6840   Texte secondaire
#   Mousse      #4c7a48   Vert forêt (pour)
#   Brique      #b84030   Rouge brique (contre)
# ─────────────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap');

    /* ── Fond global ── */
    .stApp { background-color: #080808; }
    .main .block-container {
        max-width: 460px;
        padding: 0.8rem 1rem 4rem;
        margin: auto;
    }

    /* ── Header ── */
    .agora-header { text-align: center; padding: 2rem 0 1.4rem; }
    .agora-logo   { font-size: 2rem; opacity: 0.9; }
    .agora-title  {
        font-family: 'Lora', Georgia, serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: #ede0c8;
        letter-spacing: 0.04em;
        margin-top: 0.15rem;
    }
    .agora-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        color: #5a3e28;
        margin-top: 0.3rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    /* ── Typo globale ── */
    body { font-family: 'Inter', sans-serif !important; }
    p    { font-family: 'Inter', sans-serif !important; color: #ede0c8; }
    .stMarkdown p, .stMarkdown li { color: #ede0c8; }

    /* ── Séparateur fin ── */
    hr { border: none; border-top: 1px solid #222222; margin: 1.2rem 0; }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        background: #111111;
        border: 1px solid #222222 !important;
        border-radius: 10px !important;
    }
    [data-testid="stExpander"] summary {
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        color: #8a6840 !important;
    }
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span {
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        color: #8a6840 !important;
    }

    /* ── Cards ── */
    .card {
        background: #111111;
        border: 1px solid #222222;
        border-radius: 14px;
        padding: 1.2rem;
        margin-bottom: 0.9rem;
    }
    .card-warm {
        background: #161616;
        border-color: #2a2020;
    }
    .card-amber {
        border-color: #c8860a44;
        background: #131313;
    }

    /* ── Badges ── */
    .badge {
        display: inline-block;
        font-family: 'Inter', sans-serif;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        margin-right: 0.4rem;
    }
    .badge-week  { background: #c8860a18; color: #c8860a; border: 1px solid #c8860a33; }
    .badge-source { background: #4c7a4818; color: #6aaa60; border: 1px solid #4c7a4833; }

    /* ── Label de section ── */
    .label {
        font-family: 'Inter', sans-serif;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #c8860a;
        margin-bottom: 0.55rem;
    }

    /* ── Step dots ── */
    .step-indicator {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.45rem;
        margin-bottom: 1.6rem;
    }
    .step-dot          { width: 6px; height: 6px; border-radius: 50%; background: #222222; }
    .step-dot-active   { width: 20px; height: 6px; border-radius: 3px; background: #c8860a; box-shadow: 0 0 8px #c8860a66; }
    .step-dot-done     { background: #c8860a88; }

    /* ── Boutons ── */
    .stButton > button {
        width: 100%;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600;
        font-size: 0.875rem;
        letter-spacing: 0.02em;
        border-radius: 10px;
        padding: 0.65rem 1rem;
        border: none;
        transition: opacity 0.15s, transform 0.15s;
    }
    .stButton > button[kind="primary"] {
        background: #c8860a;
        color: #080808;
    }
    .stButton > button[kind="primary"]:hover {
        opacity: 0.88;
        transform: translateY(-1px);
    }
    .stButton > button[kind="secondary"] {
        background: #161616;
        color: #ede0c8;
        border: 1px solid #222222;
    }
    .stButton > button:disabled { opacity: 0.28; }

    /* ── Inputs ── */
    .stTextInput > div > div > input {
        background: #111111 !important;
        border: 1px solid #222222 !important;
        border-radius: 10px !important;
        color: #ede0c8 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.875rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #c8860a66 !important;
        box-shadow: 0 0 0 2px #c8860a1a !important;
    }
    .stTextArea > div > div > textarea {
        background: #111111 !important;
        border: 1px solid #222222 !important;
        border-radius: 10px !important;
        color: #ede0c8 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.875rem !important;
    }
    .stTextArea > div > div > textarea:focus {
        border-color: #c8860a66 !important;
        box-shadow: 0 0 0 2px #c8860a1a !important;
    }

    /* ── Radio ── */
    .stRadio > div { gap: 0.35rem; }
    .stRadio > div > label {
        background: #111111 !important;
        border: 1px solid #222222 !important;
        border-radius: 10px !important;
        padding: 0.55rem 0.9rem !important;
        color: #ede0c8 !important;
        font-size: 0.875rem !important;
        cursor: pointer;
        transition: border-color 0.15s;
    }
    .stRadio > div > label:hover { border-color: #c8860a55 !important; }

    /* ── Checkbox ── */
    .stCheckbox { margin-top: 0.4rem; }
    .stCheckbox > label > div > p {
        font-size: 0.82rem !important;
        color: #8a6840 !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        gap: 0 !important;
        border-bottom: 1px solid #222222 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #5a3e28 !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 0 !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        color: #c8860a !important;
        border-bottom: 2px solid #c8860a !important;
    }



    /* ── Arg card (côte à côte) ── */
    .arg-col-header {
        font-family: 'Inter', sans-serif;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 0.3rem 0;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid;
    }
    .arg-col-header-pour   { color: #6aaa60; border-color: #4c7a4844; }
    .arg-col-header-contre { color: #d46050; border-color: #b8403044; }

    .arg-item {
        padding: 0.65rem 0;
        border-bottom: 1px solid #222222;
    }
    .arg-item:last-child { border-bottom: none; }
    .arg-item-rank {
        font-size: 0.6rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    .arg-item-rank-pour   { color: #4c7a48; }
    .arg-item-rank-contre { color: #9a3028; }
    .arg-item-text {
        font-size: 0.78rem;
        line-height: 1.6;
        color: #c8b898;
        margin-bottom: 0.3rem;
    }
    .arg-item-upvotes {
        font-size: 0.65rem;
        color: #5a3e28;
        font-weight: 500;
    }

    /* ── Progress bar ── */
    .bar-bg   { background: #222222; border-radius: 6px; height: 5px; margin: 0.4rem 0; }
    .bar-fill { border-radius: 6px; height: 5px; }

    /* ── Stat chip ── */
    .stat-chip {
        display: inline-block;
        background: #161616;
        border: 1px solid #222222;
        border-radius: 6px;
        padding: 0.22rem 0.55rem;
        font-size: 0.7rem;
        color: #8a6840;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── State ─────────────────────────────────────────────────────────────────────
DEFAULTS = {
    "screen": "auth",
    "otp_sent": False,
    "quiz_answers": {},
    "quiz_passed": False,
    "vote_grade": None,
    "fairplay_read": False,
    "mock_otp": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Initialise l'historique des votes avec les votes passés simulés
if "vote_history" not in st.session_state:
    st.session_state.vote_history = list(PAST_VOTES)  # shallow copy


# ── Constantes valeurs (cadre Schwartz adapté) ────────────────────────────────
# Partagées entre l'écran résultats et l'écran profil
VALUES_LABELS = ["Liberté", "Égalité", "Fraternité", "Sécurité", "Justice", "Efficacité"]
VALUES_DESCRIPTIONS = {
    "Liberté":    "Droit à l'autonomie individuelle, refus de la contrainte.",
    "Égalité":    "Représentation équitable de tous les citoyens.",
    "Fraternité": "Solidarité civique et responsabilité collective.",
    "Sécurité":   "Stabilité des institutions et de l'ordre démocratique.",
    "Justice":    "Équité des procédures et légitimité des règles.",
    "Efficacité": "Pragmatisme : ce qui marche compte plus que l'idéal.",
}
VALUES_MAP = {
    #                      Lib  Éga  Fra  Séc  Jus  Eff
    "Très favorable":   [  2,   9,   9,   7,   7,   6 ],
    "Favorable":        [  4,   7,   7,   6,   7,   8 ],
    "Neutre":           [  5,   5,   5,   5,   5,   5 ],
    "Défavorable":      [  8,   4,   4,   4,   6,   5 ],
    "Très défavorable": [ 10,   2,   2,   3,   5,   3 ],
}
VALUES_COLORS = {
    "Liberté":    "#c8860a",
    "Égalité":    "#4c8a48",
    "Fraternité": "#6aaa60",
    "Sécurité":   "#8a7a62",
    "Justice":    "#8a9a38",
    "Efficacité": "#c07030",
}
GRADE_COLORS = {
    "Très favorable":   "#4c8a48",
    "Favorable":        "#8a9a38",
    "Neutre":           "#8a7a62",
    "Défavorable":      "#c07030",
    "Très défavorable": "#b84030",
}


def go_to(screen: str):
    st.session_state.screen = screen


def header(subtitle: str = ""):
    st.markdown(
        f"""
        <div class="agora-header">
            <div class="agora-logo">🏛️</div>
            <div class="agora-title">Agora</div>
            {"<div class='agora-subtitle'>" + subtitle + "</div>" if subtitle else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def step_dots(current: int, total: int = 5):
    dots = ""
    for i in range(1, total + 1):
        if i < current:
            cls = "step-dot step-dot-done"
        elif i == current:
            cls = "step-dot step-dot-active"
        else:
            cls = "step-dot"
        dots += f'<div class="{cls}"></div>'
    st.markdown(f'<div class="step-indicator">{dots}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ÉCRAN 1 — Authentification
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.screen == "auth":
    header("Référendum citoyen")

    st.markdown(
        """
        <div class="card card-amber" style="text-align:center; padding:1.4rem;">
            <div style="font-family:'Lora',serif; font-style:italic; font-size:0.95rem;
                        color:#c8b898; line-height:1.7; margin-bottom:1rem;">
                « Une question par semaine.<br>Sourcée. Débattue. Votée. »
            </div>
            <div style="display:flex; justify-content:center; gap:2rem;">
                <div>
                    <div style="font-family:'Lora',serif; font-size:1.4rem;
                                font-weight:700; color:#c8860a;">4 821</div>
                    <div style="font-size:0.65rem; color:#5a3e28; letter-spacing:0.06em;
                                text-transform:uppercase; margin-top:0.1rem;">votes</div>
                </div>
                <div style="width:1px; background:#222222;"></div>
                <div>
                    <div style="font-family:'Lora',serif; font-size:1.4rem;
                                font-weight:700; color:#c8860a;">87%</div>
                    <div style="font-size:0.65rem; color:#5a3e28; letter-spacing:0.06em;
                                text-transform:uppercase; margin-top:0.1rem;">quiz réussi</div>
                </div>
                <div style="width:1px; background:#222222;"></div>
                <div>
                    <div style="font-family:'Lora',serif; font-size:1.4rem;
                                font-weight:700; color:#c8860a;">12</div>
                    <div style="font-size:0.65rem; color:#5a3e28; letter-spacing:0.06em;
                                text-transform:uppercase; margin-top:0.1rem;">questions</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='label' style='margin-top:1rem;'>Connexion sécurisée</div>", unsafe_allow_html=True)

    phone = st.text_input("Téléphone", placeholder="+33 6 12 34 56 78", label_visibility="collapsed")

    if not st.session_state.otp_sent:
        if st.button("Recevoir mon code SMS", type="primary"):
            if phone:
                st.session_state.mock_otp = str(random.randint(100000, 999999))
                st.session_state.otp_sent = True
                st.rerun()
            else:
                st.error("Veuillez entrer votre numéro.")
    else:
        st.success(f"Code envoyé · POC : **{st.session_state.mock_otp}**")
        otp = st.text_input("Code SMS", max_chars=6, placeholder="123456", label_visibility="collapsed")
        if st.button("Valider", type="primary"):
            if otp == st.session_state.mock_otp:
                go_to("referendum")
                st.rerun()
            else:
                st.error("Code incorrect.")

    st.markdown(
        "<div style='text-align:center; color:#3a2410; font-size:0.7rem; margin-top:1.8rem; "
        "letter-spacing:0.04em;'>Aucune publicité · Aucune donnée revendue · Vote anonyme</div>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# ÉCRAN 2 — Question de la semaine
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "referendum":
    header()
    step_dots(1)

    st.markdown(
        f"""
        <div style="margin-bottom:0.75rem;">
            <span class="badge badge-week">{REFERENDUM['week']}</span>
            <span class="badge badge-source">Sourcé</span>
        </div>
        <div style="font-family:'Lora',serif; font-size:1.15rem; font-weight:600;
                    color:#ede0c8; line-height:1.55; margin-bottom:1rem; letter-spacing:0.01em;">
            {REFERENDUM['question']}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="card">
            <p style="font-size:0.875rem; line-height:1.75; color:#9a7a58; margin:0;">
                {REFERENDUM['summary']}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Éclairage historique"):
        st.markdown(REFERENDUM["historical_context"])
    with st.expander("Éclairage scientifique"):
        st.markdown(REFERENDUM["scientific_context"])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#5a3e28; font-size:0.78rem; text-align:center; margin-bottom:0.9rem;'>"
        "Pour voter, réussis d'abord le quiz de compréhension (2/3 minimum)."
        "</div>",
        unsafe_allow_html=True,
    )
    if st.button("Passer le quiz →", type="primary"):
        go_to("quiz")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ÉCRAN 3 — Quiz
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "quiz":
    header("Quiz de validation")
    step_dots(2)

    st.markdown(
        "<div style='color:#5a3e28; font-size:0.78rem; text-align:center; margin-bottom:1.2rem;'>"
        "3 questions · 2 bonnes réponses minimum"
        "</div>",
        unsafe_allow_html=True,
    )

    answers = {}
    all_answered = True

    for i, q in enumerate(QUIZ, 1):
        st.markdown(
            f"<div class='label'>Question {i} · {i}/3</div>"
            f"<div style='font-size:0.9rem; font-weight:600; color:#ede0c8; "
            f"line-height:1.55; margin-bottom:0.5rem;'>{q['question']}</div>",
            unsafe_allow_html=True,
        )
        choice = st.radio(
            label=f"q{i}",
            options=["a", "b", "c"],
            format_func=lambda x, opts=q["options"]: opts[x],
            index=None,
            label_visibility="collapsed",
            key=f"quiz_{q['id']}",
        )
        answers[q["id"]] = choice
        if choice is None:
            all_answered = False
        st.markdown("<div style='margin-bottom:0.7rem;'></div>", unsafe_allow_html=True)

    if st.button("Valider le quiz", type="primary", disabled=not all_answered):
        score = sum(1 for q in QUIZ if answers.get(q["id"]) == q["correct"])
        passed = score >= 2
        st.session_state.quiz_answers = answers
        st.session_state.quiz_passed = passed
        if passed:
            st.success(f"Bravo · {score}/3 — Quiz réussi")
            time.sleep(1.2)
            go_to("arguments")
            st.rerun()
        else:
            st.error(f"{score}/3 — Il faut au moins 2 bonnes réponses.")
            time.sleep(1.5)
            go_to("referendum")
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ÉCRAN 4 — Arguments côte à côte
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "arguments":
    header("Les arguments")
    step_dots(3)

    st.markdown(
        f"""
        <div class="card" style="padding:0.9rem 1rem;">
            <div style="font-family:'Lora',serif; font-style:italic; font-size:0.875rem;
                        color:#9a7a58; line-height:1.55;">
                « {REFERENDUM['question']} »
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='color:#5a3e28; font-size:0.78rem; text-align:center; margin-bottom:1.1rem;'>"
        "Les meilleurs arguments des deux côtés — à lire avant de voter."
        "</div>",
        unsafe_allow_html=True,
    )

    ranks = ["1 —", "2 —", "3 —"]

    col_pour, col_contre = st.columns(2, gap="small")

    with col_pour:
        st.markdown(
            '<div class="arg-col-header arg-col-header-pour">✦ Pour</div>',
            unsafe_allow_html=True,
        )
        for i, arg in enumerate(ARGUMENTS["pour"]):
            st.markdown(
                f"""
                <div class="arg-item">
                    <div class="arg-item-rank arg-item-rank-pour">{ranks[i]}</div>
                    <div class="arg-item-text">{arg['text']}</div>
                    <div class="arg-item-upvotes">▲ {arg['upvotes']:,}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_contre:
        st.markdown(
            '<div class="arg-col-header arg-col-header-contre">✦ Contre</div>',
            unsafe_allow_html=True,
        )
        for i, arg in enumerate(ARGUMENTS["contre"]):
            st.markdown(
                f"""
                <div class="arg-item">
                    <div class="arg-item-rank arg-item-rank-contre">{ranks[i]}</div>
                    <div class="arg-item-text">{arg['text']}</div>
                    <div class="arg-item-upvotes">▲ {arg['upvotes']:,}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    fairplay = st.checkbox("J'ai lu les arguments des deux côtés (+5 pts Fair-Play)")

    st.text_area(
        "Soumettre un argument (optionnel)",
        placeholder="Rédige un argument factuel et sourcé…",
        max_chars=400,
        label_visibility="collapsed",
    )

    st.markdown("<div style='margin-top:0.4rem;'></div>", unsafe_allow_html=True)
    if st.button("Voter →", type="primary"):
        st.session_state.fairplay_read = fairplay
        go_to("vote")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ÉCRAN 5 — Vote
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "vote":
    header("Ton vote")
    step_dots(4)

    st.markdown(
        f"""
        <div class="card card-amber">
            <div class="label">La question</div>
            <div style="font-family:'Lora',serif; font-style:italic; font-size:0.9rem;
                        color:#c8b898; line-height:1.55;">
                « {REFERENDUM['question']} »
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='label' style='margin-top:0.2rem;'>Ton évaluation</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#5a3e28; font-size:0.78rem; margin-bottom:0.7rem;'>"
        "En Jugement Majoritaire, choisis la mention qui traduit le mieux ton opinion."
        "</div>",
        unsafe_allow_html=True,
    )

    GRADE_CONFIG = {
        "Très favorable":    ("●", "#4c8a48"),
        "Favorable":         ("●", "#8a9a38"),
        "Neutre":            ("●", "#8a7a62"),
        "Défavorable":       ("●", "#c07030"),
        "Très défavorable":  ("●", "#b84030"),
    }

    grade = st.radio(
        "Évaluation",
        options=list(GRADE_CONFIG.keys()),
        format_func=lambda x: f"{GRADE_CONFIG[x][0]}  {x}",
        index=None,
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Confirmer mon vote", type="primary", disabled=grade is None):
        st.session_state.vote_grade = grade
        # Ajoute ce vote à l'historique (évite les doublons en démo)
        current_entry = {
            "question": REFERENDUM["question"],
            "week":     REFERENDUM["week"],
            "grade":    grade,
        }
        already = any(v.get("week") == REFERENDUM["week"] for v in st.session_state.vote_history)
        if not already:
            st.session_state.vote_history.append(current_entry)
        go_to("results")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ÉCRAN 6 — Résultats
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "results":
    header("Résultats")
    step_dots(5)

    GRADE_ORDER = ["Très favorable", "Favorable", "Neutre", "Défavorable", "Très défavorable"]
    COLORS = GRADE_COLORS  # alias local

    median       = VOTE_RESULTS["median"]
    total_votes  = VOTE_RESULTS["total"]
    median_color = COLORS[median]
    median_idx   = GRADE_ORDER.index(median)
    user_vote    = st.session_state.vote_grade or ""
    user_color   = COLORS.get(user_vote, "#c8860a")

    # ── Score citoyen (commun aux deux onglets) ───────────────────────────────
    quiz_bonus     = 10 if st.session_state.quiz_passed else 0
    vote_bonus     = 10
    fairplay_bonus = 5 if st.session_state.fairplay_read else 0
    total_score    = 60 + quiz_bonus + vote_bonus + fairplay_bonus

    st.markdown(
        f"""
        <div class="card card-amber" style="padding:1rem 1.2rem; margin-bottom:1rem;">
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <div>
                    <div class="label" style="margin-bottom:0.3rem;">Score Citoyen Éclairé</div>
                    <div style="display:flex; align-items:baseline; gap:0.3rem;">
                        <span style="font-family:'Lora',serif; font-size:1.9rem; font-weight:700;
                                     color:#c8860a;">{total_score}</span>
                        <span style="font-size:0.75rem; color:#5a3e28;">/ 100 pts</span>
                    </div>
                </div>
                <div style="display:flex; flex-direction:column; gap:0.3rem; align-items:flex-end;">
                    <span class="stat-chip" style="color:#6aaa60;">✓ Quiz +{quiz_bonus}</span>
                    <span class="stat-chip" style="color:#c8860a;">✓ Vote +{vote_bonus}</span>
                    <span class="stat-chip" style="color:#d46050;">✓ Fair-Play +{fairplay_bonus}</span>
                </div>
            </div>
            <div class="bar-bg" style="margin-top:0.7rem;">
                <div class="bar-fill" style="width:{min(total_score,100)}%;
                     background:linear-gradient(90deg,#8a5a0a,#c8860a);"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_jm, tab_valeurs = st.tabs(["⚖️ Résultats collectifs", "🧭 Ton profil de valeurs"])

    # ════════════════════════════════════════════════════════════════════════
    with tab_jm:

        st.markdown(
            f"""
            <div class="card" style="text-align:center; padding:1.2rem;">
                <div class="label" style="margin-bottom:0.7rem;">Mention médiane · Jugement Majoritaire</div>
                <div style="font-family:'Lora',serif; font-size:1.45rem; font-weight:700;
                            color:{median_color}; margin-bottom:0.4rem;">{median}</div>
                <div style="font-size:0.72rem; color:#5a3e28;">{total_votes:,} votes exprimés</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div class='label' style='margin-top:0.2rem;'>Distribution &amp; médiane</div>", unsafe_allow_html=True)

        segments_html = ""
        for grade_label in GRADE_ORDER:
            pct    = VOTE_RESULTS[grade_label]
            color  = COLORS[grade_label]
            is_med = grade_label == median
            outline = "box-shadow:inset 0 0 0 2px rgba(237,224,200,0.3);" if is_med else ""
            inner = (
                f'<span style="font-size:0.62rem; font-weight:700; color:#ede0c8cc;">{pct}%</span>'
                if pct >= 9 else ""
            )
            segments_html += (
                f'<div style="width:{pct}%; background:{color}; {outline} '
                f'display:flex; align-items:center; justify-content:center;">{inner}</div>'
            )

        labels_html = ""
        for grade_label in GRADE_ORDER:
            pct    = VOTE_RESULTS[grade_label]
            is_med = grade_label == median
            color  = COLORS[grade_label] if is_med else "#3a2410"
            weight = "700" if is_med else "400"
            arrow  = "▲ " if is_med else ""
            short  = grade_label.replace("Très ", "T. ")
            labels_html += (
                f'<div style="width:{pct}%; text-align:center; font-size:0.58rem; '
                f'color:{color}; font-weight:{weight}; line-height:1.4; padding-top:0.25rem;">'
                f'{arrow}{short}</div>'
            )

        marker = (
            '<div style="position:absolute; top:0; bottom:0; left:50%; width:1.5px; '
            'background:rgba(237,224,200,0.7); z-index:10;">'
            '<div style="position:absolute; top:-20px; left:50%; transform:translateX(-50%); '
            'background:#ede0c8; color:#080808; font-size:0.6rem; font-weight:800; '
            'border-radius:3px; padding:1px 4px; white-space:nowrap; letter-spacing:0.04em;">50 %</div>'
            '</div>'
        )

        st.markdown(
            f"""
            <div style="position:relative; margin-top:1.6rem; margin-bottom:0.2rem;">
                <div style="display:flex; height:40px; border-radius:8px; overflow:hidden;">
                    {segments_html}
                </div>
                {marker}
            </div>
            <div style="display:flex;">{labels_html}</div>
            """,
            unsafe_allow_html=True,
        )

        cumul_parts = []
        running = 0
        for grade_label in GRADE_ORDER[: median_idx + 1]:
            pct = VOTE_RESULTS[grade_label]
            running += pct
            cumul_parts.append(
                f'<span style="color:{COLORS[grade_label]}; font-weight:600;">{pct}%</span>'
            )

        st.markdown(
            f"""
            <div class="card card-warm" style="margin-top:0.8rem; padding:0.9rem 1rem;">
                <div class="label" style="margin-bottom:0.4rem;">Pourquoi « {median} » ?</div>
                <div style="font-size:0.82rem; color:#8a6840; line-height:1.7;">
                    La médiane est le premier grade où les votes cumulés franchissent
                    <strong style="color:#ede0c8;">50 %</strong>.
                </div>
                <div style="margin-top:0.6rem; font-size:0.82rem; line-height:1.8;">
                    {" + ".join(cumul_parts)} = <strong style="color:{median_color};">{running}%</strong>
                    &nbsp;≥ 50 % &nbsp;→&nbsp;
                    <strong style="color:{median_color};">Médiane : {median}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ════════════════════════════════════════════════════════════════════════
    with tab_valeurs:

        if not user_vote:
            st.markdown(
                "<div style='color:#5a3e28; font-size:0.85rem; margin-top:1rem;'>"
                "Vote d'abord pour voir ton profil de valeurs.</div>",
                unsafe_allow_html=True,
            )
        else:
            scores = VALUES_MAP[user_vote]

            st.markdown(
                f"""
                <div style="font-size:0.82rem; color:#8a6840; line-height:1.7; margin-bottom:1rem;">
                    Ton vote <strong style="color:{user_color};">« {user_vote} »</strong>
                    sur cette question révèle une hiérarchie de valeurs esquissée ci-dessous —
                    d'après le cadre de Schwartz (1992) adapté au contexte civique français.
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ── Radar Plotly ──────────────────────────────────────────────
            theta = VALUES_LABELS + [VALUES_LABELS[0]]
            r     = scores + [scores[0]]

            fig = go.Figure()

            # Zone de fond grisée (référence neutre = 5)
            fig.add_trace(go.Scatterpolar(
                r=[5] * (len(VALUES_LABELS) + 1),
                theta=theta,
                fill="toself",
                fillcolor="rgba(138,122,98,0.06)",
                line=dict(color="rgba(138,122,98,0.25)", width=1, dash="dot"),
                hoverinfo="skip",
                name="Neutre",
            ))

            # Profil utilisateur
            fig.add_trace(go.Scatterpolar(
                r=r,
                theta=theta,
                fill="toself",
                fillcolor="rgba(200,134,10,0.12)",
                line=dict(color="#c8860a", width=2),
                marker=dict(color="#c8860a", size=6),
                hovertemplate="<b>%{theta}</b><br>Score : %{r}/10<extra></extra>",
                name=user_vote,
            ))

            fig.update_layout(
                polar=dict(
                    bgcolor="#111111",
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10],
                        tickvals=[2, 4, 6, 8, 10],
                        tickfont=dict(color="#3a2410", size=8),
                        gridcolor="#222222",
                        linecolor="#222222",
                    ),
                    angularaxis=dict(
                        tickfont=dict(
                            family="Inter, sans-serif",
                            color="#ede0c8",
                            size=11,
                        ),
                        gridcolor="#222222",
                        linecolor="#222222",
                    ),
                ),
                paper_bgcolor="#080808",
                showlegend=False,
                margin=dict(t=16, b=16, l=48, r=48),
                height=320,
            )

            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            # ── Détail des valeurs ────────────────────────────────────────
            st.markdown("<div class='label' style='margin-top:0.2rem;'>Détail</div>", unsafe_allow_html=True)

            sorted_values = sorted(
                zip(VALUES_LABELS, scores), key=lambda x: x[1], reverse=True
            )
            for name, score in sorted_values:
                color = VALUES_COLORS[name]
                bar_pct = score * 10
                st.markdown(
                    f"""
                    <div style="margin-bottom:0.7rem;">
                        <div style="display:flex; justify-content:space-between;
                                    align-items:baseline; margin-bottom:0.25rem;">
                            <span style="font-size:0.82rem; font-weight:600;
                                         color:{color};">{name}</span>
                            <span style="font-size:0.7rem; color:#5a3e28;">{score}/10</span>
                        </div>
                        <div class="bar-bg">
                            <div class="bar-fill" style="width:{bar_pct}%; background:{color};
                                 opacity:0.85;"></div>
                        </div>
                        <div style="font-size:0.72rem; color:#5a3e28; margin-top:0.2rem;
                                    line-height:1.5;">{VALUES_DESCRIPTIONS[name]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                "<div style='color:#3a2410; font-size:0.68rem; margin-top:1rem; line-height:1.6;'>"
                "Esquisse indicative · S. Schwartz, <em>Basic Human Values</em> (1992), "
                "adapté au contexte civique français. Un seul vote ne suffit pas à établir "
                "un profil complet — il se précise au fil des référendums."
                "</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center; color:#3a2410; font-size:0.7rem; margin-bottom:0.8rem; "
        "letter-spacing:0.04em;'>Classement mis à jour chaque lundi · Prochain référendum dans 5 jours</div>",
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2, gap="small")
    with col_a:
        if st.button("Mon profil →", type="secondary"):
            go_to("profil")
            st.rerun()
    with col_b:
        if st.button("Recommencer", type="primary"):
            history = st.session_state.vote_history  # conserve l'historique
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.vote_history = history
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ÉCRAN 7 — Profil de valeurs (agrégé sur tous les votes)
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "profil":
    header("Mon profil de valeurs")

    history = st.session_state.vote_history
    n = len(history)

    st.markdown(
        f"""
        <div style="text-align:center; color:#5a3e28; font-size:0.78rem; margin-bottom:1.4rem;">
            Profil construit sur <strong style="color:#c8860a;">{n} référendum{"s" if n > 1 else ""}</strong>
            · Plus vous votez, plus le profil se précise.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if n == 0:
        st.markdown(
            "<div style='color:#5a3e28; font-size:0.85rem; text-align:center; margin-top:2rem;'>"
            "Aucun vote enregistré. Participez à un référendum pour voir votre profil."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        # ── Calcul des scores moyens ──────────────────────────────────────────
        all_scores = [VALUES_MAP[v["grade"]] for v in history]
        avg_scores = [
            round(sum(s[i] for s in all_scores) / n, 1)
            for i in range(len(VALUES_LABELS))
        ]

        # ── Radar agrégé ─────────────────────────────────────────────────────
        theta = VALUES_LABELS + [VALUES_LABELS[0]]
        r     = avg_scores + [avg_scores[0]]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=[5] * (len(VALUES_LABELS) + 1),
            theta=theta,
            fill="toself",
            fillcolor="rgba(138,122,98,0.06)",
            line=dict(color="rgba(138,122,98,0.25)", width=1, dash="dot"),
            hoverinfo="skip",
            name="Neutre",
        ))

        fig.add_trace(go.Scatterpolar(
            r=r,
            theta=theta,
            fill="toself",
            fillcolor="rgba(200,134,10,0.14)",
            line=dict(color="#c8860a", width=2.5),
            marker=dict(color="#c8860a", size=7),
            hovertemplate="<b>%{theta}</b><br>Score moyen : %{r}/10<extra></extra>",
            name="Profil global",
        ))

        fig.update_layout(
            polar=dict(
                bgcolor="#111111",
                radialaxis=dict(
                    visible=True,
                    range=[0, 10],
                    tickvals=[2, 4, 6, 8, 10],
                    tickfont=dict(color="#3a2410", size=8),
                    gridcolor="#222222",
                    linecolor="#222222",
                ),
                angularaxis=dict(
                    tickfont=dict(family="Inter, sans-serif", color="#ede0c8", size=11),
                    gridcolor="#222222",
                    linecolor="#222222",
                ),
            ),
            paper_bgcolor="#080808",
            showlegend=False,
            margin=dict(t=16, b=16, l=48, r=48),
            height=320,
        )

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # ── Classement des valeurs ────────────────────────────────────────────
        st.markdown("<div class='label' style='margin-top:0.2rem;'>Hiérarchie de vos valeurs</div>", unsafe_allow_html=True)

        sorted_values = sorted(
            zip(VALUES_LABELS, avg_scores), key=lambda x: x[1], reverse=True
        )
        for rank, (name, score) in enumerate(sorted_values, 1):
            color    = VALUES_COLORS[name]
            bar_pct  = score * 10
            medal    = ["🥇", "🥈", "🥉"][rank - 1] if rank <= 3 else f"{rank}."
            st.markdown(
                f"""
                <div style="margin-bottom:0.7rem;">
                    <div style="display:flex; justify-content:space-between;
                                align-items:baseline; margin-bottom:0.25rem;">
                        <span style="font-size:0.82rem; font-weight:600; color:{color};">
                            {medal}&nbsp; {name}
                        </span>
                        <span style="font-size:0.7rem; color:#5a3e28;">{score}/10</span>
                    </div>
                    <div class="bar-bg">
                        <div class="bar-fill" style="width:{bar_pct}%; background:{color}; opacity:0.85;"></div>
                    </div>
                    <div style="font-size:0.72rem; color:#5a3e28; margin-top:0.2rem;
                                line-height:1.5;">{VALUES_DESCRIPTIONS[name]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── Historique des votes ──────────────────────────────────────────────
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='label'>Votes pris en compte</div>", unsafe_allow_html=True)

        for i, entry in enumerate(reversed(history), 1):
            grade = entry["grade"]
            color = GRADE_COLORS.get(grade, "#8a6840")
            st.markdown(
                f"""
                <div style="padding:0.6rem 0; border-bottom:1px solid #1a1a1a;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-size:0.75rem; color:#8a6840; margin-bottom:0.15rem;">
                            {entry.get('week', '')}
                        </div>
                        <div style="font-size:0.72rem; font-weight:600; color:{color};">
                            {grade}
                        </div>
                    </div>
                    <div style="font-size:0.82rem; color:#c8b898; font-style:italic; line-height:1.5;">
                        « {entry['question']} »
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div style='color:#3a2410; font-size:0.68rem; margin-top:1.2rem; line-height:1.6;'>"
            "Esquisse indicative · S. Schwartz, <em>Basic Human Values</em> (1992), "
            "adapté au contexte civique français."
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Retour aux résultats", type="secondary"):
        go_to("results")
        st.rerun()
