import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="AutoAssure · Prediction Reclamation",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp {
    background-color: #0c0a17;
    background-image:
        radial-gradient(at 0% 0%, rgba(124, 58, 237, 0.28) 0px, transparent 55%),
        radial-gradient(at 100% 30%, rgba(168, 85, 247, 0.18) 0px, transparent 50%),
        radial-gradient(at 50% 100%, rgba(192, 132, 252, 0.12) 0px, transparent 60%);
    min-height: 100vh;
}
[data-testid="stSidebar"] {
    background-color: #120e24 !important;
    border-right: 1px solid rgba(139, 92, 246, 0.18) !important;
    backdrop-filter: blur(20px);
}
.stButton > button {
    background: linear-gradient(135deg, #7c3aed 0%, #9333ea 100%);
    color: #ffffff !important;
    border: 1px solid rgba(192, 132, 252, 0.3);
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.88rem;
    padding: 9px 18px;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    width: 100%;
    box-shadow: 0 4px 14px rgba(124, 58, 237, 0.25);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
    border-color: rgba(216, 180, 254, 0.5);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(139, 92, 246, 0.45);
}
button[kind="secondary"] {
    background: rgba(26, 20, 50, 0.7) !important;
    border: 1px solid rgba(139, 92, 246, 0.22) !important;
    color: #d8b4fe !important;
}
button[kind="secondary"]:hover {
    background: rgba(124, 58, 237, 0.25) !important;
    border-color: rgba(168, 85, 247, 0.45) !important;
    color: #ffffff !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(18, 14, 36, 0.7);
    border-radius: 12px;
    padding: 6px;
    border: 1px solid rgba(139, 92, 246, 0.18);
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: #a78bfa !important;
    font-weight: 500;
    font-size: 0.88rem;
    border: none;
    padding: 8px 18px;
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.35), rgba(168, 85, 247, 0.25)) !important;
    color: #f5d0fe !important;
    font-weight: 600;
    border: 1px solid rgba(168, 85, 247, 0.4) !important;
    box-shadow: 0 4px 14px rgba(124, 58, 237, 0.25);
}
[data-testid="stMetricValue"] {
    color: #fdf4ff !important;
    font-weight: 800;
    font-size: 1.65rem !important;
}
[data-testid="stMetricLabel"] {
    color: #c4b5fd !important;
    font-size: 0.82rem !important;
    font-weight: 500;
}
hr { border-color: rgba(139, 92, 246, 0.12) !important; }
.stMarkdown p, .stMarkdown li { color: #ddd6fe; line-height: 1.65; }
.stDataFrame { border-radius: 12px; overflow: hidden; border: 1px solid rgba(139, 92, 246, 0.18); }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-thumb { background: rgba(139, 92, 246, 0.4); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "accueil"
if "df" not in st.session_state:
    st.session_state.df = None
if "data_source" not in st.session_state:
    st.session_state.data_source = None


# ── LANDING PAGE ──────────────────────────────────────────────────────────────
def show_landing():
    st.markdown("""
    <div style="text-align:center; padding:60px 20px 40px 20px;">
        <div style="font-size:4rem; margin-bottom:20px; filter:drop-shadow(0 0 30px rgba(168,85,247,0.7));">🚗</div>
        <div style="font-size:3rem; font-weight:800;
                    background:linear-gradient(90deg, #c084fc, #e879f9, #f472b6);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    background-clip:text; letter-spacing:-1px; margin-bottom:14px;">
            AutoAssure Analytics
        </div>
        <div style="color:#c4b5fd; font-size:1.1rem; max-width:620px; margin:0 auto 50px auto;
                    line-height:1.8;">
            Plateforme décisionnelle d'évaluation et de prédiction des réclamations d'assurance automobile par <b>Machine Learning</b>.<br>
            <b style="color:#e9d5ff;">Commencez par charger votre base de données.</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown("""
        <div style="background:linear-gradient(135deg, rgba(124,58,237,0.15), rgba(168,85,247,0.08));
                    border:1px solid rgba(139,92,246,0.4); border-radius:24px; padding:36px 32px;
                    box-shadow:0 20px 60px rgba(0,0,0,0.5); margin-bottom:24px;">
            <div style="color:#f5d0fe; font-size:1.15rem; font-weight:700; margin-bottom:6px; text-align:center;">
                📂 Importer votre base de données
            </div>
            <div style="color:#a78bfa; font-size:0.82rem; text-align:center; margin-bottom:22px;">
                Formats acceptés : <b style="color:#c084fc">.xlsx</b> · <b style="color:#c084fc">.xls</b> · <b style="color:#c084fc">.csv</b>
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
                with st.spinner("Chargement et analyse des données..."):
                    if uploaded_file.name.endswith(".csv"):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                st.session_state.df = df
                st.session_state.data_source = f"📄 {uploaded_file.name}"
                st.session_state.page = "accueil"
                st.success(f"✅ **{uploaded_file.name}** chargé : {len(df):,} lignes × {len(df.columns)} colonnes")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur lors du chargement : {e}")

        st.markdown("""
        <div style="text-align:center; margin:18px 0 14px 0; color:#6d6d8f; font-size:0.8rem;">
            ── ou ──
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Utiliser le jeu de données de référence", key="use_demo", type="secondary"):
            try:
                df = pd.read_csv("Car_Insurance_Claim-2.csv")
                st.session_state.df = df
                st.session_state.data_source = "📊 Jeu de données de référence (Car_Insurance_Claim-2.csv)"
                st.session_state.page = "accueil"
                st.rerun()
            except FileNotFoundError:
                st.error("Le fichier de démonstration est introuvable. Veuillez charger votre propre fichier.")

        # Feature cards
        st.markdown("""
        <div style="margin-top:48px; display:grid; grid-template-columns:1fr 1fr; gap:14px;">
            <div style="background:rgba(26,20,50,0.7); border:1px solid rgba(139,92,246,0.2);
                        border-radius:14px; padding:18px; text-align:center;">
                <div style="font-size:1.8rem; margin-bottom:8px;">📊</div>
                <div style="color:#f5d0fe; font-weight:700; font-size:0.88rem;">Tableau de Bord Analytique</div>
                <div style="color:#a78bfa; font-size:0.76rem; margin-top:4px;">Analyses dynamiques par variable</div>
            </div>
            <div style="background:rgba(26,20,50,0.7); border:1px solid rgba(139,92,246,0.2);
                        border-radius:14px; padding:18px; text-align:center;">
                <div style="font-size:1.8rem; margin-bottom:8px;">🤖</div>
                <div style="color:#f5d0fe; font-weight:700; font-size:0.88rem;">Modèles Machine Learning</div>
                <div style="color:#a78bfa; font-size:0.76rem; margin-top:4px;">Random Forest, XGBoost, LR, DT</div>
            </div>
            <div style="background:rgba(26,20,50,0.7); border:1px solid rgba(139,92,246,0.2);
                        border-radius:14px; padding:18px; text-align:center;">
                <div style="font-size:1.8rem; margin-bottom:8px;">🗺️</div>
                <div style="color:#f5d0fe; font-weight:700; font-size:0.88rem;">Distribution Territoriale</div>
                <div style="color:#a78bfa; font-size:0.76rem; margin-top:4px;">Analyse spatiale par département</div>
            </div>
            <div style="background:rgba(26,20,50,0.7); border:1px solid rgba(139,92,246,0.2);
                        border-radius:14px; padding:18px; text-align:center;">
                <div style="font-size:1.8rem; margin-bottom:8px;">📥</div>
                <div style="color:#f5d0fe; font-weight:700; font-size:0.88rem;">Reporting Décisionnel</div>
                <div style="color:#a78bfa; font-size:0.76rem; margin-top:4px;">Rapports PDF & exports Excel</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
def show_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:18px 0 22px 0;">
            <div style="display:inline-flex; align-items:center; justify-content:center;
                        width:52px; height:52px;
                        background:linear-gradient(135deg, #7c3aed, #c084fc);
                        border-radius:14px; box-shadow:0 6px 20px rgba(124,58,237,0.45);
                        font-size:1.8rem; color:#ffffff;">🚗</div>
            <div style="font-size:1.25rem; font-weight:800; margin-top:12px;
                        background:linear-gradient(90deg, #c084fc, #e879f9, #f472b6);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                        background-clip:text; letter-spacing:-0.4px;">AutoAssure</div>
            <div style="color:#a78bfa; font-size:0.75rem; margin-top:3px; font-weight:500;">
                Modélisation Prédictive & Machine Learning
            </div>
        </div>
        """, unsafe_allow_html=True)

        df = st.session_state.df
        if st.session_state.data_source:
            outcome_col = "OUTCOME" if "OUTCOME" in df.columns else df.columns[-1]
            st.markdown(f"""
            <div style="background:rgba(124,58,237,0.12); border:1px solid rgba(139,92,246,0.25);
                        border-radius:10px; padding:10px 14px; margin-bottom:14px;">
                <div style="color:#c084fc; font-weight:700; font-size:0.76rem; margin-bottom:3px;">SOURCE DU PORTEFEUILLE</div>
                <div style="color:#ddd6fe; font-size:0.78rem;">{st.session_state.data_source}</div>
                <div style="color:#a78bfa; font-size:0.75rem; margin-top:5px;">
                    {len(df):,} assurés · {len(df.columns)} variables · Cible: {outcome_col}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<p style="color:#a78bfa; font-size:0.72rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:10px; padding-left:4px;">Modules Métier</p>', unsafe_allow_html=True)

        pages_list = [
            ("🏠 Vue Synthétique", "accueil"),
            ("🔍 Exploration des Données", "exploration"),
            ("📊 Dashboard Analytique", "stats"),
            ("⚙️ Modélisation Machine Learning", "modelisation"),
            ("⚖️ Benchmark des Modèles", "comparaison"),
        ]

        current_page = st.session_state.page
        for label, key in pages_list:
            is_active = (current_page == key)
            button_label = f"✦  {label}" if is_active else label
            clicked = st.button(button_label, key=f"nav_{key}",
                                type="primary" if is_active else "secondary")
            if clicked:
                st.session_state.page = key
                st.rerun()

        st.markdown("---")
        st.markdown('<p style="color:#a78bfa;font-size:0.72rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;padding-left:4px;">Gestion des Données</p>', unsafe_allow_html=True)
        if st.button("📂 Importer un autre fichier", key="nav_reload", type="secondary"):
            st.session_state.df = None
            st.session_state.data_source = None
            st.rerun()

        st.markdown("---")
        st.markdown('<p style="color:#a78bfa;font-size:0.72rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;padding-left:4px;">Rapport d\'Audit Exécutif</p>', unsafe_allow_html=True)

        from utils_export import generate_pdf_report
        outcome_col = "OUTCOME" if "OUTCOME" in df.columns else df.columns[-1]
        n_claims = int(df[outcome_col].sum()) if pd.api.types.is_numeric_dtype(df[outcome_col]) else 0
        rate = round((n_claims / max(len(df), 1)) * 100, 1)
        pdf_global = generate_pdf_report(
            title="Rapport d'Audit Décisionnel & Machine Learning",
            dataset_kpis={"total": len(df), "claims": n_claims, "rate": rate}
        )
        st.download_button(
            label="📄 Télécharger le Rapport Complet (.pdf)",
            data=pdf_global,
            file_name="Rapport_Audit_Machine_Learning_AutoAssure.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

        st.markdown("---")
        outcome_col = "OUTCOME" if "OUTCOME" in df.columns else df.columns[-1]
        st.markdown(f"""
        <div style="padding:14px; background:rgba(30,20,60,0.6); border-radius:12px;
                    border:1px solid rgba(139,92,246,0.22);">
            <p style="color:#c4b5fd; font-size:0.73rem; margin:0; line-height:1.75;">
                <b style="color:#f5d0fe;">Lignes :</b> {len(df):,}<br>
                <b style="color:#f5d0fe;">Colonnes :</b> {len(df.columns)}<br>
                <b style="color:#f5d0fe;">Cible :</b> {outcome_col}<br>
                <b style="color:#f5d0fe;">Modèles :</b> RF, XGBoost, LR, DT
            </p>
        </div>
        """, unsafe_allow_html=True)


# ── ROUTING ───────────────────────────────────────────────────────────────────
import importlib

if st.session_state.df is None:
    show_landing()
else:
    show_sidebar()
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
