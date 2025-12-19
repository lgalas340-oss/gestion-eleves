import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Mise à jour Base Élèves", layout="centered")

st.title("🔄 Mise à jour de la Base Élèves")
st.write("Importez vos fichiers A (source) et B (destination) pour fusionner les données.")

# 1. Zone de téléchargement des fichiers
col1, col2 = st.columns(2)

with col1:
    file_a = st.file_uploader("Fichier A (Source Élèves .csv)", type=['csv'])
with col2:
    file_b = st.file_uploader("Fichier B (Base Globale .csv)", type=['csv'])

if file_a and file_b:
    try:
        # 2. Lecture des fichiers chargés en mémoire
        # On utilise cp1252 pour gérer les accents Excel
        df_a = pd.read_csv(file_a, sep=';', encoding='cp1252', encoding_errors='replace')
        df_b = pd.read_csv(file_b, sep=';', encoding='cp1252', encoding_errors='replace')

        # Nettoyage des colonnes
        df_a.columns = df_a.columns.str.strip()
        df_b.columns = df_b.columns.str.strip()

        # Bouton pour lancer le traitement
        if st.button("🚀 Lancer la fusion"):
            
            # --- TRAITEMENT ---
            # Extraction par position (A)
            df_a_extrait = df_a.iloc[:, [1, 2, 10]].copy()
            df_a_extrait.columns = ['NOM', 'PRENOM', 'BADGE']
            df_a_extrait['FAMILLE'] = 'eleve'

            # Nettoyage Badge
            df_a_extrait['BADGE'] = df_a_extrait['BADGE'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.zfill(13)

            # Filtrage B (On garde tout sauf 'eleve')
            if 'FAMILLE' in df_b.columns:
                df_b['FAMILLE'] = df_b['FAMILLE'].fillna('').astype(str).str.strip()
                df_b_conserve = df_b[df_b['FAMILLE'].str.lower() != 'eleve'].copy()
            else:
                df_b_conserve = df_b

            # Fusion
            df_final = pd.concat([df_b_conserve, df_a_extrait], ignore_index=True)
            df_final = df_final[['NOM', 'PRENOM', 'FAMILLE', 'BADGE']]

            # --- COMPTE RENDU ---
            st.success("Traitement réussi !")
            
            # Affichage des statistiques sous forme de cartes
            c1, c2, c3 = st.columns(3)
            c1.metric("Élèves importés (A)", len(df_a_extrait))
            c2.metric("Lignes conservées (B)", len(df_b_conserve))
            c3.metric("Total final", len(df_final))

            # Aperçu du résultat
            st.write("### Aperçu du nouveau fichier B")
            st.dataframe(df_final.head(10))

            # --- TÉLÉCHARGEMENT ---
            # Conversion du DataFrame en CSV (mémoire)
            output = io.BytesIO()
            df_final.to_csv(output, index=False, sep=';', encoding='utf-8-sig')
            processed_data = output.getvalue()

            st.download_button(
                label="📥 Télécharger le fichier B mis à jour",
                data=processed_data,
                file_name="B_mis_a_jour.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Erreur lors de la lecture des fichiers : {e}")
else:
    st.info("Veuillez importer les deux fichiers CSV pour commencer.")