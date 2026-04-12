"""
Génère un quiz de compréhension à partir du résumé d'un référendum.
Le client Anthropic est initialisé à la demande (lazy) pour ne pas bloquer
le démarrage si ANTHROPIC_API_KEY est absente.
"""
import json
import logging

from agora.core.config import settings

logger = logging.getLogger(__name__)

QUIZ_PROMPT = """Tu es un assistant civique. On te fournit le résumé d'une question de référendum.
Tu dois générer exactement 3 questions de quiz factuelles pour vérifier que le citoyen a compris les enjeux.

Règles strictes :
- Les questions doivent être factuelles, pas d'opinion
- Les questions ne doivent pas orienter le vote
- Chaque question a 3 options (a, b, c), une seule est correcte
- Le niveau de difficulté est modéré : ni trivial, ni expert

Réponds UNIQUEMENT avec un JSON valide, sans markdown, sans explication, au format suivant :
[
  {{
    "question_text": "...",
    "option_a": "...",
    "option_b": "...",
    "option_c": "...",
    "correct_option": "a"
  }},
  ...
]

Sujet du référendum :
{summary}
"""


def generate_quiz(summary: str) -> list[dict]:
    """
    Génère 3 questions de quiz factuelles à partir du résumé d'un référendum.
    Lève une exception si ANTHROPIC_API_KEY est absente ou en cas d'erreur réseau.
    """
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY non configurée — impossible de générer le quiz.")

    import anthropic
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": QUIZ_PROMPT.format(summary=summary),
            }
        ],
    )
    raw = message.content[0].text.strip()
    return json.loads(raw)
