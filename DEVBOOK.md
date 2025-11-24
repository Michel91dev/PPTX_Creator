# HEC Slide Generator – DevBook

## 1. Objectif

Application locale macOS (Apple Silicon) qui génère des présentations **PowerPoint (.pptx)** à partir d’un texte structuré, via une interface web **Streamlit**, avec 3 modes :

- Mode 1 : Texte seul (slides sans images).
- Mode 2 : Images Web (URLs).
- Mode 3 : IA locale (Stable Diffusion sur `mps` en `float16`).

Format d’entrée attendu :

```text
TITRE: [Titre slide]
POINTS:
- Point 1
- Point 2
VISUEL: [URL ou Prompt IA]
```

## 2. Architecture

- `app_launcher.py` : interface Streamlit, parsing du texte, choix du mode, bouton de téléchargement.
- `backend_engines.py` : logique PPTX + 3 moteurs (Texte, Web images, IA locale).
- `requirements.txt` : dépendances Python.

## 3. Installation

```bash
pip install -r requirements.txt
```

## 4. Lancement

```bash
streamlit run app_launcher.py
```

Ouvrir l’URL locale (ex. `http://localhost:8501`).
