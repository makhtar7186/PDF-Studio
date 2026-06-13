# PDF Studio

Suite complète d'outils PDF — 100 % local, aucun fichier envoyé sur un serveur.  
Interface web construite avec **Streamlit**, authentification via **Google OAuth 2.0**.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.27%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Fonctionnalités

| Onglet | Description |
|--------|-------------|
| 🔍 Aperçu | Métadonnées, dimensions, aperçu de toutes les pages |
| 🔗 Fusion | Fusionner plusieurs PDFs en un seul |
| 🗜️ Compression | 3 niveaux : légère / modérée / agressive |
| ✂️ Découpage | Par plages, toutes les N pages, ou page par page |
| 🗑️ Suppression | Supprimer des pages spécifiques |
| 📤 Extraction | Extraire un sous-ensemble de pages |
| 🔄 Rotation | Pivoter tout ou partie des pages |
| 🔀 Réordonnancement | Définir un ordre arbitraire de pages |
| 🔢 Numérotation | Ajouter des numéros de page (6 positions) |
| 📌 Insertion | Insérer un PDF dans un autre à une position donnée |
| ✂️ Rognage | Couper les bords (marges en %) |
| 🔒 Protection | Chiffrer par mot de passe |
| 💧 Filigrane | Texte en filigrane (opacité, angle, taille) |
| ✏️ Caviardage | Noircir des occurrences de texte de façon permanente |

---

## Structure du projet

```
pdf/
├── app.py                  # Point d'entrée — classe PDFStudioApp
├── auth/
│   ├── __init__.py
│   └── oauth.py            # GoogleOAuth : flux OAuth 2.0 complet
├── pdf_tools/
│   ├── __init__.py
│   ├── processor.py        # PDFProcessor : toutes les transformations PDF
│   └── viewer.py           # PDFViewer : aperçu interactif et grille de miniatures
├── ui/
│   ├── __init__.py
│   ├── components.py       # Composants réutilisables (file_card, stat_row…)
│   ├── styles.py           # CSS global + configuration de la page
│   └── tabs.py             # TabRenderer : rendu des 14 onglets
├── .env                    # Variables d'environnement (ne pas committer)
├── .gitignore
├── requirements.txt
└── README.md
```

### Architecture des classes

```
PDFStudioApp          ← orchestre l'ensemble
├── GoogleOAuth       ← gère le flux de connexion Google
├── PDFProcessor      ← opérations PDF sans état (merge, split, compress…)
├── PDFViewer         ← rendu visuel (Streamlit + PyMuPDF)
└── TabRenderer       ← UI des 14 onglets
      └── utilise → PDFProcessor + PDFViewer
```

`PDFProcessor` ne dépend pas de Streamlit — il est testable indépendamment.

---

## Installation

```bash
# Depuis le répertoire du projet
python -m venv pdfenv
pdfenv\Scripts\activate      # Windows
# source pdfenv/bin/activate  # macOS / Linux

pip install -r requirements.txt
```

---

## Configuration Google OAuth

1. Aller sur [console.cloud.google.com](https://console.cloud.google.com/)
2. **API & Services → Identifiants → Créer des identifiants → ID client OAuth 2.0**
3. Type d'application : **Application Web**
4. **Origines JavaScript autorisées** : `http://localhost:8502`
5. **URI de redirection autorisés** : `http://localhost:8502`
6. Copier le Client ID et le Secret

Renseigner le fichier `.env` à la racine du projet :

```bash
GOOGLE_CLIENT_ID     = "xxxxxx.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-xxxxxx"
REDIRECT_URI         = "http://localhost:8502"
```

---

## Lancer l'application

```bash
streamlit run app.py --server.port 8502
```

Ouvrir [http://localhost:8502](http://localhost:8502) dans le navigateur.

---

## Déploiement Streamlit Cloud

1. Pusher le code sur GitHub (`.env` est dans `.gitignore`)
2. Sur [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Dans **Advanced settings → Secrets**, ajouter :

```toml
GOOGLE_CLIENT_ID     = "xxxx.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-xxxx"
REDIRECT_URI         = "https://TON-APP.streamlit.app"
```

4. Ajouter l'URL Streamlit Cloud comme URI de redirection dans Google Cloud Console.

---

## Stack technique

| Bibliothèque | Rôle |
|---|---|
| `streamlit` | Interface web |
| `pypdf` | Lecture / écriture PDF |
| `PyMuPDF` (fitz) | Rendu des aperçus, caviardage |
| `reportlab` | Numérotation et filigrane |
| `python-dotenv` | Chargement du `.env` |
| `requests` | Appels HTTP OAuth |

---

## Sécurité

- Aucun fichier n'est transmis à un serveur externe — tout le traitement se fait en mémoire locale.
- L'authentification Google OAuth garantit que seuls les utilisateurs connectés accèdent à l'application.
- Le fichier `.env` est exclu du dépôt via `.gitignore`.
