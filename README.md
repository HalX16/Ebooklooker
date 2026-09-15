# 📚 Ebooklooker

Un bot Telegram pour rechercher et télécharger gratuitement des livres au format EPUB et PDF.

## ✨ Fonctionnalités

- 🔍 Recherche multi-sources : Internet Archive, Project Gutenberg, Open Library
- 📥 Téléchargement direct : EPUB et PDF envoyés directement dans Telegram
- 🌍 Multilingue : Français, Anglais, Arabe
- 💝 Dons via Telegram Stars (5 / 20 / 50 / 100)
- 🔗 Partage facile du bot

## 🚀 Installation

### Prérequis

- Python 3.9 ou plus récent
- Un compte Telegram
- Un bot créé via @BotFather

### Étapes

1. Cloner le dépôt

   git clone https://github.com/HalX16/Ebooklooker.git
   cd Ebooklooker

2. Créer un environnement virtuel

   python -m venv venv
   venv\Scripts\activate        (Windows)
   source venv/bin/activate     (Mac/Linux)

3. Installer les dépendances

   pip install -r requirements.txt

4. Configurer le token

   Crée un fichier .env à la racine avec :

   TELEGRAM_TOKEN=ton_token_ici

5. Lancer le bot

   python main.py

## 📖 Utilisation

- /start : Démarrer le bot et choisir la langue
- /help : Aide
- /lang : Changer de langue
- /search <mot-clé> : Rechercher un livre (ou écris directement le titre)
- /don : Soutenir le projet
- /share : Partager le bot

## 🏗️ Structure

Ebooklooker/
├── main.py              Point d'entrée
├── requirements.txt     Dépendances
├── .env                 Token (non versionné)
├── bot/                 Logique du bot
├── apis/                Clients API externes
├── locales/             Traductions
└── data/                Base SQLite (non versionné)

## 📜 Licence

MIT — voir le fichier LICENSE.

## ⚠️ Considérations légales

Ce bot privilégie les sources légales (domaine public, licences libres) :

- Project Gutenberg : livres du domaine public
- Internet Archive : contenus variés, majoritairement libres
- Open Library : métadonnées et prêts numériques

L'utilisateur est responsable du respect des lois de son pays.