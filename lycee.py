import streamlit as st
import pandas as pd
import io
import time

# Configuration de la page
st.set_page_config(
    page_title="UpdateBase Pro | Gestion Lycée",
    page_icon="🎓",
    layout="wide"
)

# Style CSS personnalisé pour améliorer l'apparence
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #004a99;
        color: white;
        font-weight: bold;
    }
    .status-box {
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Barre latérale (Sidebar) pour les instructions
with st.sidebar:
    st.image("https://www.gstatic.com/images/branding/product/2x/forms_96dp.png", width=80)
    st.title("Aide & Support")
    st.info("""
    **Instructions :**
    1. Déposez le fichier d'export des élèves (A).
    2. Déposez votre base de badge actuelle (B).
    3. Cliquez sur le bouton bleu pour fusionner.
    4. Téléchargez le résultat nettoyé.
    """)
    st.divider()
    st.caption("Version Pro v2.0 - Sécurisé localement")

# En-tête principal
st.title("🎓 Système de Mise à Jour des Badges Élèves")
st.subheader("Outil d'automatisation pour la gestion des accès")

st.divider()

# Section de téléchargement
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### 📄 Fichier Source (A)")
    file_a = st.file_uploader("Exportation Vie Scolaire / SI", type=['csv'], help="Le fichier contenant les nouveaux élèves et leurs numéros de carte.")

with col_b:
    st.markdown("### 🗄️ Base de Destination (B)")
    file_b = st.file_uploader("Fichier actuel des badges", type=['csv'], help="Le fichier complet contenant agents, profs et anciens élèves.")

# Traitement des données
if file_a and file_b:
    st.success("✅ Fichiers chargés avec succès.")
    
    if st.button("⚡ EXECUTER LA MISE À JOUR"):
        with st.status("Traitement des bases de données...", expanded=True) as status:
            try:
                # Simulation de chargement pour le feeling pro
                time.sleep(0.5)
                st.write("Lecture des encodages Windows...")
                df_a = pd.read_csv(file_a, sep=';', encoding='cp1252', encoding_errors='replace')
                df_b = pd.read_csv(file_b, sep=';', encoding='cp1252', encoding_errors='replace')
                
                st.write("Filtrage des catégories...")
                df_a.columns = df_a.columns.str.strip()
                df_b.columns = df_b.columns.str.strip()

                # Extraction (Position : 1=Nom, 2=Prénom, 10=Badge)
                df_a_extrait = df_a.iloc[:, [1, 2, 10]].copy()
                df_a_extrait.columns = ['NOM', 'PRENOM', 'BADGE']
                df_a_extrait['FAMILLE'] = 'eleve'
                
                # Nettoyage Badge
                df_a_extrait['BADGE'] = df_a_extrait['BADGE'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.zfill(13)

                # Conservation des autres familles
                if 'FAMILLE' in df_b.columns:
                    df_b['FAMILLE'] = df_b['FAMILLE'].fillna('').astype(str).str.strip()
                    df_b_conserve = df_b[df_b['FAMILLE'].str.lower() != 'eleve'].copy()
                else:
                    df_b_conserve = df_b

                # Fusion
                df_final = pd.concat([df_b_conserve, df_a_extrait], ignore_index=True)
                df_final = df_final[['NOM', 'PRENOM', 'FAMILLE', 'BADGE']]
                
                status.update(label="Mise à jour terminée !", state="complete", expanded=False)

                # --- AFFICHAGE DU COMPTE RENDU PRO ---
                st.divider()
                st.markdown("### 📊 Rapport de modification")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Élèves ajoutés", len(df_a_extrait), delta=f"+{len(df_a_extrait)}")
                m2.metric("Personnel conservé", len(df_b_conserve))
                m3.metric("Total base finale", len(df_final))

                # Zone de téléchargement avec style
                st.divider()
                st.info("Le nouveau fichier est prêt. Les doublons potentiels de la catégorie 'élève' ont été supprimés et remplacés par les données du fichier A.")
                
                output = io.BytesIO()
                df_final.to_csv(output, index=False, sep=';', encoding='utf-8-sig')
                
                st.download_button(
                    label="📥 TÉLÉCHARGER LE FICHIER B MIS À JOUR",
                    data=output.getvalue(),
                    file_name="Base_Badges_MAJ.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"Une erreur technique est survenue : {e}")
else:
    # État vide avec guide visuel
    st.warning("⚠️ En attente des fichiers pour débuter l'analyse.")