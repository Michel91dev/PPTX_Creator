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
        ["Texte Seul (Instant)", "IA Locale (Stable Diffusion)"],
        index=0
    )

    # Options avancées pour le mode IA Locale
    ia_steps = 30
    ia_per_slide = False
    if "IA Locale" in mode:
        ia_steps = st.slider(
            "Qualité IA (nombre de pas d'inférence)",
            min_value=10,
            max_value=50,
            value=30,
            step=5,
            help="Plus le nombre de pas est élevé, plus l'image est détaillée mais lente à générer."
        )
        ia_per_slide = st.checkbox(
            "Générer une image pour chaque slide",
            value=False,
            help="Si décoché, seule la première slide aura une image IA (plus rapide pour les tests)."
        )

    # Photos optionnelles par slide (utilisées uniquement en mode Texte Seul)
    uploaded_images = st.file_uploader(
        "Photos pour les slides (slide 1, slide 2, etc.)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="La 1ère image sera utilisée pour le slide 1, la 2ème pour le slide 2, etc. Si le TITRE commence par '3 -', on utilisera la 3ème image."
    )

    st.info("""
    **Format attendu pour le copier-coller :**

    TITRE: Titre de la slide
    POINTS:
    - Premier point clé
    - Deuxième point clé
    VISUEL: description courte de l'image souhaitée **en langage naturel**

    Exemples de VISUEL pour l'IA locale :
    - "photo aérienne du campus HEC au lever du soleil, style réaliste corporate"
    - "illustration flat design minimaliste d'étudiants travaillant en groupe dans une salle de cours moderne"
    - "vue isométrique d'un bâtiment de business school entouré d'arbres, couleurs sobres bleu et gris"

    Vous pouvez aussi mettre une **URL d'image** (http...) si vous utilisez le mode "Texte Seul (Instant)".
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
                # On passe la liste brute des fichiers uploadés au backend
                resultat_pptx = engine.generate_text_only(data, image_files=uploaded_images)

            elif "IA Locale" in mode:
                # Deux barres de progression spécifiques pour l'IA
                progress_global = st.progress(0, text="Initialisation IA...")
                progress_image = st.progress(0, text="En attente de la première image...")


                def update_prog(val, txt):
                    # Barre 1 : progression globale (0-100%)
                    progress_global.progress(val, text=f"Progression globale : {int(val * 100)}%")

                    # Barre 2 : mise à jour image par image avec le texte détaillé
                    progress_image.progress(1.0, text=txt)


                resultat_pptx = engine.generate_local_ai(data, update_prog, ia_steps, ia_per_slide)
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