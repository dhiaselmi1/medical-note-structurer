import streamlit as st
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import io  # Pour gérer le téléchargement de fichiers encodés

# --- Configuration de la Page Streamlit ---
st.set_page_config(
    page_title="Medical Note Structurer",
    page_icon="🏥",
    layout="wide",  # Utilise toute la largeur de l'écran
    initial_sidebar_state="expanded"  # Ouvre la sidebar par défaut
)

# --- CSS Personnalisé pour une meilleure UI ---
st.markdown("""
<style>
    /* Couleur de fond générale de l'application */
    .stApp {
        background-color: #f0f2f6; /* Gris très clair */
    }
    /* Style pour le conteneur principal du rapport */
    .reportview-container .main {
        background-color: #f0f2f6;
    }
    /* Ajustements du padding du contenu principal */
    .css-1d391kg { /* Selecteur Streamlit pour le padding du main content */
        padding-top: 3rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 3rem;
    }
    /* Style pour les boîtes de message (success, error, warning) */
    .stAlert {
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); /* Légère ombre */
    }
    /* Couleurs pour les titres */
    h1, h2, h3, h4, h5, h6 {
        color: #004d40; /* Vert foncé/Bleu canard */
    }
    /* Style pour les boutons Streamlit */
    .stButton>button {
        background-color: #00796b; /* Vert canard standard */
        color: white;
        border-radius: 0.5rem;
        border: none;
        padding: 0.6rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease; /* Transition douce pour l'hover */
    }
    .stButton>button:hover {
        background-color: #004d40; /* Vert canard plus foncé au survol */
        color: white;
        transform: translateY(-2px); /* Léger soulèvement */
        box-shadow: 0 6px 12px rgba(0,0,0,0.2); /* Ombre plus prononcée */
    }
    /* Style pour la zone de téléchargement de fichiers */
    .stFileUploader {
        border: 2px dashed #00796b; /* Bordure en pointillé */
        border-radius: 0.5rem;
        padding: 1.5rem;
        text-align: center;
        background-color: #e0f2f1; /* Fond très clair pour la zone */
    }
    /* Styles pour la barre de progression */
    .stProgress > div > div > div > div {
        background-color: #00796b;
    }
</style>
""", unsafe_allow_html=True)

# --- Section d'Entête ---
st.markdown("<h1 style='text-align: center;'>🏥 Medical Note Structurer</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Leveraging LLMs for Automated Clinical Data Extraction</h3>",
            unsafe_allow_html=True)
st.info(
    "Upload your clinical notes CSV file to automatically extract structured information like Symptoms, Diagnosis, Medications, and Follow-up Instructions. Ensure your CSV has columns named 'patient_id' and 'doctor_notes'.")

# --- Section de Téléchargement de Fichier ---
st.subheader("Upload Your Data")
uploaded_file = st.file_uploader("Select a CSV file containing clinical notes", type="csv",
                                 help="Your CSV should have 'patient_id' and 'doctor_notes' columns.")

# --- Logique Principale de l'Application ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # --- Validation des Colonnes ---
    required_cols = ["patient_id", "doctor_notes"]
    if not all(col in df.columns for col in required_cols):
        st.error(
            f"Error: The uploaded CSV must contain both '{required_cols[0]}' and '{required_cols[1]}' columns. Detected columns: {df.columns.tolist()}")
        # Arrêter l'exécution si les colonnes nécessaires ne sont pas là
        st.stop()
    else:
        st.success(f"CSV uploaded successfully! Showing first 5 rows.")
        st.dataframe(df.head())  # Afficher les premières lignes des données originales

        # --- Initialisation pour l'Extraction ---
        results = []  # Liste pour stocker les résultats structurés
        failed_extractions = 0
        total_notes = len(df)

        st.markdown("---")  # Séparateur
        st.subheader("Extraction Progress")

        progress_text = "Extraction en cours. Veuillez patienter..."
        my_bar = st.progress(0, text=progress_text)

        # --- Boucle d'Extraction des Notes ---
        for index, row in df.iterrows():
            current_patient_id = row.get("patient_id", f"Row {index}")  # Utilise patient_id ou l'index

            try:
                # Appel à l'API FastAPI
                response = requests.post(
                    "http://localhost:8000/extract/",
                    data={"note": row["doctor_notes"]}  # Assurez-vous que le nom de la colonne est 'doctor_notes'
                )
                response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP (4xx ou 5xx)
                extracted_json_str = response.json()["structured"]

                # Parsing du JSON (la fonction query_llama est censée renvoyer du JSON strict)
                structured_data = json.loads(extracted_json_str)

                # --- Conversion Robuste des Listes en Chaînes et Vérification des Clés ---
                # On s'assure que chaque champ est une chaîne pour le DataFrame final
                for key in ['Symptoms', 'Diagnosis', 'Medications', 'Follow-up Instructions']:
                    if key in structured_data:
                        if isinstance(structured_data[key], list):
                            structured_data[key] = ", ".join(map(str, structured_data[
                                key]))  # map(str, ...) pour convertir les éléments de la liste en string avant le join
                        elif not isinstance(structured_data[key], str):
                            structured_data[key] = str(structured_data[key])
                    else:
                        structured_data[key] = "N/A"  # Valeur par défaut si la clé est manquante

            except requests.exceptions.RequestException as e:
                st.error(
                    f"Erreur de connexion à l'API pour le patient {current_patient_id}: {e}. Assurez-vous que l'API FastAPI est lancée sur http://localhost:8000.")
                structured_data = {"Symptoms": "API Error", "Diagnosis": "API Error", "Medications": "API Error",
                                   "Follow-up Instructions": "API Error"}
                failed_extractions += 1
            except json.JSONDecodeError as e:
                st.warning(
                    f"Erreur de parsing JSON pour le patient {current_patient_id}: {e}. Réponse reçue: {extracted_json_str[:500]}...")
                structured_data = {"Symptoms": "JSON Error", "Diagnosis": "JSON Error", "Medications": "JSON Error",
                                   "Follow-up Instructions": "JSON Error"}
                failed_extractions += 1
            except KeyError as e:
                st.error(
                    f"Erreur de clé manquante dans le DataFrame ou la réponse API pour le patient {current_patient_id}: {e}. Vérifiez les noms de colonnes dans votre CSV ('patient_id', 'doctor_notes') et la structure JSON de l'API.")
                structured_data = {"Symptoms": "Data Error", "Diagnosis": "Data Error", "Medications": "Data Error",
                                   "Follow-up Instructions": "Data Error"}
                failed_extractions += 1
            except Exception as e:
                st.error(f"Une erreur inattendue est survenue pour le patient {current_patient_id}: {e}")
                structured_data = {"Symptoms": "Unexpected Error", "Diagnosis": "Unexpected Error",
                                   "Medications": "Unexpected Error", "Follow-up Instructions": "Unexpected Error"}
                failed_extractions += 1

            results.append({
                "patient_id": row["patient_id"],
                **structured_data
            })
            my_bar.progress((index + 1) / total_notes,
                            text=f"Processing note {index + 1} of {total_notes} for Patient ID: {current_patient_id}...")

        my_bar.empty()  # Masquer la barre de progression après la complétion

        result_df = pd.DataFrame(results)

        # --- Résumé de l'Extraction ---
        if failed_extractions == 0:
            st.success(f"Extraction complète ! Toutes les {total_notes} notes ont été structurées avec succès.")
        else:
            st.warning(
                f"Extraction terminée avec des erreurs. {total_notes - failed_extractions} notes structurées sur {total_notes}. Vérifiez les messages d'erreur ci-dessus pour les détails.")

        # --- Visualisations Front-End ---
        st.markdown("---")
        st.header("Extracted Data Overview & Visualizations")

        # Visualisation 1: Top Diagnoses
        if not result_df['Diagnosis'].eq('N/A').all() and not result_df['Diagnosis'].eq('API Error').all() and not \
        result_df['Diagnosis'].eq('JSON Error').all():
            st.subheader("Top 5 Diagnoses")
            diag_counts = result_df['Diagnosis'].value_counts().head(5)
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            sns.barplot(x=diag_counts.index, y=diag_counts.values, ax=ax1, palette="viridis")
            ax1.set_ylabel("Number of Patients")
            ax1.set_xlabel("Diagnosis")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig1)
        else:
            st.info(
                "Impossible de visualiser les diagnostics car les données sont absentes ou contiennent des erreurs.")

        # Préparation des données pour les symptômes et médicaments (split, flatten, count)
        clean_symptoms = result_df['Symptoms'].loc[~result_df['Symptoms'].isin(['N/A', 'API Error', 'JSON Error'])]
        clean_medications = result_df['Medications'].loc[
            ~result_df['Medications'].isin(['N/A', 'API Error', 'JSON Error'])]

        all_symptoms = Counter()
        for s_list_str in clean_symptoms.dropna():
            for s in s_list_str.split(', '):
                if s.strip():  # S'assurer que le symptôme n'est pas vide
                    all_symptoms[s.strip()] += 1

        all_medications = Counter()
        for m_list_str in clean_medications.dropna():
            for m in m_list_str.split(', '):
                if m.strip():  # S'assurer que le médicament n'est pas vide
                    all_medications[m.strip()] += 1

        col1_viz, col2_viz = st.columns(2)

        with col1_viz:
            # Visualisation 2: Top 10 Reported Symptoms
            if all_symptoms:
                st.subheader("Top 10 Reported Symptoms")
                top_symptoms_df = pd.DataFrame(all_symptoms.most_common(10), columns=['Symptom', 'Count'])
                fig2, ax2 = plt.subplots(figsize=(10, 6))
                sns.barplot(x=top_symptoms_df['Count'], y=top_symptoms_df['Symptom'], ax=ax2, palette="plasma")
                ax2.set_xlabel("Number of Reports")
                ax2.set_ylabel("Symptom")
                plt.tight_layout()
                st.pyplot(fig2)
            else:
                st.info(
                    "Impossible de visualiser les symptômes car les données sont absentes ou contiennent des erreurs.")

        with col2_viz:
            # Visualisation 3: Top 10 Prescribed Medications
            if all_medications:
                st.subheader("Top 10 Prescribed Medications")
                top_medications_df = pd.DataFrame(all_medications.most_common(10), columns=['Medication', 'Count'])
                fig3, ax3 = plt.subplots(figsize=(10, 6))
                sns.barplot(x=top_medications_df['Count'], y=top_medications_df['Medication'], ax=ax3, palette="magma")
                ax3.set_xlabel("Number of Prescriptions")
                ax3.set_ylabel("Medication")
                plt.tight_layout()
                st.pyplot(fig3)
            else:
                st.info(
                    "Impossible de visualiser les médicaments car les données sont absentes ou contiennent des erreurs.")

        # --- Tableau de Données Structurées ---
        st.header("Structured Clinical Notes Table")
        st.dataframe(result_df, use_container_width=True)  # Utilise la largeur complète du conteneur

        # --- Bouton de Téléchargement ---
        st.download_button(
            label="Download Structured Notes CSV",
            data=result_df.to_csv(index=False).encode('utf-8'),  # Encode en UTF-8
            file_name="structured_medical_notes.csv",
            mime="text/csv"
        )
else:
    st.info("Veuillez télécharger un fichier CSV pour commencer le processus d'extraction.")