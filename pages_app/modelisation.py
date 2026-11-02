import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (accuracy_score, classification_report,
                              confusion_matrix, roc_auc_score, roc_curve)
try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

from utils_export import export_to_excel, export_model_joblib, generate_pdf_report

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#c4c4e0"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)"),
    margin=dict(t=50, b=40, l=40, r=20),
)

def get_current_df():
    df = st.session_state.get("df", None)
    if df is not None:
        return df
    try:
        return pd.read_csv("Car_Insurance_Claim-2.csv")
    except Exception:
        return pd.DataFrame()

def preprocess(test_size, random_state):
    df = get_current_df()
    df2 = df.drop(columns=["ID"], errors="ignore").copy().dropna()

    cat_cols = df2.select_dtypes(include="object").columns.tolist()
    le = LabelEncoder()
    for c in cat_cols:
        df2[c] = le.fit_transform(df2[c].astype(str))

    target_col = "OUTCOME" if "OUTCOME" in df2.columns else df2.columns[-1]
    X = df2.drop(columns=[target_col])
    y = df2[target_col].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    return X_train, X_test, X_train_s, X_test_s, y_train, y_test, X.columns.tolist()

def train_model(model_name, X_train, X_test, X_train_s, X_test_s, y_train, y_test,
                n_estimators=100, max_depth=5, lr_C=1.0, xgb_lr=0.1):
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth if max_depth > 0 else None, random_state=42, n_jobs=-1),
        "Regression Logistique": LogisticRegression(C=lr_C, max_iter=1000, random_state=42),
        "Arbre de Decision": DecisionTreeClassifier(max_depth=max_depth if max_depth > 0 else None, random_state=42),
    }
    if HAS_XGB:
        models["XGBoost"] = XGBClassifier(n_estimators=n_estimators, max_depth=max_depth if max_depth > 0 else 6,
                                           learning_rate=xgb_lr, use_label_encoder=False,
                                           eval_metric="logloss", random_state=42, verbosity=0)

    model = models[model_name]
    needs_scale = model_name in ["Regression Logistique"]
    Xt = X_train_s if needs_scale else X_train
    Xs = X_test_s  if needs_scale else X_test

    model.fit(Xt, y_train)
    y_pred = model.predict(Xs)
    y_proba = model.predict_proba(Xs)[:, 1] if hasattr(model, "predict_proba") else None

    acc   = accuracy_score(y_test, y_pred)
    auc   = roc_auc_score(y_test, y_proba) if y_proba is not None else None
    cm    = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)

    feature_imp = None
    if hasattr(model, "feature_importances_"):
        feature_imp = model.feature_importances_

    return model, y_pred, y_proba, acc, auc, cm, report, feature_imp, Xt, Xs

def show():
    df = get_current_df()

    st.markdown("""
    <div style="margin-bottom:20px;">
        <div style="color:#f8fafc;font-size:1.8rem;font-weight:800;letter-spacing:-0.5px;">
            Modélisation Prédictive & Évaluation des Modèles
        </div>
        <div style="color:#94a3b8;font-size:0.92rem;margin-top:3px;">
            Sélectionnez un modèle de Machine Learning, configurez ses hyperparamètres et évaluez ses performances décisionnelles
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Panneau de configuration principal (Directement sur la page) ───────────
    st.markdown("""
    <div style="background:rgba(30,41,59,0.5);border:1px solid rgba(255,255,255,0.08);
                border-radius:12px;padding:20px 24px;margin-bottom:20px;">
        <div style="color:#38bdf8;font-weight:700;font-size:1rem;margin-bottom:14px;">
            1. Sélection du Modèle de Machine Learning
        </div>
    </div>
    """, unsafe_allow_html=True)

    available_models = ["Random Forest", "Régression Logistique", "Arbre de Décision"]
    if HAS_XGB:
        available_models.insert(1, "XGBoost")

    col_m1, col_m2 = st.columns([3, 2])

    with col_m1:
        model_name = st.radio(
            "Sélectionnez le modèle à entraîner :",
            available_models,
            index=0,
            horizontal=False,
            key="main_model_select"
        )

    with col_m2:
        model_descriptions = {
            "Random Forest": "🌲 **Random Forest** : Ensemble d'arbres de décision par bagging. Réduit la variance, très robuste contre le surapprentissage et capture les interactions non-linéaires complexes.",
            "XGBoost": "⚡ **XGBoost** : Gradient Boosting d'arbres décisionnels. Algorithme de référence pour données tabulaires, offrant une excellente capacité de discrimination et convergence rapide.",
            "Régression Logistique": "📈 **Régression Logistique** : Modèle linéaire probabiliste avec normalisation StandardScaler. Idéal pour estimer les probabilités de risque et interpréter le sens des coefficients.",
            "Arbre de Décision": "🌳 **Arbre de Décision** : Modèle CART intuitif découpant l'espace des données selon des seuils optimaux. Règles d'arbitrage lisibles et facilement vérifiables."
        }
        st.info(model_descriptions.get(model_name, ""))

    st.markdown("""
    <div style="background:rgba(30,41,59,0.3);border:1px solid rgba(255,255,255,0.06);
                border-radius:10px;padding:16px 20px;margin:16px 0 20px 0;">
        <div style="color:#f8fafc;font-weight:600;font-size:0.9rem;margin-bottom:10px;">
            2. Partition des Données & Hyperparamètres de l'Algorithme
        </div>
    </div>
    """, unsafe_allow_html=True)

    p1, p2, p3 = st.columns(3)
    with p1:
        test_size = st.slider("Taille de l'échantillon test (%)", 10, 40, 20, key="main_test_size") / 100
        rand_state = st.number_input("Graine aléatoire (Random state)", 0, 999, 42, key="main_rand_state")

    with p2:
        if model_name in ["Random Forest", "XGBoost"]:
            n_est = st.slider("Nombre d'arbres (n_estimators)", 50, 400, 100, 25, key="main_n_est")
            max_d = st.slider("Profondeur maximale (max_depth)", 2, 20, 6, key="main_max_d")
            lr_C = 1.0
            xgb_lr = 0.1
        elif model_name == "Régression Logistique":
            lr_C = st.slider("Inverse de la régularisation (C)", 0.01, 10.0, 1.0, 0.1, key="main_lr_c")
            n_est = 100
            max_d = 5
            xgb_lr = 0.1
        else: # Arbre de décision
            max_d = st.slider("Profondeur maximale (max_depth)", 2, 20, 5, key="main_dt_d")
            n_est = 100
            lr_C = 1.0
            xgb_lr = 0.1

    with p3:
        if model_name == "XGBoost":
            xgb_lr = st.slider("Taux d'apprentissage (learning_rate)", 0.01, 0.4, 0.1, 0.02, key="main_xgb_lr")
        st.markdown("<br>", unsafe_allow_html=True)
        run_btn = st.button("🚀 Entraîner le Modèle Machine Learning", key="main_train_btn", type="primary")

    # Mémorisation du modèle entraîné
    model_key = f"trained_{model_name.replace(' ', '_')}"
    
    if run_btn or model_key in st.session_state:
        X_train, X_test, X_train_s, X_test_s, y_train, y_test, feat_names = preprocess(test_size, rand_state)

        if run_btn:
            with st.spinner(f"Entraînement de {model_name} en cours..."):
                train_name = "Regression Logistique" if "Régression" in model_name else ("Arbre de Decision" if "Arbre" in model_name else model_name)
                result = train_model(train_name, X_train, X_test, X_train_s, X_test_s,
                                     y_train, y_test, n_est, max_d, lr_C, xgb_lr)
            st.session_state[model_key] = (model_name, result, feat_names)
            st.session_state.active_model = model_key

        active_k = st.session_state.get("active_model", model_key)
        if active_k in st.session_state:
            model_name, result, feat_names = st.session_state[active_k]
        else:
            model_name, result, feat_names = st.session_state[model_key]

        _, y_pred, y_proba, acc, auc, cm, report, feature_imp, _, _ = result

        st.markdown("---")
        st.markdown(f'<div style="color:#f8fafc;font-size:1.2rem;font-weight:700;margin-bottom:16px;">Résultats de performance : <span style="color:#38bdf8;">{model_name}</span></div>', unsafe_allow_html=True)

        m1,m2,m3,m4 = st.columns(4)
        with m1: st.metric("Accuracy", f"{acc:.4f}", f"{acc*100:.2f}%")
        with m2: st.metric("AUC-ROC", f"{auc:.4f}" if auc else "N/A")
        with m3:
            prec = report.get("1",{}).get("precision",0)
            st.metric("Précision (classe 1)", f"{prec:.4f}")
        with m4:
            rec = report.get("1",{}).get("recall",0)
            st.metric("Rappel (classe 1)", f"{rec:.4f}")

        tab1, tab2, tab3, tab4 = st.tabs(["Matrice de confusion","Courbe ROC","Rapport de classification","Importance des variables"])

        with tab1:
            fig_cm = px.imshow(cm, text_auto=True,
                               color_continuous_scale=["#0f0c29","#302b63","#818cf8"],
                               title="Matrice de confusion",
                               labels=dict(x="Prédit", y="Réel"),
                               x=["Sans récl. (0)","Réclamation (1)"],
                               y=["Sans récl. (0)","Réclamation (1)"])
            fig_cm.update_layout(**PLOTLY_LAYOUT, title_font_color="#e0e0ff",
                                  coloraxis_showscale=False, height=380)
            st.plotly_chart(fig_cm, use_container_width=True, config={"displayModeBar":False})

        with tab2:
            if y_proba is not None:
                fpr, tpr, _ = roc_curve(y_test, y_proba)
                fig_roc = go.Figure()
                fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines",
                                              line=dict(color="#818cf8", width=2.5),
                                              name=f"AUC = {auc:.4f}"))
                fig_roc.add_trace(go.Scatter(x=[0,1], y=[0,1], mode="lines",
                                              line=dict(color="rgba(255,255,255,0.3)", dash="dash"),
                                              name="Aléatoire"))
                fig_roc.update_layout(**PLOTLY_LAYOUT, title="Courbe ROC",
                                       title_font_color="#e0e0ff",
                                       legend=dict(font=dict(color="#c4c4e0")))
                st.plotly_chart(fig_roc, use_container_width=True, config={"displayModeBar":False})
            else:
                st.info("Courbe ROC non disponible pour ce modèle.")

        with tab3:
            rep_df = pd.DataFrame(report).T.round(4)
            st.dataframe(rep_df, use_container_width=True)

        with tab4:
            if feature_imp is not None:
                fi_df = pd.DataFrame({"Variable": feat_names, "Importance": feature_imp})
                fi_df = fi_df.sort_values("Importance", ascending=False).head(15)
                fig_fi = px.bar(fi_df, x="Importance", y="Variable", orientation="h",
                                color="Importance",
                                color_continuous_scale=["#302b63","#818cf8","#c084fc"],
                                title="Top 15 variables les plus importantes")
                fig_fi.update_layout(**PLOTLY_LAYOUT, title_font_color="#e0e0ff",
                                      coloraxis_showscale=False, height=450)
                st.plotly_chart(fig_fi, use_container_width=True, config={"displayModeBar":False})
            else:
                st.info("L'importance des variables n'est pas disponible pour ce modèle.")

        st.markdown("---")
        st.markdown('<div style="color:#e0e0ff;font-size:1.1rem;font-weight:700;margin-bottom:12px;">Centre d\'exportation des résultats & Modèle</div>', unsafe_allow_html=True)
        col_exp1, col_exp2, col_exp3 = st.columns(3)

        with col_exp1:
            model_bytes = export_model_joblib(result[0])
            st.download_button(
                label="💾 Télécharger le Modèle (.joblib)",
                data=model_bytes,
                file_name=f"modele_{model_name.lower().replace(' ', '_')}.joblib",
                mime="application/octet-stream",
                use_container_width=True,
                help="Fichier binaire du modèle prêt pour un déploiement API ou production"
            )

        with col_exp2:
            metrics_df = pd.DataFrame([{
                "Modele": model_name,
                "Accuracy": acc,
                "AUC-ROC": auc if auc else "N/A",
                "Precision": report.get("1", {}).get("precision", 0),
                "Recall": report.get("1", {}).get("recall", 0),
                "F1-Score": report.get("1", {}).get("f1-score", 0)
            }])
            excel_metrics = export_to_excel({
                "Performances": metrics_df,
                "Rapport_Detaille": pd.DataFrame(report).T.reset_index().rename(columns={"index": "Classe"}),
                "Matrice_Confusion": pd.DataFrame(cm, index=["Reel_0", "Reel_1"], columns=["Predit_0", "Predit_1"]).reset_index()
            })
            st.download_button(
                label="📊 Exporter les métriques (.xlsx)",
                data=excel_metrics,
                file_name=f"performances_{model_name.lower().replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help="Tableau Excel avec toutes les métriques et matrices"
            )

        with col_exp3:
            tgt = "OUTCOME" if "OUTCOME" in df.columns else df.columns[-1]
            n_cl = int(df[tgt].sum()) if pd.api.types.is_numeric_dtype(df[tgt]) else 0
            rt = round((n_cl / len(df)) * 100, 1) if len(df) > 0 else 0
            pdf_bytes = generate_pdf_report(
                title=f"Rapport d'Audit ML - {model_name}",
                dataset_kpis={"total": len(df), "claims": n_cl, "rate": rt},
                models_df=pd.DataFrame([{
                    "Modele": model_name,
                    "Accuracy": f"{acc:.4f}",
                    "AUC-ROC": f"{auc:.4f}" if auc else "N/A",
                    "F1-Score": f"{report.get('1', {}).get('f1-score', 0):.4f}",
                    "Precision": f"{report.get('1', {}).get('precision', 0):.4f}",
                    "Recall": f"{report.get('1', {}).get('recall', 0):.4f}"
                }]),
                selected_model_name=model_name
            )
            st.download_button(
                label="📄 Télécharger le Rapport (.pdf)",
                data=pdf_bytes,
                file_name=f"rapport_{model_name.lower().replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                help="Rapport PDF complet avec synthèse et recommandations"
            )

        st.markdown("---")
        st.markdown('<div style="color:#e0e0ff;font-size:1.1rem;font-weight:700;margin-bottom:16px;">Simulation & Prédiction sur un Nouvel Assuré</div>', unsafe_allow_html=True)

        with st.expander("Saisir les caractéristiques du contrat et du conducteur", expanded=True):
            c1,c2,c3 = st.columns(3)

            with c1:
                age     = st.selectbox("Tranche d'âge", ["16-25","26-39","40-64","65+"], key="p_age")
                gender  = st.selectbox("Genre", ["male","female"], key="p_gender")
                race    = st.selectbox("Catégorie sociodémographique", ["majority","minority"], key="p_race")
                drive_exp = st.selectbox("Expérience de conduite", ["0-9y","10-19y","20-29y","30y+"], key="p_drive")
                educ    = st.selectbox("Niveau d'études", ["high school","none","university"], key="p_educ")
                income  = st.selectbox("Niveau de revenu", ["poverty","working class","middle class","upper class"], key="p_income")

            with c2:
                credit  = st.slider("Score de crédit", 0.0, 1.0, 0.5, 0.01, key="p_credit")
                vehicle_own = st.selectbox("Propriétaire du véhicule (1=Oui, 0=Non)", [0,1], key="p_vown")
                vehicle_year = st.selectbox("Année du véhicule", ["before 2015","after 2015"], key="p_vyear")
                married = st.selectbox("Statut marital (1=Marié, 0=Célibataire)", [0,1], key="p_married")
                children = st.selectbox("Enfants à charge (1=Oui, 0=Non)", [0,1], key="p_children")
                postal  = st.selectbox("Code postal", [10238,32765,92101], key="p_postal")

            with c3:
                mileage = st.number_input("Kilométrage annuel estimé", 2000, 25000, 12000, 500, key="p_mileage")
                vtype   = st.selectbox("Type de carrosserie", ["sedan","sports car"], key="p_vtype")
                speeding = st.number_input("Infractions pour excès de vitesse", 0, 20, 0, key="p_speed")
                duis    = st.number_input("Conduite sous influence (DUI)", 0, 10, 0, key="p_duis")
                past_acc = st.number_input("Nombre d'accidents passés", 0, 15, 0, key="p_acc")

            if st.button("🎯 Calculer le Risque & Prédire", key="predict_btn", type="primary"):
                sample_data = {
                    "AGE": age, "GENDER": gender, "RACE": race,
                    "DRIVING_EXPERIENCE": drive_exp, "EDUCATION": educ, "INCOME": income,
                    "CREDIT_SCORE": credit, "VEHICLE_OWNERSHIP": float(vehicle_own),
                    "VEHICLE_YEAR": vehicle_year, "MARRIED": float(married),
                    "CHILDREN": float(children), "POSTAL_CODE": postal,
                    "ANNUAL_MILEAGE": float(mileage), "VEHICLE_TYPE": vtype,
                    "SPEEDING_VIOLATIONS": speeding, "DUIS": duis, "PAST_ACCIDENTS": past_acc
                }
                sample_df = pd.DataFrame([sample_data])

                # Re-encode like training
                target_col = "OUTCOME" if "OUTCOME" in df.columns else df.columns[-1]
                df_enc = get_current_df().drop(columns=["ID", target_col], errors="ignore").dropna()
                for col in df_enc.select_dtypes(include="object").columns:
                    le = LabelEncoder()
                    le.fit(df_enc[col].astype(str))
                    if col in sample_df.columns:
                        val = str(sample_df[col].iloc[0])
                        if val in le.classes_:
                            sample_df[col] = le.transform([val])
                        else:
                            sample_df[col] = 0

                expected_cols = feat_names
                for col in expected_cols:
                    if col not in sample_df.columns:
                        sample_df[col] = 0
                sample_df = sample_df[expected_cols]

                model_obj = result[0]
                needs_scale = model_name in ["Regression Logistique", "Régression Logistique"]
                if needs_scale:
                    from sklearn.preprocessing import StandardScaler
                    sc2 = StandardScaler()
                    df_train_raw = get_current_df().drop(columns=["ID", target_col], errors="ignore").dropna()
                    for col in df_train_raw.select_dtypes(include="object").columns:
                        le2 = LabelEncoder()
                        df_train_raw[col] = le2.fit_transform(df_train_raw[col].astype(str))
                    sc2.fit(df_train_raw)
                    sample_df = sc2.transform(sample_df)

                prediction = model_obj.predict(sample_df)[0]
                proba_val = model_obj.predict_proba(sample_df)[0][1] if hasattr(model_obj,"predict_proba") else None

                if prediction == 1:
                    st.markdown(f"""
                    <div style="background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.4);
                                border-radius:14px;padding:20px 24px;text-align:center;">
                        <div style="font-size:2rem;">⚠️</div>
                        <div style="color:#ef4444;font-size:1.2rem;font-weight:700;margin-top:8px;">
                            Risque Élevé : Réclamation Probable</div>
                        <div style="color:rgba(224,224,255,0.8);font-size:0.95rem;margin-top:4px;">
                            {'Probabilité estimée : ' + f'{proba_val*100:.1f}%' if proba_val else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background:rgba(52,211,153,0.12);border:1px solid rgba(52,211,153,0.35);
                                border-radius:14px;padding:20px 24px;text-align:center;">
                        <div style="font-size:2rem;">✓</div>
                        <div style="color:#34d399;font-size:1.2rem;font-weight:700;margin-top:8px;">
                            Profil Favorable : Pas de Réclamation Prévue</div>
                        <div style="color:rgba(224,224,255,0.8);font-size:0.95rem;margin-top:4px;">
                            {'Probabilité de réclamation : ' + f'{proba_val*100:.1f}%' if proba_val else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
