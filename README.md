# 🚗 Prédiction de Réclamations Automobiles

> Application d'analyse et de prédiction des sinistres automobiles basée sur des modèles de Machine Learning.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

---

## 📋 Description

Cette application interactive permet aux actuaires et analystes d'explorer, visualiser et modéliser les données de réclamations d'assurance automobile. Elle intègre plusieurs modules :

- **Accueil** — Présentation du projet et de la méthodologie
- **Exploration des données** — Audit qualité, statistiques descriptives
- **Visualisation** — Dashboard géographique et analytique
- **Modélisation ML** — Entraînement et évaluation de modèles
- **Comparaison** — Benchmark des algorithmes

## 🛠️ Technologies

| Composant | Technologie |
|-----------|-------------|
| Interface | Streamlit |
| Machine Learning | Scikit-learn, XGBoost |
| Visualisation | Plotly |
| Géographie | GeoPandas |
| Export | ReportLab (PDF) |

## 🚀 Lancement local

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run app.py
```

## 📁 Structure

```
├── app.py                  # Point d'entrée principal
├── utils_export.py         # Génération de rapports PDF
├── requirements.txt        # Dépendances Python
├── pages_app/
│   ├── accueil.py
│   ├── exploration.py
│   ├── statistiques.py
│   ├── modelisation.py
│   └── comparaison.py
├── Car_Insurance_Claim-2.csv
└── departements-france.geojson
```

## 📊 Données

Le jeu de données contient des informations sur les assurés automobiles et leurs historiques de sinistres, utilisé pour entraîner et évaluer des modèles de classification binaire (réclamation ou non).

---

*Développé avec Streamlit & Python*
