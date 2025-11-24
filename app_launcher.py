import streamlit as st
import backend_engines as engine

# Configuration de la page
st.set_page_config(page_title="HEC Slide Generator", layout="wide")


# --- FONCTION DE PARSING (TEXTE -> DONNÉES) ---
def parse_input_text(raw_text):
    """Transforme le texte copié-collé en structure de données"""
    slides = []
    current_slide = {}

    # On découpe par blocs de slides (séparateur double saut de ligne ou mot clé)
    lines = raw_text.split('\n')

    for line in lines:
        line = line.strip()
        if not line: continue

        if line.upper().startswith("TITRE:"):
            if current_slide: slides.append(current_slide)  # Save previous
            current_slide = {"titre": line.replace("TITRE:", "").strip(), "points": [], "visuel": ""}

        elif line.upper().startswith("POINTS:"):
            pass  # Juste un marqueur

        elif line.startswith("-") or line.startswith("•"):
            if "points" in current_slide:
                current_slide["points"].append(line.lstrip("-• ").strip())

        elif line.upper().startswith("VISUEL:"):
            # Peut être une URL ou un Prompt selon le mode
            current_slide["visuel"] = line.replace("VISUEL:", "").strip()

    if current_slide: slides.append(current_slide)  # Save last
    return slides


# --- INTERFACE UTILISATEUR ---
st.title("🚁 Générateur de Présentation HEC")
st.markdown("---")

col_config, col_content = st.columns([1, 2])

with col_config:
    st.header("1. Configuration")
    mode = st.radio(
        "Choisir le moteur :",
        ["Texte Seul (Instant)", "Images Web (URLs)", "IA Locale (Stable Diffusion)"],
        index=0
    )

    st.info("""
    **Format attendu pour le copier-coller :**

    TITRE: Titre de la slide
    POINTS:
    - Premier point clé
    - Deuxième point clé
    VISUEL: (URL ou Prompt IA)
    """)

with col_content:
    st.header("2. Contenu")
    raw_input = st.text_area(
        "Collez ici le contenu généré par votre IA (ChatGPT/Claude) :",
        height=400,
        placeholder="TITRE: Introduction\nPOINTS:\n- Contexte\n- Enjeux\nVISUEL: une photo de bureau..."
    )

    if st.button("Lancer la génération", type="primary"):
        if not raw_input:
            st.error("Veuillez coller du texte.")
        else:
            data = parse_input_text(raw_input)
            st.success(f"{len(data)} slides détectées.")

            resultat_pptx = None

            # ROUTAGE SELON LE MODE
            if "Texte" in mode:
                resultat_pptx = engine.generate_text_only(data)

            elif "Web" in mode:
                with st.spinner("Téléchargement des images..."):
                    resultat_pptx = engine.generate_web_images(data)

            elif "IA Locale" in mode:
                # Deux barres de progression spécifiques pour l'IA
                progress_global = st.progress(0, text="Initialisation IA...")
                progress_image = st.progress(0, text="En attente de la première image...")


                def update_prog(val, txt):
                    # Barre 1 : progression globale (0-100%)
                    progress_global.progress(val, text=f"Progression globale : {int(val * 100)}%")

                    # Barre 2 : mise à jour image par image avec le texte détaillé
                    progress_image.progress(1.0, text=txt)


                resultat_pptx = engine.generate_local_ai(data, update_prog)
                progress_global.empty()
                progress_image.empty()

            # BOUTON TELECHARGEMENT FINAL
            if resultat_pptx:
                st.balloons()
                st.download_button(
                    label="📥 Télécharger le Powerpoint (.pptx)",
                    data=resultat_pptx,
                    file_name="Presentation_HEC_Gen.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )