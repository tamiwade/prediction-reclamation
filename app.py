import streamlit as st
import pandas as pd
import importlib

st.set_page_config(
    page_title="AutoAssure · Prédiction Réclamation",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { 
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #0f172a;
}
.stApp {
    background-color: #f8fafc;
    color: #0f172a;
    min-height: 100vh;
}

/* ── Barre Latérale Élégante (Fond Blanc / Gris très clair) ── */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
    box-shadow: 2px 0 12px rgba(0, 0, 0, 0.02);
}
[data-testid="stSidebar"] hr {
    margin: 14px 0 !important;
    border-color: #f1f5f9 !important;
}

/* ── Boutons d'Action & Navigation ── */
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.86rem;
    padding: 8px 16px;
    transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
    width: 100%;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
    color: #ffffff !important;
    border: 1px solid #4338ca !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.22) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #4338ca 0%, #4f46e5 100%) !important;
    box-shadow: 0 6px 18px rgba(79, 70, 229, 0.32) !important;
    transform: translateY(-1.5px);
}
.stButton > button[kind="secondary"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    color: #334155 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #f8fafc !important;
    border-color: #cbd5e1 !important;
    color: #0f172a !important;
    transform: translateY(-1px);
    box-shadow: 0 3px 8px rgba(0,0,0,0.06) !important;
}

/* ── Onglets Modernes ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #ffffff;
    border-radius: 12px;
    padding: 5px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: #64748b !important;
    font-weight: 600;
    font-size: 0.88rem;
    border: none;
    padding: 8px 18px;
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: #eef2ff !important;
    color: #4338ca !important;
    font-weight: 700;
    border: 1px solid #c7d2fe !important;
}

/* ── Cartes d'Indicateurs Métriques ── */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    padding: 16px 20px;
    border-radius: 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.06);
    border-color: #cbd5e1;
}
[data-testid="stMetricValue"] {
    color: #0f172a !important;
    font-weight: 800;
    font-size: 1.65rem !important;
}
[data-testid="stMetricLabel"] {
    color: #64748b !important;
    font-size: 0.82rem !important;
    font-weight: 600;
}

/* ── Expanders Élégants dans la barre latérale ── */
[data-testid="stSidebar"] .streamlit-expanderHeader {
    background-color: #f8fafc !important;
    border-radius: 8px !important;
    font-size: 0.86rem !important;
    font-weight: 700 !important;
    color: #1e293b !important;
    border: 1px solid #e2e8f0 !important;
    padding: 8px 12px !important;
}
[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
    background-color: #f1f5f9 !important;
    border-color: #cbd5e1 !important;
}
[data-testid="stSidebar"] .streamlit-expanderContent {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-top: none !important;
    border-bottom-left-radius: 8px !important;
    border-bottom-right-radius: 8px !important;
    padding: 12px !important;
    font-size: 0.82rem !important;
    line-height: 1.6 !important;
}

/* ── Tableaux & Dataframes ── */
.stDataFrame { 
    background: #ffffff;
    border-radius: 12px; 
    overflow: hidden; 
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

hr { border-color: #e2e8f0 !important; }
.stMarkdown p, .stMarkdown li { color: #334155; line-height: 1.65; }
::selection { background: #c7d2fe; color: #1e1b4b; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "accueil"
if "df" not in st.session_state:
    st.session_state.df = None
if "data_source" not in st.session_state:
    st.session_state.data_source = None


# ── BARRE LATÉRALE INFORMATIVE & PÉDAGOGIQUE ──────────────────────────────────
def show_sidebar_info():
    with st.sidebar:
        # En-tête de la barre latérale
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px; padding-bottom:12px; border-bottom:1px solid #f1f5f9;">
            <div style="font-size:1.6rem; background:#eef2ff; border:1px solid #c7d2fe; border-radius:10px; width:40px; height:40px; display:flex; align-items:center; justify-content:center;">🚗</div>
            <div>
                <div style="font-size:1.05rem; font-weight:800; color:#0f172a; letter-spacing:-0.3px;">AutoAssure</div>
                <div style="font-size:0.72rem; color:#6366f1; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;">Guide & Aide Décisionnelle</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        df = st.session_state.df
        if df is not None:
            outcome_col = "OUTCOME" if "OUTCOME" in df.columns else df.columns[-1]
            n_claims = int(df[outcome_col].sum()) if pd.api.types.is_numeric_dtype(df[outcome_col]) else 0
            rate = round((n_claims / max(len(df), 1)) * 100, 1)

            st.markdown(f"""
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:10px 12px; margin-bottom:16px;">
                <div style="color:#64748b; font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em;">Portefeuille Actif</div>
                <div style="color:#0f172a; font-weight:700; font-size:0.82rem; margin-top:2px;">{st.session_state.data_source}</div>
                <div style="display:flex; justify-content:space-between; margin-top:6px; font-size:0.75rem; color:#475569; border-top:1px solid #edf2f7; padding-top:5px;">
                    <span>Assurés: <b>{len(df):,}</b></span>
                    <span>Sinistralité: <b style="color:#dc2626;">{rate}%</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── 1. Guide d'utilisation ──
        with st.expander("🧭 Mode d'Emploi & Workflow", expanded=False):
            st.markdown("""
            **Comment exploiter la plateforme :**
            
            1. **🏠 Accueil & Synthèse**  
               Vue macroscopique du portefeuille, objectifs stratégiques et volumétrie globale.
            2. **🔍 Exploration des Données**  
               Audit de complétude (valeurs manquantes), cardinalités et statistiques descriptives univariées.
            3. **📊 Dashboard Analytique**  
               Analyses croisées avec la variable cible (`OUTCOME`), matrice de corrélation de Pearson et cartographie des départements.
            4. **⚙️ Modélisation Machine Learning**  
               Entraînement pas-à-pas, matrice de confusion, courbe ROC, importance des facteurs et simulateur individuel de risque.
            5. **⚖️ Benchmark des Modèles**  
               Comparatif côte-à-côte (AUC, F1, Précision, Rappel), radar décisionnel et sélection du modèle champion.
            """)

        # ── 2. Comparatif pédagogique des modèles ──
        with st.expander("🤖 Différence entre les Modèles ML", expanded=True):
            st.markdown("""
            <div style="margin-bottom:10px;">
                <b style="color:#4f46e5;">🌲 Random Forest (Forêt Aléatoire)</b><br>
                <span style="color:#475569; font-size:0.78rem;">
                <b>Principe :</b> Agrégation (bagging) de centaines d'arbres de décision décorrélés.<br>
                <b>Points forts :</b> Très robuste face au surapprentissage, gère naturellement les relations non-linéaires complexes.<br>
                <b>Idéal pour :</b> Modèle de référence équilibré et stable.
                </span>
            </div>
            
            <div style="margin-bottom:10px; border-top:1px solid #f1f5f9; padding-top:8px;">
                <b style="color:#7c3aed;">⚡ XGBoost (Gradient Boosting)</b><br>
                <span style="color:#475569; font-size:0.78rem;">
                <b>Principe :</b> Construction séquentielle d'arbres corrigeant chacun les erreurs résiduelles des précédents.<br>
                <b>Points forts :</b> Pouvoir de discrimination maximal, rapidité de convergence.<br>
                <b>Idéal pour :</b> Scoring actuariel fin où chaque dixième de point d'AUC compte.
                </span>
            </div>
            
            <div style="margin-bottom:10px; border-top:1px solid #f1f5f9; padding-top:8px;">
                <b style="color:#2563eb;">📈 Régression Logistique</b><br>
                <span style="color:#475569; font-size:0.78rem;">
                <b>Principe :</b> Modélisation linéaire probabiliste de la log-odds de sinistre.<br>
                <b>Points forts :</b> Interprétabilité totale grâce aux coefficients (odds ratios), très rapide à déployer.<br>
                <b>Idéal pour :</b> Grilles tarifaires réglementées et transparence actuarielle.
                </span>
            </div>
            
            <div style="border-top:1px solid #f1f5f9; padding-top:8px;">
                <b style="color:#0891b2;">🌳 Arbre de Décision (CART)</b><br>
                <span style="color:#475569; font-size:0.78rem;">
                <b>Principe :</b> Segmentation séquentielle de l'échantillon par seuils optimaux.<br>
                <b>Points forts :</b> Règles d'arbitrage visuelles et compréhensibles par les souscripteurs.<br>
                <b>Idéal pour :</b> Règles d'acceptation automatique de dossiers.
                </span>
            </div>
            """, unsafe_allow_html=True)

        # ── 3. Lexique des Métriques Actuarielles ──
        with st.expander("🎯 Lexique des Métriques Actuarielles", expanded=False):
            st.markdown("""
            - **AUC-ROC (0.5 à 1.0) :**  
              Probabilité que le modèle classe un assuré sinistré au-dessus d'un non-sinistré. *Objectif > 0.85.*
            - **Rappel / Recall (Exhaustivité) :**  
              Pourcentage des vrais sinistres détectés par le modèle. Essentiel pour éviter les sinistres non-provisionnés.
            - **Précision (Fiabilité) :**  
              Pourcentage de sinistres réels parmi ceux prédits à risque. Évite de pénaliser injustement de bons conducteurs.
            - **F1-Score :**  
              Moyenne harmonique entre Précision et Rappel. Mesure le compromis optimal.
            - **Accuracy :**  
              Taux global de bonnes prédictions sur l'ensemble de la population.
            """)

        # ── 4. Cadre Réglementaire & Sécurité ──
        with st.expander("🛡️ Gouvernance & Solvabilité II", expanded=False):
            st.markdown("""
            - **Auditabilité :** Tous les calculs reposent sur des graines aléatoires reproductibles (*Random State*).
            - **Exportabilité :** Export direct des modèles sérialisés (`.joblib`), métriques (`.xlsx`) et synthèses (`.pdf`).
            - **Drift temporel :** Recommandation de ré-étalonnage semestriel des poids d'arbres.
            """)

        st.markdown("""
        <div style="margin-top:24px; padding-top:14px; border-top:1px solid #f1f5f9; text-align:center; font-size:0.72rem; color:#94a3b8;">
            AutoAssure Analytics · Modélisation Prédictive<br>
            Version 2.4 Pro · Fond Blanc Light
        </div>
        """, unsafe_allow_html=True)


# ── PAGE D'ACCUEIL / IMPORT (SI AUCUN FICHIER) ───────────────────────────────
def show_landing():
    show_sidebar_info()

    st.markdown("""
    <div style="text-align:center; padding:45px 20px 25px 20px;">
        <div style="font-size:3.5rem; margin-bottom:12px;">🚗</div>
        <div style="font-size:2.8rem; font-weight:800; color:#1e1b4b;
                    letter-spacing:-1px; margin-bottom:8px;">
            AutoAssure Analytics
        </div>
        <div style="color:#64748b; font-size:1.1rem; max-width:650px; margin:0 auto 32px auto; line-height:1.7;">
            Plateforme décisionnelle d'évaluation et de prédiction des réclamations d'assurance automobile par <b>Machine Learning</b>.<br>
            <span style="color:#4f46e5; font-weight:600;">Importez votre portefeuille pour démarrer l'analyse.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown("""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:20px;
                    padding:32px 30px; box-shadow:0 10px 30px rgba(0,0,0,0.05); margin-bottom:20px;">
            <div style="color:#0f172a; font-size:1.15rem; font-weight:700; margin-bottom:6px; text-align:center;">
                📂 Importer une base de données
            </div>
            <div style="color:#64748b; font-size:0.85rem; text-align:center; margin-bottom:20px;">
                Formats acceptés : <b style="color:#4f46e5">.xlsx</b> · <b style="color:#4f46e5">.xls</b> · <b style="color:#4f46e5">.csv</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Glissez-déposez votre fichier ici ou cliquez pour parcourir",
            type=["xlsx", "xls", "csv"],
            key="file_uploader",
        )

        if uploaded_file is not None:
            try:
                with st.spinner("Chargement et audit initial des données..."):
                    if uploaded_file.name.endswith(".csv"):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                st.session_state.df = df
                st.session_state.data_source = f"📄 {uploaded_file.name}"
                st.session_state.page = "accueil"
                st.success(f"✅ **{uploaded_file.name}** chargé avec succès : {len(df):,} lignes × {len(df.columns)} colonnes")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur lors du chargement : {e}")

        st.markdown("""
        <div style="text-align:center; margin:14px 0 12px 0; color:#94a3b8; font-size:0.85rem; font-weight:500;">
            ── ou ──
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Charger le jeu de données de référence (Démo)", key="use_demo", type="secondary"):
            try:
                df = pd.read_csv("Car_Insurance_Claim-2.csv")
                st.session_state.df = df
                st.session_state.data_source = "📊 Jeu de référence (Car_Insurance_Claim-2.csv)"
                st.session_state.page = "accueil"
                st.rerun()
            except FileNotFoundError:
                st.error("Le fichier de démonstration est introuvable sur le serveur.")

        st.markdown("""
        <div style="margin-top:36px; display:grid; grid-template-columns:1fr 1fr; gap:14px;">
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:18px; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.02);">
                <div style="font-size:1.8rem; margin-bottom:6px;">📊</div>
                <div style="color:#0f172a; font-weight:700; font-size:0.9rem;">Tableau de Bord Analytique</div>
                <div style="color:#64748b; font-size:0.78rem; margin-top:3px;">Explorations univariées & bivariées</div>
            </div>
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:18px; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.02);">
                <div style="font-size:1.8rem; margin-bottom:6px;">🤖</div>
                <div style="color:#0f172a; font-weight:700; font-size:0.9rem;">Machine Learning</div>
                <div style="color:#64748b; font-size:0.78rem; margin-top:3px;">Random Forest, XGBoost, LR, DT</div>
            </div>
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:18px; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.02);">
                <div style="font-size:1.8rem; margin-bottom:6px;">🗺️</div>
                <div style="color:#0f172a; font-weight:700; font-size:0.9rem;">Répartition Territoriale</div>
                <div style="color:#64748b; font-size:0.78rem; margin-top:3px;">Analyse cartographique par département</div>
            </div>
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:18px; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.02);">
                <div style="font-size:1.8rem; margin-bottom:6px;">📄</div>
                <div style="color:#0f172a; font-weight:700; font-size:0.9rem;">Rapport d'Audit PDF</div>
                <div style="color:#64748b; font-size:0.78rem; margin-top:3px;">Génération complète pour actuaires</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── EN-TÊTE SUPÉRIEUR & NAVIGATION HORIZONTALE EN HAUT ────────────────────────
def show_top_header():
    df = st.session_state.df
    outcome_col = "OUTCOME" if "OUTCOME" in df.columns else df.columns[-1]
    n_claims = int(df[outcome_col].sum()) if pd.api.types.is_numeric_dtype(df[outcome_col]) else 0
    rate = round((n_claims / max(len(df), 1)) * 100, 1)

    # Affichage de la barre latérale informative
    show_sidebar_info()

    # 1. Barre d'en-tête supérieure
    col_brand, col_info, col_actions = st.columns([3, 4, 3])
    with col_brand:
        st.markdown("""
        <div style="display:flex; align-items:center; gap:12px; padding:4px 0;">
            <div style="font-size:2rem; background:#eef2ff; border:1px solid #c7d2fe; border-radius:12px; width:48px; height:48px; display:flex; align-items:center; justify-content:center;">🚗</div>
            <div>
                <div style="font-size:1.25rem; font-weight:800; color:#1e1b4b; letter-spacing:-0.5px;">AutoAssure Analytics</div>
                <div style="font-size:0.75rem; color:#64748b; font-weight:500;">Prise de Décision & Modélisation Machine Learning</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_info:
        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:8px 16px; display:inline-block; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
            <div style="font-size:0.75rem; color:#475569;"><b>Source :</b> {st.session_state.data_source}</div>
            <div style="font-size:0.72rem; color:#64748b; margin-top:2px;">
                <b style="color:#4f46e5;">{len(df):,}</b> assurés · <b style="color:#4f46e5;">{len(df.columns)}</b> variables · Sinistralité : <b style="color:#dc2626;">{rate}%</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_actions:
        btn_c1, btn_c2 = st.columns([1, 1])
        with btn_c1:
            if st.button("📂 Autre fichier", key="nav_top_reload", type="secondary", use_container_width=True):
                st.session_state.df = None
                st.session_state.data_source = None
                st.rerun()
        with btn_c2:
            from utils_export import generate_pdf_report
            pdf_global = generate_pdf_report(
                title="Rapport d'Audit Décisionnel & Machine Learning",
                dataset_kpis={"total": len(df), "claims": n_claims, "rate": rate}
            )
            st.download_button(
                label="📄 Rapport PDF",
                data=pdf_global,
                file_name="Rapport_Audit_Machine_Learning_AutoAssure.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # 2. Navigation Horizontale en Haut
    pages_list = [
        ("🏠 Accueil & Synthèse", "accueil"),
        ("🔍 Exploration des Données", "exploration"),
        ("📊 Dashboard Analytique", "stats"),
        ("⚙️ Modélisation Machine Learning", "modelisation"),
        ("⚖️ Benchmark des Modèles", "comparaison"),
    ]

    current_page = st.session_state.page
    nav_cols = st.columns(len(pages_list))

    for idx, (label, key) in enumerate(pages_list):
        with nav_cols[idx]:
            is_active = (current_page == key)
            clicked = st.button(
                label,
                key=f"nav_top_{key}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            )
            if clicked:
                st.session_state.page = key
                st.rerun()

    st.markdown("<hr style='margin:14px 0 22px 0; border:none; border-top:1px solid #e2e8f0;'>", unsafe_allow_html=True)


# ── ROUTAGE PRINCIPAL ─────────────────────────────────────────────────────────
if st.session_state.df is None:
    show_landing()
else:
    show_top_header()
    page = st.session_state.page

    if page == "accueil":
        from pages_app import accueil
        importlib.reload(accueil)
        accueil.show()
    elif page == "exploration":
        from pages_app import exploration
        importlib.reload(exploration)
        exploration.show()
    elif page == "stats":
        from pages_app import statistiques
        importlib.reload(statistiques)
        statistiques.show()
    elif page == "modelisation":
        from pages_app import modelisation
        importlib.reload(modelisation)
        modelisation.show()
    elif page == "comparaison":
        from pages_app import comparaison
        importlib.reload(comparaison)
        comparaison.show()
    else:
        st.session_state.page = "accueil"
        from pages_app import accueil
        importlib.reload(accueil)
        accueil.show()
