import json

import anthropic

from agora.core.config import settings

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

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
    """Génère 3 questions de quiz factuelles à partir du résumé d'un référendum."""
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
