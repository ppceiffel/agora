REFERENDUM = {
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
        "de 10 à 50€. L'obligation a été instaurée après que les élites craignaient que "
        "les classes populaires, nouvellement autorisées à voter, ne se déplacent pas.\n\n"
        "**Australie (depuis 1924)** : Après une chute de la participation à 47% en 1922, "
        "l'Australie a rendu le vote obligatoire. Le taux est depuis supérieur à 90%. "
        "L'amende est de 20 AUD (~12€) pour les abstentionnistes sans excuse valable.\n\n"
        "**France (1793)** : La Constitution montagnarde de 1793 prévoyait déjà une forme "
        "de vote obligatoire, jamais appliquée en raison de la Terreur."
    ),
    "scientific_context": (
        "**Arend Lijphart (1997)** : Dans *\"Unequal Participation: Democracy's Unresolved "
        "Dilemma\"*, il démontre que l'abstention est socialement sélective : les classes "
        "populaires, les jeunes et les moins diplômés votent moins, ce qui biaise "
        "structurellement les résultats électoraux vers les préférences des classes aisées.\n\n"
        "**Méta-analyse Birch (2009)** : Portant sur 19 pays avec vote obligatoire, elle "
        "conclut que l'obligation augmente la participation de 7 à 16 points de pourcentage "
        "en moyenne et réduit les inégalités de représentation.\n\n"
        "**Étude Jakee & Sun (2006)** : Nuance le consensus — dans les systèmes à vote "
        "obligatoire, le vote \"blanc\" ou \"nul\" augmente significativement, suggérant "
        "qu'une partie des nouveaux votants expriment leur réticence plutôt qu'un choix."
    ),
    "week": "Semaine du 31 mars au 6 avril 2025",
}

QUIZ = [
    {
        "id": "q1",
        "question": "Quel était le taux d'abstention aux élections législatives françaises de 2022 ?",
        "options": {"a": "32%", "b": "53,77%", "c": "41%"},
        "correct": "b",
    },
    {
        "id": "q2",
        "question": "Quel pays a instauré le vote obligatoire en premier parmi les suivants ?",
        "options": {"a": "Australie", "b": "France", "c": "Belgique"},
        "correct": "c",
    },
    {
        "id": "q3",
        "question": "Selon la méta-analyse de Birch (2009), de combien de points le vote obligatoire augmente-t-il la participation ?",
        "options": {"a": "2 à 5 points", "b": "7 à 16 points", "c": "20 à 30 points"},
        "correct": "b",
    },
]

ARGUMENTS = {
    "pour": [
        {
            "rank": 1,
            "text": "Le vote obligatoire corrige une inégalité structurelle : aujourd'hui, les classes populaires votent moins, ce qui biaise les politiques publiques en faveur des plus aisés. Rendre le vote obligatoire, c'est rendre sa voix à chaque citoyen.",
            "upvotes": 1842,
            "author": "Citoyen Éclairé ⭐⭐⭐",
        },
        {
            "rank": 2,
            "text": "L'expérience australienne le prouve : en 1922, le taux de participation était de 47%. Après l'instauration du vote obligatoire, il n'est jamais redescendu sous 90%. La contrainte a créé une habitude démocratique.",
            "upvotes": 1204,
            "author": "Citoyen Éclairé ⭐⭐",
        },
        {
            "rank": 3,
            "text": "Le vote blanc devrait être comptabilisé et reconnu. Avec le vote obligatoire couplé à une vraie reconnaissance du vote blanc, on forcerait les partis à écouter les abstentionnistes plutôt que de les ignorer.",
            "upvotes": 987,
            "author": "Citoyen Éclairé ⭐",
        },
    ],
    "contre": [
        {
            "rank": 1,
            "text": "Forcer quelqu'un à voter, c'est une contradiction dans les termes. La liberté inclut le droit de ne pas participer. Un vote sous contrainte n'est pas un acte civique, c'est une formalité administrative.",
            "upvotes": 1677,
            "author": "Citoyen Éclairé ⭐⭐⭐",
        },
        {
            "rank": 2,
            "text": "Le problème n'est pas l'abstention, c'est la défiance. Forcer les gens à voter sans s'attaquer aux causes profondes — corruption perçue, déconnexion des élus — revient à traiter le symptôme en ignorant la maladie.",
            "upvotes": 1389,
            "author": "Citoyen Éclairé ⭐⭐",
        },
        {
            "rank": 3,
            "text": "Les études montrent qu'avec le vote obligatoire, le vote nul et blanc explose. On n'obtient pas une démocratie plus représentative, juste des urnes plus remplies de bulletins qui ne disent rien.",
            "upvotes": 762,
            "author": "Citoyen Éclairé ⭐",
        },
    ],
}

PAST_VOTES = [
    {
        "question": "Faut-il abaisser l'âge du droit de vote à 16 ans ?",
        "week": "Semaine du 17 au 23 mars 2025",
        "grade": "Favorable",
    },
    {
        "question": "Faut-il instaurer un revenu universel de base en France ?",
        "week": "Semaine du 24 au 30 mars 2025",
        "grade": "Très favorable",
    },
]

VOTE_RESULTS = {
    "Très favorable": 18,
    "Favorable": 24,
    "Neutre": 21,
    "Défavorable": 22,
    "Très défavorable": 15,
    "total": 4821,
    "median": "Neutre",
}
