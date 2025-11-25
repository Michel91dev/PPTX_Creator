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
st.title("🚁 Générateur de Présentations PowerPoint")
st.markdown("---")

col_config, col_content = st.columns([1, 2])

with col_config:
    st.header("1. Configuration")
    st.markdown("**Mode actif : Texte Seul (stable pour usage en ligne)**")

    # Photos optionnelles par slide
    uploaded_images = st.file_uploader(
        "Photos pour les slides (slide 1, slide 2, etc.)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="La 1ère image sera utilisée pour le 1er slide, la 2ème pour le 2ème, etc. Le titre des slides et le nom du fichier n'influencent pas le mapping, seul l'ordre compte."
    )

    with st.expander("Format du texte à coller (TITRE / POINTS / VISUEL)"):
        st.markdown("""
        **Format de base :**

        ```text
        TITRE: Titre de la slide
        POINTS:
        - Premier point clé
        - Deuxième point clé
        VISUEL: description courte de l'image souhaitée en langage naturel (optionnel)
        ```

        Si vous êtes en **mode Texte Seul (Instant)**, la ligne `VISUEL:` est ignorée pour les images
        (elle reste là pour compatibilité avec le mode IA Locale).
        """)

    with st.expander("Images en mode Texte Seul (fichiers locaux)"):
        st.markdown("""
        - Uploadez une ou plusieurs images dans la zone **"Photos pour les slides"**.
        - Le positionnement se fait **par numéro au début du nom du fichier** (1 à 99) :
          - `1 campus.jpg` ou `01 campus.jpg` → image pour le **slide 1**
          - `2 amphi.png` → image pour le **slide 2**
          - `10 salle.png` → image pour le **slide 10**
        - Le **titre de la slide** et le reste du nom du fichier n'influencent pas le mapping.
        - Si aucun fichier ne commence par le numéro d'une slide donnée, cette slide sera en **texte seul**.
        """)

    with st.expander("VISUEL et mode IA Locale (Stable Diffusion)"):
        st.markdown("""
        En mode **IA Locale (Stable Diffusion)**, le contenu après `VISUEL:` est utilisé comme
        **prompt IA** pour générer l'image.

        Exemples de VISUEL pour l'IA locale :

        - `photo aérienne du campus HEC au lever du soleil, style réaliste corporate`
        - `illustration flat design minimaliste d'étudiants travaillant en groupe dans une salle de cours moderne`
        - `vue isométrique d'un bâtiment de business school entouré d'arbres, couleurs sobres bleu et gris`

        Plus la description est précise (type d'image, sujet, style, ambiance), plus le résultat sera pertinent.
        """)

with col_content:
    st.header("2. Contenu")

    # Exemple de 4 slides que l'utilisateur peut insérer d'un clic
    example_text = (
        "TITRE: 1 - Expérience utilisateur\n"
        "POINTS:\n"
        "- Coller un texte structuré TITRE / POINTS / VISUEL dans l'interface\n"
        "- Choisir le mode 'Texte Seul' ou 'IA Locale' en un clic\n"
        "- Ajuster la qualité des images avec le slider de pas d'inférence\n"
        "VISUEL: illustration simple d'une interface web avec deux colonnes, style moderne\n\n"

        "TITRE: 2 - Mode Texte Seul\n"
        "POINTS:\n"
        "- TITRE et POINTS uniquement, VISUEL ignoré pour les images\n"
        "- Uploader des images nommées '1 campus.jpg', '2 amphi.png', etc.\n"
        "- Chaque numéro au début du fichier correspond à un numéro de slide\n"
        "VISUEL: description optionnelle, utile surtout pour le mode IA Locale\n\n"

        "TITRE: 3 - Mode IA Locale (Stable Diffusion)\n"
        "POINTS:\n"
        "- Utiliser VISUEL pour décrire l'image souhaitée en langage naturel\n"
        "- Cocher 'Générer une image pour chaque slide' si besoin\n"
        "- Laisser les champs VISUEL vides sur les slides sans image IA\n"
        "VISUEL: photo réaliste du campus HEC au lever du soleil, style corporate\n\n"

        "TITRE: 4 - Bonnes pratiques\n"
        "POINTS:\n"
        "- Limiter chaque slide à une idée principale\n"
        "- Utiliser des bullets courts et lisibles\n"
        "- Garder un ton cohérent sur toute la présentation\n"
        "VISUEL: illustration minimaliste d'un tableau blanc avec trois puces et un check vert\n"
    )

    if st.button("Insérer un exemple de 4 slides"):
        st.session_state["hec_example_text"] = example_text

    raw_input = st.text_area(
        "Collez ici le contenu généré par votre IA (ChatGPT/Claude) :",
        height=400,
        value=st.session_state.get("hec_example_text", ""),
        placeholder=(
            "TITRE: Titre de la slide\n"
            "POINTS:\n"
            "- Premier point clé\n"
            "- Deuxième point clé\n"
            "VISUEL: description courte de l'image souhaitée (optionnel)\n"
        ),
    )

    if st.button("Lancer la génération", type="primary"):
        if not raw_input:
            st.error("Veuillez coller du texte.")
        else:
            data = parse_input_text(raw_input)
            st.success(f"{len(data)} slides détectées.")

            resultat_pptx = None
            # Mode unique : Texte Seul
            resultat_pptx = engine.generate_text_only(data, image_files=uploaded_images)

            # BOUTON TELECHARGEMENT FINAL
            if resultat_pptx:
                st.balloons()
                st.download_button(
                    label="📥 Télécharger le Powerpoint (.pptx)",
                    data=resultat_pptx,
                    file_name="Presentation_HEC_Gen.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )

    # Mention auteur / date
    st.markdown("---")
    st.caption("Application 'Générateur de Présentations PowerPoint' développée par Michel Safars pour sa belle Béatrice – 24 novembre 2025, 22h15.")