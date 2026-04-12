"""
Scraper de sources d'actualité pour alimenter le pipeline AI.
- RSS Le Monde Politique
- API pétitions Assemblée Nationale
Retourne toujours une liste (vide en cas d'échec) — ne lève jamais d'exception.
"""
import logging
import xml.etree.ElementTree as ET

import httpx

logger = logging.getLogger(__name__)

RSS_LEMONDE_POLITIQUE = "https://www.lemonde.fr/politique/rss_full.xml"
AN_PETITIONS_API = "https://petitions.assemblee-nationale.fr/api/petitions?status=running&per_page=10"


def _parse_rss(xml_text: str, source: str) -> list[dict]:
    """Parse un flux RSS et retourne une liste de dicts standardisés."""
    items = []
    try:
        root = ET.fromstring(xml_text)
        channel = root.find("channel")
        if channel is None:
            return items
        for item in channel.findall("item"):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            pub_date = item.findtext("pubDate", "").strip()
            if title:
                items.append({
                    "title": title,
                    "url": link,
                    "source": source,
                    "published_at": pub_date,
                })
    except ET.ParseError as e:
        logger.warning("RSS parse error for %s: %s", source, e)
    return items


def fetch_lemonde_politique() -> list[dict]:
    """Récupère les titres d'articles politiques du Monde."""
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(RSS_LEMONDE_POLITIQUE)
            resp.raise_for_status()
        return _parse_rss(resp.text, "Le Monde Politique")
    except Exception as e:
        logger.warning("Impossible de récupérer Le Monde RSS: %s", e)
        return []


def fetch_assemblee_petitions() -> list[dict]:
    """Récupère les pétitions en cours à l'Assemblée Nationale."""
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(AN_PETITIONS_API)
            resp.raise_for_status()
        data = resp.json()
        petitions = data if isinstance(data, list) else data.get("data", [])
        items = []
        for p in petitions:
            title = p.get("title") or p.get("object") or ""
            url = p.get("url") or p.get("link") or ""
            if title:
                items.append({
                    "title": title.strip(),
                    "url": url.strip(),
                    "source": "Assemblée Nationale (pétitions)",
                    "published_at": p.get("created_at", ""),
                })
        return items
    except Exception as e:
        logger.warning("Impossible de récupérer les pétitions AN: %s", e)
        return []


def fetch_all_sources() -> list[dict]:
    """Agrège toutes les sources. Retourne une liste vide en cas d'échec total."""
    sources: list[dict] = []
    sources.extend(fetch_lemonde_politique())
    sources.extend(fetch_assemblee_petitions())
    logger.info("Sources récupérées : %d articles/pétitions", len(sources))
    return sources
