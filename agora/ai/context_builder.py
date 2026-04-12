"""
Constructeur de contexte IA pour un référendum.
5 appels Claude indépendants, lancés en parallèle via ThreadPoolExecutor.
Chaque appel est fault-tolerant — retourne une valeur par défaut en cas d'échec.
"""
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from agora.core.config import settings

logger = logging.getLogger(__name__)

# ── Prompts ────────────────────────────────────────────────────────────────────

HISTORICAL_PROMPT = """Tu es un historien civique. Pour la question suivante, fournis un éclairage historique factuel et équilibré en 3-5 paragraphes markdown.
Ne prends pas position. Cite des exemples historiques concrets (France et international si pertinent).

Question : {question}

Réponds directement en markdown, sans titre de section ni préambule."""

SCIENTIFIC_PROMPT = """Tu es un expert en sciences sociales et politiques publiques. Pour la question suivante, fournis un éclairage scientifique factuel basé sur des études et données en 3-5 paragraphes markdown.
Ne prends pas position. Cite des sources ou données chiffrées si possible.

Question : {question}

Réponds directement en markdown, sans titre de section ni préambule."""

ARGUMENTS_POUR_PROMPT = """Tu es un analyste politique neutre. Pour la question suivante, liste exactement 3 arguments POUR (favorables à la mesure), présentés de manière factuelle.
Ne prends pas position toi-même. Les arguments doivent être réels, défendables et distincts.
Chaque argument doit faire entre 50 et 150 mots.

Question : {question}

Réponds UNIQUEMENT avec un JSON valide, sans markdown :
["argument 1 complet", "argument 2 complet", "argument 3 complet"]"""

ARGUMENTS_CONTRE_PROMPT = """Tu es un analyste politique neutre. Pour la question suivante, liste exactement 3 arguments CONTRE (défavorables à la mesure), présentés de manière factuelle.
Ne prends pas position toi-même. Les arguments doivent être réels, défendables et distincts.
Chaque argument doit faire entre 50 et 150 mots.

Question : {question}

Réponds UNIQUEMENT avec un JSON valide, sans markdown :
["argument 1 complet", "argument 2 complet", "argument 3 complet"]"""

VALUES_MAPPING_PROMPT = """Tu es un expert en éthique civique et en théorie des valeurs de Schwartz.
Pour la question suivante, génère un mapping entre chaque mention du Jugement Majoritaire et les 6 valeurs civiques.
Chaque valeur est notée de 0 à 10 (10 = fortement exprimée par ce choix de vote).

Les 6 valeurs dans l'ordre : Liberté, Égalité, Fraternité, Sécurité, Justice, Efficacité

Exemples de raisonnement :
- "Très favorable" à une mesure sécuritaire → Sécurité élevée (9), Liberté faible (2)
- "Très défavorable" à cette même mesure → Liberté élevée (9), Sécurité faible (2)
- "Neutre" → toutes les valeurs à 5

Question : {question}

Réponds UNIQUEMENT avec un JSON valide, sans markdown :
{{
  "Très favorable":   [score_liberté, score_égalité, score_fraternité, score_sécurité, score_justice, score_efficacité],
  "Favorable":        [score_liberté, score_égalité, score_fraternité, score_sécurité, score_justice, score_efficacité],
  "Neutre":           [5, 5, 5, 5, 5, 5],
  "Défavorable":      [score_liberté, score_égalité, score_fraternité, score_sécurité, score_justice, score_efficacité],
  "Très défavorable": [score_liberté, score_égalité, score_fraternité, score_sécurité, score_justice, score_efficacité]
}}"""

_DEFAULT_VALUES_MAPPING = {
    "Très favorable":   [5, 5, 5, 5, 5, 5],
    "Favorable":        [5, 5, 5, 5, 5, 5],
    "Neutre":           [5, 5, 5, 5, 5, 5],
    "Défavorable":      [5, 5, 5, 5, 5, 5],
    "Très défavorable": [5, 5, 5, 5, 5, 5],
}


# ── Appel Claude unique ────────────────────────────────────────────────────────

def _call_claude(client, prompt: str, max_tokens: int = 1024) -> str:
    """Appel Claude synchrone — conçu pour tourner dans un thread."""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


# ── Fonctions individuelles (fault-tolerant) ───────────────────────────────────

def build_historical_context(client, question: str) -> str:
    try:
        return _call_claude(client, HISTORICAL_PROMPT.format(question=question), max_tokens=2048)
    except Exception as e:
        logger.error("build_historical_context error: %s", e)
        return "Contexte historique non disponible."


def build_scientific_context(client, question: str) -> str:
    try:
        return _call_claude(client, SCIENTIFIC_PROMPT.format(question=question), max_tokens=2048)
    except Exception as e:
        logger.error("build_scientific_context error: %s", e)
        return "Contexte scientifique non disponible."


def build_arguments_pour(client, question: str) -> list[str]:
    try:
        raw = _call_claude(client, ARGUMENTS_POUR_PROMPT.format(question=question))
        result = json.loads(raw)
        if isinstance(result, list):
            return [str(a) for a in result[:3]]
        return []
    except Exception as e:
        logger.error("build_arguments_pour error: %s", e)
        return []


def build_arguments_contre(client, question: str) -> list[str]:
    try:
        raw = _call_claude(client, ARGUMENTS_CONTRE_PROMPT.format(question=question))
        result = json.loads(raw)
        if isinstance(result, list):
            return [str(a) for a in result[:3]]
        return []
    except Exception as e:
        logger.error("build_arguments_contre error: %s", e)
        return []


def build_values_mapping(client, question: str) -> dict:
    try:
        raw = _call_claude(client, VALUES_MAPPING_PROMPT.format(question=question))
        result = json.loads(raw)
        expected_keys = {"Très favorable", "Favorable", "Neutre", "Défavorable", "Très défavorable"}
        if set(result.keys()) == expected_keys and all(
            isinstance(v, list) and len(v) == 6 for v in result.values()
        ):
            return result
        logger.warning("values_mapping format invalide, utilisation du mapping neutre par défaut")
    except Exception as e:
        logger.error("build_values_mapping error: %s", e)
    return _DEFAULT_VALUES_MAPPING


# ── Orchestrateur principal ────────────────────────────────────────────────────

def build_full_context(question: str) -> dict:
    """
    Lance les 5 appels Claude en parallèle et retourne le contexte complet.
    Fault-tolerant : chaque appel a une valeur par défaut en cas d'échec.

    Retourne:
        {
            "historical": str,
            "scientific": str,
            "arguments_pour": list[str],
            "arguments_contre": list[str],
            "values_mapping": dict,
        }
    """
    if not settings.anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY absente — impossible de construire le contexte.")
        return {}

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    except ImportError:
        logger.error("Bibliothèque anthropic non installée.")
        return {}

    tasks = {
        "historical": (build_historical_context, client, question),
        "scientific": (build_scientific_context, client, question),
        "arguments_pour": (build_arguments_pour, client, question),
        "arguments_contre": (build_arguments_contre, client, question),
        "values_mapping": (build_values_mapping, client, question),
    }

    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fn, *args): key
            for key, (fn, *args) in tasks.items()
        }
        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as e:
                logger.error("Tâche %s échouée: %s", key, e)

    logger.info("Contexte complet construit pour : %s", question)
    return results
