"""
Script de seed pour l'environnement de développement.

Insère :
  - L'utilisateur système "agora-ai" (auteur des arguments seed)
  - Le référendum de test (vote obligatoire en France) avec quiz et arguments

Usage :
    python scripts/seed_dev.py
    python scripts/seed_dev.py --reset   # supprime les données existantes avant

Idempotent : ne crée pas de doublons si relancé sans --reset.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Permettre l'import du package agora depuis la racine du projet
sys.path.insert(0, str(Path(__file__).parent.parent))

from agora.core.database import SessionLocal
from agora.models.argument import Argument
from agora.models.referendum import QuizQuestion, Referendum
from agora.models.user import User

# ── Données du référendum de test ────────────────────────────────────────────

AGORA_AI_PHONE = "+33000000000"  # Numéro fictif de l'utilisateur système

REFERENDUM_DATA = {
    "question": "Faut-il rendre le vote obligatoire en France pour les élections nationales ?",
    "summary": (
        "Actuellement, le vote en France est un droit mais pas une obligation. "
        "Le taux d'abstention aux élections législatives 2022 a atteint 53,77%, "
        "un record historique. Plusieurs pays comme la Belgique, l'Australie ou "
        "le Luxembourg ont rendu le vote obligatoire sous peine d'amende."
    ),
    "historical_context": (
        "**Belgique (depuis 1893)** : Pionnière du vote obligatoire, la Belgique affiche "
        "un taux de participation supérieur à 87%. Les abstentionnistes risquent une amende "
        "de 10 à 50€.\n\n"
        "**Australie (depuis 1924)** : Après une chute de la participation à 47% en 1922, "
        "l'Australie a rendu le vote obligatoire. Le taux est depuis supérieur à 90%.\n\n"
        "**France (1793)** : La Constitution montagnarde de 1793 prévoyait déjà une forme "
        "de vote obligatoire, jamais appliquée en raison de la Terreur."
    ),
    "scientific_context": (
        "**Arend Lijphart (1997)** : Dans *\"Unequal Participation\"*, il démontre que "
        "l'abstention est socialement sélective : les classes populaires votent moins, "
        "ce qui biaise les résultats vers les préférences des classes aisées.\n\n"
        "**Méta-analyse Birch (2009)** : Portant sur 19 pays, elle conclut que l'obligation "
        "augmente la participation de 7 à 16 points en moyenne.\n\n"
        "**Étude Jakee & Sun (2006)** : Le vote blanc augmente significativement dans les "
        "systèmes à vote obligatoire."
    ),
    # Semaine courante : lundi au dimanche de la semaine en cours
    "week_start": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                  - timedelta(days=datetime.utcnow().weekday()),
    "week_end": datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=0)
                + timedelta(days=6 - datetime.utcnow().weekday()),
    "is_active": True,
    "news_source_title": "Abstention record aux législatives 2022 : 53,77% — Le Monde",
    "values_mapping": json.dumps({
        "Très favorable":   [2, 9, 9, 7, 7, 6],
        "Favorable":        [4, 7, 7, 6, 7, 8],
        "Neutre":           [5, 5, 5, 5, 5, 5],
        "Défavorable":      [8, 4, 4, 4, 6, 5],
        "Très défavorable": [10, 2, 2, 3, 5, 3],
    }),
}

QUIZ_DATA = [
    {
        "order": 1,
        "question_text": "Quel était le taux d'abstention aux élections législatives françaises de 2022 ?",
        "option_a": "32%",
        "option_b": "53,77%",
        "option_c": "41%",
        "correct_option": "b",
    },
    {
        "order": 2,
        "question_text": "Quel pays a instauré le vote obligatoire en premier parmi les suivants ?",
        "option_a": "Australie",
        "option_b": "France",
        "option_c": "Belgique",
        "correct_option": "c",
    },
    {
        "order": 3,
        "question_text": "Selon Birch (2009), de combien de points le vote obligatoire augmente-t-il la participation ?",
        "option_a": "2 à 5 points",
        "option_b": "7 à 16 points",
        "option_c": "20 à 30 points",
        "correct_option": "b",
    },
]

ARGUMENTS_DATA = [
    {
        "position": "pour",
        "content": (
            "Le vote obligatoire corrige une inégalité structurelle : aujourd'hui, les classes "
            "populaires votent moins, ce qui biaise les politiques publiques en faveur des plus "
            "aisés. Rendre le vote obligatoire, c'est rendre sa voix à chaque citoyen."
        ),
        "upvotes": 1842,
    },
    {
        "position": "pour",
        "content": (
            "L'expérience australienne le prouve : en 1922, le taux de participation était de 47%. "
            "Après l'instauration du vote obligatoire, il n'est jamais redescendu sous 90%. "
            "La contrainte a créé une habitude démocratique durable."
        ),
        "upvotes": 1204,
    },
    {
        "position": "pour",
        "content": (
            "Le vote blanc devrait être comptabilisé et reconnu. Avec le vote obligatoire couplé "
            "à une vraie reconnaissance du vote blanc, on forcerait les partis à écouter les "
            "abstentionnistes plutôt que de les ignorer."
        ),
        "upvotes": 987,
    },
    {
        "position": "contre",
        "content": (
            "Forcer quelqu'un à voter, c'est une contradiction dans les termes. La liberté inclut "
            "le droit de ne pas participer. Un vote sous contrainte n'est pas un acte civique, "
            "c'est une formalité administrative."
        ),
        "upvotes": 1677,
    },
    {
        "position": "contre",
        "content": (
            "Le problème n'est pas l'abstention, c'est la défiance. Forcer les gens à voter sans "
            "s'attaquer aux causes profondes — corruption perçue, déconnexion des élus — revient "
            "à traiter le symptôme en ignorant la maladie."
        ),
        "upvotes": 1389,
    },
    {
        "position": "contre",
        "content": (
            "Les études montrent qu'avec le vote obligatoire, le vote nul et blanc explose. "
            "On n'obtient pas une démocratie plus représentative, juste des urnes plus remplies "
            "de bulletins qui ne disent rien."
        ),
        "upvotes": 762,
    },
]


def seed(reset: bool = False) -> None:
    db = SessionLocal()
    try:
        if reset:
            print("[RESET] Suppression des donnees existantes...")
            db.query(Argument).delete()
            db.query(QuizQuestion).delete()
            db.query(Referendum).delete()
            db.query(User).filter(User.phone_number == AGORA_AI_PHONE).delete()
            db.commit()

        # ── Utilisateur système agora-ai ──────────────────────────────────────
        ai_user = db.query(User).filter(User.phone_number == AGORA_AI_PHONE).first()
        if not ai_user:
            ai_user = User(
                phone_number=AGORA_AI_PHONE,
                nickname="Agora IA",
                is_system=True,
                is_active=True,
            )
            db.add(ai_user)
            db.flush()  # génère l'id sans committer
            print(f"[OK] Utilisateur agora-ai cree (id: {ai_user.id})")
        else:
            print(f"[INFO] Utilisateur agora-ai deja existant (id: {ai_user.id})")

        # ── Référendum de test ────────────────────────────────────────────────
        existing_ref = db.query(Referendum).filter(
            Referendum.question == REFERENDUM_DATA["question"]
        ).first()

        if not existing_ref:
            referendum = Referendum(**REFERENDUM_DATA)
            db.add(referendum)
            db.flush()

            # Quiz
            for q in QUIZ_DATA:
                db.add(QuizQuestion(referendum_id=referendum.id, **q))

            # Arguments seed
            for arg in ARGUMENTS_DATA:
                db.add(Argument(
                    user_id=ai_user.id,
                    referendum_id=referendum.id,
                    is_moderated=True,  # pré-approuvés par l'IA
                    **arg,
                ))

            db.commit()
            print(f"[OK] Referendum cree (id: {referendum.id})")
            print(f"   -> {len(QUIZ_DATA)} questions de quiz inserees")
            print(f"   -> {len(ARGUMENTS_DATA)} arguments seed inseres")
        else:
            print(f"[INFO] Referendum deja existant (id: {existing_ref.id})")

        print("\n[OK] Seed termine. Lancez l'API avec :")
        print("   uvicorn agora.main:app --reload")
        print("   Swagger : http://localhost:8000/docs")

    except Exception as e:
        db.rollback()
        print(f"[ERREUR] {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed la base de données de développement Agora.")
    parser.add_argument("--reset", action="store_true", help="Supprime les données existantes avant le seed")
    args = parser.parse_args()
    seed(reset=args.reset)
