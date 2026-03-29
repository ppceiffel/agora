import random
import time

import streamlit as st

from mock_data import ARGUMENTS, QUIZ, REFERENDUM, VOTE_RESULTS

# ── Configuration de la page ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Agora — Le Référendum Intelligent",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS mobile-first ──────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Fond général */
    .stApp { background-color: #0f1117; }

    /* Conteneur max-width mobile */
    .main .block-container {
        max-width: 420px;
        padding: 1.5rem 1rem;
        margin: auto;
    }

    /* Header */
    .agora-header {
        text-align: center;
        padding: 1.5rem 0 1rem;
    }
    .agora-logo {
        font-size: 2.5rem;
        margin-bottom: 0.2rem;
    }
    .agora-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    .agora-subtitle {
        font-size: 0.85rem;
        color: #8b8fa8;
        margin-top: 0.2rem;
    }

    /* Cards */
    .card {
        background: #1c1f2e;
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border: 1px solid #2a2d3e;
    }
    .card-accent {
        background: linear-gradient(135deg, #1c1f2e 0%, #1a2035 100%);
        border-color: #3b4cca44;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 0.3rem;
    }
    .badge-week {
        background: #3b4cca22;
        color: #7b8fff;
        border: 1px solid #3b4cca44;
    }
    .badge-source {
        background: #00875a22;
        color: #00d084;
        border: 1px solid #00875a44;
    }

    /* Score citoyen */
    .score-bar-bg {
        background: #2a2d3e;
        border-radius: 10px;
        height: 8px;
        margin: 0.5rem 0;
    }
    .score-bar-fill {
        background: linear-gradient(90deg, #3b4cca, #7b8fff);
        border-radius: 10px;
        height: 8px;
    }

    /* Arguments */
    .arg-pour {
        border-left: 3px solid #00d084;
        padding-left: 0.8rem;
        margin-bottom: 0.8rem;
    }
    .arg-contre {
        border-left: 3px solid #ff4d4d;
        padding-left: 0.8rem;
        margin-bottom: 0.8rem;
    }

    /* Boutons personnalisés */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        font-weight: 600;
        padding: 0.6rem 1rem;
        border: none;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b4cca, #6674e5);
        color: white;
    }

    /* Séparateur */
    hr { border-color: #2a2d3e; margin: 1.2rem 0; }

    /* Résultats JM */
    .jm-bar-label {
        font-size: 0.78rem;
        color: #8b8fa8;
        margin-bottom: 0.15rem;
    }
    .jm-median-badge {
        background: #3b4cca;
        color: white;
        border-radius: 8px;
        padding: 0.4rem 0.8rem;
        font-weight: 700;
        font-size: 1rem;
        display: inline-block;
        margin: 0.5rem 0;
    }

    /* Étapes */
    .step-indicator {
        display: flex;
        justify-content: center;
        gap: 0.4rem;
        margin-bottom: 1.2rem;
    }
    .step-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #2a2d3e;
    }
    .step-dot-active { background: #3b4cca; }
    .step-dot-done { background: #00d084; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── State ─────────────────────────────────────────────────────────────────────
if "screen" not in st.session_state:
    st.session_state.screen = "auth"
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_passed" not in st.session_state:
    st.session_state.quiz_passed = False
if "vote_grade" not in st.session_state:
    st.session_state.vote_grade = None
if "fairplay_read" not in st.session_state:
    st.session_state.fairplay_read = False
if "mock_otp" not in st.session_state:
    st.session_state.mock_otp = None


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
    header("Le référendum intelligent")

    st.markdown(
        """
        <div class="card card-accent" style="text-align:center; padding: 1.5rem;">
            <div style="font-size:0.85rem; color:#8b8fa8; margin-bottom:0.8rem;">
                Bienvenue sur Agora — 1 question citoyenne par semaine,<br>
                sourcée, contextualisée, débattue.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Connexion par SMS")
    phone = st.text_input(
        "Numéro de téléphone",
        placeholder="+33 6 12 34 56 78",
        label_visibility="collapsed",
    )

    if not st.session_state.otp_sent:
        if st.button("Recevoir mon code SMS", type="primary"):
            if phone:
                st.session_state.mock_otp = str(random.randint(100000, 999999))
                st.session_state.otp_sent = True
                st.rerun()
            else:
                st.error("Veuillez entrer votre numéro.")
    else:
        st.success(f"Code envoyé ! (POC : **{st.session_state.mock_otp}**)")
        otp_input = st.text_input("Code reçu par SMS", max_chars=6, placeholder="123456", label_visibility="collapsed")

        if st.button("Valider", type="primary"):
            if otp_input == st.session_state.mock_otp:
                go_to("referendum")
                st.rerun()
            else:
                st.error("Code incorrect.")

    st.markdown(
        "<div style='text-align:center; color:#8b8fa8; font-size:0.75rem; margin-top:1rem;'>"
        "Aucune publicité · Aucune donnée revendue · Vote anonyme"
        "</div>",
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
        <div style="margin-bottom:0.6rem;">
            <span class="badge badge-week">📅 {REFERENDUM['week']}</span>
            <span class="badge badge-source">✅ Sourcé</span>
        </div>
        <h2 style="color:#ffffff; font-size:1.25rem; line-height:1.4; margin-bottom:1rem;">
            {REFERENDUM['question']}
        </h2>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="card"><p style="color:#c8cad8; font-size:0.9rem; line-height:1.6;">{REFERENDUM["summary"]}</p></div>',
        unsafe_allow_html=True,
    )

    with st.expander("🏛️ Éclairage historique"):
        st.markdown(REFERENDUM["historical_context"])

    with st.expander("🔬 Éclairage scientifique"):
        st.markdown(REFERENDUM["scientific_context"])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#8b8fa8; font-size:0.82rem; text-align:center; margin-bottom:0.8rem;'>"
        "Pour voter, tu dois d'abord réussir le quiz de compréhension (2/3 minimum)."
        "</div>",
        unsafe_allow_html=True,
    )
    if st.button("Passer le quiz →", type="primary"):
        go_to("quiz")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ÉCRAN 3 — Quiz de validation
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "quiz":
    header("Quiz de validation")
    step_dots(2)

    st.markdown(
        "<div style='color:#8b8fa8; font-size:0.82rem; text-align:center; margin-bottom:1rem;'>"
        "3 questions · 2 bonnes réponses minimum pour débloquer le vote"
        "</div>",
        unsafe_allow_html=True,
    )

    answers = {}
    all_answered = True

    for i, q in enumerate(QUIZ, 1):
        st.markdown(f"**Question {i}** — {q['question']}")
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
        st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Valider le quiz", type="primary", disabled=not all_answered):
        score = sum(1 for q in QUIZ if answers.get(q["id"]) == q["correct"])
        passed = score >= 2
        st.session_state.quiz_answers = answers
        st.session_state.quiz_passed = passed

        if passed:
            st.success(f"Bravo ! {score}/3 — Quiz réussi !")
            time.sleep(1.2)
            go_to("vote")
            st.rerun()
        else:
            st.error(f"{score}/3 — Il faut au moins 2 bonnes réponses. Relis le sujet et réessaie.")
            time.sleep(1.5)
            go_to("referendum")
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ÉCRAN 4 — Vote Jugement Majoritaire
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "vote":
    header("Ton vote")
    step_dots(3)

    st.markdown(
        f"""
        <div class="card card-accent">
            <p style="color:#c8cad8; font-size:0.9rem; font-style:italic; line-height:1.5;">
            "{REFERENDUM['question']}"
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='color:#8b8fa8; font-size:0.82rem; margin-bottom:0.8rem;'>"
        "Évalue cette proposition par Jugement Majoritaire :"
        "</div>",
        unsafe_allow_html=True,
    )

    GRADE_CONFIG = {
        "Très favorable": ("🟢", "#00d084"),
        "Favorable": ("🟡", "#a3e635"),
        "Neutre": ("⚪", "#8b8fa8"),
        "Défavorable": ("🟠", "#f97316"),
        "Très défavorable": ("🔴", "#ff4d4d"),
    }

    grade = st.radio(
        "Mon évaluation",
        options=list(GRADE_CONFIG.keys()),
        format_func=lambda x: f"{GRADE_CONFIG[x][0]}  {x}",
        index=None,
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Voter", type="primary", disabled=grade is None):
        st.session_state.vote_grade = grade
        go_to("arguments")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ÉCRAN 5 — Arène des arguments
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "arguments":
    header("Arène des arguments")
    step_dots(4)

    st.markdown(
        "<div style='color:#8b8fa8; font-size:0.82rem; text-align:center; margin-bottom:1rem;'>"
        "Lis les meilleurs arguments des deux côtés pour gagner ton badge Fair-Play."
        "</div>",
        unsafe_allow_html=True,
    )

    tab_pour, tab_contre = st.tabs(["✅ Pour (Top 3)", "❌ Contre (Top 3)"])

    with tab_pour:
        for arg in ARGUMENTS["pour"]:
            st.markdown(
                f"""
                <div class="arg-pour">
                    <p style="color:#e8eaf6; font-size:0.88rem; line-height:1.6; margin-bottom:0.3rem;">
                        {arg['text']}
                    </p>
                    <span style="color:#8b8fa8; font-size:0.75rem;">
                        👍 {arg['upvotes']:,} · {arg['author']}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tab_contre:
        for arg in ARGUMENTS["contre"]:
            st.markdown(
                f"""
                <div class="arg-contre">
                    <p style="color:#e8eaf6; font-size:0.88rem; line-height:1.6; margin-bottom:0.3rem;">
                        {arg['text']}
                    </p>
                    <span style="color:#8b8fa8; font-size:0.75rem;">
                        👍 {arg['upvotes']:,} · {arg['author']}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    fairplay = st.checkbox("J'ai lu les arguments opposés à ma position (+5 pts Fair-Play)")

    new_arg = st.text_area(
        "Soumettre ton argument (optionnel)",
        placeholder="Rédige un argument factuel et sourcé...",
        max_chars=400,
        label_visibility="collapsed",
    )

    if st.button("Voir les résultats →", type="primary"):
        st.session_state.fairplay_read = fairplay
        go_to("results")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ÉCRAN 6 — Résultats + Score citoyen
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "results":
    header("Résultats de la semaine")
    step_dots(5)

    # Résultat JM
    st.markdown(
        f"""
        <div class="card" style="text-align:center;">
            <div style="color:#8b8fa8; font-size:0.8rem; margin-bottom:0.4rem;">
                Mention médiane · Jugement Majoritaire
            </div>
            <div class="jm-median-badge">⚖️ {VOTE_RESULTS['median']}</div>
            <div style="color:#8b8fa8; font-size:0.78rem; margin-top:0.4rem;">
                sur {VOTE_RESULTS['total']:,} votes exprimés
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Distribution
    COLORS = {
        "Très favorable": "#00d084",
        "Favorable": "#a3e635",
        "Neutre": "#8b8fa8",
        "Défavorable": "#f97316",
        "Très défavorable": "#ff4d4d",
    }

    st.markdown("**Distribution des votes**")
    for label, pct in VOTE_RESULTS.items():
        if label in ("total", "median"):
            continue
        color = COLORS.get(label, "#3b4cca")
        st.markdown(
            f"""
            <div class="jm-bar-label">{label} — {pct}%</div>
            <div class="score-bar-bg">
                <div class="score-bar-fill" style="width:{pct}%; background:{color};"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Score citoyen
    base_score = 60
    quiz_bonus = 10 if st.session_state.quiz_passed else 0
    vote_bonus = 10
    fairplay_bonus = 5 if st.session_state.fairplay_read else 0
    total_score = base_score + quiz_bonus + vote_bonus + fairplay_bonus

    st.markdown(
        f"""
        <div class="card card-accent">
            <div style="font-weight:700; color:#ffffff; margin-bottom:0.6rem;">
                🏅 Ton score Citoyen Éclairé
            </div>
            <div style="font-size:2rem; font-weight:800; color:#7b8fff; text-align:center;">
                {total_score} pts
            </div>
            <div class="score-bar-bg" style="margin:0.6rem 0;">
                <div class="score-bar-fill" style="width:{min(total_score, 100)}%;"></div>
            </div>
            <div style="font-size:0.8rem; color:#8b8fa8; display:flex; gap:0.5rem; flex-wrap:wrap;">
                <span>✅ Quiz réussi +{quiz_bonus}</span>
                <span>🗳️ Vote exprimé +{vote_bonus}</span>
                <span>🤝 Fair-Play +{fairplay_bonus}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='text-align:center; color:#8b8fa8; font-size:0.78rem; margin-top:0.5rem;'>"
        "Classement national mis à jour chaque lundi · Prochain référendum dans 5 jours"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↩️ Recommencer la démo", type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
