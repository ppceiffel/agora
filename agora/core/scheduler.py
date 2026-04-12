"""
Scheduler APScheduler — Pipeline AI hebdomadaire.
Génère automatiquement un nouveau référendum chaque lundi à 7h00 (Europe/Paris).
Peut aussi être déclenché manuellement via run_pipeline_now().
"""
import json
import logging
import threading
import uuid
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from agora.core.config import settings
from agora.core.database import SessionLocal
from agora.models.argument import Argument
from agora.models.referendum import QuizQuestion, Referendum
from agora.models.user import User

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def run_weekly_pipeline() -> None:
    """
    Génère un nouveau référendum :
    1. Scrape les sources d'actualité
    2. Sélectionne la question via Claude
    3. Construit le contexte complet en parallèle (historique, scientifique, arguments, values_mapping)
    4. Génère le quiz via Claude
    5. Persiste tout en base, désactive le référendum précédent
    """
    logger.info("[Pipeline AI] Démarrage du pipeline hebdomadaire...")

    if not settings.anthropic_api_key:
        logger.warning("[Pipeline AI] ANTHROPIC_API_KEY absente — pipeline annulé.")
        return

    # Imports locaux pour éviter les circular imports et la charge au démarrage
    from agora.scraper.sources import fetch_all_sources
    from agora.ai.question_selector import select_question
    from agora.ai.context_builder import build_full_context
    from agora.ai.quiz_generator import generate_quiz

    # ── 1. Scraping ──────────────────────────────────────────────────────────
    sources = fetch_all_sources()
    if not sources:
        logger.error("[Pipeline AI] Aucune source récupérée — pipeline annulé.")
        return

    # ── 2. Sélection de la question ───────────────────────────────────────────
    question_data = select_question(sources)
    if not question_data:
        logger.error("[Pipeline AI] Sélection de question échouée — pipeline annulé.")
        return

    question = question_data["question"]
    summary = question_data.get("summary", "")
    source_url = question_data.get("source_url")
    source_title = next(
        (s["title"] for s in sources if s.get("url") == source_url),
        source_url or "Actualité française",
    )

    # ── 3. Contexte complet (5 appels en parallèle) ───────────────────────────
    logger.info("[Pipeline AI] Construction du contexte pour : %s", question)
    context = build_full_context(question)

    historical = context.get("historical", "Contexte historique non disponible.")
    scientific = context.get("scientific", "Contexte scientifique non disponible.")
    args_pour = context.get("arguments_pour", [])
    args_contre = context.get("arguments_contre", [])
    values_mapping = context.get("values_mapping", {})

    # ── 4. Quiz ───────────────────────────────────────────────────────────────
    quiz_questions_data = []
    try:
        quiz_questions_data = generate_quiz(summary)
        logger.info("[Pipeline AI] %d questions de quiz générées.", len(quiz_questions_data))
    except Exception as e:
        logger.error("[Pipeline AI] Génération quiz échouée: %s", e)

    # ── 5. Persistance ────────────────────────────────────────────────────────
    db = SessionLocal()
    try:
        # Désactiver le référendum actif précédent
        db.query(Referendum).filter(Referendum.is_active == True).update({"is_active": False})

        # Dates de la semaine courante (lundi → dimanche)
        now = datetime.utcnow()
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)

        # Récupérer l'utilisateur système agora-ai
        system_user = db.query(User).filter(User.phone_number == "+33000000000").first()
        if not system_user:
            logger.error("[Pipeline AI] Utilisateur système agora-ai introuvable. Lancez seed_dev.py.")
            db.rollback()
            return
        created_by_id = system_user.id

        # Créer le référendum
        ref = Referendum(
            id=str(uuid.uuid4()),
            question=question,
            summary=summary,
            source_url=source_url,
            historical_context=historical,
            scientific_context=scientific,
            values_mapping=json.dumps(values_mapping, ensure_ascii=False),
            news_source_title=source_title,
            week_start=week_start,
            week_end=week_end,
            is_active=True,
        )
        db.add(ref)
        db.flush()

        # Créer les questions de quiz
        for i, q in enumerate(quiz_questions_data):
            db.add(QuizQuestion(
                id=str(uuid.uuid4()),
                referendum_id=ref.id,
                question_text=q["question_text"],
                option_a=q["option_a"],
                option_b=q["option_b"],
                option_c=q["option_c"],
                correct_option=q["correct_option"],
                order=i,
            ))

        # Créer les arguments IA (pré-modérés)
        for text in args_pour:
            if text and text.strip():
                db.add(Argument(
                    id=str(uuid.uuid4()),
                    referendum_id=ref.id,
                    user_id=created_by_id,
                    position="pour",
                    content=text.strip(),
                    upvotes=0,
                    is_moderated=True,
                ))

        for text in args_contre:
            if text and text.strip():
                db.add(Argument(
                    id=str(uuid.uuid4()),
                    referendum_id=ref.id,
                    user_id=created_by_id,
                    position="contre",
                    content=text.strip(),
                    upvotes=0,
                    is_moderated=True,
                ))

        db.commit()
        logger.info(
            "[Pipeline AI] Référendum créé avec succès : '%s' (id: %s)",
            question, ref.id,
        )

    except Exception as e:
        db.rollback()
        logger.error("[Pipeline AI] Erreur lors de la persistance: %s", e)
    finally:
        db.close()


def run_pipeline_now() -> None:
    """
    Déclenche le pipeline immédiatement dans un thread daemon.
    Appelé par l'endpoint admin POST /admin/generate-referendum.
    """
    thread = threading.Thread(target=run_weekly_pipeline, daemon=True, name="pipeline-ai-manual")
    thread.start()
    logger.info("[Pipeline AI] Déclenché manuellement (thread daemon démarré).")


def start_scheduler() -> None:
    """Démarre le scheduler APScheduler en arrière-plan."""
    global _scheduler

    if _scheduler and _scheduler.running:
        logger.info("[Scheduler] Déjà en cours d'exécution.")
        return

    _scheduler = BackgroundScheduler(timezone="Europe/Paris")
    _scheduler.add_job(
        run_weekly_pipeline,
        trigger="cron",
        day_of_week="mon",
        hour=7,
        minute=0,
        id="weekly_referendum",
        name="Génération hebdomadaire du référendum",
        replace_existing=True,
        misfire_grace_time=3600,  # 1h de tolérance si le serveur était down au moment du déclenchement
    )
    _scheduler.start()
    logger.info("[Scheduler] Démarré — pipeline chaque lundi à 07h00 (Europe/Paris).")


def stop_scheduler() -> None:
    """Arrête le scheduler proprement (appelé au shutdown FastAPI)."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Arrêté.")
