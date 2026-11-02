import streamlit as st
import pandas as pd
import numpy as np

from utils_export import export_to_excel

@st.cache_data
def load_data():
    return pd.read_csv("Car_Insurance_Claim-2.csv")

def card(title, value, color="#4f46e5"):
    st.markdown(f"""
    <div style="background:#ffffff; border:1px solid #e2e8f0;
                border-radius:14px; padding:18px 20px; margin-bottom:12px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
        <div style="color:#64748b; font-size:0.75rem; text-transform:uppercase;
                    letter-spacing:0.08em; font-weight:700;">{title}</div>
        <div style="color:{color}; font-size:1.45rem; font-weight:800; margin-top:4px;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def show():
    df = st.session_state.get("df", None)
    if df is None:
        try:
            df = pd.read_csv("Car_Insurance_Claim-2.csv")
            st.session_state.df = df
        except Exception:
            st.error("Aucune donnée disponible. Veuillez charger un fichier.")
            return

    st.markdown('<div style="color:#0f172a; font-size:1.75rem; font-weight:800; margin-bottom:4px; letter-spacing:-0.5px;">Audit & Exploration des Données</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#64748b; font-size:0.95rem; margin-bottom:20px;">Aperçu interactif, contrôle de complétude et diagnostic structurel des variables</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Aperçu du portefeuille", "Contrôle de qualité des données", "Diagnostic structurel des variables"])

    with tab1:
        n_rows = st.slider("Nombre de lignes à afficher", 5, 100, 20, key="slider_rows")

        col_filter = st.multiselect("Sélectionner les colonnes à afficher", options=df.columns.tolist(),
                                     default=df.columns.tolist()[:8], key="col_filter")

        display_df = df[col_filter].head(n_rows) if col_filter else df.head(n_rows)
        st.dataframe(display_df, use_container_width=True, height=380)

        c_exp_l, c_exp_r = st.columns([1, 2])
        with c_exp_l:
            excel_data = export_to_excel({"Extrait_Donnees": display_df})
            st.download_button(
                label="📥 Télécharger cet extrait (Excel)",
                data=excel_data,
                file_name="autoassure_donnees_extrait.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Assurés sous revue", f"{len(df):,}")
        with col2:
            st.metric("Variables totales", f"{len(df.columns)}")
        with col3:
            st.metric("Variables numériques", f"{df.select_dtypes(include='number').shape[1]}")
        with col4:
            st.metric("Variables catégoriques", f"{df.select_dtypes(include='object').shape[1]}")

    with tab2:
        st.markdown('<div style="color:#0f172a; font-weight:700; font-size:1rem; margin-bottom:14px;">Contrôle de complétude : Valeurs manquantes par variable</div>', unsafe_allow_html=True)

        missing = df.isnull().sum().reset_index()
        missing.columns = ["Variable", "Manquants"]
        missing["Taux (%)"] = (missing["Manquants"] / len(df) * 100).round(2)
        missing["Type"] = missing["Variable"].apply(lambda x: str(df[x].dtype))
        missing = missing[missing["Manquants"] > 0].sort_values("Manquants", ascending=False)

        if len(missing) == 0:
            st.success("✅ Aucune valeur manquante détectée dans ce jeu de données.")
        else:
            st.dataframe(missing, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown('<div style="color:#0f172a; font-weight:700; font-size:1rem; margin-bottom:14px;">Statistiques descriptives des variables numériques</div>', unsafe_allow_html=True)

        num_cols = df.select_dtypes(include="number").columns.tolist()
        if "ID" in num_cols:
            num_cols.remove("ID")

        st.dataframe(df[num_cols].describe().round(4), use_container_width=True)

    with tab3:
        st.markdown('<div style="color:#0f172a; font-weight:700; font-size:1rem; margin-bottom:14px;">Schéma des données & Cardinalité des variables</div>', unsafe_allow_html=True)

        info_df = pd.DataFrame({
            "Variable": df.columns,
            "Type": df.dtypes.astype(str).values,
            "Non-nuls": df.notnull().sum().values,
            "Valeurs uniques": df.nunique().values,
            "Exemple": [str(df[c].dropna().iloc[0]) if len(df[c].dropna()) > 0 else "N/A" for c in df.columns],
        })

        st.dataframe(info_df, use_container_width=True, hide_index=True, height=450)

        st.markdown("---")
        st.markdown('<div style="color:#0f172a; font-weight:700; font-size:1rem; margin-bottom:12px;">Distribution des modalités catégorielles</div>', unsafe_allow_html=True)

        cat_cols = df.select_dtypes(include="object").columns.tolist()
        if cat_cols:
            chosen_cat = st.selectbox("Sélectionner une variable catégorielle", cat_cols, key="cat_explore")
            vc = df[chosen_cat].value_counts().reset_index()
            vc.columns = ["Modalité", "Effectif"]
            vc["Proportion (%)"] = (vc["Effectif"] / len(df) * 100).round(2)
            st.dataframe(vc, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune variable catégorielle dans ce jeu de données.")
