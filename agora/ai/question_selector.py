"""
Sélectionne la question civique la plus appropriée à partir d'une liste de sources d'actualité.
Utilise Claude Sonnet pour choisir un sujet de politique publique concrète, non partisan.
"""
import json
import logging

from agora.core.config import settings

logger = logging.getLogger(__name__)

SELECTOR_PROMPT = """Tu es un assistant civique. On te fournit une liste de titres d'actualité française.
Tu dois sélectionner le sujet le plus propice à un débat civique factuel et non partisan,
portant sur une politique publique concrète.

Contraintes strictes :
- Pas de parti politique ni de personnalité politique nommée dans la question
- La question doit porter sur une mesure ou politique publique concrète
- La question doit être formulée de manière neutre (ni pour ni contre)
- Le sujet doit intéresser l'ensemble des citoyens français
- Éviter les sujets purement électoraux ou trop polémiques sans dimension civique claire
- La question doit commencer par "Faut-il" ou "Devrait-on"

Titres d'actualité :
{titles}

Réponds UNIQUEMENT avec un JSON valide, sans markdown, sans explication :
{{
  "question": "Faut-il ... ?",
  "summary": "Résumé factuel en 3-4 phrases des enjeux principaux.",
  "source_url": "URL de l'article source si disponible, sinon null",
  "topic_tags": ["tag1", "tag2"]
}}"""


def select_question(sources: list[dict]) -> dict | None:
    """
    Prend la liste des sources et retourne la question sélectionnée par Claude.
    Retourne None si le pipeline AI n'est pas disponible ou en cas d'erreur répétée.
    """
    if not settings.anthropic_api_key:
        logger.warning("ANTHROPIC_API_KEY absente — sélection de question impossible.")
        return None

    if not sources:
        logger.warning("Aucune source disponible pour sélectionner une question.")
        return None

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    except ImportError:
        logger.error("Bibliothèque anthropic non installée.")
        return None

    titles_text = "\n".join(
        f"- [{s['source']}] {s['title']} ({s['url']})"
        for s in sources[:20]  # limiter à 20 titres pour rester dans le budget tokens
    )

    for attempt in range(2):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                messages=[{"role": "user", "content": SELECTOR_PROMPT.format(titles=titles_text)}],
            )
            raw = message.content[0].text.strip()
            result = json.loads(raw)
            if "question" in result and "summary" in result:
                logger.info("Question sélectionnée : %s", result["question"])
                return result
            logger.warning("Format de réponse invalide (tentative %d)", attempt + 1)
        except json.JSONDecodeError as e:
            logger.warning("JSONDecodeError tentative %d: %s", attempt + 1, e)
        except Exception as e:
            logger.error("Erreur sélection question: %s", e)
            return None

    logger.error("Sélection de question échouée après 2 tentatives.")
    return None
