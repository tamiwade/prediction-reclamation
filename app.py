import streamlit as st
import pandas as pd
import importlib

st.set_page_config(
    page_title="AutoAssure · Prédiction Réclamation",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
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
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}

/* Boutons principaux */
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.88rem;
    padding: 8px 18px;
    transition: all 0.2s ease;
    width: 100%;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
    color: #ffffff !important;
    border: 1px solid #4338ca !important;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #4338ca 0%, #4f46e5 100%) !important;
    box-shadow: 0 6px 16px rgba(79, 70, 229, 0.3) !important;
    transform: translateY(-1px);
}
.stButton > button[kind="secondary"] {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #334155 !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #f1f5f9 !important;
    border-color: #94a3b8 !important;
    color: #0f172a !important;
}

/* Onglets */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #ffffff;
    border-radius: 12px;
    padding: 6px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
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

/* Indicateurs Métriques */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    padding: 16px 20px;
    border-radius: 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
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
hr { border-color: #e2e8f0 !important; }
.stMarkdown p, .stMarkdown li { color: #334155; line-height: 1.65; }
.stDataFrame { 
    background: #ffffff;
    border-radius: 12px; 
    overflow: hidden; 
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
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


# ── PAGE D'ACCUEIL / IMPORT (SI AUCUN FICHIER) ───────────────────────────────
def show_landing():
    st.markdown("""
    <div style="text-align:center; padding:50px 20px 30px 20px;">
        <div style="font-size:3.5rem; margin-bottom:14px;">🚗</div>
        <div style="font-size:2.8rem; font-weight:800; color:#1e1b4b;
                    letter-spacing:-1px; margin-bottom:10px;">
            AutoAssure Analytics
        </div>
        <div style="color:#64748b; font-size:1.1rem; max-width:650px; margin:0 auto 36px auto; line-height:1.7;">
            Plateforme décisionnelle d'évaluation et de prédiction des réclamations d'assurance automobile par <b>Machine Learning</b>.<br>
            <span style="color:#4338ca; font-weight:600;">Importez votre portefeuille pour démarrer l'analyse.</span>
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
        <div style="text-align:center; margin:16px 0 14px 0; color:#94a3b8; font-size:0.85rem; font-weight:500;">
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
        <div style="margin-top:40px; display:grid; grid-template-columns:1fr 1fr; gap:14px;">
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

    # 1. Barre d'en-tête supérieure
    col_brand, col_info, col_actions = st.columns([3, 4, 3])
    with col_brand:
        st.markdown("""
        <div style="display:flex; align-items:center; gap:12px; padding:6px 0;">
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

    st.markdown("<hr style='margin:16px 0 24px 0; border:none; border-top:1px solid #e2e8f0;'>", unsafe_allow_html=True)


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
