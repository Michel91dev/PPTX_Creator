# Générateur de Présentations PowerPoint

Application locale et en ligne permettant de générer des présentations **PowerPoint (.pptx)** à partir d’un texte structuré, avec deux modes :

- **Texte Seul (Instant)** : slides texte seul, avec possibilité d’ajouter des photos locales numérotées.
- **IA Locale (Stable Diffusion)** : génération d’images automatiques en local sur Mac Apple Silicon.

## 1. Format du texte d’entrée

Le texte à coller dans l’interface doit suivre ce format répété pour chaque slide :

```text
TITRE: [Titre de la slide]
POINTS:
- Point 1
- Point 2
VISUEL: [Description courte de l’image souhaitée en langage naturel]  # Optionnel
```

- `TITRE` : un titre par slide.
- `POINTS` : une liste de puces (une ligne par tiret `-`).
- `VISUEL` :
  - **ignoré pour les images en mode Texte Seul**, mais conservé pour compatibilité.
  - utilisé comme **prompt IA** en mode IA Locale (Stable Diffusion).

## 2. Images locales (mode Texte Seul)

En mode **Texte Seul (Instant)**, les images viennent uniquement des fichiers uploadés dans l’interface :

- Zone : **"Photos pour les slides (slide 1, slide 2, etc.)"**.
- Le positionnement se fait **par numéro au début du nom du fichier (1 à 99)** :
  - `1 campus.jpg` ou `01 campus.jpg` → image pour le **slide 1**
  - `2 amphi.png` → image pour le **slide 2**
  - `10 salle.png` → image pour le **slide 10**
- Le reste du nom de fichier et le titre de la slide n’influencent pas le mapping.
- Si aucune image ne correspond au numéro d’un slide, ce slide sera **texte seul**.

## 3. IA Locale (Stable Diffusion)

En mode **IA Locale (Stable Diffusion)** :

- Si une image locale est uploadée et commence par `N` (`1..99`), elle a la **priorité** sur l’IA pour la slide `N`.
- Pour les slides **sans image locale** :
  - si `VISUEL` est renseigné, une image est générée via Stable Diffusion (MPS float16 avec fallback CPU float32).
  - une option **"Tester sur un seul slide (première image uniquement)"** permet de ne générer que la première slide pour valider le rendu.

## 4. Fichiers principaux

- `app_launcher.py`  
  Interface Streamlit : configuration, upload d’images, zone de texte, boutons de génération et téléchargement.

- `backend_engines.py`  
  Logique métier : création des slides avec `python-pptx`, mapping images ↔ numéros de fichier, génération IA via `diffusers` + `torch`.

- `requirements.txt`  
  Liste des dépendances Python.

- `DEVBOOK.md`  
  Documentation plus détaillée sur l’architecture et le fonctionnement.

## 5. Installation

Dans un environnement Python (3.10+ recommandé) :

```bash
pip install -r requirements.txt
```

## 6. Lancement en local

```bash
python3 -m streamlit run app_launcher.py
```

Ouvrir ensuite l’URL locale affichée (ex. `http://localhost:8501`).

## 7. Auteur

Application "Générateur de Présentations PowerPoint" développée par **Michel Safars**, version stable du 24 novembre 2025 (commit `2025 1124 2219 Dernières améliorations UI+IA OK`).
