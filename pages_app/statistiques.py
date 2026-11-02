import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from utils_export import export_to_excel, generate_pdf_report

PL = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans, Inter, sans-serif", color="#cbd5e1"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)"),
    margin=dict(t=50, b=40, l=40, r=20),
    colorway=["#818cf8","#34d399","#f59e0b","#ef4444","#c084fc","#06b6d4"],
)
VIO = ["#818cf8", "#c084fc", "#f472b6", "#34d399", "#f59e0b", "#06b6d4"]

@st.cache_data
def load_geojson():
    if os.path.exists("departements-france.geojson"):
        with open("departements-france.geojson", "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def pch(fig):
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def stitle(title, sub=""):
    sub_html = f"<p style='color:#a78bfa;font-size:0.8rem;margin:3px 0 0 0;'>{sub}</p>" if sub else ""
    st.markdown(
        f"<div style='margin:22px 0 14px 0;padding-bottom:8px;border-bottom:1px solid rgba(139,92,246,0.2);'>"
        f"<span style='color:#f5d0fe;font-size:1.1rem;font-weight:700;'>{title}</span>"
        f"{sub_html}</div>",
        unsafe_allow_html=True
    )

def show():
    df = st.session_state.get("df", None)
    if df is None:
        st.error("Aucune donnée chargée. Veuillez charger un fichier depuis la page d'accueil.")
        return

    target_col = "OUTCOME" if "OUTCOME" in df.columns else df.columns[-1]
    all_vars = [c for c in df.columns if c not in ["ID", target_col]]

    st.markdown(
        "<div style='margin-bottom:24px;'>"
        "<div style='color:#fdf4ff;font-size:1.85rem;font-weight:800;letter-spacing:-0.5px;margin-bottom:4px;'>"
        "📊 Dashboard Analytique & Études Statistiques</div>"
        "<div style='color:#a78bfa;font-size:0.92rem;'>"
        "Sélectionnez une variable pour afficher son tableau de bord d'analyse multidimensionnel</div></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div style='background:linear-gradient(135deg,rgba(124,58,237,0.18),rgba(168,85,247,0.1));"
        "border:1px solid rgba(139,92,246,0.35);border-radius:16px;padding:20px 24px;margin-bottom:22px;'>"
        "<div style='color:#c084fc;font-size:0.78rem;font-weight:700;text-transform:uppercase;"
        "letter-spacing:0.1em;margin-bottom:12px;'>🎯 Sélection de la Variable d'Étude</div></div>",
        unsafe_allow_html=True
    )

    col_sel1, col_sel2 = st.columns([3, 1])
    with col_sel1:
        chosen_var = st.selectbox("Variable", options=all_vars, key="dash_chosen_var")
    with col_sel2:
        show_target = st.checkbox("Croiser avec la variable cible", value=True, key="dash_show_target")

    var_is_numeric = pd.api.types.is_numeric_dtype(df[chosen_var])
    df_clean = df[[chosen_var, target_col]].dropna().copy()
    df_clean["Classe"] = df_clean[target_col].apply(
        lambda x: f"Réclamation ({target_col}=1)" if x == 1 else f"Sans réclamation ({target_col}=0)"
    )

    stitle("Indicateurs Clés de Risque", f"Variable : {chosen_var}")
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Effectif total", f"{df[chosen_var].count():,}", f"{df[chosen_var].isnull().sum()} manquants")
    with k2:
        st.metric("Valeurs uniques", f"{df[chosen_var].nunique():,}")
    with k3:
        if var_is_numeric:
            st.metric("Moyenne", f"{df[chosen_var].mean():.2f}", f"Médiane: {df[chosen_var].median():.2f}")
        else:
            top_v = df[chosen_var].value_counts().index[0] if len(df[chosen_var].dropna()) > 0 else "N/A"
            st.metric("Mode", str(top_v))
    with k4:
        if var_is_numeric:
            st.metric("Écart-type", f"{df[chosen_var].std():.2f}",
                      f"{df[chosen_var].min():.1f} - {df[chosen_var].max():.1f}")
        else:
            pct_top = df[chosen_var].value_counts(normalize=True).iloc[0] * 100 if len(df[chosen_var].dropna()) > 0 else 0
            st.metric("Fréq. mode", f"{pct_top:.1f}%")
    with k5:
        if var_is_numeric:
            corr_v = df[[chosen_var, target_col]].dropna().corr().iloc[0, 1]
            st.metric("Corrélation cible", f"{corr_v:.3f}")
        else:
            tg = df.groupby(chosen_var)[target_col].mean()
            st.metric("Taux max récl.", f"{tg.max() * 100:.1f}%" if len(tg) > 0 else "N/A")

    st.markdown("<br>", unsafe_allow_html=True)

    if var_is_numeric:
        stitle("Analyse Univariée de la Variable Numérique", chosen_var)
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            fig = px.histogram(df_clean, x=chosen_var,
                               color="Classe" if show_target else None,
                               nbins=40, marginal="rug",
                               color_discrete_sequence=VIO, barmode="overlay", opacity=0.75,
                               title=f"Distribution - {chosen_var}")
            fig.update_layout(**PL, title_font_color="#f5d0fe", legend=dict(font=dict(color="#c4b5fd")))
            pch(fig)
        with r1c2:
            fig2 = px.box(df_clean, x="Classe" if show_target else None, y=chosen_var,
                          color="Classe" if show_target else None,
                          color_discrete_sequence=VIO, points="outliers",
                          title=f"Boîte à moustaches - {chosen_var}")
            fig2.update_layout(**PL, title_font_color="#f5d0fe", showlegend=False)
            pch(fig2)

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            fig3 = px.violin(df_clean, x="Classe" if show_target else None, y=chosen_var,
                             color="Classe" if show_target else None,
                             color_discrete_sequence=VIO, box=True, points="outliers",
                             title=f"Violin plot - {chosen_var}")
            fig3.update_layout(**PL, title_font_color="#f5d0fe", showlegend=False)
            pch(fig3)
        with r2c2:
            fig4 = px.ecdf(df_clean, x=chosen_var,
                           color="Classe" if show_target else None,
                           color_discrete_sequence=VIO,
                           title=f"Distribution cumulée (ECDF) - {chosen_var}")
            fig4.update_layout(**PL, title_font_color="#f5d0fe", legend=dict(font=dict(color="#c4b5fd")))
            pch(fig4)

        if show_target:
            stitle("Segmentation & Taux de Sinistralité par Tranches", f"Fréquence selon {chosen_var}")
            n_bins = st.slider("Nombre de tranches d'analyse", 3, 20, 8, key="dash_nbins")
            df_binned = df[[chosen_var, target_col]].dropna().copy()
            df_binned["Tranche"] = pd.cut(df_binned[chosen_var], bins=n_bins)
            tranche_stats = df_binned.groupby("Tranche", observed=True).agg(
                Effectif=(target_col, "count"), Taux=(target_col, "mean")
            ).reset_index()
            tranche_stats["Taux_pct"] = (tranche_stats["Taux"] * 100).round(2)
            tranche_stats["Tranche"] = tranche_stats["Tranche"].astype(str)
            tr1, tr2 = st.columns(2)
            with tr1:
                fig_t1 = px.bar(tranche_stats, x="Tranche", y="Effectif",
                                color="Effectif",
                                color_continuous_scale=["#302b63", "#818cf8", "#c084fc"],
                                title=f"Effectif par tranche - {chosen_var}", text="Effectif")
                fig_t1.update_traces(texttemplate="%{text:,}", textposition="outside")
                fig_t1.update_layout(**PL, title_font_color="#f5d0fe",
                                     coloraxis_showscale=False, xaxis_tickangle=-30)
                pch(fig_t1)
            with tr2:
                fig_t2 = px.bar(tranche_stats, x="Tranche", y="Taux_pct",
                                color="Taux_pct",
                                color_continuous_scale=["#302b63", "#f59e0b", "#ef4444"],
                                title=f"Taux de réclamation (%) par tranche - {chosen_var}",
                                text="Taux_pct")
                fig_t2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                fig_t2.update_layout(**PL, title_font_color="#f5d0fe",
                                     coloraxis_showscale=False, xaxis_tickangle=-30)
                pch(fig_t2)

        stitle("Statistiques Descriptives & Comparaison par Classe")
        stats_df = df[chosen_var].describe().reset_index()
        stats_df.columns = ["Statistique", "Valeur globale"]
        stats_df["Valeur globale"] = stats_df["Valeur globale"].round(4)
        if show_target:
            s0 = df[df[target_col] == 0][chosen_var].describe().reset_index()
            s1 = df[df[target_col] == 1][chosen_var].describe().reset_index()
            s0.columns = ["Statistique", "Classe 0 (Sans récl.)"]
            s1.columns = ["Statistique", "Classe 1 (Avec récl.)"]
            merged = stats_df.merge(s0, on="Statistique").merge(s1, on="Statistique")
            merged.iloc[:, 1:] = merged.iloc[:, 1:].round(4)
            st.dataframe(merged, use_container_width=True, hide_index=True)
        else:
            st.dataframe(stats_df, use_container_width=True, hide_index=True)

    else:
        stitle("Répartition & Fréquence de la Variable Catégorielle", chosen_var)
        vc = df[chosen_var].value_counts().reset_index()
        vc.columns = [chosen_var, "Effectif"]
        vc["Proportion (%)"] = (vc["Effectif"] / len(df) * 100).round(2)
        vc = vc.sort_values("Effectif", ascending=False)

        r1c1, r1c2 = st.columns(2)
        with r1c1:
            fig_b = px.bar(vc, x=chosen_var, y="Effectif", color="Effectif",
                           color_continuous_scale=["#302b63", "#818cf8", "#c084fc"],
                           text="Effectif", title=f"Effectifs - {chosen_var}")
            fig_b.update_traces(texttemplate="%{text:,}", textposition="outside")
            fig_b.update_layout(**PL, title_font_color="#f5d0fe",
                                coloraxis_showscale=False, xaxis_tickangle=-20)
            pch(fig_b)
        with r1c2:
            fig_p = px.pie(vc, names=chosen_var, values="Effectif",
                           color_discrete_sequence=VIO, hole=0.5,
                           title=f"Répartition - {chosen_var}")
            fig_p.update_traces(textposition="outside", textfont_size=12,
                                marker=dict(line=dict(color="rgba(0,0,0,0.3)", width=2)))
            fig_p.update_layout(**PL, title_font_color="#f5d0fe",
                                legend=dict(font=dict(color="#c4b5fd")))
            pch(fig_p)

        if show_target:
            stitle("Analyse Bivariée vs Variable Cible", f"{chosen_var} × {target_col}")
            r2c1, r2c2 = st.columns(2)
            with r2c1:
                pivot = df.groupby([chosen_var, target_col]).size().reset_index(name="n")
                pivot["Classe"] = pivot[target_col].apply(
                    lambda x: f"{target_col}=1 (Réclamation)" if x == 1 else f"{target_col}=0 (Sans réclamation)"
                )
                fig_gb = px.bar(pivot, x=chosen_var, y="n", color="Classe",
                                barmode="group", text="n",
                                color_discrete_sequence=["#34d399", "#818cf8"],
                                title=f"{chosen_var} croisé avec {target_col}")
                fig_gb.update_traces(texttemplate="%{text:,}", textposition="outside")
                fig_gb.update_layout(**PL, title_font_color="#f5d0fe",
                                     legend=dict(font=dict(color="#c4b5fd")), xaxis_tickangle=-20)
                pch(fig_gb)
            with r2c2:
                taux = df.groupby(chosen_var)[target_col].mean().reset_index()
                taux.columns = [chosen_var, "Taux (%)"]
                taux["Taux (%)"] = (taux["Taux (%)"] * 100).round(2)
                taux = taux.sort_values("Taux (%)", ascending=False)
                fig_t = px.bar(taux, x=chosen_var, y="Taux (%)", color="Taux (%)",
                               color_continuous_scale=["#302b63", "#f59e0b", "#ef4444"],
                               text="Taux (%)", title=f"Taux de réclamation (%) par {chosen_var}")
                fig_t.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                fig_t.update_layout(**PL, title_font_color="#f5d0fe",
                                    coloraxis_showscale=False, xaxis_tickangle=-20)
                pch(fig_t)

            r3c1, r3c2 = st.columns(2)
            with r3c1:
                pct_df = df.groupby([chosen_var, target_col]).size().reset_index(name="n")
                pct_df["Classe"] = pct_df[target_col].apply(
                    lambda x: "Réclamation" if x == 1 else "Sans réclamation"
                )
                tot = pct_df.groupby(chosen_var)["n"].transform("sum")
                pct_df["Pct"] = (pct_df["n"] / tot * 100).round(1)
                fig_stk = px.bar(pct_df, x=chosen_var, y="Pct", color="Classe",
                                 barmode="stack", text="Pct",
                                 color_discrete_sequence=["#34d399", "#818cf8"],
                                 title=f"Répartition normalisée 100% - {chosen_var}")
                fig_stk.update_traces(texttemplate="%{text:.0f}%", textposition="inside")
                fig_stk.update_layout(**PL, title_font_color="#f5d0fe",
                                      legend=dict(font=dict(color="#c4b5fd")), xaxis_tickangle=-20)
                pch(fig_stk)
            with r3c2:
                tc_df = df_clean.groupby([chosen_var, "Classe"]).size().reset_index(name="n")
                fig_tm = px.treemap(tc_df, path=[chosen_var, "Classe"], values="n",
                                    color="n",
                                    color_continuous_scale=["#302b63", "#818cf8", "#c084fc"],
                                    title=f"Treemap hiérarchique : {chosen_var} × Classe")
                fig_tm.update_layout(**PL, title_font_color="#f5d0fe", coloraxis_showscale=False)
                pch(fig_tm)

        stitle("Tableau Récapitulatif Détaillé des Modalités")
        if show_target:
            t2 = df.groupby(chosen_var)[target_col].agg(["count", "sum", "mean"]).reset_index()
            t2.columns = [chosen_var, "Assurés", "Réclamations", "Taux moyen"]
            t2["Taux (%)"] = (t2["Taux moyen"] * 100).round(2)
            t2["Proportion (%)"] = (t2["Assurés"] / len(df) * 100).round(2)
            t2 = t2.drop(columns=["Taux moyen"]).sort_values("Assurés", ascending=False)
            st.dataframe(t2, use_container_width=True, hide_index=True)
        else:
            st.dataframe(vc, use_container_width=True, hide_index=True)

    st.markdown("---")
    tabs_extra = st.tabs(["🔗 Matrice de Corrélation & Dépendance", "🔀 Analyse Bivariée Croisée", "🗺️ Répartition Territoriale (France)"])

    with tabs_extra[0]:
        stitle("Matrice de Corrélation Linéaire (Pearson)", "Corrélations de Pearson entre prédicteurs numériques")
        num_for_corr = [c for c in df.select_dtypes(include="number").columns if c != "ID"]
        if len(num_for_corr) >= 2:
            df_corr = df[num_for_corr].dropna()
            corr_matrix = df_corr.corr().round(3)
            fig_corr = px.imshow(corr_matrix,
                                 color_continuous_scale=["#0f0c29", "#302b63", "#818cf8", "#c084fc", "#f8faff"],
                                 zmin=-1, zmax=1, text_auto=True,
                                 title="Matrice de corrélation de Pearson", aspect="auto")
            fig_corr.update_layout(**PL, title_font_color="#f5d0fe", height=550)
            pch(fig_corr)
            if target_col in num_for_corr:
                stitle("Hiérarchie d'Association avec la Variable Cible", f"Intensité de corrélation avec {target_col}")
                corr_target = corr_matrix[target_col].drop(target_col).abs().sort_values(ascending=False)
                fig_ci = px.bar(x=corr_target.values, y=corr_target.index, orientation="h",
                                color=corr_target.values,
                                color_continuous_scale=["#302b63", "#818cf8", "#c084fc"],
                                title=f"Importance (|corrélation|) avec {target_col}",
                                labels={"x": "Corrélation absolue", "y": "Variable"})
                fig_ci.update_layout(**PL, title_font_color="#f5d0fe",
                                     coloraxis_showscale=False, height=380)
                pch(fig_ci)
        else:
            st.info("Nombre insuffisant de variables numériques pour calculer la matrice de corrélation.")

    with tabs_extra[1]:
        stitle("Exploration Interactive des Relations Bivariées", "Analyse conditionnelle entre deux variables")
        avail = [c for c in df.columns if c != "ID"]
        cx1, cx2, cx3 = st.columns([2, 2, 1])
        with cx1:
            col_x = st.selectbox("Variable X", avail, index=0, key="cross_x2")
        with cx2:
            col_y = st.selectbox("Variable Y", avail, index=min(5, len(avail) - 1), key="cross_y2")
        with cx3:
            hue_opt = st.checkbox("Distinguer par la cible", value=True, key="cross_hue2")
        df_cr = df[[col_x, col_y, target_col]].dropna().copy()
        df_cr["Classe"] = df_cr[target_col].apply(
            lambda x: "Réclamation (1)" if x == 1 else "Sans réclamation (0)"
        )
        x_num = pd.api.types.is_numeric_dtype(df[col_x])
        y_num = pd.api.types.is_numeric_dtype(df[col_y])
        cc = "Classe" if hue_opt else None
        cs = ["#34d399", "#818cf8"]
        if x_num and y_num:
            fig_c = px.scatter(df_cr, x=col_x, y=col_y, color=cc,
                               color_discrete_sequence=cs, opacity=0.55,
                               trendline="ols" if not hue_opt else None,
                               title=f"{col_x} vs {col_y}")
        elif not x_num and y_num:
            fig_c = px.box(df_cr, x=col_x, y=col_y, color=cc,
                           color_discrete_sequence=cs, title=f"{col_x} vs {col_y}")
        elif x_num and not y_num:
            fig_c = px.box(df_cr, x=col_y, y=col_x, color=cc,
                           color_discrete_sequence=cs, title=f"{col_x} vs {col_y}")
        else:
            pivot_hm = pd.crosstab(df_cr[col_x], df_cr[col_y])
            fig_c = px.imshow(pivot_hm,
                              color_continuous_scale=["#0f0c29", "#818cf8", "#c084fc"],
                              title=f"Tableau croisé : {col_x} × {col_y}", text_auto=True)
        fig_c.update_layout(**PL, title_font_color="#f5d0fe", legend=dict(font=dict(color="#c4b5fd")))
        pch(fig_c)

    with tabs_extra[2]:
        stitle("Distribution Territoriale des Sinistres (France)", "Analyse spatiale des taux réels observés par département")
        geojson_data = load_geojson()
        if "POSTAL_CODE" not in df.columns:
            st.info("La colonne POSTAL_CODE est absente. La carte n'est pas disponible pour ce fichier.")
        elif geojson_data is None:
            st.warning("Le fichier departements-france.geojson est introuvable.")
        else:
            df_geo = df.copy()
            df_geo["DEPT"] = df_geo["POSTAL_CODE"].astype(str).str[:2].str.zfill(2)
            dept_names = {"10": "Aube (10)", "21": "Côte-d'Or (21)",
                          "32": "Gers (32)", "92": "Hauts-de-Seine (92)"}
            all_depts_list = [
                {"DEPT": feat["properties"]["code"], "Nom_Complet": feat["properties"]["nom"]}
                for feat in geojson_data["features"]
            ]
            df_france_all = pd.DataFrame(all_depts_list)
            df_france_all["Nom_Departement"] = df_france_all.apply(
                lambda r: dept_names.get(r["DEPT"], r["Nom_Complet"].replace("\ufffd", "o")), axis=1
            )
            geo_summary = df_geo.groupby("DEPT").agg(
                Assures=(target_col, "count"),
                Reclamations=(target_col, "sum"),
                Taux=(target_col, "mean")
            ).reset_index()
            geo_summary["Taux_pct"] = (geo_summary["Taux"] * 100).round(2)
            geo_summary["Nom_Departement"] = geo_summary["DEPT"].map(
                lambda x: dept_names.get(x, f"Département {x}")
            )
            col_th, _ = st.columns([2, 3])
            with col_th:
                map_theme = st.selectbox("Fond de carte",
                                         ["Clair (Carto-Positron)", "Sombre (Carto-Darkmatter)", "OpenStreetMap"],
                                         key="geo_theme")

            col_display = "Taux_pct"
            label_color = "Taux Réel Réclamations (%)"

            map_merged = df_france_all.merge(geo_summary, on="DEPT", how="left")
            map_merged["Taux_Affiche"] = map_merged[col_display].fillna(0)
            hn_col = "Nom_Departement_x" if "Nom_Departement_x" in map_merged.columns else "Nom_Departement"
            cg1, cg2, cg3 = st.columns(3)
            with cg1:
                st.metric("Territoire", "France (96 dépt.)", f"{len(geo_summary)} zones renseignées")
            with cg2:
                top_r = geo_summary.sort_values(col_display, ascending=False).iloc[0]
                st.metric("Taux le plus élevé", f"{top_r[col_display]}%", top_r["Nom_Departement"])
            with cg3:
                low_r = geo_summary.sort_values(col_display, ascending=True).iloc[0]
                st.metric("Taux le plus bas", f"{low_r[col_display]}%", low_r["Nom_Departement"])

            style_code = ("carto-positron" if "Clair" in map_theme
                          else "carto-darkmatter" if "Sombre" in map_theme else "open-street-map")
            if hasattr(px, "choropleth_map"):
                fig_map = px.choropleth_map(
                    map_merged, geojson=geojson_data,
                    locations="DEPT", featureidkey="properties.code",
                    color="Taux_Affiche",
                    color_continuous_scale=["#f1f5f9", "#38bdf8", "#3b82f6", "#f59e0b", "#ef4444"],
                    range_color=[0, 100], map_style=style_code,
                    center={"lat": 46.5, "lon": 2.2}, zoom=4.8, opacity=0.75,
                    hover_name=hn_col,
                    hover_data={"DEPT": True, "Assures": True, "Taux_Affiche": ":.1f"},
                    labels={"Taux_Affiche": label_color, "DEPT": "Code", "Assures": "Total Assurés"}
                )
            else:
                fig_map = px.choropleth_mapbox(
                    map_merged, geojson=geojson_data,
                    locations="DEPT", featureidkey="properties.code",
                    color="Taux_Affiche",
                    color_continuous_scale=["#f1f5f9", "#38bdf8", "#3b82f6", "#f59e0b", "#ef4444"],
                    range_color=[0, 100], mapbox_style=style_code,
                    center={"lat": 46.5, "lon": 2.2}, zoom=4.8, opacity=0.75,
                    hover_name=hn_col,
                    hover_data={"DEPT": True, "Assures": True, "Taux_Affiche": ":.1f"},
                    labels={"Taux_Affiche": label_color, "DEPT": "Code", "Assures": "Total Assurés"}
                )
            fig_map.update_layout(
                margin=dict(r=0, t=10, l=0, b=0), height=560,
                paper_bgcolor="rgba(0,0,0,0)",
                coloraxis_colorbar=dict(title=label_color, tickfont=dict(color="#94a3b8"),
                                        title_font=dict(color="#f8fafc", size=12))
            )
            pch(fig_map)

            st.markdown("---")
            dcols = ["Nom_Departement", "Assures", "Reclamations", "Taux_pct"]
            crn = {"Nom_Departement": "Département", "Assures": "Total Assurés",
                   "Reclamations": "Réclamations", "Taux_pct": "Taux Réel (%)"}
            ex_cols = [c for c in dcols if c in geo_summary.columns]
            st.dataframe(geo_summary[ex_cols].rename(columns=crn), use_container_width=True, hide_index=True)
            cd1, cd2 = st.columns(2)
            with cd1:
                eg = export_to_excel({"Cartographie": geo_summary[ex_cols].rename(columns=crn)})
                st.download_button("📥 Télécharger les données (.xlsx)", data=eg,
                                   file_name="carte_reclamations.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   use_container_width=True)
            with cd2:
                n_cl = int(df[target_col].sum()) if pd.api.types.is_numeric_dtype(df[target_col]) else 0
                rt = round(df[target_col].mean() * 100, 1) if pd.api.types.is_numeric_dtype(df[target_col]) else 0
                pg = generate_pdf_report(
                    title="Rapport Territorial - Données Observées",
                    dataset_kpis={"total": len(df), "claims": n_cl, "rate": rt},
                    geo_df=geo_summary[ex_cols].rename(columns=crn)
                )
                st.download_button("📄 Télécharger le rapport (.pdf)", data=pg,
                                   file_name="Rapport_Territorial.pdf",
                                   mime="application/pdf", use_container_width=True)
