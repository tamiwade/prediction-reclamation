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
    <div style="background:linear-gradient(135deg, #eef2ff 0%, #f5f3ff 100%);
                border:1px solid #e0e7ff; border-radius:18px; padding:32px 36px;
                margin-bottom:24px; text-align:center;
                box-shadow: 0 4px 16px -2px rgba(99, 102, 241, 0.08);">
        <div style="font-size:2.4rem; font-weight:800; color:#1e1b4b;
                    letter-spacing:-0.8px; margin-bottom:8px;">AutoAssure Analytics</div>
        <div style="font-size:1.05rem; color:#475569; font-weight:400; max-width:720px; margin:0 auto;">
            Plateforme interactive de Machine Learning pour l'évaluation et la prédiction des réclamations d'assurance automobile
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Assurés analysés", f"{n:,}", "Dataset complet")
    with c2:
        st.metric("Réclamations (Cible)", f"{n_claims:,}", f"{rate}% du total")
    with c3:
        st.metric("Variables", f"{len(df.columns)}", f"dont {n_preds} prédicteurs")
    with c4:
        st.metric("Valeurs manquantes", f"{missing:,}", "Sur l'ensemble des colonnes")

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="color:#0f172a; font-size:1.25rem; font-weight:700; margin-bottom:14px; letter-spacing:-0.3px;">
    Contexte Stratégique & Objectifs Métier
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0;
                    border-radius:16px; padding:24px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
            <p style="color:#334155; line-height:1.8; font-size:0.95rem; margin-bottom:14px;">
            Ce système d'aide à la décision vise à évaluer et prédire avec précision la survenance d'une réclamation d'assurance 
            (<b style="color:#dc2626;">{target_col} = 1</b>) par rapport aux contrats sans sinistre (<b style="color:#059669;">{target_col} = 0</b>).
            </p>
            <p style="color:#334155; line-height:1.8; font-size:0.95rem; margin-bottom:14px;">
            Le portefeuille analysé regroupe <b style="color:#0f172a;">{n:,} assurés</b> caractérisés par des attributs 
            sociodémographiques (tranche d'âge, revenu, éducation), des facteurs comportementaux (infractions, antécédents d'accidents) 
            et des caractéristiques techniques du véhicule (catégorie, ancienneté, kilométrage).
            </p>
            <p style="color:#334155; line-height:1.8; font-size:0.95rem; margin-bottom:0;">
            Quatre familles majeures d'algorithmes de <b>Machine Learning</b> sont benchmarkées : 
            <b style="color:#4f46e5;">Random Forest</b>, 
            <b style="color:#7c3aed;">XGBoost</b>, 
            <b style="color:#2563eb;">Régression Logistique</b> et 
            <b style="color:#0891b2;">Arbre de Décision</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background:#ffffff; border:1px solid #e2e8f0;
                    border-radius:16px; padding:24px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
            <p style="color:#4338ca; font-size:0.78rem; font-weight:700;
                      text-transform:uppercase; letter-spacing:0.08em; margin-bottom:16px;">
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
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;
                        padding:12px 14px; background:#f8fafc;
                        border-radius:10px; border:1px solid #e2e8f0;">
                <div style="width:10px; height:10px; border-radius:50%;
                            background:#4f46e5; flex-shrink:0;"></div>
                <div>
                    <div style="color:#0f172a; font-weight:600; font-size:0.88rem;">{p}</div>
                    <div style="color:#64748b; font-size:0.78rem;">{d}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
