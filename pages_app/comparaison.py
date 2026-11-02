import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (accuracy_score, roc_auc_score, f1_score,
                              precision_score, recall_score, roc_curve)
try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

from utils_export import export_to_excel, generate_pdf_report

PLOTLY_LAYOUT = dict(
    paper_bgcolor="#ffffff",
    plot_bgcolor="#ffffff",
    font=dict(family="Plus Jakarta Sans, Inter, sans-serif", color="#334155"),
    xaxis=dict(gridcolor="#f1f5f9", linecolor="#cbd5e1", tickfont=dict(color="#475569")),
    yaxis=dict(gridcolor="#f1f5f9", linecolor="#cbd5e1", tickfont=dict(color="#475569")),
    margin=dict(t=50, b=40, l=40, r=20),
)

def load_and_prep():
    df = st.session_state.get("df", None)
    if df is None:
        try:
            df = pd.read_csv("Car_Insurance_Claim-2.csv")
        except Exception:
            return pd.DataFrame(), pd.Series()
    df2 = df.drop(columns=["ID"], errors="ignore").dropna().copy()
    cat_cols = df2.select_dtypes(include="object").columns.tolist()
    le = LabelEncoder()
    for c in cat_cols:
        df2[c] = le.fit_transform(df2[c].astype(str))
    target_col = "OUTCOME" if "OUTCOME" in df2.columns else df2.columns[-1]
    X = df2.drop(columns=[target_col])
    y = df2[target_col].astype(int)
    return X, y

@st.cache_data(show_spinner="Entraînement et évaluation de tous les modèles...")
def compare_all_models(test_size, random_state):
    X, y = load_and_prep()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    models = {
        "Random Forest":        (RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1), False),
        "XGBoost":              (XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1, use_label_encoder=False, eval_metric="logloss", random_state=42, verbosity=0), False) if HAS_XGB else None,
        "Régression Logistique":(LogisticRegression(C=1.0, max_iter=1000, random_state=42), True),
        "Arbre de Décision":    (DecisionTreeClassifier(max_depth=8, random_state=42), False),
    }
    if not HAS_XGB:
        del models["XGBoost"]

    results = []
    roc_data = {}

    for name, (model, scaled) in models.items():
        Xt = X_train_s if scaled else X_train.values
        Xs = X_test_s  if scaled else X_test.values

        model.fit(Xt, y_train)
        y_pred  = model.predict(Xs)
        y_proba = model.predict_proba(Xs)[:,1]

        acc  = accuracy_score(y_test, y_pred)
        auc  = roc_auc_score(y_test, y_proba)
        f1   = f1_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec  = recall_score(y_test, y_pred)

        results.append({
            "Modèle": name,
            "Accuracy": round(acc, 4),
            "AUC-ROC":  round(auc, 4),
            "F1-Score": round(f1, 4),
            "Précision": round(prec, 4),
            "Rappel":   round(rec, 4),
        })

        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_data[name] = (fpr, tpr, auc)

    return pd.DataFrame(results).sort_values("AUC-ROC", ascending=False), roc_data

def show():
    st.markdown('<div style="color:#0f172a;font-size:1.75rem;font-weight:800;margin-bottom:6px;letter-spacing:-0.5px;">Benchmark & Comparaison des Modèles</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#64748b;font-size:0.95rem;margin-bottom:24px;">Évaluez et comparez les performances de tous les modèles de Machine Learning</div>', unsafe_allow_html=True)

    c_param1, c_param2, c_param3 = st.columns([2, 2, 2])
    with c_param1:
        test_size  = st.slider("Taille du jeu test (%)", 10, 40, 20, key="cmp_test") / 100
    with c_param2:
        rand_state = st.number_input("Graine aléatoire (Random state)", 0, 999, 42, key="cmp_rand")
    with c_param3:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        run = st.button("🚀 Lancer le Benchmark des Modèles", key="compare_btn", type="primary")

    if run or "compare_results" in st.session_state:
        if run:
            results_df, roc_data = compare_all_models(test_size, rand_state)
            st.session_state.compare_results = (results_df, roc_data)
        else:
            results_df, roc_data = st.session_state.compare_results

        best_model = results_df.iloc[0]["Modèle"]
        best_auc   = results_df.iloc[0]["AUC-ROC"]

        st.success(f"🏆 Meilleur modèle sélectionné : **{best_model}** avec un AUC-ROC de **{best_auc:.4f}**")

        # ── Tableau recap ──────────────────────────────────────────────────
        st.markdown('<div style="color:#0f172a;font-size:1.1rem;font-weight:700;margin:18px 0 12px 0;">Tableau comparatif des performances</div>', unsafe_allow_html=True)

        def highlight_best(s):
            if s.name in ["Accuracy","AUC-ROC","F1-Score","Précision","Rappel"]:
                max_val = s.max()
                return ["background: #eef2ff; color:#4338ca; font-weight:700"
                        if v == max_val else "" for v in s]
            return [""] * len(s)

        styled = results_df.style.apply(highlight_best).format({
            "Accuracy":  "{:.4f}",
            "AUC-ROC":  "{:.4f}",
            "F1-Score": "{:.4f}",
            "Précision":"{:.4f}",
            "Rappel":   "{:.4f}",
        })
        st.dataframe(styled, use_container_width=True, hide_index=True)

        col_c_exp1, col_c_exp2 = st.columns(2)
        with col_c_exp1:
            excel_cmp = export_to_excel({"Comparatif_Modeles": results_df})
            st.download_button(
                label="📊 Exporter le Benchmark sous Excel (.xlsx)",
                data=excel_cmp,
                file_name="benchmark_modeles_autoassure.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )
        with col_c_exp2:
            df_curr = st.session_state.get("df", None)
            tot = len(df_curr) if df_curr is not None else 10000
            tgt = "OUTCOME" if (df_curr is not None and "OUTCOME" in df_curr.columns) else (df_curr.columns[-1] if df_curr is not None else "OUTCOME")
            n_cl = int(df_curr[tgt].sum()) if (df_curr is not None and pd.api.types.is_numeric_dtype(df_curr[tgt])) else 3133
            rt = round((n_cl / tot) * 100, 1) if tot > 0 else 31.3
            pdf_cmp = generate_pdf_report(
                title="Rapport d'Audit & Sélection du Meilleur Modèle",
                dataset_kpis={"total": tot, "claims": n_cl, "rate": rt},
                models_df=results_df,
                selected_model_name=best_model
            )
            st.download_button(
                label="📄 Télécharger le Rapport d'Audit Complet (.pdf)",
                data=pdf_cmp,
                file_name="Rapport_Audit_Modeles_AutoAssure.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        tab1, tab2, tab3 = st.tabs(["Comparaison des métriques", "Courbes ROC", "Classement visuel"])

        with tab1:
            metrics = ["Accuracy","AUC-ROC","F1-Score","Précision","Rappel"]
            metric_sel = st.multiselect("Métriques à afficher", metrics, default=metrics, key="metric_sel")

            if metric_sel:
                df_melt = results_df.melt(id_vars="Modèle", value_vars=metric_sel,
                                           var_name="Métrique", value_name="Score")
                fig_bar = px.bar(df_melt, x="Modèle", y="Score", color="Métrique",
                                  barmode="group", text_auto=".3f",
                                  color_discrete_sequence=["#4f46e5","#7c3aed","#2563eb","#059669","#d97706"],
                                  title="Comparaison des métriques par modèle")
                fig_bar.update_layout(**PLOTLY_LAYOUT, title_font_color="#0f172a",
                                       legend=dict(font=dict(color="#334155")),
                                       yaxis_range=[0, 1.05])
                st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar":False})

                # Radar chart
                fig_radar = go.Figure()
                radar_configs = [
                    {"line": "#4f46e5", "fill": "rgba(79, 70, 229, 0.12)"},
                    {"line": "#059669", "fill": "rgba(5, 150, 105, 0.12)"},
                    {"line": "#d97706", "fill": "rgba(217, 119, 6, 0.12)"},
                    {"line": "#7c3aed", "fill": "rgba(124, 58, 237, 0.12)"},
                ]
                for i, (_, row) in enumerate(results_df.iterrows()):
                    vals = [row[m] for m in metric_sel]
                    vals_closed = vals + [vals[0]]
                    cats_closed = metric_sel + [metric_sel[0]]
                    cfg = radar_configs[i % len(radar_configs)]
                    fig_radar.add_trace(go.Scatterpolar(
                        r=vals_closed,
                        theta=cats_closed,
                        fill="toself",
                        name=row["Modèle"],
                        line=dict(color=cfg["line"], width=2.5),
                        fillcolor=cfg["fill"],
                        opacity=0.85,
                    ))
                fig_radar.update_layout(
                    polar=dict(
                        bgcolor="#ffffff",
                        radialaxis=dict(visible=True, range=[0, 1], gridcolor="#e2e8f0", tickfont=dict(color="#64748b")),
                        angularaxis=dict(gridcolor="#e2e8f0", tickfont=dict(color="#334155")),
                    ),
                    paper_bgcolor="#ffffff",
                    font=dict(family="Plus Jakarta Sans, Inter, sans-serif", color="#334155"),
                    title="Radar comparatif des performances",
                    title_font_color="#0f172a",
                    legend=dict(font=dict(color="#334155")),
                    margin=dict(t=60, b=40, l=60, r=60),
                )
                st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar":False})

        with tab2:
            fig_roc = go.Figure()
            colors_roc = {"Random Forest":"#4f46e5","XGBoost":"#7c3aed",
                          "Régression Logistique":"#2563eb","Arbre de Décision":"#059669"}
            for name, (fpr, tpr, auc) in roc_data.items():
                fig_roc.add_trace(go.Scatter(
                    x=fpr, y=tpr, mode="lines",
                    name=f"{name} (AUC={auc:.4f})",
                    line=dict(color=colors_roc.get(name,"#4f46e5"), width=2.5),
                ))
            fig_roc.add_trace(go.Scatter(
                x=[0,1], y=[0,1], mode="lines",
                line=dict(color="#94a3b8", dash="dash"),
                name="Aléatoire",
            ))
            fig_roc.update_layout(**PLOTLY_LAYOUT,
                                   title="Courbes ROC - Comparaison",
                                   title_font_color="#0f172a",
                                   legend=dict(font=dict(color="#334155")))
            st.plotly_chart(fig_roc, use_container_width=True, config={"displayModeBar":False})

        with tab3:
            sort_metric = st.selectbox("Trier par", ["AUC-ROC","Accuracy","F1-Score","Précision","Rappel"], key="sort_metric")
            df_sorted = results_df.sort_values(sort_metric, ascending=True)

            fig_h = px.bar(df_sorted, x=sort_metric, y="Modèle", orientation="h",
                            color=sort_metric,
                            color_continuous_scale=["#e0e7ff", "#6366f1", "#312e81"],
                            text=sort_metric,
                            title=f"Classement par {sort_metric}")
            fig_h.update_traces(texttemplate="%{text:.4f}", textposition="outside")
            fig_h.update_layout(**PLOTLY_LAYOUT, title_font_color="#0f172a",
                                 coloraxis_showscale=False,
                                 xaxis_range=[0, 1.05])
            st.plotly_chart(fig_h, use_container_width=True, config={"displayModeBar":False})

            # Score cards
            st.markdown('<div style="color:#0f172a;font-size:1.05rem;font-weight:700;margin:20px 0 12px 0;">Cartes de performance synthétiques</div>', unsafe_allow_html=True)
            cols_score = st.columns(len(results_df))
            clrs = ["#4f46e5","#7c3aed","#2563eb","#059669"]
            for i, (_, row) in enumerate(results_df.iterrows()):
                with cols_score[i]:
                    badge = "⭐ Meilleur" if row["Modèle"] == best_model else ""
                    st.markdown(f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0;
                                border-top: 4px solid {clrs[i%4]};
                                border-radius:14px; padding:20px 16px; text-align:center; box-shadow:0 1px 4px rgba(0,0,0,0.03);">
                        <div style="color:{clrs[i%4]}; font-size:0.75rem; font-weight:700; text-transform:uppercase;
                                    letter-spacing:0.08em; min-height:18px; margin-bottom:4px;">{badge}</div>
                        <div style="color:#0f172a; font-weight:700; font-size:0.92rem; margin-bottom:10px;">{row["Modèle"]}</div>
                        <div style="color:{clrs[i%4]}; font-size:1.65rem; font-weight:800;">{row["AUC-ROC"]:.4f}</div>
                        <div style="color:#64748b; font-size:0.74rem; font-weight:600;">AUC-ROC</div>
                        <div style="margin-top:12px; color:#475569; font-size:0.8rem; line-height:1.75; border-top:1px solid #f1f5f9; padding-top:8px;">
                            Accuracy: <b>{row["Accuracy"]:.4f}</b><br>
                            F1-Score: <b>{row["F1-Score"]:.4f}</b><br>
                            Précision: <b>{row["Précision"]:.4f}</b><br>
                            Rappel: <b>{row["Rappel"]:.4f}</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
