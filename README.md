# 🚗 Prédiction de Réclamations Automobiles

> Plateforme analytique interactive pour l'analyse et la prédiction des sinistres automobiles, basée sur des modèles de **Machine Learning**.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/tamiwade/prediction-reclamation)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/Licence-MIT-green.svg)

---

## 🎯 Objectif

Ce projet vise à aider les actuaires et analystes en assurance automobile à :
- **Explorer** la qualité et la structure des données de sinistres
- **Visualiser** les tendances géographiques et statistiques des réclamations
- **Prédire** la probabilité qu'un assuré soumette une réclamation
- **Comparer** les performances de plusieurs algorithmes de Machine Learning
- **Exporter** des rapports PDF complets pour la prise de décision

---

## 📊 Fonctionnalités

| Module | Description |
|--------|-------------|
| 🏠 **Accueil** | Présentation du projet, chargement du fichier Excel/CSV |
| 🔍 **Exploration** | Audit qualité des données, statistiques descriptives, détection de valeurs manquantes |
| 📈 **Visualisation** | Dashboard analytique : distributions, corrélations, carte géographique des sinistres |
| 🤖 **Modélisation** | Entraînement de modèles ML (Régression Logistique, Random Forest, XGBoost, etc.) |
| ⚖️ **Comparaison** | Benchmark des modèles : AUC, F1-Score, précision, rappel, matrices de confusion |
| 📄 **Export PDF** | Génération d'un rapport structuré avec métriques et recommandations actuarielles |

---

## 🛠️ Technologies utilisées

| Catégorie | Librairies |
|-----------|------------|
| Interface web | `Streamlit` |
| Machine Learning | `Scikit-learn`, `XGBoost` |
| Traitement des données | `Pandas`, `NumPy` |
| Visualisation | `Plotly` |
| Cartographie | `GeoPandas` |
| Export PDF | `ReportLab` |
| Fichiers Excel | `Openpyxl` |

---

## 🚀 Lancement en local

```bash
# 1. Cloner le dépôt
git clone https://github.com/tamiwade/prediction-reclamation.git
cd prediction-reclamation

# 2. Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
streamlit run app.py
```

---

## 📁 Structure du projet

```
prediction-reclamation/
├── app.py                        # Point d'entrée Streamlit
├── utils_export.py               # Génération de rapports PDF (ReportLab)
├── requirements.txt              # Dépendances Python
├── Car_Insurance_Claim-2.csv     # Jeu de données d'exemple
├── departements-france.geojson   # Données géographiques des départements
├── .streamlit/
│   └── config.toml               # Configuration du serveur Streamlit
└── pages_app/
    ├── accueil.py                # Page d'accueil et chargement données
    ├── exploration.py            # Audit et exploration des données
    ├── statistiques.py           # Visualisations et dashboard
    ├── modelisation.py           # Entraînement et évaluation ML
    └── comparaison.py            # Comparaison des algorithmes
```

---

## 📂 Format des données

L'application accepte les fichiers **CSV** et **Excel (.xlsx)** contenant des données d'assurés automobiles avec des variables telles que :
- Informations démographiques (âge, genre, région)
- Caractéristiques du véhicule (ancienneté, valeur)
- Historique de conduite (accidents, permis)
- Variable cible : `OUTCOME` (1 = réclamation, 0 = pas de réclamation)

---

## 👤 Auteur

Développé par **tamiwade** — Analyse prédictive des sinistres automobiles

---

*Propulsé par Streamlit & Python 🐍*
