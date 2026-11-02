import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data
def load_data():
    df = pd.read_csv("Car_Insurance_Claim-2.csv")
    return df

def show():
    df = st.session_state.get("df", None)
    if df is None:
        try:
            df = pd.read_csv("Car_Insurance_Claim-2.csv")
            st.session_state.df = df
        except Exception:
            st.error("Aucune donnée disponible. Veuillez charger un fichier.")
            return

    target_col = "OUTCOME" if "OUTCOME" in df.columns else df.columns[-1]
    n = len(df)
    n_claims = int(df[target_col].sum()) if pd.api.types.is_numeric_dtype(df[target_col]) else 0
    rate = round((n_claims / n) * 100, 1) if n > 0 else 0
    missing = int(df.isnull().sum().sum())
    n_preds = len(df.columns) - 1

    st.markdown("""
    <div style="background:linear-gradient(135deg, rgba(124, 58, 237, 0.24), rgba(168, 85, 247, 0.14));
                border:1px solid rgba(168, 85, 247, 0.35); border-radius:24px; padding:44px 48px;
                margin-bottom:32px; backdrop-filter:blur(16px); text-align:center;
                box-shadow: 0 12px 40px rgba(124, 58, 237, 0.22);">
        <div style="font-size:3.2rem; font-weight:800; background:linear-gradient(90deg, #c084fc, #e879f9, #f472b6);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
                    letter-spacing:-1px; margin-bottom:10px;">AutoAssure Analytics</div>
        <div style="font-size:1.15rem; color:#e9d5ff; font-weight:400; max-width:700px; margin:0 auto;">
            Plateforme interactive de Machine Learning pour l'évaluation et la prédiction des réclamations d'assurance automobile
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.metric("Assurés analysés", f"{n:,}", "Dataset complet")
    with c2:
        st.metric("Réclamations (Cible)", f"{n_claims:,}", f"{rate}% du total")
    with c3:
        st.metric("Variables", f"{len(df.columns)}", f"dont {n_preds} prédicteurs")
    with c4:
        st.metric("Valeurs manquantes", f"{missing:,}", "Sur l'ensemble des colonnes")

    st.markdown("---")
    st.markdown("""
    <div style="color:#fdf4ff;font-size:1.25rem;font-weight:700;margin-bottom:16px;letter-spacing:-0.3px;">
    Contexte Stratégique & Objectifs Métier
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3,2])
    with col1:
        st.markdown(f"""
        <div style="background:rgba(26,20,50,0.65);border:1px solid rgba(139,92,246,0.22);
                    border-radius:18px;padding:26px;box-shadow:0 8px 30px rgba(0,0,0,0.25);">
            <p style="color:#ddd6fe;line-height:1.8;font-size:0.95rem;">
            Ce système d'aide à la décision vise à évaluer et prédire avec précision la survenance d'une réclamation d'assurance 
            (<b style="color:#f472b6">{target_col} = 1</b>) par rapport aux contrats sans sinistre (<b style="color:#34d399">{target_col} = 0</b>).
            </p>
            <p style="color:#ddd6fe;line-height:1.8;font-size:0.95rem;">
            Le portefeuille analysé regroupe <b style="color:#fdf4ff">{n:,} assurés</b> caractérisés par des attributs 
            sociodémographiques (tranche d'âge, revenu, éducation), des facteurs comportementaux (infractions, antécédents d'accidents) 
            et des caractéristiques techniques du véhicule (catégorie, ancienneté, kilométrage).
            </p>
            <p style="color:#ddd6fe;line-height:1.8;font-size:0.95rem;">
            Quatre familles majeures d'algorithmes de <b>Machine Learning</b> sont benchmarkées : 
            <b style="color:#c084fc">Random Forest</b>, 
            <b style="color:#e879f9">XGBoost</b>, 
            <b style="color:#a78bfa">Régression Logistique</b> et 
            <b style="color:#f472b6">Arbre de Décision</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background:rgba(26,20,50,0.65);border:1px solid rgba(139,92,246,0.22);
                    border-radius:18px;padding:26px;box-shadow:0 8px 30px rgba(0,0,0,0.25);">
            <p style="color:#c084fc;font-size:0.78rem;font-weight:700;
                      text-transform:uppercase;letter-spacing:0.1em;margin-bottom:16px;">
              Architecture Fonctionnelle de la Plateforme
            </p>
        """, unsafe_allow_html=True)

        pages_info = [
            ("Exploration des Données", "Audit structurel, qualité des données & schéma des variables"),
            ("Dashboard Analytique", "Analyses univariées/bivariées & distribution territoriale"),
            ("Modélisation Machine Learning", "Entraînement des modèles & simulateur individuel de risque"),
            ("Benchmark des Modèles", "Comparatif multi-métriques, courbes ROC & radar décisionnel"),
        ]
        for p, d in pages_info:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;
                        padding:12px 16px;background:rgba(124,58,237,0.12);
                        border-radius:12px;border:1px solid rgba(168,85,247,0.22);">
                <div style="width:10px;height:10px;border-radius:50%;
                            background:linear-gradient(135deg,#c084fc,#f472b6);flex-shrink:0;box-shadow:0 0 10px rgba(192,132,252,0.6);"></div>
                <div>
                    <div style="color:#fdf4ff;font-weight:600;font-size:0.88rem;">{p}</div>
                    <div style="color:#c4b5fd;font-size:0.76rem;">{d}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

