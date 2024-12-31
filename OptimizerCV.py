import streamlit as st
import openai
from openai import OpenAIError
from typing import Dict, Tuple

# Configuration de la clé API
if "OPENAI_API_KEY" not in st.session_state:
    st.session_state.OPENAI_API_KEY = None

def init_openai():
    api_key = st.sidebar.text_input("Entrez votre clé API OpenAI", type="password")
    if api_key:
        st.session_state.OPENAI_API_KEY = api_key
        openai.api_key = api_key
        return True
    return False

class CVEvaluator:
    def evaluate_cv(self, cv: str, job_description: str) -> str:
        prompt = f"""Mets-toi dans la peau d'un recruteur. J'ai reçu ce CV et je veux que tu m'aides à l'évaluer. Tu vas me faire une analyse en 4 parties.

Partie 1 : Un résumé rapide du profil du candidat
Partie 2 : Les points forts du profil par rapport à ma fiche de poste
Partie 3 : Les points de vigilance du profil par rapport à ma fiche de poste
Partie 4 : Une note sur 100 du profil avec une synthèse de son analyse

CV:
{cv}

Fiche de poste:
{job_description}"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response['choices'][0]['message']['content']
        except OpenAIError as e:
            return f"Erreur lors de l'appel à OpenAI : {e}"

class CVOptimizer:
    def optimize_cv(self, experiences: str, job_description: str) -> str:
        prompt = f"""Agis en tant qu'expert en recrutement et optimise mon CV pour qu'il réponde précisément à l'offre d'emploi suivante. N'ajoute aucune nouvelle expérience professionnelle au CV.

Ajoute en dessous du titre une liste concise et impactante en moins de 70 caractères des 3 atouts clés du CV par rapport à l'offre d'emploi intitulée [Mes atouts clés].

En dessous, liste 6 compétences de mon CV qui correspondent à l'offre d'emploi en les intitulant [Compétences clés].

Intègre les 10 mots-clés essentiels de l'annonce dans ta proposition que tu inséreras dans l'expérience professionnelle ou les atouts clés.

Assure-toi de mettre en avant les missions de mes expériences professionnelles en lien avec les missions de l'offre d'emploi.

Mets en valeur [en gras] les résultats chiffrés et qualitatifs dans chacune des expériences professionnelles sans créer une partie distincte. Surtout n'ajoute aucun résultat dans les expériences professionnelles.

Corrige les fautes d'orthographe et coquilles.

CV:
{experiences}

Offre d'emploi:
{job_description}"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response['choices'][0]['message']['content']
        except OpenAIError as e:
            return f"Erreur lors de l'appel à OpenAI : {e}"

def main():
    st.title("Optimiseur de CV avec Évaluation")
    
    # Vérification de la clé API avant tout
    if not init_openai():
        st.warning("Veuillez entrer votre clé API OpenAI dans la barre latérale pour continuer")
        return
    
    if 'experiences' not in st.session_state:
        st.session_state.experiences = {}
    
    with st.expander("Ajouter une expérience"):
        titre = st.text_input("Titre du poste")
        description = st.text_area("Description de l'expérience")
        dates = st.text_input("Période (ex: 2020-2023)")
        if st.button("Ajouter l'expérience"):
            if titre and description and dates:
                st.session_state.experiences[titre] = {
                    "description": description,
                    "dates": dates
                }
                st.success("Expérience ajoutée avec succès!")
            else:
                st.error("Veuillez remplir tous les champs")
    
    st.subheader("Vos expériences")
    for titre, info in st.session_state.experiences.items():
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.write(f"**{titre}** ({info['dates']})")
            st.write(info['description'])
        with col2:
            if st.button("🗑️", key=f"delete_{titre}"):
                del st.session_state.experiences[titre]
                st.rerun()
    
    st.divider()
    
    st.subheader("Optimisation et Évaluation")
    job_description = st.text_area("Collez l'offre d'emploi ici")
    
    if st.button("Analyser et Optimiser"):
        if not job_description:
            st.error("Veuillez coller une offre d'emploi")
            return
            
        if not st.session_state.experiences:
            st.error("Veuillez ajouter au moins une expérience")
            return
        
        with st.spinner("Analyse en cours..."):
            formatted_experiences = "\n".join([
                f"{titre} ({info['dates']})\n{info['description']}\n"
                for titre, info in st.session_state.experiences.items()
            ])
            
            # Évaluation initiale
            evaluator = CVEvaluator()
            st.subheader("Évaluation du CV Initial")
            initial_evaluation = evaluator.evaluate_cv(formatted_experiences, job_description)
            st.markdown(initial_evaluation)
            
            # Optimisation
            optimizer = CVOptimizer()
            optimized_cv = optimizer.optimize_cv(formatted_experiences, job_description)
            
            st.subheader("CV Optimisé")
            st.markdown(optimized_cv)
            
            # Évaluation après optimisation
            st.subheader("Évaluation du CV Optimisé")
            final_evaluation = evaluator.evaluate_cv(optimized_cv, job_description)
            st.markdown(final_evaluation)
            
            # Boutons de téléchargement
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    "📄 CV Optimisé",
                    optimized_cv,
                    "cv_optimise.txt",
                    mime="text/plain"
                )
            with col2:
                st.download_button(
                    "📊 Évaluation Initiale",
                    initial_evaluation,
                    "evaluation_initiale.txt",
                    mime="text/plain"
                )
            with col3:
                st.download_button(
                    "📈 Évaluation Finale",
                    final_evaluation,
                    "evaluation_finale.txt",
                    mime="text/plain"
                )

if __name__ == "__main__":
    main()
