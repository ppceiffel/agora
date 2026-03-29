# Agora — Le Référendum Intelligent

> Transformer chaque citoyen en Citoyen Éclairé. Pas de bla-bla partisan : du débat constructif, de la data, des référendums.

---

## Le problème

On ne vote plus, ou alors on vote par colère. La politique est devenue un match de boxe où personne n'écoute les arguments de l'autre. Résultat : une polarisation totale et des citoyens qui se sentent impuissants.

## La solution

Une application mobile qui conditionne le vote à la compréhension. Chaque semaine, une question de référendum national — sourcée, contextualisée, débattue. Avec un système de vote par **Jugement Majoritaire** (5 niveaux) plutôt qu'un simple oui/non.

---

## Comment ça marche

### 1. La Question de la Semaine
Un pipeline automatique scrape chaque semaine l'Assemblée Nationale, pétitions.gouv.fr et l'actualité. Claude sélectionne et formule **LA question citoyenne de la semaine** — factuelle, non polémique.

### 2. Le Quiz de Validation
Avant de voter, tu réponds à **3 questions factuelles** générées par l'IA sur les enjeux réels du texte. Pas de compréhension → pas de vote. Ça évite le vote par réflexe.

### 3. Le Vote par Jugement Majoritaire
5 niveaux de réponse :
- Très favorable
- Favorable
- Neutre
- Défavorable
- Très défavorable

Le Jugement Majoritaire est mathématiquement plus résistant aux extrêmes qu'un vote binaire.

### 4. L'Arène des Arguments
Après avoir voté, tu accèdes au **Top 3 Pour** et **Top 3 Contre**, rédigés et notés par la communauté. Tu peux soumettre ton propre argument. Les meilleurs arguments te font gagner des badges.

### 5. L'Éclairage Scientifique & Historique
Pour chaque sujet, Claude recherche :
- **L'histoire** : "Est-ce que ça a déjà été testé ailleurs ? Avec quels résultats ?"
- **La science** : "Que disent les études et publications récentes ?"

### 6. Le Score Citoyen Éclairé
L'app te récompense si tu lis les arguments opposés aux tiens. Plus tu es ouvert au débat, plus ton badge de citoyen brille. Un classement national des citoyens les plus éclairés de France.

---

## Fonctionnalités supplémentaires

- **Soumettre une question** : N'importe quel utilisateur peut proposer un sujet de référendum. Si la communauté valide, c'est la question nationale de la semaine suivante.
- **Validation par les Éclairés** : Les questions proposées sont validées par les citoyens au score le plus élevé.
- **Gouvernance par les utilisateurs** : Les évolutions de l'application elle-même sont votées par tous les utilisateurs.
- **Modèle de financement par dons** : Pas de publicité, pas d'actionnaire. Financement par dons avec un plafond individuel pour éviter toute prise de pouvoir par l'argent.

---

## Architecture Technique

```
agora/
├── api/                    # FastAPI — routes REST
│   ├── auth/               # Authentification (OTP SMS via Twilio)
│   ├── referendum/         # Questions, votes (Jugement Majoritaire)
│   ├── arguments/          # Soumission, notation des arguments
│   ├── quiz/               # Génération et validation du quiz
│   └── users/              # Profils, scores, badges
│
├── scraper/                # Pipeline de veille hebdomadaire
│   ├── sources/            # Assemblée Nationale, pétitions.gouv, presse
│   └── scheduler/          # Cron job hebdomadaire
│
├── ai/                     # Intégration Claude API
│   ├── question_selector.py    # Sélection et formulation de la question
│   ├── quiz_generator.py       # Génération des 3 questions de validation
│   ├── context_builder.py      # Éclairage historique & scientifique
│   └── argument_moderator.py   # Modération des arguments
│
├── models/                 # Modèles de données (SQLAlchemy)
│   ├── user.py
│   ├── referendum.py
│   ├── vote.py
│   └── argument.py
│
├── core/                   # Config, sécurité, utils
│   ├── config.py
│   └── database.py
│
└── main.py                 # Point d'entrée FastAPI
```

### Stack

| Composant | Technologie |
|-----------|-------------|
| Backend | Python 3.12 + FastAPI |
| Base de données | PostgreSQL (Supabase) |
| Authentification | OTP SMS via Twilio |
| IA | Claude API (claude-sonnet-4-6) |
| Scraping | BeautifulSoup + Playwright |
| Tâches planifiées | APScheduler |
| Hébergement backend | Railway / Render |
| Frontend mobile | React Native + Expo *(à venir)* |

### Flux de données

```
[Cron hebdomadaire]
      │
      ▼
[Scraper] ──── Assemblée Nationale, pétitions.gouv, presse
      │
      ▼
[Claude] ──── Sélection question + Quiz + Contexte historique/scientifique
      │
      ▼
[Base de données] ──── Question publiée
      │
      ▼
[Utilisateur] ──── Inscription (OTP SMS) → Quiz → Vote (JM) → Arguments
      │
      ▼
[Score Citoyen] ──── Lecture arguments opposés + Qualité contributions
```

---

## Installation (développement local)

### Prérequis
- Python 3.12+
- PostgreSQL
- Clé API Anthropic (Claude)
- Compte Twilio (SMS OTP)

### Setup

```bash
# Cloner le dépôt
git clone https://github.com/ppceiffel/agora.git
cd agora

# Environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate

# Dépendances
pip install -r requirements.txt

# Variables d'environnement
cp .env.example .env
# Remplir les clés dans .env

# Lancer l'API
uvicorn agora.main:app --reload
```

### Variables d'environnement

```env
DATABASE_URL=postgresql://user:password@localhost/agora
ANTHROPIC_API_KEY=sk-ant-...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+33...
SECRET_KEY=...
```

---

## Roadmap

### Phase 1 — POC (MVP)
- [ ] Authentification par numéro de téléphone (OTP SMS)
- [ ] Pipeline scraping + sélection de question par Claude
- [ ] Quiz de validation généré par IA
- [ ] Vote par Jugement Majoritaire (5 niveaux)
- [ ] API REST documentée (Swagger)

### Phase 2 — Communauté
- [ ] Arène des arguments (soumission + notation)
- [ ] Score Citoyen Éclairé
- [ ] Badges et classement national
- [ ] Éclairage historique & scientifique par Claude

### Phase 3 — Gouvernance
- [ ] Soumission de questions par les utilisateurs
- [ ] Validation par les citoyens les plus éclairés
- [ ] Vote communautaire sur les évolutions de l'app
- [ ] Système de dons avec plafond individuel
- [ ] Application mobile React Native

---

## Philosophie du projet

- **Pas de publicité.** Jamais.
- **Pas d'algorithme de recommandation addictif.** Une question par semaine, c'est tout.
- **L'argent ne donne pas de pouvoir.** Les dons ont un plafond individuel.
- **La qualité du débat prime sur la vitesse.**
- **Open source.** Le code est public. La gouvernance aussi.

---

## Contribuer

Les contributions sont les bienvenues. Les grandes décisions sur l'évolution du projet sont soumises au vote de la communauté.

1. Fork le projet
2. Crée une branche (`git checkout -b feature/ma-fonctionnalite`)
3. Commit (`git commit -m 'feat: ajoute ma fonctionnalité'`)
4. Push (`git push origin feature/ma-fonctionnalite`)
5. Ouvre une Pull Request

---

## Licence

MIT — Le savoir et le débat appartiennent à tous.
