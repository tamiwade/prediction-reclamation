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
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#c4c4e0"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)"),
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

@st.cache_data(show_spinner="Entrainement et evaluation de tous les modeles...")
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
        "Regression Logistique":(LogisticRegression(C=1.0, max_iter=1000, random_state=42), True),
        "Arbre de Decision":    (DecisionTreeClassifier(max_depth=8, random_state=42), False),
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
            "Modele": name,
            "Accuracy": round(acc, 4),
            "AUC-ROC":  round(auc, 4),
            "F1-Score": round(f1, 4),
            "Precision": round(prec, 4),
            "Recall":   round(rec, 4),
        })

        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_data[name] = (fpr, tpr, auc)

    return pd.DataFrame(results).sort_values("AUC-ROC", ascending=False), roc_data

def show():
    st.markdown('<div style="color:#e0e0ff;font-size:1.8rem;font-weight:800;margin-bottom:6px;">Comparaison des Modeles</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:rgba(224,224,255,0.5);font-size:0.95rem;margin-bottom:28px;">Evaluez et comparez les performances de tous les modeles</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("---")
        st.markdown('<p style="color:rgba(224,224,255,0.35);font-size:0.72rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;">Parametres comparaison</p>', unsafe_allow_html=True)
        test_size  = st.slider("Taille du test set (%)", 10, 40, 20, key="cmp_test") / 100
        rand_state = st.number_input("Random state", 0, 999, 42, key="cmp_rand")

    run = st.button("Comparer tous les modeles", key="compare_btn", type="primary")

    if run or "compare_results" in st.session_state:
        if run:
            results_df, roc_data = compare_all_models(test_size, rand_state)
            st.session_state.compare_results = (results_df, roc_data)
        else:
            results_df, roc_data = st.session_state.compare_results

        best_model = results_df.iloc[0]["Modele"]
        best_auc   = results_df.iloc[0]["AUC-ROC"]

        st.success(f"Meilleur modele : **{best_model}** (AUC = {best_auc:.4f})")

        # ── Tableau recap ──────────────────────────────────────────────────
        st.markdown('<div style="color:#e0e0ff;font-size:1.05rem;font-weight:700;margin:20px 0 12px 0;">Tableau des performances</div>', unsafe_allow_html=True)

        def highlight_best(s):
            if s.name in ["Accuracy","AUC-ROC","F1-Score","Precision","Recall"]:
                max_val = s.max()
                return ["background: rgba(99,102,241,0.25); color:#818cf8; font-weight:700"
                        if v == max_val else "" for v in s]
            return [""] * len(s)

        styled = results_df.style.apply(highlight_best).format({
            "Accuracy":  "{:.4f}",
            "AUC-ROC":  "{:.4f}",
            "F1-Score": "{:.4f}",
            "Precision":"{:.4f}",
            "Recall":   "{:.4f}",
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

        tab1, tab2, tab3 = st.tabs(["Comparaison des metriques", "Courbes ROC", "Classement visuel"])

        with tab1:
            metrics = ["Accuracy","AUC-ROC","F1-Score","Precision","Recall"]
            metric_sel = st.multiselect("Metriques a afficher", metrics, default=metrics, key="metric_sel")

            if metric_sel:
                df_melt = results_df.melt(id_vars="Modele", value_vars=metric_sel,
                                           var_name="Metrique", value_name="Score")
                fig_bar = px.bar(df_melt, x="Modele", y="Score", color="Metrique",
                                  barmode="group", text_auto=".3f",
                                  color_discrete_sequence=["#818cf8","#c084fc","#38bdf8","#34d399","#fb923c"],
                                  title="Comparaison des metriques par modele")
                fig_bar.update_layout(**PLOTLY_LAYOUT, title_font_color="#e0e0ff",
                                       legend=dict(font=dict(color="#c4c4e0")),
                                       yaxis_range=[0, 1.05])
                st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar":False})

                # Radar chart
                fig_radar = go.Figure()
                radar_configs = [
                    {"line": "#3b82f6", "fill": "rgba(59, 130, 246, 0.18)"},
                    {"line": "#10b981", "fill": "rgba(16, 185, 129, 0.18)"},
                    {"line": "#f59e0b", "fill": "rgba(245, 158, 11, 0.18)"},
                    {"line": "#8b5cf6", "fill": "rgba(139, 92, 246, 0.18)"},
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
                        name=row["Modele"],
                        line=dict(color=cfg["line"], width=2),
                        fillcolor=cfg["fill"],
                        opacity=0.85,
                    ))
                fig_radar.update_layout(
                    polar=dict(
                        bgcolor="rgba(30,41,59,0.3)",
                        radialaxis=dict(visible=True, range=[0, 1], gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="#94a3b8")),
                        angularaxis=dict(gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="#cbd5e1")),
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Plus Jakarta Sans, Inter, sans-serif", color="#cbd5e1"),
                    title="Radar comparatif des performances",
                    title_font_color="#f8fafc",
                    legend=dict(font=dict(color="#cbd5e1")),
                    margin=dict(t=60, b=40, l=60, r=60),
                )
                st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar":False})

        with tab2:
            fig_roc = go.Figure()
            colors_roc = {"Random Forest":"#818cf8","XGBoost":"#c084fc",
                          "Regression Logistique":"#38bdf8","Arbre de Decision":"#34d399"}
            for name, (fpr, tpr, auc) in roc_data.items():
                fig_roc.add_trace(go.Scatter(
                    x=fpr, y=tpr, mode="lines",
                    name=f"{name} (AUC={auc:.4f})",
                    line=dict(color=colors_roc.get(name,"#818cf8"), width=2.5),
                ))
            fig_roc.add_trace(go.Scatter(
                x=[0,1], y=[0,1], mode="lines",
                line=dict(color="rgba(255,255,255,0.25)", dash="dash"),
                name="Aleatoire",
            ))
            fig_roc.update_layout(**PLOTLY_LAYOUT,
                                   title="Courbes ROC - Comparaison",
                                   title_font_color="#e0e0ff",
                                   legend=dict(font=dict(color="#c4c4e0")))
            st.plotly_chart(fig_roc, use_container_width=True, config={"displayModeBar":False})

        with tab3:
            sort_metric = st.selectbox("Trier par", ["AUC-ROC","Accuracy","F1-Score","Precision","Recall"], key="sort_metric")
            df_sorted = results_df.sort_values(sort_metric, ascending=True)

            fig_h = px.bar(df_sorted, x=sort_metric, y="Modele", orientation="h",
                            color=sort_metric,
                            color_continuous_scale=["#302b63","#6366f1","#c084fc"],
                            text=sort_metric,
                            title=f"Classement par {sort_metric}")
            fig_h.update_traces(texttemplate="%{text:.4f}", textposition="outside")
            fig_h.update_layout(**PLOTLY_LAYOUT, title_font_color="#e0e0ff",
                                 coloraxis_showscale=False,
                                 xaxis_range=[0, 1.05])
            st.plotly_chart(fig_h, use_container_width=True, config={"displayModeBar":False})

            # Score cards
            st.markdown('<div style="color:#e0e0ff;font-size:1rem;font-weight:700;margin:20px 0 12px 0;">Cartes de performance</div>', unsafe_allow_html=True)
            cols_score = st.columns(len(results_df))
            clrs = ["#818cf8","#c084fc","#38bdf8","#34d399"]
            for i, (_, row) in enumerate(results_df.iterrows()):
                with cols_score[i]:
                    badge = "Meilleur" if row["Modele"] == best_model else ""
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);
                                border-top: 3px solid {clrs[i%4]};
                                border-radius:14px;padding:20px 16px;text-align:center;">
                        <div style="color:{clrs[i%4]};font-size:0.7rem;font-weight:600;text-transform:uppercase;
                                    letter-spacing:0.08em;margin-bottom:6px;">{badge}</div>
                        <div style="color:#e0e0ff;font-weight:700;font-size:0.88rem;margin-bottom:12px;">{row["Modele"]}</div>
                        <div style="color:{clrs[i%4]};font-size:1.6rem;font-weight:800;">{row["AUC-ROC"]:.4f}</div>
                        <div style="color:rgba(224,224,255,0.4);font-size:0.72rem;">AUC-ROC</div>
                        <div style="margin-top:12px;color:rgba(224,224,255,0.6);font-size:0.78rem;line-height:1.8;">
                            Acc: {row["Accuracy"]:.4f}<br>
                            F1: {row["F1-Score"]:.4f}<br>
                            Prec: {row["Precision"]:.4f}<br>
                            Rec: {row["Recall"]:.4f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
