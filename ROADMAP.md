# Agora — Roadmap & État du projet

> Fichier de référence pour reprendre le développement entre les sessions.
> **Dernière mise à jour : 11 avril 2026**

---

## Vision du produit

Application web civique permettant à des citoyens de voter chaque semaine sur une question d'intérêt public, générée automatiquement par l'IA à partir de l'actualité française. Le vote utilise le **Jugement Majoritaire** (5 mentions). Chaque votant doit d'abord réussir un quiz de compréhension (2/3). Un profil de valeurs (cadre Schwartz) est esquissé à partir des votes successifs.

---

## Architecture technique

| Couche | Technologie | Hébergement |
|--------|------------|-------------|
| Backend | FastAPI + SQLAlchemy + Alembic | Railway (free tier ~0-5€/mois) |
| Base de données dev | SQLite (`agora_dev.db`) | Local |
| Base de données prod | PostgreSQL via Supabase | Supabase free tier |
| Frontend | Next.js 14 (App Router) — **à créer** | Vercel (gratuit) |
| Auth | OTP SMS Twilio (code déjà écrit) | — |
| AI | Claude API (Anthropic) | — |
| POC référence | Streamlit (`poc/app.py`) | Streamlit Cloud |

### Structure du dépôt

```
agora/                    ← Package Python backend (FastAPI)
  api/
    auth/router.py        ← OTP SMS + JWT (fonctionnel)
    referendum/router.py  ← GET /current, GET /quiz, POST /quiz/validate (fonctionnel)
    votes/router.py       ← POST /votes/, GET /results (fonctionnel)
    arguments/            ← VIDE — à implémenter (Phase 1)
  ai/
    quiz_generator.py     ← Génération de quiz via Claude (lazy client)
    question_selector.py  ← Sélection de la question civique (Claude Sonnet)
    context_builder.py    ← 5 appels Claude en parallèle (historique, scientifique, arguments, valeurs)
  core/
    config.py             ← Settings Pydantic (Twilio/Claude optionnels en dev)
    database.py           ← SQLAlchemy engine (SQLite/PostgreSQL)
    security.py           ← JWT + génération OTP
    scheduler.py          ← APScheduler (lundi 07h00 Europe/Paris) + run_pipeline_now()
  models/
    user.py               ← User, OTPCode
    referendum.py         ← Referendum, QuizQuestion
    vote.py               ← Vote (enum MajorityJudgmentGrade)
    argument.py           ← Argument, ArgumentRead, ArgumentVote
  scraper/
    sources.py            ← RSS Le Monde + API pétitions AN (fault-tolerant)

migrations/               ← Alembic (2 migrations appliquées)
scripts/
  seed_dev.py             ← Seed idempotent (user agora-ai + référendum de test)
poc/                      ← POC Streamlit de référence (NE PAS MODIFIER)
  app.py                  ← App complète avec tous les écrans
  mock_data.py            ← Données de test
frontend/                 ← ABSENT — à créer (Phase 3)
```

---

## Phases de développement

### ✅ Phase 0 — Fondations (TERMINÉ — 11 avril 2026)

**Objectif :** Backend qui tourne en local avec de vraies données.

- [x] **Corrections modèles SQLAlchemy**
  - `vote.py` : corrigé `quiz_passed` de `String` → `Boolean`
  - `referendum.py` : ajouté `values_mapping` (JSON), `ai_arguments_seed` (JSON), `news_source_title` + FK manquant sur `QuizQuestion.referendum_id`
  - `user.py` : ajouté `nickname`, `values_profile` (JSON Schwartz agrégé), `is_system`
  - `argument.py` : ajouté `ArgumentVote` (upvotes avec contrainte UNIQUE user+argument)
- [x] **Environnement de développement**
  - `agora/core/config.py` : Twilio et Claude optionnels (champs `str | None`), `frontend_url` ajouté
  - `agora/core/database.py` : support SQLite (`check_same_thread=False`)
  - `agora/api/auth/router.py` : mode dev — OTP retourné dans la réponse JSON si Twilio absent
  - `.env` créé (SQLite local, zéro configuration requise)
  - `.gitignore` mis à jour (`agora_dev.db`)
- [x] **Alembic**
  - `alembic init migrations` exécuté
  - `migrations/env.py` configuré pour importer tous les modèles et lire `DATABASE_URL` depuis les settings
  - Migration `initial_schema` générée et appliquée
  - Migration `add_quiz_fk` générée et appliquée
- [x] **Seed de développement**
  - `scripts/seed_dev.py` : insère l'utilisateur système `agora-ai` + le référendum "vote obligatoire" + 3 questions de quiz + 6 arguments (pour/contre)
  - Idempotent (relançable sans créer de doublons), supporte `--reset`
  - Les dates `week_start`/`week_end` sont dynamiques (semaine courante)
- [x] **Validation** : flow complet testé
  - `GET /health` → 200
  - `POST /auth/send-otp` → retourne `dev_code` en mode dev
  - `POST /auth/verify-otp` → retourne JWT
  - `GET /referendums/current` → retourne le référendum de la semaine
  - `GET /referendums/{id}/quiz` → retourne les 3 questions
  - `POST /votes/` → enregistre le vote
  - `GET /votes/{id}/results` → retourne la distribution + médiane JM

**Pour démarrer l'API en local :**
```bash
# Depuis la racine du projet
python scripts/seed_dev.py          # À faire une seule fois (ou --reset pour réinitialiser)
uvicorn agora.main:app --reload
# Swagger : http://localhost:8000/docs
# En mode dev, l'OTP est retourné dans la réponse /auth/send-otp (champ dev_code)
```

---

### ✅ Phase 1 — Backend complet (TERMINÉ — 11 avril 2026)

**Objectif :** Tous les endpoints dont le frontend a besoin.

#### 1.1 Router arguments (`agora/api/arguments/router.py`) ✅
- [x] `GET /arguments/{referendum_id}` — top 3 pour + top 3 contre (triés par upvotes)
- [x] `POST /arguments/` — soumettre un argument (auth requise, 1 par position par user par référendum)
- [x] `POST /arguments/{id}/upvote` — upvoter (contrainte unique via `ArgumentVote`, 409 si déjà upvoté)
- [x] `DELETE /arguments/{id}/upvote` — retirer son upvote
- [x] `POST /arguments/{id}/read` — tracer lecture (alimente `ArgumentRead`, +1 fairplay_count)
- [x] Branché dans `agora/main.py`

#### 1.2 Router users (`agora/api/users/router.py`) ✅
- [x] `GET /users/me` — profil complet : score, votes_count, values_profile (JSON décodé), nickname
- [x] `PATCH /users/me` — mettre à jour le nickname (validation 2-50 chars, unicité)
- [x] `GET /users/me/history` — votes passés avec scores Schwartz par vote
- [x] Branché dans `agora/main.py`

#### 1.3 Middleware profil Schwartz ✅
- [x] Après chaque `POST /votes/` réussi, `_update_values_profile()` recalcule la moyenne Schwartz
  - Lit tous les votes de l'user + `referendum.values_mapping` de chaque référendum
  - Sauvegarde en JSON dans `user.values_profile` : `{scores: {valeur: float}, votes_count: int}`

#### 1.4 Endpoints admin (`agora/api/admin/router.py`) ✅
- [x] `GET /admin/referendums` — liste tous les référendums avec nombre de votes
- [x] `POST /admin/generate-referendum` — stub (branché en Phase 2), vérifie ANTHROPIC_API_KEY
- [x] `PATCH /admin/referendums/{id}/deactivate` — désactive un référendum
- [x] Protégé par header `X-Admin-Secret` (valeur `ADMIN_SECRET` dans `.env`)
- [x] Branché dans `agora/main.py`

#### 1.5 Corrections votes/router.py ✅
- [x] Bonus quiz (+10), bonus vote (+10), bonus fair-play (+5 si ≥2 arguments lus)
- [x] `distribution_pct` ajouté dans `VoteResultOut`
- [x] `CORS` mis à jour : `allow_origins=[settings.frontend_url]` (plus de `"*"`)

---

### ✅ Phase 2 — Pipeline AI (TERMINÉ — 12 avril 2026)

**Objectif :** Génération automatique du contenu hebdomadaire.

#### 2.1 Scraper RSS (`agora/scraper/sources.py`) ✅
- [x] Fetch RSS Le Monde Politique (`https://www.lemonde.fr/politique/rss_full.xml`)
- [x] Fetch top pétitions Assemblée Nationale (`https://petitions.assemblee-nationale.fr/api/petitions?status=running&per_page=10`)
- [x] Retourne une liste de dicts : `[{title, url, source, published_at}]`
- [x] Gérer les timeouts et erreurs réseau (retourne une liste vide en cas d'échec, pas d'exception)

#### 2.2 Sélecteur de question IA (`agora/ai/question_selector.py`) ✅
- [x] Prend la liste de titres, appelle Claude Sonnet
- [x] Prompt : sélectionner le sujet le plus propice au débat civique factuel, non partisan
- [x] Contraintes dans le prompt : pas de parti/personnalité politique, question neutre, politique publique concrète
- [x] Retourne JSON : `{question, summary, source_url, topic_tags}`
- [x] Valider le format de sortie (JSONDecodeError → retry 1 fois)

#### 2.3 Constructeur de contexte IA (`agora/ai/context_builder.py`) ✅
- [x] 5 appels Claude séparés (fault-tolerant — valeur par défaut si échec) :
  - `build_historical_context(client, question)` → markdown
  - `build_scientific_context(client, question)` → markdown
  - `build_arguments_pour(client, question)` → liste de 3 strings
  - `build_arguments_contre(client, question)` → liste de 3 strings
  - `build_values_mapping(client, question)` → JSON `{grade: [6 scores]}`
- [x] 5 appels en parallèle via `ThreadPoolExecutor(max_workers=5)`

#### 2.4 Scheduler APScheduler (`agora/core/scheduler.py`) ✅
- [x] `BackgroundScheduler` configuré avec timezone `Europe/Paris`
- [x] Job hebdomadaire : chaque lundi à 7h00 (`misfire_grace_time=3600`)
- [x] Orchestration complète : scraper → question_selector → context_builder → quiz_generator → persist
- [x] Désactive le référendum précédent avant d'en créer un nouveau
- [x] En cas d'échec : rollback DB, log l'erreur, garde le référendum précédent actif
- [x] `run_pipeline_now()` pour déclenchement manuel (thread daemon)

#### 2.5 Mise à jour `agora/main.py` ✅
- [x] `@app.on_event("startup")` appelle `start_scheduler()`
- [x] `@app.on_event("shutdown")` appelle `stop_scheduler()`
- [x] `logging.basicConfig()` configuré au démarrage
- [x] `agora/ai/quiz_generator.py` : client Anthropic initialisé en lazy (plus d'échec au démarrage si clé absente)
- [x] `POST /admin/generate-referendum` : branche le vrai pipeline via `run_pipeline_now()`

---

### 🚧 Phase 3 — Frontend Next.js (EN COURS — 12 avril 2026)

**Objectif :** App partageable via URL, flow complet utilisable depuis un téléphone.

**Contexte technique :** Next.js 16.2.3 + React 19 + Tailwind v4 + Node.js 22.15.0 portable
(`$env:LOCALAPPDATA\node` — installé sans admin via zip portable)

#### 3.1 Setup ✅
- [x] `create-next-app@latest frontend` exécuté (Next.js 16, React 19, Tailwind v4, App Router)
- [x] Tailwind v4 configuré via CSS `@theme` dans `app/globals.css` (pas de tailwind.config.js en v4)
- [x] Polices Google Fonts (Lora + Inter) dans `app/layout.tsx` via `next/font/google`
- [x] `frontend/.env.local` : `NEXT_PUBLIC_API_URL=http://localhost:8000`
- [x] `frontend/lib/api.ts` : toutes les fonctions fetch typées (auth, referendum, quiz, arguments, votes, users)
- [x] `frontend/lib/constants.ts` : VALUES_LABELS, GRADE_ORDER, GRADE_COLORS, GRADE_SLUGS, etc.

#### 3.2 Store global (`frontend/lib/store.ts`) ✅
- [x] Zustand store : `token`, `referendum`, `quizPassed`, `voteGrade`, `fairplayRead`, `readArgumentIds`
- [x] `token` et `enlightenedScore` persistés en localStorage via `persist` middleware
- [ ] **À faire** : vérifier l'expiration du token JWT au chargement (décoder le payload, comparer `exp`)

#### 3.3 Composants partagés ✅
- [x] `components/AgoraHeader.tsx` — logo + titre + sous-titre
- [x] `components/StepDots.tsx` — indicateur de progression 1–5
- [x] `components/ValuesRadar.tsx` — Plotly.js via `dynamic(..., { ssr: false })`

#### 3.4 Pages ✅ (toutes créées — **à tester**)
- [x] `app/page.tsx` — redirect → /auth
- [x] `app/auth/page.tsx` — téléphone + OTP + JWT + mode dev (affiche le dev_code)
- [x] `app/referendum/page.tsx` — question + résumé + expanders historique/scientifique
- [x] `app/quiz/page.tsx` — 3 questions radio + validation (2/3 requis)
- [x] `app/arguments/page.tsx` — colonnes pour/contre + markAsRead + Fair-Play checkbox
- [x] `app/vote/page.tsx` — radio 5 mentions JM + castVote
- [x] `app/results/page.tsx` — score citoyen + barre JM + radar valeurs (onglets)
- [x] `app/profil/page.tsx` — radar agrégé + classement Schwartz + historique des votes

#### 3.5 PWA ✅
- [x] `public/manifest.json` créé (nom, thème #080808)
- [x] `viewport`, `themeColor` dans `layout.tsx`

#### ⚠️ À FAIRE POUR FINALISER PHASE 3

1. **Vérifier les dépendances npm** — zustand et plotly.js pas encore confirmés installés :
   ```powershell
   $env:PATH = "$env:LOCALAPPDATA\node;$env:PATH"
   cd frontend
   npm install zustand plotly.js react-plotly.js @types/react-plotly.js
   ```

2. **Build TypeScript** — vérifier qu'il n'y a pas d'erreurs de typage :
   ```powershell
   cd frontend && npx tsc --noEmit
   ```

3. **Lancer le dev server et tester le flow complet** :
   ```powershell
   # Terminal 1 : backend
   uvicorn agora.main:app --reload
   python scripts/seed_dev.py  # si pas déjà fait

   # Terminal 2 : frontend
   $env:PATH = "$env:LOCALAPPDATA\node;$env:PATH"
   cd frontend && npm run dev
   # Ouvrir http://localhost:3000
   ```

4. **Corrections connues possibles** :
   - `ValuesRadar` : les types Plotly peuvent nécessiter un cast (`as Plotly.Data[]`)
   - `results/page.tsx` : le `valuesScores` est `null` si le serveur ne renvoie pas le profil immédiatement — OK, l'onglet "profil" renvoie vers `/profil`
   - Ajouter `frontend/.gitignore` pour exclure `.env.local` et `node_modules`

5. **Optimisations UI** :
   - Ajouter un `loading.tsx` global (spinner amber)
   - Ajouter un `error.tsx` global

---

### 🔲 Phase 4 — Mise en production (À FAIRE)

**Objectif :** URL publique, partageable, premier vrai référendum.

#### 4.1 Supabase (base de données prod)
- [ ] Créer un projet Supabase (supabase.com — free tier)
- [ ] Récupérer la `DATABASE_URL` (Settings > Database > URI)
- [ ] Tester la connexion : `python -c "from agora.core.database import engine; engine.connect()"`

#### 4.2 Variables d'environnement
- [ ] Générer une vraie `SECRET_KEY` : `openssl rand -hex 32`
- [ ] Configurer Twilio (account SID, auth token, numéro) — compte Twilio Trial gratuit
- [ ] Configurer `ANTHROPIC_API_KEY`
- [ ] Créer `.env.production` (ne jamais committer)

#### 4.3 Railway (backend)
- [ ] Créer un compte Railway (railway.app)
- [ ] Connecter le dépôt GitHub
- [ ] Créer un `Dockerfile` à la racine :
  ```dockerfile
  FROM python:3.12-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY agora/ ./agora/
  COPY migrations/ ./migrations/
  COPY alembic.ini .
  CMD ["uvicorn", "agora.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```
- [ ] Configurer les variables d'environnement dans Railway
- [ ] Ajouter un "Start command" : `alembic upgrade head && uvicorn agora.main:app --host 0.0.0.0 --port $PORT`
- [ ] Mettre à jour `requirements.txt` : retirer `psycopg2-binary`, ajouter `psycopg2-binary==2.9.9` (sera compilé correctement sur Linux)

#### 4.4 Vercel (frontend)
- [ ] Connecter le sous-dossier `frontend/` au projet Vercel
- [ ] Configurer `NEXT_PUBLIC_API_URL` → URL Railway
- [ ] Vérifier HTTPS et CORS (`settings.frontend_url` = URL Vercel)

#### 4.5 Premier référendum réel
- [ ] `POST /admin/generate-referendum` — déclencher manuellement le pipeline AI
- [ ] Vérifier le contenu généré dans Swagger
- [ ] Tester le flow complet depuis un vrai téléphone

---

## Notes techniques importantes

### Clé de mapping valeurs (Schwartz)
Les 6 valeurs civiques : `Liberté · Égalité · Fraternité · Sécurité · Justice · Efficacité`

Le mapping est **spécifique à chaque référendum** et stocké dans `referendum.values_mapping` (JSON).
En dev, il est pré-rempli dans le seed. En prod, il est généré par `context_builder.build_values_mapping()`.

Format :
```json
{
  "Très favorable":   [2, 9, 9, 7, 7, 6],
  "Favorable":        [4, 7, 7, 6, 7, 8],
  "Neutre":           [5, 5, 5, 5, 5, 5],
  "Défavorable":      [8, 4, 4, 4, 6, 5],
  "Très défavorable": [10, 2, 2, 3, 5, 3]
}
```

### Jugement Majoritaire
La médiane est calculée dans `agora/api/votes/router.py::compute_majority_judgment_median()`.
L'enum `MajorityJudgmentGrade` utilise des slugs snake_case en base (`tres_favorable`) — les labels français ("Très favorable") sont dans `GRADE_LABELS`.

### Mode développement
- Twilio absent → `POST /auth/send-otp` retourne `{"dev_code": "123456"}` dans la réponse JSON
- Claude absent → le pipeline AI ne tourne pas, mais l'API démarre normalement
- Pas de migrations automatiques au démarrage (`Base.metadata.create_all` supprimé en Phase 2) — toujours passer par `alembic upgrade head`

### Commandes utiles
```bash
# Lancer l'API
uvicorn agora.main:app --reload

# Seed / reset
python scripts/seed_dev.py
python scripts/seed_dev.py --reset

# Migrations
python -m alembic revision --autogenerate -m "description"
python -m alembic upgrade head
python -m alembic downgrade -1

# Vérifier les tables SQLite
sqlite3 agora_dev.db ".tables"
sqlite3 agora_dev.db "SELECT id, question FROM referendums"
```

---

## Référence — POC Streamlit

Le POC (`poc/app.py`) est la **référence UI** pour le frontend Next.js. Il contient :
- La palette de couleurs complète (fond `#080808`, ambre `#c8860a`, crème `#ede0c8`)
- Les polices (Lora serif + Inter)
- Tous les écrans avec leur logique (quiz, JM stacked bar, radar Plotly, profil valeurs)
- Les données mock dans `poc/mock_data.py`

Ne pas modifier le POC — il sert de spec visuelle.

Pour le lancer : `cd poc && streamlit run app.py`
