# HEC Slide Generator – DevBook

## 1. Objectif

Application locale macOS (Apple Silicon) qui génère des présentations **PowerPoint (.pptx)** à partir d’un texte structuré, via une interface web **Streamlit**.

Deux modes principaux :

- **Texte Seul (Instant)** : slides texte seul, avec possibilité d’insérer des **photos locales** préparées à l’avance.
- **IA Locale (Stable Diffusion)** : génération d’images automatiques en local, optimisée pour Apple Silicon (MPS + fallback CPU).

## 2. Format d’entrée

Texte collé dans l’interface, au format :

```text
TITRE: [Titre de la slide]
POINTS:
- Point 1
- Point 2
VISUEL: [Description de l'image souhaitée en langage naturel]  # Optionnel
```

- `TITRE` : un titre par slide.
- `POINTS` : une liste de puces (une ligne par tiret `-`).
- `VISUEL` :
  - **ignoré pour les images en mode Texte Seul**,
  - utilisé comme **prompt IA** en mode IA Locale.

## 3. Mapping des images

### 3.1. Mode Texte Seul (photos locales)

- Dans la colonne de configuration, uploadez une ou plusieurs images dans
  **“Photos pour les slides (slide 1, slide 2, etc.)”**.
- Le positionnement se fait **par numéro au début du nom de fichier (1 à 99)** :
  - `1 campus.jpg` ou `01 campus.jpg` → image pour le **slide 1**
  - `2 amphi.png` → image pour le **slide 2**
  - `10 salle.png` → image pour le **slide 10**
- Le **titre de la slide** et le reste du nom du fichier n’influencent pas le mapping.
- Si aucune image ne correspond au numéro d’un slide, ce slide sera **texte seul**.

### 3.2. Mode IA Locale (Stable Diffusion)

- Si des images sont uploadées et numérotées (`1 ...`, `2 ...`, ...), elles ont la **priorité** :
  - la slide 1 utilisera l’image `1 ...` si elle existe,
  - la slide 2 utilisera l’image `2 ...`, etc.
- Pour les slides **sans image uploadée** :
  - si `VISUEL` est renseigné, une image est générée via Stable Diffusion,
  - la checkbox “Générer une image pour chaque slide” contrôle si toutes les slides sont illustrées ou seulement la première.

## 4. Fichiers principaux

- `app_launcher.py`  
  Interface Streamlit :
  - sélection du mode (Texte Seul / IA Locale),
  - upload des images locales,
  - zone de texte avec exemple insérable (4 slides),
  - routage vers les fonctions backend et bouton de téléchargement `.pptx`.

- `backend_engines.py`  
  Logique métier :
  - création et mise en forme des slides via `python-pptx`,
  - `generate_text_only(...)` : gestion du mapping images ↔ numéros de fichier,
  - `generate_local_ai(...)` : gestion du mapping images ↔ numéros de fichier puis fallback IA (Stable Diffusion) si besoin.

- `requirements.txt`  
  Dépendances Python (Streamlit, python-pptx, requests, torch, diffusers, transformers, accelerate, etc.).

## 5. Installation

Dans un environnement Python adapté (3.10+ recommandé) :

```bash
pip install -r requirements.txt
```

## 6. Lancement de l’application

```bash
streamlit run app_launcher.py
```

Puis ouvrir l’URL locale affichée (ex. `http://localhost:8501`).
